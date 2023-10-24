from . import basemode
class TestMode(basemode.BaseMode):

    def __init__(self):
        self.registerMode('test')
        self.keyCommands = {
            '<KeyPress-Escape>' : self.selectBaseMode
            }
    
    def selectBaseMode(self, programState):
        programState.setMode('base')