from . import basemode, testmode, editjobmode

class Mode():
    def __init__(self):
        pass

class Modes():
    Base = basemode.BaseMode()
    Test = testmode.TestMode()
    EditJob = editjobmode.EditJobMode()
    
