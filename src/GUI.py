import tkinter as tk
from tkinter import ttk

import os
import numpy as np
import copy
import subprocess
import queue
from typing import Any, Union, Callable

import matplotlib
matplotlib.rcParams["path.simplify"] = True
matplotlib.rcParams["path.simplify_threshold"] = 1.0
matplotlib.rcParams["image.interpolation"] = "none"
matplotlib.rcParams['agg.path.chunksize'] = 100000
# matplotlib.rcParams["image.interpolation_stage"] = "data"
matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib import widgets, text
from matplotlib.text import Text
from matplotlib.backend_bases import MouseButton
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.transforms as transforms
from PIL import Image

from Misc import *
from Callbacks import *
from MarkingPoint import *
from pyLMDCalculation import *
from PictureData import *
from ProgressBarWindow import *
from pyLMDSpinboxParameter import *
import CalculationThreads

Image.MAX_IMAGE_PIXELS=None

window=tk.Tk()
window.wm_title("Window title")


def test_Func(inputData: str) -> bool:
    print(inputData)
    print(type(inputData))
    if type(inputData) is not str:
        return False
    if len(inputData) == 0:
        return False
    if not inputData.isdigit():
        return False


    return True

class Gui():
    def __init__(self, picData1 = None, picData2 = None, slicingFactor: int = 1):
        window.geometry(str(Gui.__MIN_WINDOW_WIDTH) + "x" + str(Gui.__MIN_WINDOW_HEIGHT))
        window.minsize(Gui.__MIN_WINDOW_WIDTH, Gui.__MIN_WINDOW_HEIGHT)

        is_Type(slicingFactor, int)
        is_Type_If_Not_None(picData1, np.ndarray)
        is_Type_If_Not_None(picData2, np.ndarray)

        self.__pictureData = PictureData(picData1=picData1, picData2=picData2, slicingFactor=slicingFactor)

        if self.__pictureData.get_Data_Slicing_Factor() > 1:
            if self.__pictureData.get_Picture_Data(PictureData.FIRST_PIC) is not None:
                print("Using sliced pic data 1 on GUI: " + str(self.__pictureData.get_Picture_Data_Sliced(PictureData.FIRST_PIC).shape)
                    + " | Orig. size: " + str(self.__pictureData.get_Picture_Data(PictureData.FIRST_PIC).shape), flush=True)
            if self.__pictureData.get_Picture_Data(PictureData.SEC_PIC) is not None:
                print("Using sliced pic data 2 on GUI: " + str(self.__pictureData.get_Picture_Data_Sliced(PictureData.SEC_PIC).shape)
                    + " | Orig. size: " + str(self.__pictureData.get_Picture_Data(PictureData.SEC_PIC).shape), flush=True)

        self.__callbacks = Callbacks(self)
        self.__validations = Validations(self.__callbacks)
        self.__origAxes=plt.gca()
        self.__origFigure=plt.gcf()
        self.__calPointsLabel = []
        self.__calPointsRB = []
        self.__showPictureRB = []
        self.__sameAsPictureInputPathRB = []
        self.__markingPoints = []
        for index in range(3):
            self.__markingPoints.append(MarkingPoint(origAxes=self.__origAxes, origFigure=self.__origFigure, position=[ 0.0, 0.0 ],
                                                     color=self.__calPointsColor[index][1]))
            self.__markingPoints[index].hide()
        self.__openPictureOne: str = ""
        self.__openPictureTwo: str = ""

        # Configure plot
        self.__im = self.__origAxes.imshow([ [ 0 ] ], aspect="equal", cmap="binary", interpolation="none")
        if self.__pictureData.is_Picture_Data_Loaded(PictureData.FIRST_PIC):
            self.__im = self.__origAxes.imshow(self.__pictureData.get_Picture_Data_Sliced(PictureData.FIRST_PIC), aspect="equal",
                                               interpolation="none")#, cmap="binary")
        elif self.__pictureData.is_Picture_Data_Loaded(PictureData.SEC_PIC):
            self.__im = self.__origAxes.imshow(self.__pictureData.get_Picture_Data_Sliced(PictureData.SEC_PIC), aspect="equal",
                                               interpolation="none")#, cmap="binary")
        # Disable unnecessary features / optimize parameters
        self.__origAxes.set_box_aspect(1.0)
        self.__origAxes.set_position(( 0.0, 0.0, 1.0, 1.0 ))
        self.__origAxes.set_axis_off()
        self.__origAxes.margins(0)
        self.__origAxes.grid(False)
        self.__origAxes.set_xticks([])
        self.__origAxes.set_yticks([])
        plt.style.use("fast")

        # FigureCanvasTkAgg converts the pyPlot objects to a compatible Tkinter widget
        # At the end the plot can be used like a regular Tkinter widget
        self.__pyPlotCanvas = FigureCanvasTkAgg(self.__origFigure, master=window)
        self.__pyPlotCanvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Main Frame for the widgets
        widgetsFrame=tk.Frame(window)

        # Label frame for the calibration points
        calPointsFrame=tk.LabelFrame(widgetsFrame, text="Calibration points", font=Gui.__LABEL_FRAME_FONT,
                                     padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)
        calPointsFrame.grid_columnconfigure(0, weight=1)
        calPointsFrame.grid_columnconfigure(1, weight=1)


        ##### BEGIN Widgets for calibration point selection #####
        labelConfig = [ ]
        for i in range(3):
            newStr = "Point " + str(i + 1) + ":"
            newStr += f"{0:{self.__SPACE_PREFIX_FOR_COORDS}d}" + "," + f"{0:{self.__SPACE_PREFIX_FOR_COORDS}d}"
            labelConfig.append(newStr)
        counter = 0
        for conf in labelConfig:
            label=tk.Label(calPointsFrame, text=conf, font=("monofont", 10))
            label.grid(row=counter, column=0, padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)
            self.__calPointsLabel.append(label)
            counter += 1

        # Radio buttons for the calibration points
        self.__varRbCalPointsSelection=tk.IntVar()
        rbConfig = [ [ "Override point 1", Gui.__calPointsColor[0][0] ], [ "Override point 2", Gui.__calPointsColor[1][0] ],
                     [ "Override point 3", Gui.__calPointsColor[2][0] ] ]
        counter = 0
        for i in range(len(rbConfig)):
            rButton=tk.Radiobutton(calPointsFrame, text=rbConfig[i][0], variable=self.__varRbCalPointsSelection,
                                value=counter, foreground=rbConfig[i][1])
            rButton.grid(row=counter, column=1, padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)
            if counter == 0:
                rButton.select()
            self.__calPointsRB.append(rButton)
            counter += 1
        calPointsFrame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=Gui.__PADX, pady=Gui.__PADY, ipadx=Gui.__IPADX, ipady=Gui.__IPADY)
        self.__calPointsFrame = calPointsFrame
        ##### END Widgets for calibration point selection #####


        # Radio buttons for the chosen picture, if two are loaded
        self.__showPictureFrame = tk.LabelFrame(widgetsFrame, text = "Show picture", font=Gui.__LABEL_FRAME_FONT,
                                                padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)
        self.__showPictureFrame.grid_columnconfigure(0, weight=1)
        self.__showPictureFrame.grid_columnconfigure(1, weight=1)


        ##### BEGIN Show picture widgets #####
        self.__varRbShowPictureSelection = tk.IntVar()
        showPictureRButton1 = tk.Radiobutton(self.__showPictureFrame, text="Picture 1", variable = self.__varRbShowPictureSelection,
            value = PictureData.FIRST_PIC, command = self.__callbacks.callback_Gui_Rb_Show_Picture_Changed)
        showPictureRButton1.grid(row = 0, column = 0)
        showPictureRButton2 = tk.Radiobutton(self.__showPictureFrame, text="Picture 2", variable = self.__varRbShowPictureSelection,
            value = PictureData.SEC_PIC, command = self.__callbacks.callback_Gui_Rb_Show_Picture_Changed)
        showPictureRButton2.grid(row = 0, column = 1)
        # Activate the radio buttons only, when two pictures were loaded
        if self.__pictureData.is_Picture_Data_Loaded(PictureData.FIRST_PIC) == False:
            showPictureRButton1["state"] = "disabled"
            showPictureRButton1.select()
        if self.__pictureData.is_Picture_Data_Loaded(PictureData.SEC_PIC) == False:
            showPictureRButton2["state"] = "disabled"
        if self.__pictureData.is_Picture_Data_Loaded(PictureData.FIRST_PIC) == False and self.__pictureData.is_Picture_Data_Loaded(PictureData.SEC_PIC):
            showPictureRButton2.select()
        self.__showPictureRB.append(showPictureRButton1)
        self.__showPictureRB.append(showPictureRButton2)
        self.__showPictureFrame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=Gui.__PADX, pady=Gui.__PADY, ipadx=Gui.__IPADX, ipady=Gui.__IPADY)
        ##### END Show picture widgets #####


        # Label frame for the output path
        self.__outputPathFrame = tk.LabelFrame(widgetsFrame, text="Output path", font=Gui.__LABEL_FRAME_FONT,
                                               padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)
        for i in range(3):
            self.__outputPathFrame.grid_columnconfigure(i, weight=[1, 3, 2][i])


        ##### BEGIN Manual outputh path input entry and select path button #####
        self.__pathInputLabel = tk.Label(self.__outputPathFrame, text="Path:")
        self.__pathInputLabel.grid(row=0, column=0, padx=0, pady=Gui.__LABELFRAME_PADY)
        self.__pathInputLabel["state"] = "disabled"
        self.__varPathInputEntry = tk.StringVar()
        self.__pathInputEntry = tk.Entry(self.__outputPathFrame, textvariable=self.__varPathInputEntry)
        self.__pathInputEntry.grid(row=0, column=1, padx=0, pady=Gui.__LABELFRAME_PADY, sticky="ew")
        self.__pathInputEntry["state"] = "disabled"
        self.__selectOutputPathButton=tk.Button(self.__outputPathFrame, text="Select path",
                                                command=self.__callbacks.callback_Gui_Button_Select_Output_Path)
        self.__selectOutputPathButton.grid(row=0, column=2, padx=0, pady=Gui.__LABELFRAME_PADY)
        self.__selectOutputPathButton["state"] = "disabled"

        self.__varRbSameAsPictureInputPath = tk.IntVar()
        sameAsPictureInputPathRButton1 = tk.Radiobutton(self.__outputPathFrame, text="Same as picture 1 path", variable = self.__varRbSameAsPictureInputPath,
            value = 0, command = self.__callbacks.callback_Gui_Rb_Same_As_Picture_Path_Changed)
        sameAsPictureInputPathRButton1.grid(row = 1, column = 1)
        sameAsPictureInputPathRButton2 = tk.Radiobutton(self.__outputPathFrame, text="Same as picture 2 path", variable = self.__varRbSameAsPictureInputPath,
            value = 1, command = self.__callbacks.callback_Gui_Rb_Same_As_Picture_Path_Changed)
        sameAsPictureInputPathRButton2.grid(row = 1, column = 2)

        self.__varManualPathCb = tk.IntVar()
        self.__manualPathCheckBox = tk.Checkbutton(self.__outputPathFrame, text="Manual path", variable=self.__varManualPathCb,
                                          onvalue=1, offvalue=0, command=self.__toggle_Manual_Path_State)
        self.__manualPathCheckBox.grid(row = 1, column = 0)

        if self.__pictureData.is_Picture_Data_Loaded(PictureData.FIRST_PIC) == False:
            sameAsPictureInputPathRButton1["state"] = "disabled"
            sameAsPictureInputPathRButton1.select()
        if self.__pictureData.is_Picture_Data_Loaded(PictureData.SEC_PIC) == False:
            sameAsPictureInputPathRButton2["state"] = "disabled"
        self.__sameAsPictureInputPathRB.append(sameAsPictureInputPathRButton1)
        self.__sameAsPictureInputPathRB.append(sameAsPictureInputPathRButton2)
        self.__outputPathFrame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=Gui.__PADX, pady=Gui.__PADY, ipadx=Gui.__IPADX, ipady=Gui.__IPADY)
        ##### END Manual outputh path input entry and select path button #####


        # Label frame for Etc.
        self.__additionalSettingsFrame = tk.LabelFrame(widgetsFrame, text="Etc.", font=Gui.__LABEL_FRAME_FONT,
                                                       padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)
        for i in range(3):
            self.__additionalSettingsFrame.grid_columnconfigure(i, weight=[ 4, 1, 1 ][i])


        ##### BEGIN Auto increment checkbox #####
        self.__varAutoIncrementRb = tk.IntVar()
        self.__varAutoIncrementRb.set(0)
        self.__autoIncrementRbCheckBox = tk.Checkbutton(self.__additionalSettingsFrame, text=" Auto increment radio buttons", variable=self.__varAutoIncrementRb,
                                          onvalue=1, offvalue=0, command=self.__callbacks.callback_Gui_Toggle_AutoIncrement_Checkbox)
        self.__autoIncrementRbCheckBox.grid(row=0, column=0, padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)
        ##### END Auto increment checkbox #####


        ##### BEGIN Widgets for the slicing factor #####
        variable = tk.StringVar()
        variable.set(str(self.__pictureData.get_Coordinate_Slicing_Factor()))
        optionsList = []
        for i in range(self.__MIN_SLICING_FACTOR, self.__MAX_SLICING_FACTOR + 1):
            optionsList.append(str(i))
        slicingFactorOptionMenu = tk.OptionMenu(self.__additionalSettingsFrame, variable, *optionsList,
                                                command=self.__callbacks.callback_Gui_Options_Menu_Slicing_Factor_Changed)
        slicingFactorOptionMenu.grid(row=0, column=2, padx=0, pady=Gui.__LABELFRAME_PADY)

        slicingFactorOptionMenuPrefix = tk.Label(self.__additionalSettingsFrame, text="Slicing factor:")
        slicingFactorOptionMenuPrefix.grid(row=0, column=1, padx=0, pady=Gui.__LABELFRAME_PADY)
        self.__additionalSettingsFrame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=Gui.__PADX, pady=Gui.__PADY, ipadx=Gui.__IPADX, ipady=Gui.__IPADY)
        ##### END Widgets for the slicing factor #####


        ##### BEGIN Widgets for pyLMD parameter #####
        self.__pylmdParameterFrame = tk.LabelFrame(widgetsFrame, text="pyLMD settings", font=Gui.__LABEL_FRAME_FONT, padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)

        self.__varUseDefaultpylmdSettings = tk.IntVar()
        self.__varUseDefaultpylmdSettings.set(1)
        self.__useDefaultpylmdSettings = tk.Checkbutton(self.__pylmdParameterFrame, text="Use default settings", variable=self.__varUseDefaultpylmdSettings,
                                          command=self.__toggle_Pylmd_Option_Menus_State)
        self.__useDefaultpylmdSettings.grid(row=0, column=0, padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)

        # Option: shape_dilation
        widgetData = [ pyLMDSpinboxParameter(text="Shape dilation", **pyLMDParameterLimits.get_Shape_Dilation_All(),
            callback=self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Shape_Dilation) ]
        # Option: shape_erosion
        widgetData.append(pyLMDSpinboxParameter(text="Shape erosion", **pyLMDParameterLimits.get_Shape_Erosion_All(),
            callback=self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Shape_Erosion))
        # Option: binary_smoothing
        widgetData.append(pyLMDSpinboxParameter(text="Binary smoothing", **pyLMDParameterLimits.get_Binary_Smoothing_All(),
            callback=self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Binary_Smoothing))
        # Option: convolution_smoothing
        widgetData.append(pyLMDSpinboxParameter(text="Convolution smoothing", **pyLMDParameterLimits.get_Convolution_Smoothing_All(),
            callback=self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Convolution_Smoothing))
        # Option: poly_compression_factor
        widgetData.append(pyLMDSpinboxParameter(text="Poly compression factor", **pyLMDParameterLimits.get_Poly_Compression_Factor_All(),
            callback=self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Poly_Compression_Factor))
        # Option: distance_heuristic
        widgetData.append(pyLMDSpinboxParameter(text="Distance Heuristic", **pyLMDParameterLimits.get_Distance_Heuristic_All(),
            callback=self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Distance_Heuristic))

        self.__pylmdOptionMenus = []
        self.__pylmdOptionsMenuSelected = []

        counter = 0
        # Create labels, parameter and option menus
        for currWidgetData in widgetData:
            prefix = tk.Label(self.__pylmdParameterFrame, text=currWidgetData.text + ":")
            prefix.grid(row=[1, 1, 2, 2, 3, 3][counter], column=[0, 2, 0, 2, 0, 2][counter], padx=0, pady=Gui.__LABELFRAME_PADY)
            selected = tk.StringVar()
            selected.set(str(currWidgetData.default))
            option = tk.Spinbox(self.__pylmdParameterFrame, from_=currWidgetData.minVal, to=currWidgetData.maxVal,
                                textvariable=selected, wrap=False, command=None, width=6)
            option["state"] = "disabled" if self.__varUseDefaultpylmdSettings.get() == 1 else "normal"
            option.grid(row=[1, 1, 2, 2, 3, 3][counter], column=[1, 3, 1, 3, 1, 3][counter], padx=Gui.__LABELFRAME_PADX, pady=Gui.__LABELFRAME_PADY)

            counter += 1
            # Save references to the option menus
            # This is necessary to disable and enable these widgets afterwards
            self.__pylmdOptionMenus.append(option)
            self.__pylmdOptionsMenuSelected.append(selected)

        for i in range(4):
            self.__pylmdParameterFrame.grid_columnconfigure(i, weight=[3, 1, 3, 1][i])


        # Due to issues with some Tkinter implementations; the callback can only be attached with the expected
        # functionality after all Spinboxes were created
        # This must not be done with a loop! I don't know why ...
        self.__pylmdOptionMenus[0]["command"] = lambda: widgetData[0].callback(self.__pylmdOptionMenus[0].get())
        self.__pylmdOptionMenus[1]["command"] = lambda: widgetData[1].callback(self.__pylmdOptionMenus[1].get())
        self.__pylmdOptionMenus[2]["command"] = lambda: widgetData[2].callback(self.__pylmdOptionMenus[2].get())
        self.__pylmdOptionMenus[3]["command"] = lambda: widgetData[3].callback(self.__pylmdOptionMenus[3].get())
        self.__pylmdOptionMenus[4]["command"] = lambda: widgetData[4].callback(self.__pylmdOptionMenus[4].get())
        self.__pylmdOptionMenus[5]["command"] = lambda: widgetData[5].callback(self.__pylmdOptionMenus[5].get())

        # Replace an empty input after the focus was lost with the min value
        self.__pylmdOptionMenus[0].bind("<FocusOut>", lambda e: self.__pylmdOptionsMenuSelected[0].set(widgetData[0].minVal) if len(self.__pylmdOptionsMenuSelected[0].get()) == 0 else "")
        self.__pylmdOptionMenus[1].bind("<FocusOut>", lambda e: self.__pylmdOptionsMenuSelected[1].set(widgetData[1].minVal) if len(self.__pylmdOptionsMenuSelected[1].get()) == 0 else "")
        self.__pylmdOptionMenus[2].bind("<FocusOut>", lambda e: self.__pylmdOptionsMenuSelected[2].set(widgetData[2].minVal) if len(self.__pylmdOptionsMenuSelected[2].get()) == 0 else "")
        self.__pylmdOptionMenus[3].bind("<FocusOut>", lambda e: self.__pylmdOptionsMenuSelected[3].set(widgetData[3].minVal) if len(self.__pylmdOptionsMenuSelected[3].get()) == 0 else "")
        self.__pylmdOptionMenus[4].bind("<FocusOut>", lambda e: self.__pylmdOptionsMenuSelected[4].set(widgetData[4].minVal) if len(self.__pylmdOptionsMenuSelected[4].get()) == 0 else "")
        self.__pylmdOptionMenus[5].bind("<FocusOut>", lambda e: self.__pylmdOptionsMenuSelected[5].set(widgetData[5].minVal) if len(self.__pylmdOptionsMenuSelected[5].get()) == 0 else "")

        # Register validation functions
        validateFunction0 = self.__pylmdParameterFrame.register(self.__validations.validate_Spinbox_Input_Shape_Dilation)
        self.__pylmdOptionMenus[0].config(validate="all", validatecommand=(validateFunction0, "%P"))
        validateFunction1 = self.__pylmdParameterFrame.register(self.__validations.validate_Spinbox_Input_Shape_Erosion)
        self.__pylmdOptionMenus[1].config(validate="all", validatecommand=(validateFunction1, "%P"))
        validateFunction2 = self.__pylmdParameterFrame.register(self.__validations.validate_Spinbox_Input_Binary_Smoothing)
        self.__pylmdOptionMenus[2].config(validate="all", validatecommand=(validateFunction2, "%P"))
        validateFunction3 = self.__pylmdParameterFrame.register(self.__validations.validate_Spinbox_Input_Convolution_Smoothing)
        self.__pylmdOptionMenus[3].config(validate="all", validatecommand=(validateFunction3, "%P"))
        validateFunction4 = self.__pylmdParameterFrame.register(self.__validations.validate_Spinbox_Input_Poly_Compression_Factor)
        self.__pylmdOptionMenus[4].config(validate="all", validatecommand=(validateFunction4, "%P"))
        validateFunction5 = self.__pylmdParameterFrame.register(self.__validations.validate_Spinbox_Input_Distance_Heuristic)
        self.__pylmdOptionMenus[5].config(validate="all", validatecommand=(validateFunction5, "%P"))

        self.__pylmdParameterFrame.pack(side=tk.TOP, fill=tk.X, expand=True, padx=Gui.__PADX, pady=Gui.__PADY, ipadx=Gui.__IPADX, ipady=Gui.__IPADY)

        # The object with the calculation parameter | prefilled with the default values
        self.__calculationParameter = pyLMDCalculationParameter(shapeDilation=pyLMDParameterLimits.get_Shape_Dilation_Default(),
            shapeErosion=pyLMDParameterLimits.get_Shape_Erosion_Default(),
            binarySmoothing=pyLMDParameterLimits.get_Binary_Smoothing_Default(),
            convolutionSmoothing=pyLMDParameterLimits.get_Convolution_Smoothing_Default(),
            polyCompressionFactor=pyLMDParameterLimits.get_Poly_Compression_Factor_Default(),
            distanceHeuristic=pyLMDParameterLimits.get_Distance_Heuristic_Default())
        ##### END Widgets for pyLMD parameter #####


        ##### BEGIN Menubar #####
        menubar = tk.Menu(window)
        # Adding File Menu and commands
        menubarFile = tk.Menu(menubar, tearoff = 0)
        menubar.add_cascade(label = "File", menu = menubarFile)
        menubarFile.add_command(label = "Open picture 1 ...", command = self.__callbacks.callback_Gui_Open_Picture_One)
        menubarFile.add_command(label = "Open picture 2 ...", command = self.__callbacks.callback_Gui_Open_Picture_Two)
        menubarFile.add_separator()
        menubarFile.add_command(label = "Exit", command = window.destroy)

        # Display the menu on the GUI
        window.config(menu = menubar)
        ##### END Menubar #####


        # Job list with label
        self.__taskList = tk.Listbox(widgetsFrame, height=4, width=10)
        self.__taskList.xView = True
        self.__taskList.yView = True
        self.__taskListLabel = tk.Label(widgetsFrame, text="Tasks (0) | Finished (0) | Errors (0)")
        self.__taskListLabel.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.__taskList.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=Gui.__PADX, pady=Gui.__PADY, ipadx=Gui.__IPADX, ipady=Gui.__IPADY)

        # Start button
        self.__startCalcButton=tk.Button(widgetsFrame, text="Start calculation", width=40, height=5,
                                  command=self.__callbacks.callback_Gui_Button_Start_Calc_Event)
        self.__startCalcButton["state"] = "disabled"
        self.__startCalcButton.pack(side=tk.TOP, fill=tk.NONE, expand=False)

        # Matplotlib toolbar
        self.__pyPlotToolbar=NavigationToolbar2Tk(self.__pyPlotCanvas, window, pack_toolbar=True)
        self.__pyPlotToolbar.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=False)
        widgetsFrame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Register callbacks
        self.__origFigure.canvas.mpl_connect("key_press_event", self.__callbacks.callback_Gui_Key_Press_Event)
        self.__origFigure.canvas.mpl_connect("button_press_event", self.__callbacks.callback_Gui_Mouse_On_Press_Event)
        self.__origFigure.canvas.mpl_connect("resize_event", self.__callbacks.callback_Gui_Resize_Event)
        self.__origAxes.callbacks.connect("xlim_changed", self.__callbacks.callback_Gui_Xlim_Changed)
        self.__origAxes.callbacks.connect("ylim_changed", self.__callbacks.callback_Gui_Ylim_Changed)

        # Method that handels the resizing of some widgets when the main window will be resized
        window.bind("<Configure>", self.__resize_Gui)

        window.protocol("WM_DELETE_WINDOW", self.__close_Gui)

        self.__pyLMDProcs: queue.Queue = queue.Queue()
        self.__pyLMDStdoutThreads: queue.Queue = queue.Queue()
        self.__pyLMDStderrThreads: queue.Queue = queue.Queue()

        self.__updateTaskOutputThread = threading.Thread(target=self.__update_Task_List)
        self.__updateTaskOutputThreadStopFlag: bool = False
        self.__updateTaskOutputThread.start()

        # Remove potential old temp files in the original folder
        # Pattern: "stdout" "_" Int ".txt"
        # or:      "stderr" "_" Int ".txt"
        remove_Temp_Files_In_Path(".")

    def __del__(self) -> None:
        start("Close GUI ...")
        if self.__updateTaskOutputThread.is_alive():
            self.__updateTaskOutputThreadStopFlag = True
            self.__updateTaskOutputThread.join()
        end()

