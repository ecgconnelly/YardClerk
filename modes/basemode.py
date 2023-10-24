class BaseMode():
    
    allModes = {}

    def __init__(self):
        self.keyCommands = {
            '<Control-KeyPress-R>' : self.RestartProgram,
            '<Control-KeyPress-t>' : self.selectTestMode
            }
        self.registerMode('base')

    def registerMode(self, modeKey:str):        
        if modeKey not in self.allModes:
            self.allModes[modeKey] = self

    def RestartProgram(self, programState):
        print("night night")

    def selectTestMode(self, programState):
        programState.setMode('test')





    def HandleKeyEvent(self, keyEventString, programState):
        if keyEventString not in self.keyCommands:
            return None
        
        handler = self.keyCommands[keyEventString]
        handler(programState)
        # if keystroke in self.keyEvents:
        #     return self.keyEvents[keystroke]
        # else:
        #     return None