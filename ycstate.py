import World
import YCUI
import PySimpleGUI as sg
from modes import Modes

class YCState():
    def __init__(self, 
                 world:World.WorldState = None, 
                 mainWindow:sg.Window = None, 
                 activeMode:Modes.Base = None,
                 nextJobNumber:int = None,
                 visualizers:dict = None,
                 ops:list = None,
                 jobs:list = None
                 ):
        self.world = world
        self.mainWindow = mainWindow
        self.activeMode = activeMode
        self.nextJobNumber = nextJobNumber
        self.visualizers = visualizers
        self.ops = ops
        self.jobs = jobs
        self.setMode('base')
    
    def setBanner(self, newText:str):
        print(newText)
        self.mainWindow['bannerText'].update(newText)

    def setMode(self, modeKey):
        self.activeMode.deactivate()
        self.activeMode = Modes.Base.allModes[modeKey]
        self.activeMode.activate(self)

    def addHumpOperation(self, trackName):
        # hump the rightmost unit on selected track
        # iterate one by one until track is empty
        # create undo stack for each humped unit
        moves = []
        while True:
        # what is that unit??
            sourceTrackObj = self.world.getTrackObject(trackName)
            units = sourceTrackObj.units
            uCount = len(units)
            if uCount == 0:
                break # stop humping, we have no cars
            humpUnit = units[uCount-1]
            if humpUnit.isLoco():
                break # don't hump engines
            tag = humpUnit.destinationTag
            
            source = trackName
            sourceIndex = uCount - 1
            count = 1
            destIndex = 0
            dest = self.world.getHumpTrack(tag)
            
            mv = World.Movement(self.world, source, dest,
                           count, sourceIndex, destIndex)
                                 
            mv.execute()
            
            moves.append(mv)
        
        # done humping, put all those movements into an Operation
        op = World.Operation(movements = moves, 
                         operationType= World.Operation.OperationTypes.Hump)
        
        # put the new Operation into the world ops list
        self.ops.append(op)
        YCUI.updateOpsTable(self)
        
        
        # show the results
        self.world.redrawAllVisualizers()
        
    