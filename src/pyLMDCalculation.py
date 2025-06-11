import skimage
import threading
import os
import sys
from typing import Any

from lmd.lib import SegmentationLoader, Collection, Shape

from Misc import *
from CalculationThreads import *
from pyLMDCalculationParameter import *

Image.MAX_IMAGE_PIXELS=None



# =====================================================================================================================

class pyLMDCalculation():
    def __init__(self, picData: np.ndarray, calibrationPoints: list, calculationParameter: pyLMDCalculationParameter):
        is_Type(picData, np.ndarray)
        is_Type(calibrationPoints, list)
        is_Type(calculationParameter, pyLMDCalculationParameter)

        self.__picData = picData
        self.__calibrationPoints = calibrationPoints
        self.__calculationParameter = calculationParameter

# ---------------------------------------------------------------------------------------------------------------------

    def start(self) -> None:
        self.__label_Connected_Regions()

        # Remove regions that are too small for further processing
        invalidList: list[int] = [ 1, 2 ]
        flattenPicData = self.__greyscaleData.ravel()
        unique, frequency = np.unique(flattenPicData, return_counts = True)

        print("Step 1:", flush=True)
        start_Interval("Remove areas with the sizes: " + str(invalidList) + " ... \n")
        for i in range(len(unique)):
            if frequency[i] <= self.__TOO_SMALL_AREAS_END:
                flattenPicData[flattenPicData == unique[i]] = self.__BACKGROUND_COL
        end("Done")

        # Create sub-picutures
        print("Step 2:", flush=True)
        start_Interval("Create sub images ... \n")
        subPictures: list[np.ndarray] = self.__create_Sub_Pictures()
        end_Interval("Done")

        # Use the previous generated sub pictures and start pyLMD on this pictures
        self.__XML_files: list[str] = []
        self.__PNG_files: list[str] = []
        counter: int = 0
        print("")
        for curr_pic in subPictures:
            counter += 1
            print("Using sub image " + str(counter), flush=True)
            curr_greyscale_image = np.array(curr_pic).astype(np.uint16)

            if len(np.unique(curr_greyscale_image)) == 1 and np.unique(curr_greyscale_image)[0] == self.__BACKGROUND_COL:
                print("Skip sub image: " + str(counter) + ". Picture contains only background color!", flush=True)
                del curr_greyscale_image
                continue

            all_classes = np.unique(curr_greyscale_image)
            # Remove the first entry if it is 0, because 0 is a reserved class in pyLMD
            if all_classes[0] == self.__BACKGROUND_COL:
                all_classes = all_classes[1 : len(all_classes)]
            cell_sets = [{"classes": all_classes, "well": "A1"}]

            # Fill the config
            loader_config = {
                "orientation_transform": np.array([[0, -1], [1, 0]]), # This transformation is mandatory!
                "binary_smoothing": self.__calculationParameter.get_Binary_Smoothing(),
                "convolution_smoothing": self.__calculationParameter.get_Convolution_Smoothing(),
                "poly_compression_factor": self.__calculationParameter.get_Poly_Compression_Factor(),
                "shape_dilation": self.__calculationParameter.get_Shape_Dilation(),
                "shape_erosion": self.__calculationParameter.get_Shape_Erosion(),
                "distance_heuristic": self.__calculationParameter.get_Distance_Heuristic(),
                "path_optimization": "none"
            }


            sl = SegmentationLoader(config = loader_config, verbose=False)

            outputFileBasename = self.__calculationParameter.get_Output_Basename()
            outputFilePath = self.__calculationParameter.get_Output_Path()
            print("Output file basename: " + outputFileBasename, flush=True)
            print("Output file path: " + outputFilePath, flush=True)
            print("Output XML-File (the file for the LMD device): " + outputFileBasename + ".xml")

            print("Step 3:", flush=True)
            start_Interval("Create shape collection ... ")
            shape_collection = sl(curr_greyscale_image,
                            cell_sets,
                            self.__calibrationPoints)
            end_Interval("Done")

            print(shape_collection.stats(), flush=True)
            # No plotting anymore because it destroys the plot on the GUI!

            # Show the plot and save it
            # shape_collection.plot(calibration = True, save_name = outputFilePath + "/" + outputFileBasename + "_Plot.png", fig_size = (12, 12))
            # Only save the XML file without showing the plot
            shape_collection.save(outputFilePath + "/" + outputFileBasename + ".xml")

            self.__XML_files.append(outputFileBasename + ".xml")
            self.__PNG_files.append(outputFileBasename + "_Plot.png")
            del shape_collection
            del sl

# ---------------------------------------------------------------------------------------------------------------------

    def get_XML_Files(self) -> list[str]:
        return is_Type_R(self.__XML_files, list)

    def get_PNG_Files(self) -> list[str]:
        return is_Type_R(self.__PNG_files, list)

    @staticmethod
    def get_Last_Calc_Step() -> int:
        return is_Type_R(pyLMDCalculation.__LAST_CALC_STEP, int)

    @staticmethod
    def get_Step_Desciption(step: int) -> str:
        is_Type(step, int)
        if step >= len(pyLMDCalculation.__CALC_STEP_NAMES):
            print("Index: " + str(step) + " | Max. len: " + str(len(pyLMDCalculation.__CALC_STEP_NAMES)))
            return ""
        return is_Type_R(pyLMDCalculation.__CALC_STEP_NAMES[step], str)

    @staticmethod
    def is_Percent_Value_Possible(step: int) -> bool:
        is_Type(step, int)
        return is_Type_R(pyLMDCalculation.__PERCENT_VALUES_POSSIBLE[step], bool)

    @staticmethod
    def get_Num_Of_Calc_Steps() -> int:
        return is_Type_R(len(pyLMDCalculation.__CALC_STEP_NAMES), int)

