import tkinter as tk
from time import sleep
from tkinter import ttk

from Misc import *

class ProgressBarWindow():
    def __init__(self, mainWindow, title: str = "", msg: str = "", width: int = 300, height: int = 200):
        is_Type(title, str)
        is_Type(msg, str)
        is_Type(width, int)
        is_Type(height, int)
        if width <= 0:
            raise ValueError("Invalid width for ProgressBarWindow. Valid: > 0. Given: " + str(width))
        if height <= 0:
            raise ValueError("Invalid height for ProgressBarWindow. Valid: > 0. Given: " + str(height))
        self.__origTitle = title

        self.__mainWindow = mainWindow

        # Sub window
        self.__window = tk.Toplevel(self.__mainWindow, width=width, height=height)
        self.__window.title(self.__origTitle)
        self.__window.minsize(width=width, height=height)
        self.__window.maxsize(width=width, height=height)

        # Progressbar
        self.__progressbar = ttk.Progressbar(self.__window, value=0, orient=tk.HORIZONTAL, length=width // 2, mode="determinate")
        self.__progressbarPercent = tk.Label(self.__window, text="0 %", font=("Arial", 14))

        # Label for main msg
        self.__mainMsgLabel = tk.Label(self.__window, text=msg, font=("Arial", 14))

        # Button for canceling the process
        self.__stopOperation=tk.Button(self.__window, text="Cancel", width=10, height=4,
            command=self.__cancel_Button_Callback)

        self.__progressbar.pack(side=tk.TOP, fill=tk.X, expand=True, padx=self.__padx, pady=self.__pady,
            ipadx=self.__ipadx, ipady=self.__ipady // 4)
        self.__progressbarPercent.pack(side=tk.TOP, fill=tk.X, expand=True, padx=self.__padx, pady=0,
            ipadx=self.__ipadx, ipady=0)
        # Reduce space when there is no additional msg on the GUI
        if len(msg) == 0:
            self.__mainMsgLabel.pack(side=tk.TOP, fill=tk.X, expand=True, padx=1, pady=1, ipadx=1, ipady=1)
        else:
            self.__mainMsgLabel.pack(side=tk.TOP, fill=tk.X, expand=True, padx=self.__padx, pady=self.__pady,
                ipadx=self.__ipadx, ipady=self.__ipady)
        self.__stopOperation.pack(side=tk.TOP, expand=False, padx=self.__padx, pady=self.__pady * 3,
            ipadx=self.__ipadx, ipady=self.__ipady * 3)

        self.__stopped_Via_User = False

# ---------------------------------------------------------------------------------------------------------------------

    def update_Title(self, newTitle: str) -> None:
        has_Content(newTitle)
        self.__window.title(self.__origTitle + " | " + newTitle)
        self.__window.update()

# ---------------------------------------------------------------------------------------------------------------------

    def update_Value(self, newValue: int, sleepTime: float = 0.0) -> None:
        is_Type(newValue, int)
        is_Type(sleepTime, float)
        if newValue < 0 or newValue > 100:
            raise ValueError("Invalid value for progress bar given! Valid: 0 - 100. Given: " + str(newValue))

        self.__progressbar["value"] = newValue
        self.__progressbarPercent["text"] = str(newValue) + " %"

        self.__window.title(self.__origTitle + " | " + str(newValue) + " %")
        self.__window.update()
        if sleepTime > 0.0:
        # To avoid massive CPU usage due to many update operations
            sleep(sleepTime)

# ---------------------------------------------------------------------------------------------------------------------

    def __cancel_Button_Callback(self) -> None:
        self.__stopped_Via_User = True

# ---------------------------------------------------------------------------------------------------------------------

    def stopped_Via_User(self) -> bool:
        return is_Type_R(self.__stopped_Via_User, bool)

# ---------------------------------------------------------------------------------------------------------------------

    def destroy(self) -> None:
        self.__stopOperation.destroy()
        self.__mainMsgLabel.destroy()
        self.__progressbarPercent.destroy()
        self.__progressbar.destroy()
        self.__window.destroy()

# ---------------------------------------------------------------------------------------------------------------------

    __padx: int = 10
    __pady: int = 10
    __ipadx: int = 10
    __ipady: int = 5
