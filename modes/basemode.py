class BaseMode():
    
    allModes = {}

    def __init__(self):
        self.keyCommands = {
            '<Control-KeyPress-R>' : self.RestartProgram,
            '<Control-KeyPress-t>' : self.selectTestMode,
            '<Control-KeyPress-n>' : self.createNewJob,
            }
        self.registerMode('base')

    def registerMode(self, modeKey:str):        
        if modeKey not in self.allModes:
            self.allModes[modeKey] = self

    def RestartProgram(self, programState):
        print("night night")

    def createNewJob(self, programState):
        programState.setMode('editjob')

    def selectTestMode(self, programState):
        programState.setMode('test')


    def HandleEvent(self, event, values, programState):
        if event in self.keyCommands:
            handler = self.keyCommands[event]
            handler(programState)

    def activate(self):
        print(f"Entering {self.__class__}")    

    def deactivate(self):
        print(f"Leaving {self.__class__}")