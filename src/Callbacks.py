from matplotlib.backend_bases import MouseButton
from Misc import *
from PictureData import *
from pyLMDParameterLimits import *
import tkinter as tk



class Callbacks():
    def __init__(self, gui):
        self.__gui = gui
        self.__lastSlicingFactor: int = -1

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Key_Press_Event(self, event) -> None:
        if event is None:
            return
        if event.key == "delete" or event.key == "backspace":
            print(event)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Button_Start_Calc_Event(self) -> None:
        self.__gui.start_Calc()

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Button_Select_Output_Path(self) -> None:
        pathName = tk.filedialog.askdirectory(initialdir = ".", title = "Select path for results")
        if pathName is not None and len(pathName) > 0:
            self.__gui.set_Result_Path(pathName)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Open_Picture_One(self) -> None:
        fileName = tk.filedialog.askopenfilename(initialdir = ".", title = "Select picture 1",
                                          filetypes = (("Pictures", "*.png"), ("Pictures", "*.tif"), ("Pictures", "*.tiff")))
        if fileName is not None and len(fileName) > 0:
            print("Using file \"" + fileName + "\" as first picture")
            self.__gui.open_Picture(fileName, PictureData.FIRST_PIC)
            self.__gui.set_Open_Picture_Name(fileName, PictureData.FIRST_PIC)
            self.__gui.activate_Same_As_Input_Picture_Path_Rb(PictureData.FIRST_PIC)
            self.__gui.activate_Start_Calculation_Button()
            self.callback_Gui_Rb_Same_As_Picture_Path_Changed()

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Open_Picture_Two(self) -> None:
        fileName = tk.filedialog.askopenfilename(initialdir = ".", title = "Select picture 2",
                                          filetypes = (("Pictures", "*.png"), ("Pictures", "*.tif"), ("Pictures", "*.tiff")))
        if fileName is not None and len(fileName) > 0:
            print("Using file \"" + fileName + "\" as second picture")
            self.__gui.open_Picture(fileName, PictureData.SEC_PIC)
            self.__gui.set_Open_Picture_Name(fileName, PictureData.SEC_PIC)
            self.__gui.activate_Same_As_Input_Picture_Path_Rb(PictureData.SEC_PIC)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Radiobutton_Changed(self) -> None:
        var = self.__gui.toggle_Show_Picture_Selection()

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Use_Default_Settings_Changed(self, newState) -> None:
        self.__toggle_Pylmd_Option_Menus_State()

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Options_Menu_Slicing_Factor_Changed(self, newValue: str) -> None:
        has_Content(newValue)
        newValueInt = int(newValue)
        # Is it the first call?
        if self.__lastSlicingFactor == -1:
            self.__lastSlicingFactor = newValueInt
            self.__gui.update_Slicing_Factor(newValueInt)
        # Check whether the new value is a different value, because the same value can be selected multiple times
        elif self.__lastSlicingFactor != newValueInt:
            self.__lastSlicingFactor = newValueInt
            self.__gui.update_Slicing_Factor(newValueInt)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Options_Pylmd_Parameter_Shape_Dilation(self, newValue: str) -> None:
        has_Content(newValue)
        calcParam = self.__gui.get_Calculation_Parameter()
        calcParam.set_Shape_Dilation(int(newValue))
        # print("New Shape_dilation: " + newValue)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Options_Pylmd_Parameter_Shape_Erosion(self, newValue: str) -> None:
        has_Content(newValue)
        calcParam = self.__gui.get_Calculation_Parameter()
        calcParam.set_Shape_Erosion(int(newValue))
        # print("New shape_erosion: " + newValue)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Options_Pylmd_Parameter_Binary_Smoothing(self, newValue: str) -> None:
        has_Content(newValue)
        calcParam = self.__gui.get_Calculation_Parameter()
        calcParam.set_Binary_Smoothing(int(newValue))
        # print("New binary_smoothing: " + newValue)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Options_Pylmd_Parameter_Convolution_Smoothing(self, newValue: str) -> None:
        has_Content(newValue)
        calcParam = self.__gui.get_Calculation_Parameter()
        calcParam.set_Convolution_Smoothing(int(newValue))
        # print("New convolution_smoothing: " + newValue)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Options_Pylmd_Parameter_Poly_Compression_Factor(self, newValue: str) -> None:
        has_Content(newValue)
        calcParam = self.__gui.get_Calculation_Parameter()
        calcParam.set_Poly_Compression_Factor(int(newValue))
        # print("New poly_compression_factor: " + newValue)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Options_Pylmd_Parameter_Distance_Heuristic(self, newValue: str) -> None:
        has_Content(newValue)
        calcParam = self.__gui.get_Calculation_Parameter()
        calcParam.set_Distance_Heuristic(int(newValue))
        # print("New distance_heuristic: " + newValue)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Mouse_On_Press_Event(self, event) -> None:
        if event is None:
            return
        if event.dblclick == True:
            return
        if event.button is not MouseButton.RIGHT:
            return
        x, y = event.xdata, event.ydata
        if x is None or y is None or event.inaxes is None:
            return
        x = float(x)
        y = float(y)
        # Are the coordinates too small?
        if x < 0.0 or y < 0.0:
            return
        # Are the coordinates larger than the imported picture?
        # Yes testing first y; then x
        if self.__gui.is_Picture_Loaded(PictureData.FIRST_PIC):
            if y > self.__gui.get_Orig_picData_Dimensions(PictureData.FIRST_PIC)[0] or x > self.__gui.get_Orig_picData_Dimensions(PictureData.FIRST_PIC)[1]:
                return
        if self.__gui.is_Picture_Loaded(PictureData.SEC_PIC):
            if y > self.__gui.get_Orig_picData_Dimensions(PictureData.SEC_PIC)[0] or x > self.__gui.get_Orig_picData_Dimensions(PictureData.SEC_PIC)[1]:
                return

        # print("(" + str(x) + ", " + str(y) + ")")
        # Yes the coordinates are swapped!
        self.__gui.update_Radio_Button_Marking_Point(x, y)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Resize_Event(self, event) -> None:
        if event is None:
            return
        newWidth, newHeight = event.width, event.height
        if newWidth is None or newHeight is None:
            return
        print("New figure canvas: " + str(newWidth) + " | " + str(newHeight))

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Xlim_Changed(self, event) -> None:
        if event is None:
            return
        newXlim = event.get_xlim()
        if newXlim is None:
            return
        if (int(newXlim[0]) == int(newXlim[1])) or (int(newXlim[0]) < 0 or int(newXlim[1]) < 0):
            return
        print("New x limits: " + str(int(newXlim[0])) + " | " + str(int(newXlim[1])))

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Ylim_Changed(self, event) -> None:
        if event is None:
            return
        newYlim = event.get_ylim()
        if newYlim is None:
            return
        if (int(newYlim[0]) == int(newYlim[1])) or (int(newYlim[0]) < 0 or int(newYlim[1]) < 0):
            return
        print("New y limits: " + str(int(newYlim[0])) + " | " + str(int(newYlim[1])))

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Rb_Show_Picture_Changed(self) -> None:
        self.__gui.set_Picture_Data(self.__gui.get_Selected_Picture_Rb())

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Rb_Same_As_Picture_Path_Changed(self) -> None:
        pictureSlot: int = self.__gui.get_Same_As_Input_Picutre_Path_Rb()
        filePath: str = path_Head(self.__gui.get_Open_Picture_Name(pictureSlot))
        self.__gui.set_Result_Path(filePath)

