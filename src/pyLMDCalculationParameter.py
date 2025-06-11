import copy

from Misc import *
from pyLMDParameterLimits import *



class pyLMDCalculationParameter():
    def __init__(self, shapeDilation: int, shapeErosion: int, binarySmoothing: int, convolutionSmoothing: int,
        polyCompressionFactor: int, distanceHeuristic: int, outputPath: str = ""):
        is_Type(shapeDilation, int)
        is_Type(shapeErosion, int)
        is_Type(binarySmoothing, int)
        is_Type(convolutionSmoothing, int)
        is_Type(polyCompressionFactor, int)
        is_Type(distanceHeuristic, int)
        is_Type(outputPath, str)

        if shapeDilation < pyLMDParameterLimits.get_Shape_Dilation_Min():
            raise ValueError("Shape dilation is lower than " + str(pyLMDParameterLimits.get_Shape_Dilation_Min()) +
            ". Given value: " + str(shapeDilation))
        if shapeErosion < pyLMDParameterLimits.get_Shape_Erosion_Min():
            raise ValueError("Shape erosion is lower than " + str(pyLMDParameterLimits.get_Shape_Erosion_Min()) +
            ". Given value: " + str(shapeErosion))
        if binarySmoothing < pyLMDParameterLimits.get_Binary_Smoothing_Min():
            raise ValueError("Binary smoothing is lower than " + str(pyLMDParameterLimits.get_Binary_Smoothing_Min()) +
            ". Given value: " + str(binarySmoothing))
        if convolutionSmoothing < pyLMDParameterLimits.get_Convolution_Smoothing_Min():
            raise ValueError("Convolution smoothing is lower than " + str(pyLMDParameterLimits.get_Convolution_Smoothing_Min()) +
            ". Given value: " + str(convolutionSmoothing))
        if polyCompressionFactor < pyLMDParameterLimits.get_Poly_Compression_Factor_Min():
            raise ValueError("Poly compression factor is lower than " + str(pyLMDParameterLimits.get_Poly_Compression_Factor_Min()) +
            ". Given value: " + str(polyCompressionFactor))
        if distanceHeuristic < pyLMDParameterLimits.get_Distance_Heuristic_Min():
            raise ValueError("Distance heuristic is lower than " + str(pyLMDParameterLimits.get_Distance_Heuristic_Min()) +
            ". Given value: " + str(distanceHeuristic))

        self.__shapeDilation = shapeDilation
        self.__shapeErosion = shapeErosion
        self.__binarySmoothing = binarySmoothing
        self.__convolutionSmoothing = convolutionSmoothing
        self.__polyCompressionFactor = polyCompressionFactor
        self.__distanceHeuristic = distanceHeuristic
        self.__outputName = copy.deepcopy(outputPath)

# ---------------------------------------------------------------------------------------------------------------------

    def __str__(self) -> str:
        strRep  = "shapeDilation:         " + str(self.__shapeDilation) + "\n"
        strRep += "shapeErosion:          " + str(self.__shapeErosion) + "\n"
        strRep += "binarySmoothing:       " + str(self.__binarySmoothing) + "\n"
        strRep += "convolutionSmoothing:  " + str(self.__convolutionSmoothing) + "\n"
        strRep += "polyCompressionFactor: " + str(self.__polyCompressionFactor) + "\n"
        strRep += "distanceHeuristic:     " + str(self.__distanceHeuristic)
        if len(self.__outputName) > 0:
            strRep += "\nOutputPath:            " + path_Head(self.__outputName)

        prefix = "(!) "

        # Add hints when the values are greater than the recommended maximum
        recommendedExceededHints = "\n\n"
        if self.__shapeDilation > pyLMDParameterLimits.get_Shape_Dilation_Recommended_Max():
            recommendedExceededHints += prefix + "Recommended maximum for shapeDilation is: " + str(pyLMDParameterLimits.get_Shape_Dilation_Recommended_Max()) + "\n"
        if self.__shapeErosion > pyLMDParameterLimits.get_Shape_Erosion_Recommended_Max():
            recommendedExceededHints += prefix + "Recommended maximum for shapeErosion is: " + str(pyLMDParameterLimits.get_Shape_Erosion_Recommended_Max()) + "\n"
        if self.__binarySmoothing > pyLMDParameterLimits.get_Binary_Smoothing_Recommended_Max():
            recommendedExceededHints += prefix + "Recommended maximum for binarySmoothing is: " + str(pyLMDParameterLimits.get_Binary_Smoothing_Recommended_Max()) + "\n"
        if self.__convolutionSmoothing > pyLMDParameterLimits.get_Convolution_Smoothing_Recommended_Max():
            recommendedExceededHints += prefix + "Recommended maximum for convolutionSmoothing is: " + str(pyLMDParameterLimits.get_Convolution_Smoothing_Recommended_Max()) + "\n"
        if self.__polyCompressionFactor > pyLMDParameterLimits.get_Poly_Compression_Factor_Recommended_Max():
            recommendedExceededHints += prefix + "Recommended maximum for polyCompressionFactor is: " + str(pyLMDParameterLimits.get_Poly_Compression_Factor_Recommended_Max()) + "\n"
        if self.__distanceHeuristic > pyLMDParameterLimits.get_Distance_Heuristic_Recommended_Max():
            recommendedExceededHints += prefix + "Recommended maximum for distanceHeuristic is: " + str(pyLMDParameterLimits.get_Distance_Heuristic_Recommended_Max()) + "\n"
        if len(strRep) > len("\n\n"):
            strRep += recommendedExceededHints
        return is_Type_R(strRep, str)

