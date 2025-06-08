import numpy as np
import copy
import io
import threading
import sys
from PIL import Image

from Misc import *



class PictureData():
    """
    Container object for the two picture data arrays.
    """
    
    def __init__(self, slicingFactor: int = 1, picData1 = None, picData2 = None):
        """
        The PictureData constructor.
        
        Args:
            slicingFactor:  Slicing factor for the picture data
            picData1:       Data of the first picture
            picData2:       Data of the second picture
            
        Raises:
            TypeError, ValueError
        """
        is_Type(slicingFactor, int)
        if slicingFactor < 1:
            raise ValueError("slicingFactor must be at least 1. Given value: " + str(slicingFactor))
        is_Type_If_Not_None(picData1, np.ndarray)
        is_Type_If_Not_None(picData2, np.ndarray)

        self.__picData1 = picData1
        self.__picData2 = picData2
        self.__picData1Sliced = picData1
        self.__picData2Sliced = picData2

        self.__coordinateSlicingFactor = slicingFactor
        self.__dataSlicingFactor = slicingFactor
        if picData1 is not None:
            self.set_Picture_Data(picData1, PictureData.FIRST_PIC)
        if picData2 is not None:
            self.set_Picture_Data(picData2, PictureData.SEC_PIC)
        self.update_Slicing_Factor(slicingFactor)

        # Variable shows the current process of a loading operation
        self.__loadPictureProgress = 0
        self.__stopEvent = threading.Event()

# ---------------------------------------------------------------------------------------------------------------------

    def load_Picture(self, fileName: str, pictureSlot: int) -> None:
        """
        Loads picture data without progress information.
        
        Args:
            fileName:       Name of the file
            pictureSlot:    Slot for the loaded picutre (Is it picture one or two?)
            
        Raises:
            TypeError, ValueError
        """
        has_Content(fileName)
        self.__check_Picture_Slot(pictureSlot)
        
        newImg = Image.open(fileName)
        picData = np.array(newImg).astype(np.uint8)

        self.set_Picture_Data(picData, pictureSlot)

# ---------------------------------------------------------------------------------------------------------------------

    def load_Picture_Progress(self, fileName: str, pictureSlot: int) -> None:
        """
        Loads picture data with progress information.
        
        Args:
            fileName:       Name of the file
            pictureSlot:    Slot for the loaded picutre (Is it picture one or two?)
            
        Raises:
            TypeError, ValueError
        """
        has_Content(fileName)
        self.__check_Picture_Slot(pictureSlot)
        
        try:
            # Open the file in binary mode
            with open(fileName, "rb") as f:
                fileBuffer = io.BytesIO()
                bytesRead = 0
                fileSize = get_File_Size(fileName)

                # Load while the file was read completely or stop when the stop event was set
                while not self.__stopEvent.is_set():
                    chunk = f.read(self.__LOADING_PROCESS_CHUNK_SIZE)
                    if not chunk:
                        break
                    fileBuffer.write(chunk)
                    bytesRead += self.__LOADING_PROCESS_CHUNK_SIZE

                    # Calculate process
                    self.__loadPictureProgress = int((bytesRead / fileSize) * 100.0)
            fileBuffer.seek(0)
        except FileNotFoundError:
            print("File \"" + fileName + "\": The file was not found.", file=sys.stderr)
            return
        except PermissionError:
            print("File \"" + fileName + "\": You don't have permission to read this file.", file=sys.stderr)
            return
        except IOError as e:
            print(f"File \"" + fileName + "\": An I/O error occurred: {e}", file=sys.stderr)
            return
        except Exception as e:
            print(f"File \"" + fileName + "\": An unexpected error occurred: {e}", file=sys.stderr)
            return
                    

        # After the file was loaded in memory, the Image.open uses the data, that was previously loaded, instead of
        # handling a file
        try:
            newImg = Image.open(fileBuffer)
            picData = np.array(newImg).astype(np.uint8)
            self.set_Picture_Data(picData, pictureSlot)
        except OSError:
            # When the loading was interrupted by the user, the data in the buffer will be no valid picture
            # -> Exception will be raised
            # There cannot be a suitable operation executed here, with the exception to prevent any altering of the
            # previous picture data
            i = 0 # Dummy code
            return
        except Exception as e:
            print(f"An unexpected error occurred after the file \"" + fileName + "\" was loaded: {e}", file=sys.stderr)

# ---------------------------------------------------------------------------------------------------------------------

    def set_Picture_Data(self, picData, pictureSlot: int) -> None:
        """
        Sets the picture data of a slot with a deep copy of the data.
        
        Args:
            picData:        Data of an already loaded file
            pictureSlot:    Slot for the loaded picutre (Is it picture one or two?)
            
        Raises:
            TypeError, ValueError
        """
        is_Type(picData, np.ndarray)
        self.__check_Picture_Slot(pictureSlot)

        if pictureSlot == PictureData.FIRST_PIC:
            self.__picData1 = copy.deepcopy(picData)
        elif pictureSlot == PictureData.SEC_PIC:
            self.__picData2 = copy.deepcopy(picData)
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) + ". Valid are " +
                             str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))
        self.has_Picture_Data_The_Same_Shape(printErrMsg = True)
        self.update_Slicing_Factor(self.__dataSlicingFactor)

