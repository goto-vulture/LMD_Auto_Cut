import os
import time
import numpy as np
import datetime
import re
import ntpath
import sys
from typing import Any, Union

# ---------------------------------------------------------------------------------------------------------------------

def is_Type(var: Any, expected: Any, additionalInfo: str = "") -> None:
    if not isinstance(additionalInfo, str):
        raise TypeError("Expected type: str | Got: " + str(type(additionalInfo)) + "!")
    if var is None:
        raise TypeError("Given variable is None. Expected type: " + str(expected) + additionalInfo)
    if type(var) != expected:
        raise TypeError("Expected type: " + str(expected) + " | Got: " + str(type(var)) + "! " + additionalInfo)

def is_Int(var: int, additionalInfo: str = "") -> None:
    if not isinstance(var, int):
        raise TypeError("Expected type: int | Got: " + str(type(var)) + "!")
    if not isinstance(additionalInfo, str):
        raise TypeError("Expected type: str | Got: " + str(type(additionalInfo)) + "!")

def is_Type_R(var: Any, expected: Any, additionalInfo: str = "") -> Any:
    is_Type(var, expected, additionalInfo)
    return var

def is_Int_R(var: int, additionalInfo: str = "") -> int:
    is_Int(var, additionalInfo)
    return var

def is_Type_If_Not_None(var: Any, expected: Any, additionalInfo: str = "") -> None:
    if var is not None:
        is_Type(var, expected, additionalInfo)

def tuple_Type_Check(var: tuple, expected: Any, additionalInfo: str = "") -> None:
    is_Type(additionalInfo, str)
    if not isinstance(var, tuple):
        raise TypeError("Expected type: " + str(tuple) + " | Got: " + str(type(var)) + "! " + additionalInfo)

    if list(map(type, var)) != expected:
        errMsg = "Expected type: tuple("
        for i in range(len(expected)):
            errMsg += str(expected[i])
            if i + 1 < len(expected):
                errMsg += " "

        errMsg += ") | Got: tuple("
        for i in range(len(var)):
            errMsg += str(type(var[i]))
            if i + 1 < len(var):
                errMsg += " "
        errMsg += ")! " + additionalInfo
        raise TypeError(errMsg)

def tuple_Type_Check_R(var: tuple, expected: Any, additionalInfo: str = "") -> tuple:
    is_Type(additionalInfo, str)
    tuple_Type_Check(var, expected, additionalInfo)
    return var

def is_Not_None(var: Any, additionalInfo: str = "") -> None:
    is_Type(additionalInfo, str)
    if var is None:
        raise TypeError("Given variable is None. " + additionalInfo)

def has_Content(var: Union[str, np.ndarray], additionalInfo: str = "") -> None:
    is_Not_None(var)
    is_Type(additionalInfo, str)
    if type(var) == str:
        if len(var) == 0:
            raise ValueError("Given string is empty. " + additionalInfo)
    if type(var) == np.ndarray:
        if var.shape[0] == 0:
            raise ValueError("Numpy array is empty. " + additionalInfo)

def has_List_Type(var: list, expected: Any, additionalInfo: str = "") -> None:
    is_Type(var, list)
    is_Type(additionalInfo, str)
    for i in range(len(var)):
        additionalInfo=""
        # Give the underlying test function an additional info where the error occured
        if type(var[i]) != expected:
            additionalInfo += "Error on index: " + str(i) + " | List length: " + str(len(var))
        is_Type(var[i], expected, additionalInfo)

def has_Content_R(var: Union[str, np.ndarray], additionalInfo: str = "") -> Union[str, np.ndarray]:
    is_Not_None(var)
    is_Type(additionalInfo, str)
    if type(var) == str:
        if len(var) == 0:
            raise ValueError("Given string is empty. " + additionalInfo)
    if type(var) == np.ndarray:
        if var.shape[0] == 0:
            raise ValueError("Numpy array is empty. " + additionalInfo)
    return var

def has_Len_In_Dimension_1(var: list, expectedDimensions: int, additionalInfo: str = "") -> None:
    is_Type(var, list, additionalInfo)
    is_Type(expectedDimensions, int, additionalInfo)
    if len(var) != expectedDimensions:
        raise TypeError("Expected list length in dimension 1: " + str(expectedDimensions) + " | Got: " + str(len(var)) + "! " +
                        additionalInfo)

def has_Len_In_Dimension_2(var: list, expectedDimensions: int, additionalInfo: str = "") -> None:
    is_Type(var, list, additionalInfo)
    is_Type(expectedDimensions, int, additionalInfo)
    for obj in var:
        if len(obj) != expectedDimensions:
            raise TypeError("Expected list length in dimension 2: " + str(expectedDimensions) + " | Got: " + str(len(obj)) + "! " +
                            additionalInfo)
        
def is_Valid_Float(var: float, additionalInfo: str = "") -> None:
    is_Type(var, float, additionalInfo)
    if np.isnan(var):
        raise ValueError("Got NaN! " + additionalInfo)
    if np.isinf(var):
        raise ValueError("Got Inf! " + additionalInfo)