# ---------------------------------------------------------------------------------------------------------------------

    def __update_Task_List(self) -> None:
        nextProc = None
        currCalcStep = 0
        percentValue = 0.0
        lastPercentValue = percentValue
        taskListEntry = 0
        numDots = 0
        print("\nStart update thread ...", flush=True)
        while True:
            time.sleep(0.25)
            # Stop the thread when the stop flag was set
            if self.__updateTaskOutputThreadStopFlag == True:
                break
            # Are there any available tasks? (Either in the queue or in use)
            if self.__pyLMDProcs.empty() and nextProc == None:
                continue
            # Are there tasks in the queue while currently is no task in use
            if self.__pyLMDProcs.empty() == False and nextProc == None:
                nextProc = self.__pyLMDProcs.get()
                print("New process (pid: " + str(nextProc.pid) + ") found at: " + get_Current_Time(), flush=True)
                currCalcStep = 0
                percentValue = 0.0
                lastPercentValue = percentValue
                numDots = 0
            # A task is in use
            else:
                if nextProc.poll() != None:
                    print("Process (pid: " + str(nextProc.pid) + ") returned at " + get_Current_Time() + " with: " + str(nextProc.returncode), flush=True)
                    if self.__taskList.size() >= taskListEntry:
                        self.__taskList.delete(taskListEntry)
                    self.__taskList.insert(taskListEntry, "Calculation finished at " + get_Current_Time() + " with: " + str(nextProc.returncode))
                    self.__taskList.itemconfigure(taskListEntry, fg="green" if nextProc.returncode == 0 else "red")

                    # Try to delete the temp files
                    # remove_File("stdout_" + str(nextProc.pid) + ".txt")
                    remove_File("tmp.png")
                    # Remove the error file only when the subprocess returned with 0
                    if nextProc.returncode == 0:
                        remove_File("stderr_" + str(nextProc.pid) + ".txt")

                    nextProc = None
                    taskListEntry += 1
                else:
                    # Extract percent from the file and update GUI ...
                    percentValues = extract_Percentages(get_Last_Line_From_File("stderr_" + str(nextProc.pid) + ".txt"))
                    if len(percentValues) > 0:
                        lastPercentValue = percentValue
                        percentValue = percentValues[0]
                    # Extract the current calc step, if the last step was not started
                    if currCalcStep < pyLMDCalculation.get_Last_Calc_Step():
                        currCalcStep = get_Current_Calc_Step_From_File("stdout_" + str(nextProc.pid) + ".txt")
                    else:
                        if lastPercentValue > percentValue:
                            currCalcStep += 1
                    if self.__taskList.size() >= taskListEntry:
                        self.__taskList.delete(taskListEntry)
                    newText = "Calculation step"
                    newText += " (" + str(currCalcStep) + "/" + str(pyLMDCalculation.get_Num_Of_Calc_Steps() - 1) + "): "
                    newText += pyLMDCalculation.get_Step_Desciption(currCalcStep) + " "
                    if pyLMDCalculation.is_Percent_Value_Possible(currCalcStep):
                        newText += "| " + str(int(percentValue)) + " % "
                    for i in range(numDots):
                        newText += "."
                    numDots = (numDots + 1) % 4
                    self.__taskList.insert(taskListEntry, newText)
                    self.__taskList.itemconfigure(taskListEntry, fg="black")
        print("\nStop update thread ...", flush=True)

