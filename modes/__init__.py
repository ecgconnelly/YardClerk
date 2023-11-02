from . import basemode, switchmode, testmode, inboundtrainmode, humpmode

class Mode():
    def __init__(self):
        pass

class Modes():
    Base = basemode.BaseMode()
    Test = testmode.TestMode()
    EditJob = switchmode.SwitchMode()
    InboundTrain = inboundtrainmode.InboundTrainMode()
    Hump = humpmode.HumpMode()