# ---------------------------------------------------------------------------------------------------------------------

    def get_Parameter_As_Str_List(self) -> list[str]:
        result = [ str(self.__shapeDilation), str(self.__shapeErosion), str(self.__binarySmoothing),
                   str(self.__convolutionSmoothing), str(self.__polyCompressionFactor), str(self.__distanceHeuristic) ]
        return result

# ---------------------------------------------------------------------------------------------------------------------

    def set_Shape_Dilation(self, newVal: int) -> None:
        is_Type(newVal, int)
        if newVal < pyLMDParameterLimits.get_Shape_Dilation_Min():
            raise ValueError("New shape dilation is lower than " + str(pyLMDParameterLimits.get_Shape_Dilation_Min()) +
            ". Given value: " + str(newVal))
        self.__shapeDilation = newVal

    def get_Shape_Dilation(self) -> int:
        return is_Type_R(self.__shapeDilation, int)

# ---------------------------------------------------------------------------------------------------------------------

    def set_Shape_Erosion(self, newVal: int) -> None:
        is_Type(newVal, int)
        if newVal < pyLMDParameterLimits.get_Shape_Erosion_Min():
            raise ValueError("New shape erosion is lower than " + str(pyLMDParameterLimits.get_Shape_Erosion_Min()) +
            ". Given value: " + str(newVal))
        self.__shapeErosion = newVal

    def get_Shape_Erosion(self) -> int:
        return is_Type_R(self.__shapeErosion, int)

# ---------------------------------------------------------------------------------------------------------------------

    def set_Binary_Smoothing(self, newVal: int) -> None:
        is_Type(newVal, int)
        if newVal < pyLMDParameterLimits.get_Binary_Smoothing_Min():
            raise ValueError("New binary smoothing is lower than " + str(pyLMDParameterLimits.get_Binary_Smoothing_Min()) +
            ". Given value: " + str(newVal))
        self.__binarySmoothing = newVal

    def get_Binary_Smoothing(self) -> int:
        return is_Type_R(self.__binarySmoothing, int)

# ---------------------------------------------------------------------------------------------------------------------

    def set_Convolution_Smoothing(self, newVal: int) -> None:
        is_Type(newVal, int)
        if newVal < pyLMDParameterLimits.get_Convolution_Smoothing_Min():
            raise ValueError("New convolution smoothing is lower than " + str(pyLMDParameterLimits.get_Convolution_Smoothing_Min()) +
            ". Given value: " + str(newVal))
        self.__convolutionSmoothing = newVal

    def get_Convolution_Smoothing(self) -> int:
        return is_Type_R(self.__convolutionSmoothing, int)

# ---------------------------------------------------------------------------------------------------------------------

    def set_Poly_Compression_Factor(self, newVal: int) -> None:
        is_Type(newVal, int)
        if newVal < pyLMDParameterLimits.get_Poly_Compression_Factor_Min():
            raise ValueError("New poly compression factor is lower than " + str(pyLMDParameterLimits.get_Poly_Compression_Factor_Min()) +
            ". Given value: " + str(newVal))
        self.__polyCompressionFactor = newVal

    def get_Poly_Compression_Factor(self) -> int:
        return is_Type_R(self.__polyCompressionFactor, int)

# ---------------------------------------------------------------------------------------------------------------------

    def set_Distance_Heuristic(self, newVal: int) -> None:
        is_Type(newVal, int)
        if newVal < pyLMDParameterLimits.get_Distance_Heuristic_Min():
            raise ValueError("New distance heuristic is lower than " + str(pyLMDParameterLimits.get_Distance_Heuristic_Min()) +
            ". Given value: " + str(newVal))
        self.__distanceHeuristic = newVal

    def get_Distance_Heuristic(self) -> int:
        return is_Type_R(self.__distanceHeuristic, int)

# ---------------------------------------------------------------------------------------------------------------------

    def get_Output_Basename(self) -> str:
        return is_Type_R(path_Basename(self.__outputName), str)

    def get_Output_Path(self) -> str:
        return is_Type_R(path_Head(self.__outputName), str)

    def get_Output_Name(self) -> str:
        return is_Type_R(self.__outputName, str)