# ---------------------------------------------------------------------------------------------------------------------

    def update_Radio_Button_Marking_Point(self, x: float = 0.0, y: float = 0.0) -> None:
        is_Valid_Coordinate(x)
        is_Valid_Coordinate(y)
        index = self.__varRbCalPointsSelection.get()
        self.__markingPoints[index].set_Position(x, y)
        self.__markingPoints[index].show()

        slicingFactor = self.__pictureData.get_Coordinate_Slicing_Factor()

        # Update label for the altered radio button
        # Provide always the same length, regardless of the integer value itself
        newLabel = "Point " + str(index + 1) + ":"
        newLabel += f"{int(x * slicingFactor):{self.__SPACE_PREFIX_FOR_COORDS}d}" + ","
        newLabel += f"{int(y * slicingFactor):{self.__SPACE_PREFIX_FOR_COORDS}d}"

        self.__calPointsLabel[index].config(text=newLabel)

        # Is auto increment enabled?
        if self.__varAutoIncrementRb.get() == 1:
            self.__calPointsRB[(index + 1) % 3].select()

        # Redraw the pyplot object to make the marking point visible
        start("New point")
        self.__pyPlotCanvas.draw()

        # Old updating approach with blitting -> Is here not feasible
        #self.__origFigure.canvas.restore_region(self.__background)
        #self.__markingPoints[index].get_Line2D().draw(self.__origFigure.canvas.get_renderer())
        #self.__origFigure.canvas.blit(self.__origAxes.bbox)
        end()

    def get_Selected_Picture_Rb(self) -> int:
        return is_Int_R(self.__varRbShowPictureSelection.get())

    def get_Same_As_Input_Picutre_Path_Rb(self) -> int:
        return is_Int_R(self.__varRbSameAsPictureInputPath.get())

    def get_Open_Picture_Name(self, pictureSlot: int) -> str:
        is_Type(pictureSlot, int)
        returnValue: str = ""

        if pictureSlot == 0:
            returnValue = copy.deepcopy(self.__openPictureOne)
        elif pictureSlot == 1:
            returnValue = copy.deepcopy(self.__openPictureTwo)
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) +
                ". Valid are " + str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))
        return is_Type_R(returnValue, str)

    def activate_Same_As_Input_Picture_Path_Rb(self, pictureSlot: int) -> None:
        is_Type(pictureSlot, int)
        if pictureSlot != 0 and pictureSlot != 1:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) +
                ". Valid are " + str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))
        self.__sameAsPictureInputPathRB[pictureSlot]["state"] = "active"

    def set_Open_Picture_Name(self, picturePath: str, pictureSlot: int) -> None:
        has_Content(picturePath)
        is_Type(pictureSlot, int)
        if pictureSlot == 0:
            self.__openPictureOne = copy.deepcopy(picturePath)
        elif pictureSlot == 1:
            self.__openPictureTwo = copy.deepcopy(picturePath)
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) +
                ". Valid are " + str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))

