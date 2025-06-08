import numpy as np
import copy
import skimage
import queue
from PIL import Image

from Misc import *
from PictureData import *

# ---------------------------------------------------------------------------------------------------------------------

def create_Sub_Pictures_Thread(subImg: np.ndarray, resultSubImg: list, counter: int, backgroundColor: int):
    is_Type(subImg, np.ndarray)
    has_List_Type(resultSubImg, np.ndarray)
    is_Type(counter, int)
    is_Type(backgroundColor, int)

    if len(np.unique(subImg)) == 1 and np.unique(subImg)[0] == 0:
        print("Skip sub picture " + str(counter) + ". No content!", flush=True)
        return

    # Mark the whole border black
    for x in range(subImg.shape[0]):
        subImg[x, 0] = 0
        subImg[x, subImg.shape[1] - 1] = backgroundColor
    for y in range(subImg.shape[1]):
        subImg[0, y] = 0
        subImg[subImg.shape[0] - 1, y] = backgroundColor

    # Re-label independent objects to reduce the size of an object with the same color
    # This can (and usually will) reduce the runtime of pyLMD
    (label, num_shapes) = skimage.morphology.label(subImg, background=backgroundColor, return_num=True, connectivity=2)
    resultSubImg.append(copy.deepcopy(label))

    # Save the current sub image in a file
    # saveImageToFile(label, str(counter) + "_sub_img")

    del label

# ---------------------------------------------------------------------------------------------------------------------

def write_Stdout_To_File(fileName: str, process):
    has_Content(fileName)
    if process is None:
        return
    with open(fileName, "w") as outFile:
        while True:
            output = process.stdout.readline()
            if not output:
                break
            outFile.write(get_Current_Time() + ": " + output)
            outFile.flush()

# ---------------------------------------------------------------------------------------------------------------------

def write_Stderr_To_File(fileName: str, process):
    has_Content(fileName)
    if process is None:
        return
    with open(fileName, "w") as outFile:
        while True:
            output = process.stderr.readline()
            if not output:
                break
            outFile.write(get_Current_Time() + ": " + output)
            outFile.flush()

# ---------------------------------------------------------------------------------------------------------------------

def load_Picture_Thread(pictureDataObj: PictureData, fileName: str, pictureSlot: int = 1):
    is_Type(pictureDataObj, PictureData)
    is_Type(pictureSlot, int)
    has_Content(fileName)

    start("Load picture: " + fileName)
    pictureDataObj.load_Picture_Progress(fileName, pictureSlot)
    end()

# ---------------------------------------------------------------------------------------------------------------------