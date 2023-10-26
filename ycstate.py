import World
import PySimpleGUI as sg
from modes import Modes

class YCState():
    def __init__(self, 
                 world:World.WorldState = None, 
                 mainWindow:sg.Window = None, 
                 activeMode:Modes.Base = None,
                 nextJobNumber:int = None,
                 visualizers:dict = None,
                 jobs:list = None
                 ):
        self.world = world
        self.mainWindow = mainWindow
        self.activeMode = activeMode
        self.nextJobNumber = nextJobNumber
        self.visualizers = visualizers
        self.jobs = jobs
        self.setMode('base')
    
    def setBanner(self, newText:str):
        print(newText)
        self.mainWindow['bannerText'].update(newText)

    def setMode(self, modeKey):
        self.activeMode.deactivate()
        self.activeMode = Modes.Base.allModes[modeKey]
        self.activeMode.activate(self)
        
    