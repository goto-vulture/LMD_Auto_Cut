from Misc import *



class pyLMDSpinboxParameter():
    def __init__(self, text: str, callback, **param):
        has_Content(text)
        is_Type(param["Min"], int)
        is_Type(param["Max"], int)
        is_Type(param["Default"], int)
        is_Type(param["Step"], int)
        is_Not_None(callback, "Callback function for the Spinboxes.")
        self.text = text
        self.callback = callback
        self.minVal = param["Min"]
        self.maxVal = param["Max"]
        self.default = param["Default"]
        self.step = param["Step"]
