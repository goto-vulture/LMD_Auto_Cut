class pyLMDParameterLimits():
    #def __init__(self):
        # Nothing to do ...
        # Only a class with static methods

    @staticmethod
    def get_Shape_Dilation_Min() -> int:
        return pyLMDParameterLimits.__SHAPE_DILATION_LIMITS["Min"]
    @staticmethod
    def get_Shape_Dilation_Max() -> int:
        return pyLMDParameterLimits.__SHAPE_DILATION_LIMITS["Max"]
    @staticmethod
    def get_Shape_Dilation_Recommended_Max() -> int:
        return pyLMDParameterLimits.__SHAPE_DILATION_LIMITS["RecommendedMax"]
    @staticmethod
    def get_Shape_Dilation_Step() -> int:
        return pyLMDParameterLimits.__SHAPE_DILATION_LIMITS["Step"]
    @staticmethod
    def get_Shape_Dilation_Default() -> int:
        return pyLMDParameterLimits.__SHAPE_DILATION_LIMITS["Default"]
    @staticmethod
    def get_Shape_Dilation_All() -> dict:
        return pyLMDParameterLimits.__SHAPE_DILATION_LIMITS

    @staticmethod
    def get_Shape_Erosion_Min() -> int:
        return pyLMDParameterLimits.__SHAPE_EROSION_LIMITS["Min"]
    @staticmethod
    def get_Shape_Erosion_Max() -> int:
        return pyLMDParameterLimits.__SHAPE_EROSION_LIMITS["Max"]
    @staticmethod
    def get_Shape_Erosion_Recommended_Max() -> int:
        return pyLMDParameterLimits.__SHAPE_EROSION_LIMITS["RecommendedMax"]
    @staticmethod
    def get_Shape_Erosion_Step() -> int:
        return pyLMDParameterLimits.__SHAPE_EROSION_LIMITS["Step"]
    @staticmethod
    def get_Shape_Erosion_Default() -> int:
        return pyLMDParameterLimits.__SHAPE_EROSION_LIMITS["Default"]
    @staticmethod
    def get_Shape_Erosion_All() -> dict:
        return pyLMDParameterLimits.__SHAPE_EROSION_LIMITS

    @staticmethod
    def get_Binary_Smoothing_Min() -> int:
        return pyLMDParameterLimits.__BINARY_SMOOTHING["Min"]
    @staticmethod
    def get_Binary_Smoothing_Max() -> int:
        return pyLMDParameterLimits.__BINARY_SMOOTHING["Max"]
    @staticmethod
    def get_Binary_Smoothing_Recommended_Max() -> int:
        return pyLMDParameterLimits.__BINARY_SMOOTHING["RecommendedMax"]
    @staticmethod
    def get_Binary_Smoothing_Step() -> int:
        return pyLMDParameterLimits.__BINARY_SMOOTHING["Step"]
    @staticmethod
    def get_Binary_Smoothing_Default() -> int:
        return pyLMDParameterLimits.__BINARY_SMOOTHING["Default"]
    @staticmethod
    def get_Binary_Smoothing_All() -> dict:
        return pyLMDParameterLimits.__BINARY_SMOOTHING

    @staticmethod
    def get_Convolution_Smoothing_Min() -> int:
        return pyLMDParameterLimits.__CONVOLUTION_SMOOTHING["Min"]
    @staticmethod
    def get_Convolution_Smoothing_Max() -> int:
        return pyLMDParameterLimits.__CONVOLUTION_SMOOTHING["Max"]
    @staticmethod
    def get_Convolution_Smoothing_Recommended_Max() -> int:
        return pyLMDParameterLimits.__CONVOLUTION_SMOOTHING["RecommendedMax"]
    @staticmethod
    def get_Convolution_Smoothing_Step() -> int:
        return pyLMDParameterLimits.__CONVOLUTION_SMOOTHING["Step"]
    @staticmethod
    def get_Convolution_Smoothing_Default() -> int:
        return pyLMDParameterLimits.__CONVOLUTION_SMOOTHING["Default"]
    @staticmethod
    def get_Convolution_Smoothing_All() -> dict:
        return pyLMDParameterLimits.__CONVOLUTION_SMOOTHING

    @staticmethod
    def get_Poly_Compression_Factor_Min() -> int:
        return pyLMDParameterLimits.__POLY_COMPRESSION_FACTOR["Min"]
    @staticmethod
    def get_Poly_Compression_Factor_Max() -> int:
        return pyLMDParameterLimits.__POLY_COMPRESSION_FACTOR["Max"]
    @staticmethod
    def get_Poly_Compression_Factor_Recommended_Max() -> int:
        return pyLMDParameterLimits.__POLY_COMPRESSION_FACTOR["RecommendedMax"]
    @staticmethod
    def get_Poly_Compression_Factor_Step() -> int:
        return pyLMDParameterLimits.__POLY_COMPRESSION_FACTOR["Step"]
    @staticmethod
    def get_Poly_Compression_Factor_Default() -> int:
        return pyLMDParameterLimits.__POLY_COMPRESSION_FACTOR["Default"]
    @staticmethod
    def get_Poly_Compression_Factor_All() -> dict:
        return pyLMDParameterLimits.__POLY_COMPRESSION_FACTOR

    @staticmethod
    def get_Distance_Heuristic_Min() -> int:
        return pyLMDParameterLimits.__DISTANCE_HEURISTIC["Min"]
    @staticmethod
    def get_Distance_Heuristic_Max() -> int:
        return pyLMDParameterLimits.__DISTANCE_HEURISTIC["Max"]
    @staticmethod
    def get_Distance_Heuristic_Recommended_Max() -> int:
        return pyLMDParameterLimits.__DISTANCE_HEURISTIC["RecommendedMax"]
    @staticmethod
    def get_Distance_Heuristic_Step() -> int:
        return pyLMDParameterLimits.__DISTANCE_HEURISTIC["Step"]
    @staticmethod
    def get_Distance_Heuristic_Default() -> int:
        return pyLMDParameterLimits.__DISTANCE_HEURISTIC["Default"]
    @staticmethod
    def get_Distance_Heuristic_All() -> dict:
        return pyLMDParameterLimits.__DISTANCE_HEURISTIC

    # Step is currently not in use
    __SHAPE_DILATION_LIMITS     = { "Min": 0, "Max": 100,  "RecommendedMax": 10,  "Step": 1,   "Default": 0   }
    __SHAPE_EROSION_LIMITS      = { "Min": 0, "Max": 100,  "RecommendedMax": 10,  "Step": 1,   "Default": 0   }
    __BINARY_SMOOTHING          = { "Min": 0, "Max": 100,  "RecommendedMax": 30,  "Step": 2,   "Default": 14  }
    __CONVOLUTION_SMOOTHING     = { "Min": 0, "Max": 400,  "RecommendedMax": 40,  "Step": 5,   "Default": 15  }
    __POLY_COMPRESSION_FACTOR   = { "Min": 0, "Max": 500,  "RecommendedMax": 50,  "Step": 10,  "Default": 30  }
    __DISTANCE_HEURISTIC        = { "Min": 0, "Max": 5000, "RecommendedMax": 500, "Step": 100, "Default": 300 }