# ---------------------------------------------------------------------------------------------------------------------

    def set_Result_Path(self, resultPath: str) -> None:
        has_Content(resultPath)
        print("Result path: " + resultPath, flush=True)
        self.__varPathInputEntry.set(resultPath)

# ---------------------------------------------------------------------------------------------------------------------

    def start_Calc(self) -> None:
        calibrationCoordinates = []
        for obj in self.__markingPoints:
            if obj is None:
                calibrationCoordinates.append([ 0.0, 0.0 ])
            else:
                x = obj.get_Position()[0] * self.__pictureData.get_Coordinate_Slicing_Factor()
                y = obj.get_Position()[1] * self.__pictureData.get_Coordinate_Slicing_Factor()
                # Yes the coordinates are swapped!
                lmd_x = y
                lmd_y = x
                calibrationCoordinates.append([ lmd_x, lmd_y ])

        print("Start XML calculation with calibration points: " + str(calibrationCoordinates))
        print("> Using parameter <\n" + str(self.__calculationParameter) + "\n", flush=True)
        im = Image.fromarray(self.__pictureData.get_Picture_Data_Sliced(PictureData.FIRST_PIC))
        im.save("tmp.png")

        # Construct the process call
        processCall = [ "python3", "./src/pyLMDCalculation.py", "tmp.png" ]
        # Add calibration points
        for coord in calibrationCoordinates:
            is_Valid_Coordinate(coord[0])
            is_Valid_Coordinate(coord[1])
            processCall.append(str(coord[0]))
            processCall.append(str(coord[1]))
        # Add pyLMD parameter
        processCall.append(str(self.__calculationParameter.get_Shape_Dilation()))
        processCall.append(str(self.__calculationParameter.get_Shape_Erosion()))
        processCall.append(str(self.__calculationParameter.get_Binary_Smoothing()))
        processCall.append(str(self.__calculationParameter.get_Convolution_Smoothing()))
        processCall.append(str(self.__calculationParameter.get_Poly_Compression_Factor()))
        processCall.append(str(self.__calculationParameter.get_Distance_Heuristic()))

        # Optional: Result path
        # If not set: Path of the input picture will be used
        if len(self.__varPathInputEntry.get()) > 0:
            # print("Using: " + self.__varPathInputEntry.get() + " as output path")
            fullOutputName = self.__varPathInputEntry.get()
            if self.__varPathInputEntry.get() is not None and len(self.__varPathInputEntry.get()) > 0:
                if self.__varPathInputEntry.get()[len(self.__varPathInputEntry.get()) - 1] != "/":
                    fullOutputName += "/"
            fullOutputName += path_Basename(path_Tail(self.__openPictureOne))
            processCall.append(fullOutputName + ".xml")

        print("Using subprocess call: \"", end="")
        for i in range(len(processCall)):
            print(processCall[i], end="")
            if i + 1 < len(processCall):
                print(" ", end="")
        print("\"", flush=True)

        proc = subprocess.Popen(processCall, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, encoding="utf-8", bufsize=1)
        procID = proc.pid

        threadStdout = threading.Thread(target=write_Stdout_To_File, args=("stdout_" + str(procID) + ".txt", proc))
        threadStderr = threading.Thread(target=write_Stderr_To_File, args=("stderr_" + str(procID) + ".txt", proc))

        threadStdout.start()
        threadStderr.start()

        self.__pyLMDProcs.put(proc)
        self.__pyLMDStdoutThreads.put(threadStdout)
        self.__pyLMDStderrThreads.put(threadStderr)

