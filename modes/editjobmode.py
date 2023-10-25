from . import basemode
class EditJobMode(basemode.BaseMode):

    def __init__(self):
        self.registerMode('editjob')
        self.keyCommands = {
            '<KeyPress-Escape>' : self.selectBaseMode
            }
    
    def selectBaseMode(self, programState):
        programState.setMode('base')