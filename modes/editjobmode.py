import enum
import PySimpleGUI as sg

from YCUI import TrackVisualizer

from . import basemode
class EditJobMode(basemode.BaseMode):

    def __init__(self):
        self.registerMode('editjob')
        self.settingUpJob = None
        self.currentState = self.EditorState.Resting
        self.selectedSourceTrack = None
        self.selectedDestinationTrack = None
        self.keyCommands = {
            '<KeyPress-Escape>' : self.selectBaseMode,

            '<Control-KeyPress-m>' : self.startMovement,
            }
        
    class EditorState(enum.Enum):
        Resting = enum.auto()
        SelectSourceLimit0 = enum.auto()
        SelectSourceLimit1 = enum.auto()
        SelectMoveDestination = enum.auto()
        ConfirmMove = enum.auto()
        SelectInboundDestination = enum.auto()
        SelectInboundDirection = enum.auto()

    def startMovement(self, programState):
        self.currentState = self.EditorState.SelectSourceLimit0

    def handleDestinationClick(self, event, values, programState):
        # what track??
        trackName = event.replace('subyardVis', '')
        world = programState.world
        trackObj = world.getTrackObject(trackName)
        unitCount = len(trackObj.units)

        if trackObj == self.selectedSourceTrack:
            sg.popup('Destination and source tracks must be different',
                     no_titlebar = True)
            return

        self.selectedDestinationTrack = trackObj
        print(f"Destination: track {trackName} which has {unitCount} units")

        # if we're here, source and destination are different
        trackObj.pointers = []
        
        # where on the track?

        # clamp x between the ends of track
        coords = values[event]
        x = coords[0]
        if x < 1:
            x = 0.5
        if x > unitCount:
            x = unitCount + 0.5
                    
        # now put x at a coupler, not a carbody
        floor = int(x)
        x = floor + 0.5
        
        # record the pointer in the track object to be drawn
        trackObj.pointers.append({'xCoord':x})
        world.redrawAllVisualizers()

        if self.currentState == self.EditorState.SelectInboundDestination:
            print("Normally you'd select the inbound direction now, but that's not implemented yet")
        else:
            # we're moving stuff around the yard
            # now confirm the move
            self.currentState = self.EditorState.ConfirmMove
            print("Confirm move?")



    def handleSourceLimitClick(self, event, values, programState):
        # what track??
        trackName = event.replace('subyardVis', '')
        world = programState.world
        trackObj = world.getTrackObject(trackName)
        unitCount = len(trackObj.units)
        print(f"Source: track {trackName} which has {unitCount} units")

        if self.currentState == self.EditorState.SelectSourceLimit0:
            # we were expecting to get the first source limit
            self.selectedSourceTrack = trackObj
            trackObj.pointers = []
            self.currentState = self.EditorState.SelectSourceLimit1

        elif self.currentState == self.EditorState.SelectSourceLimit1:
            # we were expecting to get the second source limit
            # check whether the user clicked on the same track as limit0
            if trackObj == self.selectedSourceTrack:
                print("Thanks for clicking on the same track")
            else:
                # user clicked on a different track
                self.selectedSourceTrack.pointers = []
                self.selectedSourceTrack = trackObj
                trackObj.pointers = []

        else:
            raise RuntimeError(
                f"Tried to handle source limit click but editor state was {self.currentState}")

        # where on the track?

        # clamp x between the ends of track
        coords = values[event]
        x = coords[0]
        if x < 1:
            x = 0.5
        if x > unitCount:
            x = unitCount + 0.5
                    
        # now put x at a coupler, not a carbody
        floor = int(x)
        x = floor + 0.5
        
        # record the pointer in the track object to be drawn
        trackObj.pointers.append({'xCoord':x})
        

        # was this the second pointer?
        if len(trackObj.pointers) == 2:
            # make sure the pointers aren't in the same place
            p0 = trackObj.pointers[0]['xCoord']
            p1 = trackObj.pointers[1]['xCoord']
            
            if p0 == p1:
                sg.popup(f"Select at least one unit",
                            no_titlebar = True)
                del trackObj.pointers[1]
                return
                
            # if we're here, we have two distinct source pointers on the same track
            
            # now it's time to select the destination
            
            self.currentState = self.EditorState.SelectMoveDestination
            
        world.redrawAllVisualizers()
                    



    def handleVisualizerClick(self, event, values, programState):

        if self.currentState == self.EditorState.Resting:
            return super().handleVisualizerClick(event, values, programState)
        
        elif self.currentState in [self.EditorState.SelectSourceLimit0,
                                   self.EditorState.SelectSourceLimit1]:
            self.handleSourceLimitClick(event, values, programState)
        
        elif self.currentState == self.EditorState.SelectMoveDestination:
            self.handleDestinationClick(event, values, programState)


    def selectBaseMode(self, programState):
        programState.setMode('base')

    def activate(self):
        self.settingUpJob = None
        self.currentState = self.EditorState.Resting
        self.selectedSourceTrack = None
        self.selectedDestinationTrack = None