# ---------------------------------------------------------------------------------------------------------------------

    def get_Calculation_Parameter(self) -> pyLMDCalculationParameter:
        return is_Type_R(self.__calculationParameter, pyLMDCalculationParameter)

# ---------------------------------------------------------------------------------------------------------------------

    def open_Picture(self, fileName: str, pictureSlot: int) -> None:
        has_Content(fileName)
        is_Type(pictureSlot, int)

        if pictureSlot == 0:
            self.__openPictureOne = fileName
        elif pictureSlot == 1:
            self.__openPictureTwo = fileName
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) +
                ". Valid are " + str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))
        threadArgs = (self.__pictureData, fileName, pictureSlot)
        myThread = threading.Thread(target=CalculationThreads.load_Picture_Thread, args=threadArgs)
        fileSize = int(get_File_Size(fileName, "KByte"))
        fileSizeStr = str(fileSize // 1024) + " MB" if fileSize > 1024 else str(fileSize) + " KB"

        myProgressbarWindow = ProgressBarWindow(window, width=350, height=200, title="Load file (" + fileSizeStr + ")", msg="")
        myThread.start()
        while myThread.is_alive():
            myProgressbarWindow.update_Value(min(self.__pictureData.get_Loading_Process(), 100), 0.0)
            # When the operation was canceled from the user: stop loading process and destroy the progress bar window
            # without a change of the GUI data
            if myProgressbarWindow.stopped_Via_User():
                self.__pictureData.set_Stop_Event()
                myThread.join()
                myProgressbarWindow.destroy()
                # Clear stop event to make a second picture loading possible
                self.__pictureData.clear_Stop_Event()
                return

        myThread.join()
        myProgressbarWindow.update_Title("Update GUI ...")

        self.__im = self.__origAxes.imshow(self.__pictureData.get_Picture_Data_Sliced(pictureSlot), aspect="equal", cmap="gray",
                                           interpolation="none")
        # Activate the radio button, if the loading was successful
        if self.__pictureData.is_Picture_Data_Loaded(pictureSlot):
            self.__showPictureRB[pictureSlot]["state"] = "active"
            self.__showPictureRB[pictureSlot].select()
        self.__pyPlotCanvas.draw()
        myProgressbarWindow.destroy()

# ---------------------------------------------------------------------------------------------------------------------

    def get_Orig_picData_Dimensions(self, pictureSlot: int) -> tuple[int, ...]:
        is_Type(pictureSlot, int)
        return is_Type_R(self.__pictureData.get_Picture_Data(pictureSlot).shape, tuple)

# ---------------------------------------------------------------------------------------------------------------------

    def is_Picture_Loaded(self, pictureSlot: int) -> bool:
        is_Type(pictureSlot, int)
        if pictureSlot == PictureData.FIRST_PIC or pictureSlot == PictureData.SEC_PIC:
            return is_Type_R(self.__pictureData.is_Picture_Data_Loaded(pictureSlot), bool)
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) +
                ". Valid are " + str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))