# ---------------------------------------------------------------------------------------------------------------------

    def __label_Connected_Regions(self) -> None:
        # Label connected regions for pyLMD
        start_Interval("Label connected regions ... ")
        (label, num_shapes) = skimage.morphology.label(self.__picData, background=self.__BACKGROUND_COL, return_num=True, connectivity=2)
        self.__greyscaleData = np.array(label).astype(np.uint16)
        end_Interval("Done")
        print(str(num_shapes) + " shapes found", flush=True)
        del label

# ---------------------------------------------------------------------------------------------------------------------

    def __create_Sub_Pictures(self) -> list [np.ndarray]:
        subPictures: list [np.ndarray] = []
        numSubPictures: int = self.__determine_Num_Of_Sub_Pics()

        greyscale_image_thread: np.ndarray = np.array([], np.int16)
        counter_thread: int = 0
        threads: list = []
        counter: int = 0
        for i in range(0, self.__greyscaleData.shape[0], self.__MAX_PICTURE_SIZE):
            for i2 in range(0, self.__greyscaleData.shape[1], self.__MAX_PICTURE_SIZE):
                counter += 1
                end_i: int = 0
                if i + self.__MAX_PICTURE_SIZE < self.__greyscaleData.shape[0]:
                    end_i = i + self.__MAX_PICTURE_SIZE
                else:
                    end_i = self.__greyscaleData.shape[0]
                end_i2: int = 0
                if i2 + self.__MAX_PICTURE_SIZE < self.__greyscaleData.shape[1]:
                    end_i2 = i2 + self.__MAX_PICTURE_SIZE
                else:
                    end_i2 = self.__greyscaleData.shape[1]

                greyscale_image_thread = self.__greyscaleData[i : end_i, i2 : end_i2]
                counter_thread = counter

                threadArgs = (greyscale_image_thread, subPictures, counter_thread, self.__BACKGROUND_COL)
                threads.append(threading.Thread(target=create_Sub_Pictures_Thread, args=threadArgs))

        for i in range(len(threads)):
            threads[i].start()

        for i in range(len(threads)):
            threads[i].join()

        has_List_Type(subPictures, np.ndarray)
        return subPictures

# ---------------------------------------------------------------------------------------------------------------------

    def __determine_Num_Of_Sub_Pics(self) -> int:
        greyscale_image_shape = self.__greyscaleData.shape
        num_sub_pictures = 0
        for i in range(0, greyscale_image_shape[0], self.__MAX_PICTURE_SIZE):
            for i2 in range(0, greyscale_image_shape[1], self.__MAX_PICTURE_SIZE):
                num_sub_pictures += 1
        print("Up to " + str(num_sub_pictures) + " sub images necessary.")
        return is_Type_R(num_sub_pictures, int)

# ---------------------------------------------------------------------------------------------------------------------

    # The normal picture data contains 8 bit RGB data
    __picData: np.ndarray = np.array([], np.int8)
    # Because there are usually more than 255 ROIs, at least 16 bit is necessary
    # In theory this could be not enough. In practice pictures with many ROIs have approx. 5 to 10k
    __greyscaleData: np.ndarray = np.array([], np.int16)
    __calibrationPoints: list [list[float]] = [ [ 0.0, 0.0 ], [ 0.0, 0.0 ], [ 0.0, 0.0 ] ]

    __BACKGROUND_COL: int = 0
    __MAX_PICTURE_SIZE: int = 15000
    __TOO_SMALL_AREAS_END: int = 10

    __LAST_CALC_STEP: int = 3
    __CALC_STEP_NAMES: list[str] = [ "Prepare data", "Remove too small areas", "Create sub images", "Create shape collection - Dilating shapes",
        "Create shape collection - Create shapes", "Create shape collection - Calculating polygons" ]
    __PERCENT_VALUES_POSSIBLE: list[bool] = [ False, False, False, True, True, True ]

# =====================================================================================================================



if __name__ == "__main__":
    # First param: file name of the picutre
    fileName = sys.argv[1]
    # The next six: calibration points
    calPointsTemp: list[float] = []
    for i in range(6):
        calPointsTemp.append(float(sys.argv[2 + i]))
    calPoints: list[list[float]] = [ [ calPointsTemp[0], calPointsTemp[1] ], [ calPointsTemp[2], calPointsTemp[3] ], [ calPointsTemp[4], calPointsTemp[5] ] ]

    # Is there an optional output path?
    outputPath: str = ""
    if len(sys.argv) > 14:
        outputPath = sys.argv[14]
        print("Using: \"" + path_Head(sys.argv[14]) + "\" as output path")

    # The rest are the pyLMD settings
    param = pyLMDCalculationParameter(int(sys.argv[8]), int(sys.argv[9]), int(sys.argv[10]), int(sys.argv[11]), int(sys.argv[12]),
                                      int(sys.argv[13]), outputPath)

    print("PID: " + str(os.getpid()))
    print("Calibration points: " + str(calPoints))
    print("> pyLMD settings <\n" + str(param) + "\n", flush=True)

    try:
        img = Image.open(fileName)
    except FileNotFoundError:
        print("The file was not found.", file=sys.stderr, flush=True)
    except PermissionError:
        print("You don't have permission to read this file.", file=sys.stderr, flush=True)
    except IOError as e:
        print("An I/O error occurred: " + str(e), file=sys.stderr, flush=True)
    except Exception as e:
        print("An unexpected error occurred: " + str(e), file=sys.stderr, flush=True)
    picData = np.array(img).astype(np.uint8)

    # Now are all data and information available for creating the calculation object
    calcObj = pyLMDCalculation(picData, calPoints, param)
    calcObj.start()
    print("END", flush=True)
    exit(0)
