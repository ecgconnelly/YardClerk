### YARDCLERK FOR RUN8
### (C) EMILIA CONNELLY 


################################################################################
# OPERATING PARAMETERS

DEFAULT_YARD = 'barstow'
DEFAULT_WORLD_XML = 'D:\Run8Studios\Run8 Train Simulator V3\Content\V3Routes\Regions\SouthernCA\Trains\yardclerk.xml'

################################################################################
#
################################################################################
# STANDARD IMPORTS

import copy
import datetime


################################################################################
#
################################################################################
# THIRD PARTY IMPORTS

import PySimpleGUI as sg


################################################################################
#
################################################################################
# PROJECT IMPORTS

import World
import YCUI
from modes import Modes
from ycstate import YCState

################################################################################
#
################################################################################
# MAIN PROGRAM


def main():

    # what yard are we working today?
    # TODO: ask which yard to work
    yardName = DEFAULT_YARD
    
    
    # what world files are we using?
    # TODO: ask which world files to load
    worldFilenames = [DEFAULT_WORLD_XML]    
    
    # analyze world
    # this includes analyzing the yard config for our selected yard
    baseWorld = World.WorldState(worldName = 'Base',
                                  yardName = yardName, 
                                  stateFilenames = worldFilenames)
    
    allVisualizers = {}
    
    # build UI to show results of analysis
    mainw = YCUI.buildMainWindow(baseWorld, allVisualizers).Finalize()

    baseWorld.redrawAllVisualizers()

    #mainw.maximize()
    #mainw.refresh()

    YCUI.updateInventoryTable(baseWorld, mainw)
       
    
    
    
    # show UI
    
    
    banner = mainw['bannerText']
    
    nextJobNumber = 1
    
    status = {'settingUpJob' : None,
              'query' : None,
              'sourceTrack' : None}
    
    # program_state = {"world":baseWorld, 
    #                  "mainw":mainw, 
    #                  "uiStatus":status,
    #                  "nextJobNumber" : nextJobNumber,
    #                  "allVisualizers" : allVisualizers,
    #                  "jobs" : []}
    
    

    programState = YCState(
        baseWorld, mainw, Modes.Base, 1, allVisualizers, []
    )
    
    printEventSpam = True
    YCUI.bindMainWindowKeys(mainw)

    while True:
        (event, values) = mainw.read()

        if printEventSpam == True:
            print (f"{event=}, {type(event)}")
            try:
                print(f"{values[event]=}")
            except:
                pass
        
        if event == sg.WIN_CLOSED:
            # our main window was closed, exit the program
            break

        if 'KeyPress' in event:
            programState.activeMode.HandleKeyEvent(event, programState)
            print(programState.activeMode)


    
    #return YCUI.mainLoop_OLD(program_state)
    

if __name__ == '__main__':
    while True:
        res = main()
        if res == 'softReset':
            continue
        else:
            break