# ---------------------------------------------------------------------------------------------------------------------

    def set_Picture_Data(self, pictureSlot: int) -> None:
        is_Type(pictureSlot, int)
        start("Set data for picture " + str(pictureSlot) + " ...")
        if pictureSlot == PictureData.FIRST_PIC and self.__pictureData.is_Picture_Data_Loaded(PictureData.FIRST_PIC):
            self.__im.set_data(self.__pictureData.get_Picture_Data_Sliced(PictureData.FIRST_PIC))
        elif pictureSlot == PictureData.SEC_PIC and self.__pictureData.is_Picture_Data_Loaded(PictureData.SEC_PIC):
            self.__im.set_data(self.__pictureData.get_Picture_Data_Sliced(PictureData.SEC_PIC))
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) +
                ". Valid are " + str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))
        self.__pyPlotCanvas.draw()
        end()

# ---------------------------------------------------------------------------------------------------------------------

    def update_Slicing_Factor(self, newVal: int) -> None:
        is_Type(newVal, int)
        if newVal < self.__MIN_SLICING_FACTOR or newVal > self.__MAX_SLICING_FACTOR:
            raise ValueError("Invalid slicing factor. Valid range: " + str(self.__MIN_SLICING_FACTOR) + " and " +
                             str(self.__MAX_SLICING_FACTOR) + ". Given: " + str(newVal))
        oldSlicingFactor = self.__pictureData.get_Data_Slicing_Factor()
        self.__pictureData.update_Slicing_Factor(newVal)

        start("Update slicing factor (" + str(oldSlicingFactor) + " -> " + str(self.__pictureData.get_Data_Slicing_Factor()) + ")")
        if self.__varRbShowPictureSelection.get() == PictureData.FIRST_PIC and self.__pictureData.is_Picture_Data_Loaded(PictureData.FIRST_PIC):
            self.__im.set_data(self.__pictureData.get_Picture_Data_Sliced(PictureData.FIRST_PIC))
        elif self.__varRbShowPictureSelection.get() == PictureData.SEC_PIC and self.__pictureData.is_Picture_Data_Loaded(PictureData.SEC_PIC):
            self.__im.set_data(self.__pictureData.get_Picture_Data_Sliced(PictureData.SEC_PIC))
        else:
            raise ValueError("Invalid combination of selected and loaded picture. Selected: " + str(self.__varRbShowPictureSelection.get()) +
                             " | Is loaded: " + str(self.__pictureData.is_Picture_Data_Loaded(self.__varRbShowPictureSelection.get())))
        self.__pyPlotCanvas.draw()
        end()