# ---------------------------------------------------------------------------------------------------------------------

    def is_Picture_Data_Loaded(self, pictureSlot: int) -> bool:
        self.__check_Picture_Slot(pictureSlot)
        
        if pictureSlot == PictureData.FIRST_PIC:
            return True if self.__picData1 is not None else False
        elif pictureSlot == PictureData.SEC_PIC:
            return True if self.__picData2 is not None else False
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) + ". Valid are " +
                             str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))

# ---------------------------------------------------------------------------------------------------------------------

    def has_Picture_Data_The_Same_Shape(self, printErrMsg: bool = True) -> bool:
        is_Type(printErrMsg, bool)
        if self.is_Picture_Data_Loaded(PictureData.FIRST_PIC) == False or self.is_Picture_Data_Loaded(PictureData.SEC_PIC) == False:
            return False
        picData1Shape = [ self.__picData1.shape[0], self.__picData1.shape[1] ]
        picData2Shape = [ self.__picData2.shape[0], self.__picData2.shape[1] ]
        if picData1Shape != picData2Shape:
            if printErrMsg:
                print("\nMismatch of picure sizes. Picture 1: " + str(picData1Shape) + " | Picture 2: " + str(picData2Shape) +
                    "\nThis could lead to a reduced precision while selecting the marking points!", flush = True)
            return False
        else:
            return True

# ---------------------------------------------------------------------------------------------------------------------

    def get_Picture_Data(self, pictureSlot: int) -> np.ndarray:
        self.__check_Picture_Slot(pictureSlot)
        
        if pictureSlot == PictureData.FIRST_PIC:
            return is_Type_R(self.__picData1, np.ndarray)
        elif pictureSlot == PictureData.SEC_PIC:
            return is_Type_R(self.__picData2, np.ndarray)
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) + ". Valid are " +
                             str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))

# ---------------------------------------------------------------------------------------------------------------------

    def get_Picture_Data_Sliced(self, pictureSlot: int) -> np.ndarray:
        self.__check_Picture_Slot(pictureSlot)
        
        if pictureSlot == PictureData.FIRST_PIC:
            return is_Type_R(self.__picData1Sliced, np.ndarray)
        elif pictureSlot == PictureData.SEC_PIC:
            return is_Type_R(self.__picData2Sliced, np.ndarray)
        else:
            raise ValueError("Invalid picutre selected. Selected was " + str(pictureSlot) + ". Valid are " +
                             str(PictureData.FIRST_PIC) + " or " + str(PictureData.SEC_PIC))

# ---------------------------------------------------------------------------------------------------------------------

    def update_Slicing_Factor(self, newSlicingFactor: int) -> None:
        is_Type(newSlicingFactor, int)
        if newSlicingFactor < 1:
            raise ValueError("slicingFactor must be at least 1. Given value: " + str(slicingFactor))

        self.__dataSlicingFactor = newSlicingFactor
        if self.__picData1 is not None:
            self.__picData1Sliced = self.__picData1[::self.__dataSlicingFactor, ::self.__dataSlicingFactor]
        if self.__picData2 is not None:
            self.__picData2Sliced = self.__picData2[::self.__dataSlicingFactor, ::self.__dataSlicingFactor]

# ---------------------------------------------------------------------------------------------------------------------

    def get_Data_Slicing_Factor(self) -> int:
        return is_Type_R(self.__dataSlicingFactor, int)

    def get_Coordinate_Slicing_Factor(self) -> int:
        return is_Type_R(self.__coordinateSlicingFactor, int)

    def get_Loading_Process(self) -> int:
        return is_Type_R(self.__loadPictureProgress, int)

    def set_Stop_Event(self) -> None:
        self.__stopEvent.set()

    def clear_Stop_Event(self) -> None:
        self.__stopEvent.clear()

# ---------------------------------------------------------------------------------------------------------------------

    def __check_Picture_Slot(self, pictureSlot) -> None:
        is_Type(pictureSlot, int)
        if pictureSlot is not PictureData.FIRST_PIC and pictureSlot is not PictureData.SEC_PIC:
            raise ValueError("Invalid picture slot was given. Valid are " + str(PictureData.FIRST_PIC) + " and " +
                             str(PictureData.SEC_PIC) + ". Given value: " + str(pictureSlot))
        
# ---------------------------------------------------------------------------------------------------------------------

    FIRST_PIC: int = 0
    SEC_PIC: int = 1
    # Unit: byte
    __LOADING_PROCESS_CHUNK_SIZE: int = 65536
