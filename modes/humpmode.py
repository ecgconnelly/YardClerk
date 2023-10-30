import enum
import PySimpleGUI as sg

import YCUI
from YCUI import TrackVisualizer
import World

from . import switchmode
class HumpMode(switchmode.SwitchMode):

    def __init__(self):
        self.registerMode('hump')
        #self.currentState = self.EditorState.Resting
        self.currentState = self.EditorState.SelectHumpTrack
        self.selectedSourceTrack = None
        self.keyCommands = {
            # '<KeyPress-Escape>' : self.keypress_escape,
            # '<KeyPress-Return>' : self.keypress_return,
            # '<KeyPress-y>' : self.keypress_y,
            # '<KeyPress-n>' : self.keypress_n,
            # # '<KeyPress-h>' : self.keypress_h,


            # '<KeyPress-s>' : self.startSwitchMove,
            # '<Control-KeyPress-z>' : self.undo,
            }


    # def keypress_escape(self):
    #     if self.currentState == self.EditorState.ConfirmMove:
    #         self.confirmMove(False)
    #         return
        
    #     elif self.currentState in [self.EditorState.SelectSourceLimit0,
    #                              self.EditorState.SelectSourceLimit1,
    #                              self.EditorState.SelectMoveDestination]:
    #         self.confirmMove(confirmed=False)

    #     elif self.currentState == self.EditorState.Resting:
    #         self.programState.setMode('base')

    # def keypress_return(self):
    #     if self.currentState == self.EditorState.ConfirmMove:
    #         self.confirmMove(True)

    # def keypress_y(self):
    #     if self.currentState == self.EditorState.ConfirmMove:
    #         self.confirmMove(True)
    # def keypress_n(self):
    #     if self.currentState == self.EditorState.ConfirmMove:
    #         self.confirmMove(False)

    # def keypress_h(self):
    #     if self.currentState == self.EditorState.Resting:
    #         job:World.Job = self.settingUpJob

    #         if job is None:
    #             self.programState.setBanner(
    #                 "Start setting up a job before trying to hump cars")
    #             return
            
    #         self.currentState = self.EditorState.SelectHumpTrack
    #         self.programState.setBanner(
    #             "Hump which track?"
    #         )
    #         visTab = self.programState.mainWindow['visualInventoryTab']
    #         visTab.select()
    #         recTab = self.programState.mainWindow['subyardTabReceiving']
    #         recTab.select()

    # def undo(self):
    #     # are we setting up a job?
    #     job = self.settingUpJob
    #     if job is None:
    #         sg.popup("No job to undo from!", no_titlebar = True)
    #         return
        
    #     # ok, there is a job
    #     try:
    #         job.undoLast()
    #     except IndexError:
    #         sg.popup(f"Nothing to undo in job {job.jobID}",
    #                     no_titlebar = True)
    #         self.programState.setBanner("Undo failed")
    #     else:
    #         self.programState.setBanner("Undo successful")

    def selectHumpTrack(self, event, values):

        if 'subyardButton' in event:
            trackName = event.replace('subyardButton', '')
        elif 'subyardVis' in event:
            trackName = event.replace('subyardVis', '')
        

        
        # self.currentState = self.EditorState.Resting
        
        visTab = self.programState.mainWindow['visualInventoryTab']
        bowlTab = self.programState.mainWindow['subyardTabBowl']
        visTab.select()
        bowlTab.select()
            
        
        # job = self.settingUpJob
        self.programState.addHumpOperation(trackName)
        
        overs = self.programState.world.listOverLengthTracks(subyard = 'Bowl')
        
        if overs == []:                
            self.programState.setBanner(f"Hump {trackName} OK")
        else:
            txt = f"Hump {trackName} - OVERFLOW {' ,'.join(overs)}"
            self.programState.setBanner(txt)

    def confirmMove(self, confirmed:bool):
        # handles the user response to asking whether to move cars or not
        # which tracks?
        sourceTrack:World.Track = self.selectedSourceTrack
        destTrack:World.Track = self.selectedDestinationTrack

        if confirmed == True:

            
            # get the indices
            sourceCoords = [p['xCoord'] for p in sourceTrack.pointers]
            destCoords = [p['xCoord'] for p in destTrack.pointers]
            
            sourceCoords = sorted(sourceCoords) # put left coord at idx 0
            sourceIndices = [int(x) for x in sourceCoords]
            count = sourceIndices[1] - sourceIndices[0]
            sourceIndex = sourceIndices[0]
            destIndex = int(destCoords[0])
            
            # create the move and an Operation to hold it
            mv = World.Movement(self.programState.world, 
                                sourceTrack.trackName, destTrack.trackName, count,
                                sourceIndex, destIndex, reverse = False)
                                
            op = World.Operation([mv], operationType=World.Operation.OperationTypes.BasicSwitch)
            op.execute()

            self.programState.ops.append(op)
            YCUI.updateOpsTable(self.programState)
            
            # job = self.settingUpJob
            # job.steps.append(step)
            
            
            # clear pointers
            sourceTrack.pointers = []
            destTrack.pointers = []
            
            # clear query
            self.selectedSourceTrack = None
            self.selectedDestinationTrack = None
            
            self.programState.world.redrawAllVisualizers()
            
            self.programState.setBanner("Move confirmed")
        else:
            # clear pointers
            if sourceTrack is not None:
                sourceTrack.pointers = []
            if destTrack is not None:
                destTrack.pointers = []
            
            # clear query
            self.selectedSourceTrack = None
            self.selectedDestinationTrack = None
            
            self.programState.world.redrawAllVisualizers()

            self.programState.setBanner("Move cancelled")

        self.currentState = None
        self.programState.setMode('base')

    def startSwitchMove(self):
        self.currentState = self.EditorState.SelectSourceLimit0
        self.programState.setBanner("Select units to move")

    def handleDestinationClick(self, event, values):
        # what track??
        trackName = event.replace('subyardVis', '')
        world = self.programState.world
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
            self.programState.setBanner("Normally you'd select the inbound direction now, but that's not implemented yet")
        else:
            # we're moving stuff around the yard
            # now confirm the move
            self.currentState = self.EditorState.ConfirmMove
            self.programState.setBanner('Confirm move? Y/N/Enter/Esc')



    def handleSourceLimitClick(self, event, values):
        # what track??
        trackName = event.replace('subyardVis', '')
        world = self.programState.world
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
                self.programState.setBanner("Select move destination")
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
                    



    def handleVisualizerClick(self, event, values):

        # if self.currentState == self.EditorState.Resting:
        #     return super().handleVisualizerClick(event, values)
        
        if self.currentState in [self.EditorState.SelectSourceLimit0,
                                   self.EditorState.SelectSourceLimit1]:
            self.handleSourceLimitClick(event, values)
        
        elif self.currentState == self.EditorState.SelectMoveDestination:
            self.handleDestinationClick(event, values)

        elif self.currentState == self.EditorState.SelectHumpTrack:
            self.selectHumpTrack(event, values)
        
        else:
            super().handleVisualizerClick(event, values)


    def selectBaseMode(self):
        self.programState.setMode('base')
    
    def focusOnJob(self, jobToFocus:World.Job):
        self.settingUpJob = jobToFocus

    def activate(self, programState):
        self.programState = programState
        # self.settingUpJob = None
        #self.currentState = self.EditorState.Resting
        self.currentState = self.EditorState.SelectHumpTrack
        self.selectedSourceTrack = None
        self.selectedDestinationTrack = None

        programState