# ---------------------------------------------------------------------------------------------------------------------

    def activate_Start_Calculation_Button(self) -> None:
        self.__startCalcButton["state"] = "active"

# ---------------------------------------------------------------------------------------------------------------------

    def __toggle_Manual_Path_State(self) -> None:
        if self.__varManualPathCb.get() == 1:
            for i in range(len(self.__sameAsPictureInputPathRB)):
                self.__sameAsPictureInputPathRB[i]["state"] = "disabled"
            self.__pathInputLabel["state"] = "active"
            self.__pathInputEntry["state"] = "normal"
            self.__selectOutputPathButton["state"] = "active"
        else:
            # Activate the RadioButtons only if a picture for this slot was loaded
            if self.__openPictureOne is not None and len(self.__openPictureOne) > 0:
                self.__sameAsPictureInputPathRB[0]["state"] = "active"
            if self.__openPictureTwo is not None and len(self.__openPictureTwo) > 0:
                self.__sameAsPictureInputPathRB[1]["state"] = "active"
            # Disable all three widgets for the manual path input
            self.__pathInputLabel["state"] = "disabled"
            self.__pathInputEntry["state"] = "disabled"
            self.__selectOutputPathButton["state"] = "disabled"

            # Restore the path of the pre-selected Radiobutton picture via a callback function
            # This callback will be used after a new file was loaded
            self.__callbacks.callback_Gui_Rb_Same_As_Picture_Path_Changed()

