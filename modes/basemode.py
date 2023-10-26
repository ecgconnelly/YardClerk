import PySimpleGUI as sg
import ycstate
import YCUI

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
        

    def createNewJob(self):
        programState = self.programState
        opsTab = programState.mainWindow['operationsTab']
        opsTab.select()

        newJob = YCUI.newJobPopup(programState)

        if newJob is not None:
            programState.nextJobNumber += 1
            programState.jobs.append(newJob)
            YCUI.updateJobsTable(programState)
            programState.setMode('editjob')
            programState.activeMode.settingUpJob = newJob


    def selectTestMode(self, programState):
        programState.setMode('test')


    def HandleEvent(self, event, values):
        if event in self.keyCommands:
            handler = self.keyCommands[event]
            handler()

        if 'subyardVis' in event:
            handler = self.handleVisualizerClick(event, values)

    def handleVisualizerClick(self, event, values):
        print(f"You clicked on visualizer {event} but this mode doesn't care")

    def activate(self, programState):
        print(f"Entering {self.__class__}")
        self.programState = programState

    def deactivate(self):
        print(f"Leaving {self.__class__}")