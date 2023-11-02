import PySimpleGUI as sg
import ycstate
import YCUI

class BaseMode():
    
    allModes = {}

    def __init__(self):
        self.keyCommands = {
            #'<Control-KeyPress-R>' : self.RestartProgram,
            '<Control-KeyPress-t>' : self.selectTestMode,
            # '<Control-KeyPress-n>' : self.createNewJob,
            '<KeyPress-i>' : self.inboundTrain,
            '<KeyPress-s>' : self.createSwitchMove,
            '<KeyPress-h>' : self.humpFullTrack,
            }
        self.registerMode('base')

    def registerMode(self, modeKey:str):        
        if modeKey not in self.allModes:
            self.allModes[modeKey] = self

    #def RestartProgram(self):
    #    print("night night")
    #    raise RuntimeError("HardReset")

    def humpFullTrack(self):
        programState = self.programState
        visTab = programState.mainWindow['visualInventoryTab']
        visTab.select()

        programState.setMode('hump')
        
    def createSwitchMove(self):
        programState = self.programState
        visTab = programState.mainWindow['visualInventoryTab']
        visTab.select()

        programState.setMode('switch')
        
    def inboundTrain(self):
        programState = self.programState
        visTab = programState.mainWindow['visualInventoryTab']
        visTab.select()

        programState.setMode('inboundtrain')

    
    # def createNewJob(self):
    #     programState = self.programState
    #     opsTab = programState.mainWindow['operationsTab']
    #     opsTab.select()

    #     newJob = YCUI.newJobPopup(programState)

    #     if newJob is not None:
    #         programState.nextJobNumber += 1
    #         programState.jobs.append(newJob)
    #         YCUI.updateJobsTable(programState)
    #         programState.setMode('switch')
    #         programState.activeMode.settingUpJob = newJob


    def selectTestMode(self, programState):
        programState.setMode('test')


    def HandleEvent(self, event, values):
        if event in self.keyCommands:
            handler = self.keyCommands[event]
            handler()

        if 'subyardVis' in event:
            # handler = self.handleVisualizerClick(event, values)
            # what was that?!
            self.handleVisualizerClick(event, values)

    def handleVisualizerClick(self, event, values):
        # base functionality: show infobox for the clicked unit

            allVisualizers = self.programState.visualizers
        
            point = values[event]

            graph = self.programState.mainWindow[event]
            
            figures = graph.get_figures_at_location(point)
            #print(f"{figures=}")
            if len(figures) > 0:
                
                # figure index is no longer guaranteed to be the unit index
                # 
                
                figIndex = figures[0]
                
                vis = allVisualizers[event] # get the Visualizer object by track name
                
                try:
                    unit = vis.unitFromFigIdx[figIndex]
                except KeyError:
                    dString = f"{figIndex=}"
                    sg.popup("oops", dString)
                    return
                    
                
                trackCount = len(vis.units)
                
                
                try:
                    nextTrainStr = f"Next: {' / '.join(unit.nextTrain)}"
                except AttributeError:
                    nextTrainStr = "ENG"
                except TypeError:
                    nextTrainStr = "No scheduled outbound train"
                    
                #calculate lengfth and tonnage to car from each end
                leftTons = 0
                leftFt = 0
                unitIdx = vis.units.index(unit)
                for count in range(0, unitIdx + 1):
                    thisUnit = vis.units[count]
                    leftFt += thisUnit.lengthFt
                    if thisUnit.isLoco():
                        continue #don't count engine weight
                    leftTons += thisUnit.totalWeight()
                
                rightTons = 0
                rightFt = 0
                for count in range(trackCount - 1, unitIdx - 1, -1):
                    thisUnit = vis.units[count]
                    rightFt += thisUnit.lengthFt
                    if thisUnit.isLoco():
                        continue # don't count engine weight
                    rightTons += thisUnit.totalWeight()
                
                leftTons = round(leftTons)
                leftFt = round(leftFt)
                rightTons = round(rightTons)
                rightFt = round(rightFt)
                
                tonnageStr = f"{leftTons} T --> X <-- {rightTons} T"
                lengthStr = f"{leftFt} FT --> X <-- {rightFt} FT"
                sg.popup(#dString,
                         f"{unit.initials} {unit.unitNumber}",
                         f"Tag: {unit.destinationTag}",
                         f"{round(unit.lengthFt)} FT - {round(unit.totalWeight())} TONS",
                         nextTrainStr,
                         f"{unitIdx + 1} --> X <-- {trackCount - (unitIdx)}", 
                         lengthStr,
                         tonnageStr,
                         any_key_closes = True,
                         background_color = '#666666',
                         
                         no_titlebar = True)


    def activate(self, programState):
        print(f"Entering {self.__class__}")
        self.programState = programState

    def deactivate(self):
        print(f"Leaving {self.__class__}")