def is_Valid_Coordinate(var: float, additionalInfo: str = "") -> None:
    is_Valid_Float(var, additionalInfo)
    if var < 0.0:
        raise ValueError("Negative coordinate (" + str(var) + ")! " + additionalInfo)

# ---------------------------------------------------------------------------------------------------------------------

def get_File_Size(fileName: str, unit: str = "B") -> float:
    is_Type(fileName, str)
    is_Type(unit, str)
    # Float, because /= 1024.0 will be done a few lines later
    retValue = float(os.stat(fileName).st_size)
    if unit == "KB" or unit == "KByte":
        retValue /= 1024.0
    elif unit == "MB" or unit == "MByte":
        retValue /= 1024.0 / 1024.0
    elif unit == "GB" or unit == "GByte":
        retValue /= 1024.0 / 1024.0 / 1024.0
    return is_Type_R(retValue, float)

#----------------------------------------------------------------------------------------------------------------------

def get_Percent(onehundredPercent: float, currValue: float) -> float:
    is_Valid_Float(onehundredPercent)
    is_Valid_Float(currValue)
    return is_Type_R((currValue / onehundredPercent) * 100.0, float)

# ---------------------------------------------------------------------------------------------------------------------

def digits_In_Number(number: int = 0) -> int:
    return sum(1 for char in str(number) if char.isdigit())

#----------------------------------------------------------------------------------------------------------------------

def get_Current_Time() -> str:
    return is_Type_R(datetime.datetime.now().strftime("%H:%M:%S"), str)

#----------------------------------------------------------------------------------------------------------------------

def get_Last_Line_From_File(fileName: str) -> str:
    has_Content(fileName)
    lastLine = ""
    try:
        with open(fileName, "r") as inFile:
            lastLine = inFile.readlines()[-1]
    except IndexError:
        # There is no content in the file -> return an empty string
        lastLine = ""
    return is_Type_R(lastLine, str)

#----------------------------------------------------------------------------------------------------------------------

def get_Current_Calc_Step_From_File(fileName: str) -> int:
    has_Content(fileName)
    currCalcStep = 0
    try:
        with open(fileName, "r") as inFile:
            lines = inFile.readlines()
            for i in range(len(lines) - 1, -1, -1):
                matches = re.findall(r"Step\s+(\d+)", lines[i])
                if len(matches) > 0:
                    currCalcStep = int(matches[0])
                    break
    except IndexError:
        # There is no suitable content in the file -> return -1
        currCalcStep = 0
    return is_Type_R(currCalcStep, int)

#----------------------------------------------------------------------------------------------------------------------

def extract_Percentages(inputStr: str) -> list[float]:
    if len(inputStr) == 0:
        return []
    matches = re.findall(r"(\d+\.?\d*)%", inputStr)
    percentages = [float(match) for match in matches]
    return is_Type_R(percentages, list)

#----------------------------------------------------------------------------------------------------------------------

def remove_File(fileName: str) -> None:
    has_Content(fileName)
    errMsgBegin = "Try to delete the file \"" + fileName + "\": "
    try:
        os.remove(fileName)
    except FileNotFoundError:
        print(errMsgBegin + "The file was not found.", file=sys.stderr, flush=True)
    except PermissionError:
        print(errMsgBegin + "You don't have permission to read this file.", file=sys.stderr, flush=True)
    except IOError as e:
        print(errMsgBegin + "An I/O error occurred: " + str(e), file=sys.stderr, flush=True)
    except Exception as e:
        print(errMsgBegin + "An unexpected error occurred: " + str(e), file=sys.stderr, flush=True)
        
#----------------------------------------------------------------------------------------------------------------------
        
def path_Head(fileName: str) -> str:
    has_Content(fileName)
    head, tail = os.path.split(fileName)
    return is_Type_R(head, str)

def path_Tail(fileName: str) -> str:
    has_Content(fileName)
    head, tail = os.path.split(fileName)
    return is_Type_R(tail, str)

def path_Basename(fileName: str) -> str:
    has_Content(fileName)
    result = os.path.splitext(os.path.basename(fileName))[0]
    return is_Type_R(result, str)

#----------------------------------------------------------------------------------------------------------------------

g_lastStartTime: float = 0.0
g_lastEndTime: float = 0.0
def start_Interval(string: str) -> None:
    is_Type(string, str)
    print(string, end="", flush=True)
    global g_lastStartTime
    g_lastStartTime = time.perf_counter()

def end_Interval(string: str) -> None:
    is_Type(string, str)
    global g_lastEndTime
    g_lastEndTime = time.perf_counter()
    print(string + " (" + str("{:7.3f}".format(g_lastEndTime - g_lastStartTime)) + " s)", flush=True)

def start(string: str = "") -> None:
    start_Interval(string)

def end(string: str = "") -> None:
    end_Interval(string)

#----------------------------------------------------------------------------------------------------------------------