# ---------------------------------------------------------------------------------------------------------------------

    def callback_Gui_Toggle_AutoIncrement_Checkbox(self) -> None:
        # Dummy function
        i = 0

# =====================================================================================================================

class Validations():
    def __init__(self, callbacks: Callbacks):
        is_Type(callbacks, Callbacks)
        self.__callbacks = callbacks

    def validate_Spinbox_Input_Shape_Dilation(self, inputData: str) -> bool:
        is_Type(inputData, str)
        # An empty input must be always true, because an input via keyboard with a leading remove of the Spinbox value
        # needs this exception
        if len(inputData) == 0:
            return True
        min_: int = pyLMDParameterLimits.get_Shape_Dilation_Min()
        max_: int = pyLMDParameterLimits.get_Shape_Dilation_Max()
        res: bool = Validations.__real_Validation(inputData, min_, max_)
        if res is True:
            self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Shape_Dilation(inputData)
        return res

    def validate_Spinbox_Input_Shape_Erosion(self, inputData: str) -> bool:
        is_Type(inputData, str)
        if len(inputData) == 0:
            return True
        min_: int = pyLMDParameterLimits.get_Shape_Erosion_Min()
        max_: int = pyLMDParameterLimits.get_Shape_Erosion_Max()
        res: bool = Validations.__real_Validation(inputData, min_, max_)
        if res is True:
            self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Shape_Erosion(inputData)
        return res

    def validate_Spinbox_Input_Binary_Smoothing(self, inputData: str) -> bool:
        is_Type(inputData, str)
        if len(inputData) == 0:
            return True
        min_: int = pyLMDParameterLimits.get_Binary_Smoothing_Min()
        max_: int = pyLMDParameterLimits.get_Binary_Smoothing_Max()
        res: bool = Validations.__real_Validation(inputData, min_, max_)
        if res is True:
            self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Binary_Smoothing(inputData)
        return res

    def validate_Spinbox_Input_Convolution_Smoothing(self, inputData: str) -> bool:
        is_Type(inputData, str)
        if len(inputData) == 0:
            return True
        min_: int = pyLMDParameterLimits.get_Convolution_Smoothing_Min()
        max_: int = pyLMDParameterLimits.get_Convolution_Smoothing_Max()
        res: bool = Validations.__real_Validation(inputData, min_, max_)
        if res is True:
            self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Convolution_Smoothing(inputData)
        return res

    def validate_Spinbox_Input_Poly_Compression_Factor(self, inputData: str) -> bool:
        is_Type(inputData, str)
        if len(inputData) == 0:
            return True
        min_: int = pyLMDParameterLimits.get_Poly_Compression_Factor_Min()
        max_: int = pyLMDParameterLimits.get_Poly_Compression_Factor_Max()
        res: bool = Validations.__real_Validation(inputData, min_, max_)
        if res is True:
            self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Poly_Compression_Factor(inputData)
        return res

    def validate_Spinbox_Input_Distance_Heuristic(self, inputData: str) -> bool:
        is_Type(inputData, str)
        if len(inputData) == 0:
            return True
        min_: int = pyLMDParameterLimits.get_Distance_Heuristic_Min()
        max_: int = pyLMDParameterLimits.get_Distance_Heuristic_Max()
        res: bool = Validations.__real_Validation(inputData, min_, max_)
        if res is True:
            self.__callbacks.callback_Gui_Options_Pylmd_Parameter_Distance_Heuristic(inputData)
        return res

    @staticmethod
    def __real_Validation(inputData: str, min_: int, max_: int) -> bool:
        is_Type(inputData, str)
        is_Type(min_, int)
        is_Type(max_, int)
        if len(inputData) == 0:
            return False
        if not inputData.isdigit():
            return False
        if int(inputData) < min_ or int(inputData) > max_:
            return False
        return True

# =====================================================================================================================