# ---------------------------------------------------------------------------------------------------------------------

    def __toggle_Pylmd_Option_Menus_State(self) -> None:
        for currOptionWidget in self.__pylmdOptionMenus:
            if self.__varUseDefaultpylmdSettings.get() == 1:
                currOptionWidget["state"] = "disabled"
            else:
                currOptionWidget["state"] = "normal"

        if self.__varUseDefaultpylmdSettings.get() == 1:
            defaultValues = [ pyLMDParameterLimits.get_Shape_Dilation_Default(), pyLMDParameterLimits.get_Shape_Erosion_Default(),
                pyLMDParameterLimits.get_Binary_Smoothing_Default(), pyLMDParameterLimits.get_Convolution_Smoothing_Default(),
                pyLMDParameterLimits.get_Poly_Compression_Factor_Default(), pyLMDParameterLimits.get_Distance_Heuristic_Default() ]
            for i in range(len(defaultValues)):
                self.__pylmdOptionsMenuSelected[i].set(defaultValues[i])

# ---------------------------------------------------------------------------------------------------------------------

    def __calc_Font_Size(self, height: int = 0) -> int:
        is_Type(height, int)
        if height < 0:
            raise ValueError("Negative height (" + str(height) + ") given!")
        return is_Int_R(height // 100 + 2)

# ---------------------------------------------------------------------------------------------------------------------

    def __resize_Gui(self, event: tk.Event) -> None:
        is_Type(event, tk.Event)
        if event is None:
            return
        # Sometimes a resize event is emitted with wrong width and height values
        # So when the values are smaller than the min window size, then this are invalid data
        if event.width < Gui.__MIN_WINDOW_WIDTH or event.height < Gui.__MIN_WINDOW_HEIGHT:
            return
        newW = event.width
        newH = event.height
        newFontSize = self.__calc_Font_Size(newH)
        if self.__startCalcButton is not None:
            self.__startCalcButton.config(width=newW // 75, height=newH // 400, font=Gui.__LABEL_FRAME_FONT)
            # print(str(newW) + ", " + str(newH))

        # Resize radio buttons and their labels
        for i in range(len(self.__calPointsLabel)):
            self.__calPointsRB[i].config(font=("Arial", newFontSize))
            self.__calPointsLabel[i].config(font=("TkFixedFont", newFontSize))

        newFontFrame = tk.font.Font(family="Arial", size=newFontSize, weight=tk.font.BOLD)
        self.__calPointsFrame.config(font=newFontFrame)
        self.__additionalSettingsFrame.config(font=newFontFrame)
        # self.__selectedDirFrame.config(font=newFontFrame)

    def __close_Gui(self) -> None:
        if self.__updateTaskOutputThread.is_alive():
            self.__updateTaskOutputThreadStopFlag = True
            self.__updateTaskOutputThread.join()
        window.quit()
        window.destroy()

# ---------------------------------------------------------------------------------------------------------------------

    __LABELFRAME_PADX: int = 1
    __LABELFRAME_PADY: int = 1
    __FONT_SIZE_LABELFRAME: int = 11
    __SPACE_PREFIX_FOR_COORDS: int = 7
    __MIN_SLICING_FACTOR: int = 1
    __MAX_SLICING_FACTOR: int = 10
    __PADX: int = 10
    __PADY: int = 10
    __IPADX: int = 3
    __IPADY: int = 3
    __LABEL_FRAME_FONT: tk.font.Font = tk.font.Font(family = "Arial", size = __FONT_SIZE_LABELFRAME, weight = "bold")
    __MIN_WINDOW_WIDTH: int = 1280
    __MIN_WINDOW_HEIGHT: int = 720

    __calPointsColor: list [list[str]]= [ [ "red", "r" ], [ "green", "g" ], [ "blue", "b" ] ]
