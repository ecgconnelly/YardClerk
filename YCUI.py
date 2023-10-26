VISUALIZER_CANVAS_SIZE = (1280, 60)
VISUALIZER_COORD1 = (-1, -1)
VISUALIZER_COORD2 = (150, 3)
VISUALIZER_BG_COLOR = '#111111'


import datetime
import enum
import string


import World


# event lists

UPDATE_INVENTORY_TABLE = ['inventoryFilterOnlyHump',
                          'inventoryFilterIncludesLocos',
                          'inventoryFilterIncludesCars',
                          'inventoryFilterApplyTrackFilter',
                          'inventoryFilterClearTrackFilter']

UPDATE_INVENTORY_FINDER_TABLE = ['inventoryFilterFinderTableButton']

import PySimpleGUI as sg



def newJobPopup(program_state):
    
    # need info:
    # job ID
    # job name
    # job type (hump, general)
    
    # set up defaults
    
    jobNumber = program_state.nextJobNumber
    
    # default job ID
    now = datetime.datetime.now()
    day = now.day
    jobID = f"{day}-{str(jobNumber).zfill(3)}"

    
    # set up layout for popup
    layout = []
    
    row = []
    row.append(sg.Text("Job ID:"))
    row.append(sg.Input(jobID,
                        s = 20,
                        k = 'newJobID'))
    
    layout.append(row)
    
    row = []
    row.append(sg.Text("Job Name:"))
    row.append(sg.Input("",
                        s = 20,
                        k = 'newJobName',
                        focus = True))
    layout.append(row)
    
    row = []
    row.append(sg.Checkbox("Hump Job?",
                           default = False,
                           k = 'newJobIsHump'))
                           
    layout.append(row)
    
    
    row = []
    row.append(sg.Button("OK",
                         k = 'newJobOK'))
    row.append(sg.Button("Cancel",
                         k = 'newJobCancel'))
     
    layout.append(row)
    
    
    pop = sg.Window("Job Setup",
                            layout, 
                            modal = True,
                            finalize = True)
    
    pop['newJobName'].set_focus()                        
    
    event, vals = pop.read(close = True)
    
    # did we get the OK?  If not, return None
    if event != 'newJobOK':
        return None
        
    # job was ok'd    
    # build the job object
    
    if vals['newJobIsHump']:
        jobType = 'HUMP'
    else:
        jobType = 'SWITCH'
        
        
    job = World.Job(world = program_state.world,
                    jobID = vals['newJobID'],
                    jobName = vals['newJobName'],
                    jobType = jobType)

    return job
    
def bindMainWindowKeys(mainw):

    # bind all the letters with all combinations of ctrl and shift      
    # known issue: cannot bind to - key (lots of false positives)
    bases_cased = list(string.ascii_letters + string.digits + '!"#$%&\'()*+,./:;<=>?@[\\]^_`{|}~')
    bases_nocase = [f"F{n}" for n in range(1, 13)]
    bases_nocase += ['Left', 'Up', 'Right', 'Down', 
                     'Insert', 'Delete', 'Home', 'End', 'Prior', 'Next',
                     'Escape', 'Tab', 'BackSpace', 'Return', 'space']

    for base in bases_cased + bases_nocase:
        # no control 
        tk_event_string = f"<KeyPress-{base}>"
        mainw.bind(tk_event_string, tk_event_string)

        # control
        tk_event_string = f"<Control-KeyPress-{base}>"
        mainw.bind(tk_event_string, tk_event_string)

        # alt
        tk_event_string = f"<Alt-KeyPress-{base}>"
        mainw.bind(tk_event_string, tk_event_string)

        # control-alt
        tk_event_string = f"<Control-Alt-KeyPress-{base}>"
        mainw.bind(tk_event_string, tk_event_string)

        if base in bases_nocase:
            # shift
            tk_event_string = f"<Shift-KeyPress-{base}>"
            mainw.bind(tk_event_string, tk_event_string)  

            # control shift
            tk_event_string = f"<Control-Shift-KeyPress-{base}>"
            mainw.bind(tk_event_string, tk_event_string)  

            # alt shift
            tk_event_string = f"<Alt-Shift-KeyPress-{base}>"
            mainw.bind(tk_event_string, tk_event_string)

            # control alt shift
            tk_event_string = f"<Control-Alt-Shift-KeyPress-{base}>"
            mainw.bind(tk_event_string, tk_event_string)

    #mainw.bind("<Key-Control_L>", "LCtrl")
    #mainw.bind('<Key-Shift_L>', 'Shift_Down')
    #mainw.bind('<Key-Shift_R>', 'Shift_Down')
    #mainw.bind('<KeyPress-Shift_L>', 'LShift Down')
    #mainw.bind('<KeyRelease-Shift_L>', 'LShift Up')
    #mainw.bind('Control-KeyPress-b', 'ControlB_Down')




def updateJobsTable(program_state):
    mainw = program_state.mainWindow
    jobs = program_state.jobs

    # create table row for each job
    values = []
    for job in jobs:
        tracks = job.listAffectedTracks()
        trackStr = ' '.join(tracks)
        row = [job.jobID, 
               job.jobName, 
               '', 
               job.jobType, 
               '', 
               trackStr]
        values.append(row)
        
    jobsTable = mainw['jobsTable']
    jobsTable.update(values = values)

def clickedToSelectMoveDest(query, event):
    # are we looking to select a destination point?
    if query == 'selectCarsToMoveDest':
        # was this a click on a visualizer?
        if event.startswith('subyardVis'):
            return True
    # otherwise no
    return False
    
    
def clickedToSelectSourceUnits(query, event):
    # are we even looking to select source cars??
    if (query == 'selectCarsToMoveSource' or
        query == 'selectCarsToOutboundSource'):
        # was this a click on a visualizer?
        if event.startswith('subyardVis'):
            return True
    
    return False
        
    
    
def mainLoop_OLD(program_state):

    printEventSpam = True

    # unpack dict
    world = program_state['world']
    mainw = program_state['mainw']
    status = program_state['uiStatus']
    jobs = program_state['jobs']
    allVisualizers = program_state['allVisualizers']
    
    bindMainWindowKeys(mainw)
    
    banner = mainw['bannerText']

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
        
        if event in ['newJob', 'newJobButton']:
            if status['settingUpJob'] is None:
                # if we're not already setting up a job
                
                newJob = newJobPopup(program_state)
                
                if newJob is None:
                    continue
                    
                status['settingUpJob'] = newJob
                
                banner.update(f"Creating job {newJob.jobID} {newJob.jobName} (Ctrl-C to finish, Ctrl-Q to abort)")
                
                visTab = mainw['visualInventoryTab']
                visTab.select()
            else:
                # oops, we're already setting up a job
                currentJob = status['settingUpJob']
                sg.popup(f"Finish or abort job {currentJob.jobID} before planning a new one.",
                         title = "Job setup busy",
                         no_titlebar = True)
        
        
        if event == 'abortJob':
            job = status['settingUpJob']
            if job is None:
                sg.popup("No job to abort!", no_titlebar = True)
                continue
            
            # if we're here, there is a job to abort
            
            # undo the whole job
            job.undo()
            
            # we're no longer setting up that job
            status['settingUpJob'] = None
            
            # but DO NOT increment job number
            
            # update banner
            banner.update(f"Job {job.jobID} aborted")
            
            # no queries
            status['query'] = None
            
            
        if event == 'finishJob':
            job = status['settingUpJob']
            if job is None:
                sg.popup("No job to finish!", no_titlebar = True)
                continue
            
            # if we're here, we were setting up a job
            
            # add the job to our jobs list
            jobs.append(job)
            
            # update the jobs table
            updateJobsTable(program_state)
            
            # we're no longer setting up the job
            status['settingUpJob'] = None
            
            # increment next job number
            program_state['nextJobNumber'] += 1
            
            # update banner
            banner.update(f"Job {job.jobID} created")
            
            status['query'] = None
        
        if event == 'inboundUnits':
            job = status['settingUpJob']
            if job is None:
                sg.popup("Start setting up a job first.",
                         no_titlebar = True)
                continue # nothing to do
            
            # if we're here, we do have a job in process of being set up
            
            # what file should we load from?
            trainFile = sg.popup_get_file("Select train XML to inbound",
                                          title = "Inbound Train",
                                          #default_path = 'C:\Run8Studios\Run8 Train Simulator V3\Content\V3Routes\Regions\SouthernCA\Trains',
                                          default_extension = 'xml',
                                          file_types = (("XML Files", ".xml"),),
                                          initial_folder = 'C:\Run8Studios\Run8 Train Simulator V3\Content\V3Routes\Regions\SouthernCA\Trains'
                                          )
            
            if trainFile is None:
                banner.update("Inbounding cancelled.")
                continue # wait for next event
            
            

            
            # load the file, make a list of units
            inboundTrainList = world.trainsFromFile(trainFile)
            
            if len(inboundTrainList) > 1:
                sg.popup_error("That file contains more than one train.")
                continue
            elif len(inboundTrainList) == 0:
                sg.popup_error("That file doesn't contain any trains.")
                continue
            
            # if we're here, we loaded a file with exactly one train
            inboundTrain = inboundTrainList[0]
            inboundUnits = inboundTrain.units
            
            # determine which units in the inbound train are for customers
            for unit in inboundUnits:
                unit.isCustomerOrder = world.isUnitCustomerOrder(unit)
            
            
            # check whether we already have a dummy track for inbounds on this job
            dummyTrackName = f'inbound{job.jobID}'
            dummyTrackObj = world.getTrackObject(dummyTrackName)
            if dummyTrackObj is None:
                dummyTrackObj = World.Track(world, 'inbounds', dummyTrackName)
                world.trackObjects[dummyTrackName] = dummyTrackObj
                            
            # add the inbound units to the dummy track
            dummyTrackObj.units += inboundUnits
            
            # where should the units go?
            status['query'] = 'selectCarsToMoveDest'
            status['sourceTrack'] = dummyTrackName
            dummyTrackObj.pointers = []
            dummyTrackObj.pointers.append({'xCoord':0})
            dummyTrackObj.pointers.append({'xCoord':len(inboundUnits)})
            banner.update("Place inbound units where?")
            continue
            
        
    
        if event == 'outboundUnits':
            job = status['settingUpJob']
            if job is None:
                sg.popup("Start setting up a job first.",
                         no_titlebar = True)
                continue # nothing to do
            banner.update("Select units to depart")
            visTab = mainw['visualInventoryTab']
            visTab.select()
            status['query'] = 'selectCarsToOutboundSource'
            continue
        
        if event == 'moveCars':
            job = status['settingUpJob']
            if job is None:
                sg.popup("Start setting up a job first.",
                         no_titlebar = True)
                continue # nothing to do
            
            banner.update("Select cars to move")
            visTab = mainw['visualInventoryTab']
            visTab.select()
            status['query'] = 'selectCarsToMoveSource'
            continue
            
        if status['query'] == 'confirmOutboundSelection':
            if event in ['y', 'Y']:
                doClear = True
                job = status['settingUpJob']
                
                
                # get the indices
                sourceCoords = [p['xCoord'] for p in trackObj.pointers]
                sourceCoords = sorted(sourceCoords) # put left coord at idx 0
                sourceIndices = [int(x) for x in sourceCoords]
                count = sourceIndices[1] - sourceIndices[0]
                sourceIndex = sourceIndices[0]
                
                job.addOutboundStep(trackName, sourceIndex, count)
                
                banner.update("Units outbounded")

            elif event in ['n', 'N']:
                doClear = True
                banner.update("Outbound cancelled")
                
            else:
                #don't clear pointers for timeout or other irrelvant events
                continue 
            
            # if we're here, we got a y/n to outbound or not 
            trackObj.pointers = []
            
            # clear query
            status['query'] = None
            status['sourceTrack'] = None
            status['destTrack'] = None
            
            world.redrawAllVisualizers()
                
                
        
        if clickedToSelectMoveDest(status['query'], event):
            # select the destination for cars to move to
            trackName = event.replace('subyardVis', '')
            trackObj = world.getTrackObject(trackName)
            unitCount = len(trackObj.units)
            
            
            
            if trackName == status['sourceTrack']:
                sg.popup('Destination and source tracks must be different',
                         no_titlebar = True)
                # next event
                continue
                
            # if we're here, source and destination are different
               
            status['destTrack'] = trackName
            trackObj.pointers = []
            
            # where on the track?
            coords = values[event]
            
            # round to the nearest half-int
            x = coords[0]
            
            # clamp x between the ends of track
            if x < 1:
                x = 0.5
            
            if x > unitCount:
                x = unitCount + 0.5
                     
            # now put x at a coupler, not a carbody
            floor = int(x)
            x = floor + 0.5
            
            
            # and record the pointer in the track object to be drawn
            trackObj.pointers.append({'xCoord':x})
            world.redrawAllVisualizers()

            if status['sourceTrack'].startswith('inbound'):
                # we are inbounding a train, 
                status['query'] = 'confirmInbound'
                banner.update("Inbound faces which direction? E/W/Esc")
            else:
                # we're moving stuff around the yard
                # now confirm the move
                status['query'] = 'confirmMove'
                banner.update("Confirm move? (Y/N)")
            continue
        
        if status['query'] in ['confirmMove', 'confirmInbound']:
            if status['query'] == 'confirmInbound':
                if event in ['e', 'E']:
                    reverse = True
                    confirm = True
                elif event in ['w', 'W']:
                    reverse = False
                    confirm = True
                elif event == 'Escape':
                    reverse = None
                    confirm = False
                else:
                    continue #this event wasn't relevant to inbounding
            else:
                # if we're just moving stuff around the yard
                if event in ['y', 'Y']:
                    reverse = False
                    confirm = True
                elif event in ['n', 'N']:
                    reverse = False
                    confirm = False
                else:
                    continue # not a relevant event
            
            if confirm == True:
                # which tracks?
                sourceName = status['sourceTrack']
                destName = status['destTrack']
                sourceObj = world.getTrackObject(sourceName)
                destObj = world.getTrackObject(destName)
                
                # get the indices
                sourceCoords = [p['xCoord'] for p in sourceObj.pointers]
                destCoords = [p['xCoord'] for p in destObj.pointers]
                
                sourceCoords = sorted(sourceCoords) # put left coord at idx 0
                sourceIndices = [int(x) for x in sourceCoords]
                count = sourceIndices[1] - sourceIndices[0]
                sourceIndex = sourceIndices[0]
                destIndex = int(destCoords[0])
                
                # create job step for the move
                op = World.Operation(world, sourceName, destName, count, 
                                     sourceIndex, destIndex, reverse = reverse)
                                     
                step = World.JobStep([op])
                step.execute()
                
                job = status['settingUpJob']
                job.steps.append(step)
                
                
                # clear pointers
                sourceObj.pointers = []
                destObj.pointers = []
                
                # clear query
                status['query'] = None
                status['sourceTrack'] = None
                status['destTrack'] = None
                
                world.redrawAllVisualizers()
                
                banner.update("Move/inbound confirmed")
                
            else:
                # if operation was cancelled
                
                # which tracks were we dealing with?
                sourceName = status['sourceTrack']
                destName = status['destTrack']
                sourceObj = world.getTrackObject(sourceName)
                destObj = world.getTrackObject(destName)
                
                # clear pointers
                sourceObj.pointers = []
                destObj.pointers = []
                
                # clear query
                status['query'] = None
                status['sourceTrack'] = None
                status['destTrack'] = None
                
                banner.update("Move cancelled")
                world.redrawAllVisualizers()
                
            continue
            
        if clickedToSelectSourceUnits(status['query'], event):
            # what track??
            trackName = event.replace('subyardVis', '')
            trackObj = world.getTrackObject(trackName)
            unitCount = len(trackObj.units)
            
            # is this the first source cursor?
            if status['sourceTrack'] is None:
                # this is the first cursor
                # remember the source track
                status['sourceTrack'] = trackName
                # initialize the track's pointer list
                trackObj.pointers = []
            else:
                # we already determined the source track
                # make sure this click matches
                if trackName != status['sourceTrack']:
                    sg.popup("Select cars from a single track",
                             no_titlebar = True)
                    #handle next event, can't select from multiple tracks
                    continue 
                    
            
            # where on the track?
            coords = values[event]
            
            # round to the nearest half-int
            x = coords[0]
            
            # clamp x between the ends of track
            if x < 1:
                x = 0.5
            
            if x > unitCount:
                x = unitCount + 0.5
                     
            # now put x at a coupler, not a carbody
            floor = int(x)
            x = floor + 0.5
            
            
            # and record the pointer in the track object to be drawn
            trackObj.pointers.append({'xCoord':x})
            
            
            # was this the second pointer?
            if len(trackObj.pointers) == 2:
                # make sure the pointers aren't in the same place
                p0 = trackObj.pointers[0]['xCoord']
                p1 = trackObj.pointers[1]['xCoord']
                
                if p0 == p1:
                    if "outbound" in status['query']:
                        opString = "depart"
                    else:
                        opString = "move"
                    sg.popup(f"Select at least one unit to {opString}",
                             no_titlebar = True)
                    del trackObj.pointers[1]
                    continue # don't change status yet!
                    
                # we have two distinct source pointers
                
                # now it's time to select the destination,
                # or if we're outbounding cars, to do the outbounding
                
                outbounding = 'Outbound' in status['query']
                if outbounding:
                    
                    status['query'] = 'confirmOutboundSelection'
                    banner.update("Outbound selected units?")
                    
                else:
                    # this is an in-yard move
                    status['query'] = 'selectCarsToMoveDest'
                    banner.update("Move cars to where?")
                
            world.redrawAllVisualizers()
                    
        
        
        if event == 'humpTrack':
            if status['settingUpJob'] is None:
                sg.popup("Start setting up a job first.",
                         no_titlebar = True)
            else:
                banner.update("Hump which track?")
                visTab = mainw['visualInventoryTab']
                rcvTab = mainw['subyardTabReceiving']
                visTab.select()
                rcvTab.select()
                status['query'] = 'humpWhichTrack'
        
        if event.startswith('subyardButton'):
            if status['query'] == 'humpWhichTrack':
                # hump the clicked track
                trackName = event.replace('subyardButton', '')
                
                status['query'] = None
                
                visTab = mainw['visualInventoryTab']
                bowlTab = mainw['subyardTabBowl']
                visTab.select()
                bowlTab.select()
                 
                
                job = status['settingUpJob']
                job.addHumpStep(trackName)
                
                overs = world.listOverLengthTracks(subyard = 'Bowl')
                
                if overs == []:                
                    banner.update(f"Hump {trackName} OK")
                else:
                    txt = f"Hump {trackName} - OVERFLOW {' ,'.join(overs)}"
                    banner.update(txt)
                
        if event == 'undo':
            # are we setting up a job?
            job = status['settingUpJob']
            if job is None:
                sg.popup("No job to undo from!", no_titlebar = True)
                continue
            
            # ok, there is a job
            try:
                job.undoLast()
            except IndexError:
                sg.popup(f"Nothing to undo in job {job.jobID}",
                         no_titlebar = True)
                banner.update("Undo failed")
            else:
                banner.update("Undo successful")
                

        
        if event == '__TIMEOUT__':
            pass
            
        if event == 'Restart':
            mainw.close()
            return 'softReset'
            
        
        if event == 'buildCMD_Enter':
            cmd = values['buildCMD']
            print(mainw['buildCMD'].get())
            mainw['buildCMD'].update(value = '')
            
            
        if event == 'inventoryFilterClearTrackFilter':
            mainw['inventoryFilterTrackFilterEnable'].update(value = False)
            mainw['inventoryFilterTracks'].update(value = '')
            
        elif event == 'inventoryFilterApplyTrackFilter':
            if values['inventoryFilterTracks'].strip() == '':
                # this is an empty filter, treat it as clearing
                mainw['inventoryFilterTrackFilterEnable'].update(value = False)
            else:
                mainw['inventoryFilterTrackFilterEnable'].update(value = True)
            
        if event in UPDATE_INVENTORY_TABLE:
            updateInventoryTable(world, mainw)
            
        if event in UPDATE_INVENTORY_FINDER_TABLE:
            updateInventoryFindTable(world, 
                                      mainw,
                                      values['inventoryTable'])
            
        if event.startswith('subyardVis'):

            point = values[event]

            graph = mainw[event]
            
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
                    #sg.popup("oops", dString)
                    continue
                    
                
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
                
            
      


def buildInventoryFilterFrame(world):
    filterLayout = []
    
    
    # row 0
    row = []
    row.append(sg.Checkbox('Include cars?',
                                  default = True,
                                  key = 'inventoryFilterIncludesCars',
                                  enable_events = True,
                                  background_color = '#333333'))
    
    row.append(sg.Checkbox('Include locos?',
                                  default = False,
                                  key = 'inventoryFilterIncludesLocos',
                                  enable_events = True,
                                  background_color = '#333333'))                     

    filterLayout.append(row)
    
    # row 1   
    
    row = []
    
    humpSetUp = "humpTags" in world.yardSettings
    
    row.append(sg.Checkbox('Only hump tags?',
                                  default = humpSetUp,
                                  key = 'inventoryFilterOnlyHump',
                                  enable_events = True,
                                  background_color = '#333333',
                                  disabled = not(humpSetUp)))
    
    filterLayout.append(row)
    
    
    # sep
    row = []
    row.append(sg.HorizontalSeparator('white'))
    filterLayout.append(row)
    
    # filter by current track
    row = []
    row.append(sg.Checkbox("Filter by track (trailing * permitted):",
                           background_color = '#333333',
                           enable_events = True,
                           k = 'inventoryFilterTrackFilterEnable'))
                           
    filterLayout.append(row)
    
    # row 4
    row = []
    row.append(sg.Input('',
                        size = 20,
                        expand_x = True, 
                        k = 'inventoryFilterTracks',
                        ))
    
    row.append(sg.Button('Apply',
                         k = 'inventoryFilterApplyTrackFilter'))
    row.append(sg.Button('Clear',
                         k = 'inventoryFilterClearTrackFilter'))
    
    filterLayout.append(row)
    
    # sep
    row = []
    row.append(sg.HorizontalSeparator('white'))
    filterLayout.append(row)
    
    # filter by next train
    row = []
    orgTrains = world.yardSettings['originateTrains']
    row.append(sg.Text("Filter by next train:",
                       background_color = '#333333'))
    row.append(sg.Combo(values = orgTrains,
                        readonly = True,
                        size = (20, 8),
                        k = 'inventoryFilterSelectTrain'))
    
    filterLayout.append(row)
    
    # sep
    row = []
    row.append(sg.HorizontalSeparator('white'))
    filterLayout.append(row)
    
    
    # row for finder table controls
    row = []
    row.append(sg.Button("Find Table Selection", 
                         k = 'inventoryFilterFinderTableButton'))
    
    filterLayout.append(row)
    
    # new row for finder table
    row = []
    row.append(sg.Table(values = [[]],
                        headings = ['TRK', 'COUNT', 'LENGTH', 'WEIGHT', '# LDS', '# MTS', ],
                        col_widths = [16, 8, 8, 8, 8, 8],
                        auto_size_columns = False,
                        justification = 'center',
                        background_color = '#333333',
                        expand_x = True,
                        expand_y = True,
                        hide_vertical_scroll = True,
                        font = 'Consolas 10',
                        k = 'inventoryFindTable',
                        display_row_numbers = True
                        ))
    
    filterLayout.append(row)
    
    # now assemble the frame
    filterFrame = sg.Frame('',
                           filterLayout,
                           expand_x = True,
                           expand_y = True,
                           k = 'inventoryFilterFrame',
                           background_color = '#333333')
    
    return filterFrame
    

def updateInventoryFindTable(world, window, selectedRows):
    # finder table headings:
    # headings = ['TRK', 'COUNT', 'LENGTH', 'WEIGHT', '# LDS', '# MTS']
    
    tracks = {}
    humpOnly = window['inventoryFilterOnlyHump'].get()
    includeLocos = window['inventoryFilterIncludesLocos'].get() 
    includeCars = window['inventoryFilterIncludesCars'].get() 
    trackFilterEnable = window['inventoryFilterTrackFilterEnable'].get()
    
    if trackFilterEnable:
        trackFilterTokens = window['inventoryFilterTracks'].get().split()
    
    tagStrings = []
    for n in selectedRows:
        tagStrings.append(window['inventoryTable'].get()[n][0])
           
    
    
    total = {'count':0,
            'length':0,
            'weight':0,
            'loads':0,
            'empties':0}

    for unit in world.units:
        # first, ignore all the stuff we're filtering out
        if unit.isLoco() and includeLocos == False:
            continue
        if not(unit.isLoco()) and includeCars == False:
            continue
        
        
        if trackFilterEnable:
            trackOK = False
            # where is this unit currently?
            onGroups = unit.trackGroupsForUnit(world.trackGroups)
            for g in onGroups:
                for tok in trackFilterTokens:
                    if '*' in tok:
                        tok = tok.split('*')[0]
                        if g.upper().startswith(tok.upper()):
                            trackOK = True
                    else:
                        # no wildcard
                        if tok.upper() == g.upper():
                            trackOK = True
                            
                            
            if not trackOK:
                continue # ignore this unit entirely
        
        # ok, now we've discarded everything that's the wrong 
        # type or is on a filtered-out track
            
        # does this unit match the table selections?
        
        if humpOnly:
            dtag = world.getHumpTag(unit.destinationTag)
        else:
            # inventory ALL the tags
            try:
                dtag = unit.destinationTag.strip()
            except AttributeError:
                # if the unit has no tag
                dtag = "<< No Tag >>"
                
            if dtag == "None":
                dtag = "<< Tagged 'None' >>"
        
        # now we've got the relevant tag for this unit
        
        if dtag not in tagStrings:
            # this unit is not relevant (wrong tag)
            # ignore it
            continue
        
        try:
            utrack = unit.trackGroupsForUnit(world.trackGroups)[0]
        except IndexError:
            utrack = '<< ???? >>'
            
        if utrack not in tracks:
            tracks[utrack] = {'count':0,
                            'length':0,
                            'weight':0,
                            'loads':0,
                            'empties':0}
    
        track = tracks[utrack]
        track['count'] += 1
        track['length'] += unit.lengthFt
        track['weight'] += unit.totalWeight()
        track['loads'] += unit.isLoaded()
        track['empties'] += unit.isEmpty()
        
        
        total['count'] += 1
        total['length'] += unit.lengthFt
        total['weight'] += unit.totalWeight()
        total['loads'] += unit.isLoaded()
        total['empties'] += unit.isEmpty()
    
    
    values = []
    for track in tracks:
        row = [track,
               tracks[track]['count'], 
               round(tracks[track]['length']), 
               round(tracks[track]['weight']),
               tracks[track]['loads'],
               tracks[track]['empties']
               ]
        values.append(row)
    
    values.sort(key = lambda e: e[0])
    
    # now add the total on top
    values.insert(0,  ['<< TOTAL >>',
               total['count'], 
               round(total['length']), 
               round(total['weight']),
               total['loads'],
               total['empties']
               ])
       
    
    window['inventoryFindTable'].update(values = values)
    
    
    
    
def buildInventoryFrame(world):
    layout = [[]]
    layout[0].append(sg.Table(values = [[]],
                        headings = ['TAG', 'COUNT', 'LENGTH', 'WEIGHT', '# LDS', '# MTS', '# ENG'],
                        col_widths = [40, 8, 8, 8, 8, 8, 8],
                        auto_size_columns = False,
                        justification = 'center',
                        background_color = '#333333',
                        expand_x = True,
                        expand_y = True,
                        hide_vertical_scroll = True,
                        font = 'Consolas 10',
                        k = 'inventoryTable',
                        display_row_numbers = True
                        ))
    
    return sg.Frame("", 
                    layout,
                    expand_x = True,
                    expand_y  = True,
                    element_justification = 'left',
                    background_color = '#333333',
                    k = 'inventoryFrame'
                    )
    

def updateInventoryTable(world, window):
    # inventory table headings:
    # headings = ['TAG', 'COUNT', 'LENGTH', 'WEIGHT', '# LDS', '# MTS', '# ENG']
    
    tags = {}
    humpOnly = window['inventoryFilterOnlyHump'].get()
    includeLocos = window['inventoryFilterIncludesLocos'].get() 
    includeCars = window['inventoryFilterIncludesCars'].get() 
    trackFilterEnable = window['inventoryFilterTrackFilterEnable'].get()
    
    if trackFilterEnable:
        trackFilterTokens = window['inventoryFilterTracks'].get().split()
        
    
    total = {'count':0,
            'length':0,
            'weight':0,
            'loads':0,
            'empties':0,
            'engines':0}

    for unit in world.units:
        # first, ignore all the stuff we're filtering out
        if unit.isLoco() and includeLocos == False:
            continue
        if not(unit.isLoco()) and includeCars == False:
            continue
        
        
        if trackFilterEnable:
            trackOK = False
            # where is this unit?
            onGroups = unit.trackGroupsForUnit(world.trackGroups)
            for g in onGroups:
                for tok in trackFilterTokens:
                    if '*' in tok:
                        tok = tok.split('*')[0]
                        if g.upper().startswith(tok.upper()):
                            trackOK = True
                    else:
                        # no wildcard
                        if tok.upper() == g.upper():
                            trackOK = True
                            
                            
            if not trackOK:
                continue # ignore this unit entirely
            
        if humpOnly:
            dtag = world.getHumpTag(unit.destinationTag)
        else:
            # inventory ALL the tags
            try:
                dtag = unit.destinationTag.strip()
            except AttributeError:
                # if the unit has no tag
                dtag = "<< No Tag >>"
                
            if dtag == "None":
                dtag = "<< Tagged 'None' >>"
                
        if dtag not in tags:
            tags[dtag] = {'count':0,
                            'length':0,
                            'weight':0,
                            'loads':0,
                            'empties':0,
                            'engines':0}
        
        tag = tags[dtag]
        tag['count'] += 1
        tag['length'] += unit.lengthFt
        tag['weight'] += unit.totalWeight()
        tag['loads'] += unit.isLoaded()
        tag['empties'] += unit.isEmpty()
        tag['engines'] += unit.isLoco()
        
        
        total['count'] += 1
        total['length'] += unit.lengthFt
        total['weight'] += unit.totalWeight()
        total['loads'] += unit.isLoaded()
        total['empties'] += unit.isEmpty()
        total['engines'] += unit.isLoco()
    
    
    values = []
    for tag in tags:
        row = [tag,
               tags[tag]['count'], 
               round(tags[tag]['length']), 
               round(tags[tag]['weight']),
               tags[tag]['loads'],
               tags[tag]['empties'],
               tags[tag]['engines']
               ]
        values.append(row)
    
    values.sort(key = lambda e: e[0])
    
    # now add the total on top
    values.insert(0,  ['<< TOTAL >>',
               total['count'], 
               round(total['length']), 
               round(total['weight']),
               total['loads'],
               total['empties'],
               total['engines']
               ])
       
    
    window['inventoryTable'].update(values = values)
        
    
def buildOpsTab(world):
    
    layout = []
    
    # top row
    row = []
    row.append(sg.Table(values = [[]],
                        headings = ["Job ID",
                                    "Job Name",
                                    "Visible",
                                    "Type",
                                    "Status",
                                    "Tracks"],
                        col_widths = [20, 30, 10, 10, 10, 50], 
                        auto_size_columns = False,
                        justification = 'center',
                        background_color = '#333333',
                        expand_x = False,
                        expand_y = True,
                        hide_vertical_scroll = False,
                        font = 'Consolas 10',
                        k = 'jobsTable',
                        display_row_numbers = False
                        ))
    layout.append(row)
    
    # control row
    row = []
    
    row.append(sg.Button("New Job",
                         k = "newJobButton"))
    
    #row.append(sg.Button("Edit Job",
    #                     k = "editJobButton"))
    
    row.append(sg.Button("Issue Job",
                         k = "issueJobButton"))
    
    row.append(sg.Button("Remove Job",
                         k = "removeJobButton"))
        
    row.append(sg.Button("Complete Job",
                         k = "completeJobButton"))
    layout.append(row)
    
    
    return sg.Tab("Operations",
                  layout,
                  background_color = '#333333',
                  element_justification = 'left',
                  expand_x = True,
                  k='operationsTab')
    
def buildInventoryTab(world):
    layout = []
    
    #row 0
    row = []
    
    
    inventoryFrame = buildInventoryFrame(world)
    inventoryFilterFrame = buildInventoryFilterFrame(world)
    
    row.append(inventoryFrame)
    row.append(inventoryFilterFrame)
    
    layout.append(row)
                        
    
    return sg.Tab("Yard Inventory",
                  layout,
                  background_color = '#333333',
                  element_justification = 'left',
                  expand_x = True
                  )
                  
                  
def buildTrainBuilderTab(world):
    layout = []
    
    # top row
    row = []
    orgTrains = world.yardSettings['originateTrains']
    buildTracks = world.yardSettings['buildableTracks']
    
    row.append(sg.Text("Train:",
                       background_color = '#333333'))
    row.append(sg.Combo(values = orgTrains,
                        readonly = True,
                        size = (20, 8),
                        k = 'buildSelectTrain'))
    row.append(sg.Text("Build on:",
                       background_color = '#333333'))
    row.append(sg.Combo(values = ["HEAD:"] + buildTracks,
                        default_value = "HEAD:",
                        readonly = True,
                        size = (20, 8),
                        k = 'buildSelectBuildTrack1'))
    row.append(sg.Combo(values = ["MID:"] + buildTracks,
                        default_value = "MID:",
                        readonly = True,
                        size = (20, 8),
                        k = 'buildSelectBuildTrack2'))
    row.append(sg.Combo(values = ["REAR:"] + buildTracks,
                        default_value = "REAR:",
                        readonly = True,
                        size = (20, 8),
                        k = 'buildSelectBuildTrack3'))
                        
    row.append(sg.Button("Start",
                         k = 'buildStart'))
    
    row.append(sg.Button("Clear Selections",
                         k = 'buildClearBuildSelections'))
    
    layout.append(row)
    
    # sep
    row = []
    row.append(sg.HorizontalSeparator())
    layout.append(row)
    
    
    
    # sep
    row = []
    row.append(sg.HorizontalSeparator())
    layout.append(row)
    
    
  
    
    return sg.Tab("Build Train",
                  layout,
                  background_color = '#333333')
                  
    
def buildYardSettingsTab(world):
    layout = [[]]
    
    return sg.Tab("Yard Settings",
                  layout,
                  background_color = '#333333')
   

class TrackVisualizer():
    """ Class defining a track visualizer. 
    
    Attributes:
        element: the actual PySG Graph element
        track: the track name we're associated with (must match yard.json)
        subyard: the subyard name we're associated with (must match yard.json)
        units: points to the units list of the associated track
    
    Methods:
        __init__(): sets up all attributes.  element is automatically created
            Parameters:
                subyard: a string matching a subyard name in yard.json
                track: string matching a track name in yard.json
                size: the visualizer element size in pixels
                
                
                
        redraw(): redraws the entire visualizer element from scratch
        
    
    """
    
    def redraw(self):

        self.units = self.trackObject.units
        
        self.element.erase()
        
        self.unitFromFigIdx = {}
        
        coLines = []
        hazLines = []
        
        x = 1
        y = 1
            
        for unitIdx in range(0, len(self.units)):
            unit = self.units[unitIdx]
            
            try:
                prevUnitTag = self.units[unitIdx-1].destinationTag
                prevUnitHaz = self.units[unitIdx-1].isHazmat()
            except IndexError:
                prevUnitTag = None
                prevUnitHaz = False
            
            try:
                nextUnitTag = self.units[unitIdx+1].destinationTag
                nextUnitHaz = self.units[unitIdx+1].isHazmat()
            except IndexError:
                nextUnitTag = None
                nextUnitHaz = False
                
            center = (x, y)
            radius = 0.4
            
            lowY = y - 0.2
            ulineY = y - 0.5
            hazlineY = y - 0.7
            highY = y + 0.2
            lowX = x - 0.3
            lowXext = x - 0.6
            highX = x + 0.3
            highXext = x + 0.6 
            
            if unit.isLoco():
                # draw locomotive
                
                
                points = [ (lowX, lowY),
                           (x, highY),
                           (highX, lowY) ]
                           
                
                figIdx = self.element.draw_polygon(points, 
                                         fill_color = 'white',
                                         line_color = 'white',
                                         line_width = 1)
            else:
                # draw railcar
                
                # what color??
                
                carColor = self.getHumpColor(unit.destinationTag)
                
                
                # open shape for empty
                if unit.isLoaded():
                    fill = carColor
                else:
                    fill = '#111111'
                
                
                if unit.isHazmat():
                    # add to list of hazmat lines
                    if prevUnitHaz:
                        thisLowX = lowXext
                    else:
                        thisLowX = lowX
                    if nextUnitHaz:
                        thisHighX = highXext
                    else:
                        thisHighX = highX
                        
                    linePoints = [(thisLowX, hazlineY), (thisHighX, hazlineY)]
                    hazLines.append(linePoints)
                
                # draw circle for unit 
                # all cars are circles now
                figIdx = self.element.draw_circle(center,
                                     radius, 
                                     fill_color = fill,
                                     line_color = carColor,
                                     line_width = 1)
                                         
                
                
                
                # prepare to mark customer orders
                # (compile list of points to connect with line segments)
                if unit.isCustomerOrder:
                    if unit.destinationTag == prevUnitTag:
                        thisLowX = lowXext
                    else:
                        thisLowX = lowX
                    if unit.destinationTag == nextUnitTag:
                        thisHighX = highXext
                    else:
                        thisHighX = highX
                        
                    linePoints = [(thisLowX, ulineY), (thisHighX, ulineY)]
                    coLines.append(linePoints)
            
            
            self.unitFromFigIdx[figIdx] = unit
            x += 1
            
            
        # draw underlines for customer orders
        for line in coLines:
            self.element.draw_line(line[0],
                                   line[1],
                                   color = 'white',
                                   width = 2)
        # draw underlines for hazmat
        for line in hazLines:
            self.element.draw_line(line[0],
                                   line[1],
                                   color = 'red',
                                   width = 2)
        
        # draw selection pointers
        # set up coords for pointers
        pointers = self.trackObject.pointers


        for ptr in self.trackObject.pointers:
            x = ptr['xCoord']
            y = 0.25
            lowY = y - 0.2
            ulineY = y - 0.5
            highY = y + 0.2
            lowX = x - 0.3
            lowXext = x - 0.6
            highX = x + 0.3
            highXext = x + 0.6
            
            points = [ (lowX, lowY),
                       (x, highY),
                       (highX, lowY) ]
            
            figIdx = self.element.draw_polygon(points, 
                                         fill_color = '#33ff33',
                                         line_color = '#33ff33',
                                         line_width = 1)
            
        
        # print text info
        trackLength = self.trackObject.length
        occLength = round(sum([unit.lengthFt for unit in self.units]))
        remLength = trackLength - occLength
        
        weight = round(sum([unit.totalWeight() for unit in self.units 
                                if unit.isLoco() == False]))
        
        if remLength > 500:
            tColor = 'white'
        elif remLength > 100:
            tColor = 'yellow'
        else:
            tColor = 'red'
            
        if remLength < 0:
            remLength = f"({remLength})" # negative in parens for emphasis
            foul = True
        else:
            foul = False
        
        txt = f"{self.trackName} - {occLength} / {trackLength} FT - "
        txt += f"{remLength} FT AVAIL - "
        if foul:
            txt += "** OVER ** - "
        txt += f"{weight} TONS"
        if self.trackObject.visTag is not None:
            txt += f" <{self.trackObject.visTag}>"
        self.element.draw_text(txt,
                               (0, 2.25),
                               color = tColor,
                               text_location = sg.TEXT_LOCATION_LEFT,
                               font = "Consolas 11")


    def __init__(self, world, subyardName, trackName, size):
        if type(subyardName) is not str:
            raise TypeError("Track visualizer: subyardName must be a string")
        if type(trackName) is not str:
            raise TypeError("Track visualizer: trackName must be a string (track name)")
        if type(size) is not tuple:
            raise TypeError("Track visualizer: size must be a tuple")
            
        self.subyardName = subyardName
        self.trackName = trackName
        
        #TODO: allow use of other colorsets
        self.colorFilters = world.yardSettings['filterColors']['humpColors']
        self.getHumpColor = world.getHumpColor #reference to function
        
        el = sg.Graph(size,
                      VISUALIZER_COORD1,
                      VISUALIZER_COORD2,
                      background_color = VISUALIZER_BG_COLOR,
                      k = f'subyardVis{trackName}',
                      enable_events = True,
                      float_values = True)
        
        self.trackObject = world.getTrackObject(trackName)

        self.units = self.trackObject.units

        
        self.element = el
                      
                      
             
def buildSubyardLayout(world, subyardName, allVisualizers):
    """ 
    builds the layout of a subtab (for one individual subyard)
    """
    
    syLayout = []
    
    subyard = world.yardSettings['subyards'][subyardName]
    
    for trackName in subyard:
        trackButton = sg.Button(trackName,
                                size = 4,
                                p = 0,
                                k = f'subyardButton{trackName}',
                                button_color = 'white on #111111',
                                font = 'Consolas 11 bold')
        vis = TrackVisualizer(world, subyardName, trackName, VISUALIZER_CANVAS_SIZE)
        syLayout.append([trackButton, vis.element])
        
        trackObj = world.getTrackObject(trackName)

        trackObj.registerVisualizer(vis)
        
        allVisualizers[f'subyardVis{trackName}'] = vis
    
    
    tabLayout = [[]]
    tabLayout[0].append(sg.Column(syLayout,
                             background_color = '#333333',
                             expand_x = True,
                             expand_y = True,
                             scrollable = True))
    
    return tabLayout
    
def buildSubyardTab(world, allVisualizers):
    subTabs = []
    
    subyards = world.yardSettings["subyards"]
    
    for sy in subyards:
        name = sy
        tracks = subyards[sy]
        
        subyardLayout = buildSubyardLayout(world, sy, allVisualizers)
        
        subTabs.append(sg.Tab(sy,
                           subyardLayout,
                           background_color = '#333333',
                           k = f'subyardTab{name}'))
                           
    subyardTabGroup = sg.TabGroup([subTabs],
                         k = 'subyardTabGroup',
                         title_color = '#AAAAAA',
                         selected_title_color = '#66FF66',
                         background_color = 'black',
                         tab_background_color = 'black',
                         selected_background_color = '#333333',
                         focus_color = 'black',
                         tab_border_width = 2,
                         border_width = 0,
                         font = 'Consolas 10 bold',
                         expand_x = True,
                         expand_y = True)
    
    tabLayout = [[subyardTabGroup]]
    
    subyardTab = sg.Tab("Visual Inventory",
                        tabLayout,
                        background_color = '#333333',
                        k = 'visualInventoryTab')
    
    return subyardTab
                  
def buildTerminalTab(world):
    layout = [[]]

    return sg.Tab("Terminal",
                  layout,
                  background_color='#333333')

def buildTabList(world, allVisualizers):
    tabs = []

    terminalTab = buildTerminalTab(world)
    tabs.append(terminalTab)
    
    opsTab = buildOpsTab(world)
    tabs.append(opsTab)
    
    inventoryTab = buildInventoryTab(world)
    
    tabs.append(inventoryTab)
    
    # build tab for each subyard
    syTab = buildSubyardTab(world, allVisualizers)
    tabs.append(syTab)
            
    
    trainBuilderTab = buildTrainBuilderTab(world)
    yardSettingsTab = buildYardSettingsTab(world)
    
    tabs.append(trainBuilderTab)
    tabs.append(yardSettingsTab)
    
    return tabs

def buildMainWindow(world, allVisualizers):
    print("Building UI...")
    
    try:
        title = f"{world.yardSettings['displayName']}"
    except KeyError:
        # if our yard file doesn't have a display name defined
        title = f"Yard Clerk" 
    
    
  
    
    
    layout = []
    
    # status bar
    row = []
    row.append(sg.Text(f"Good morning {world.yardSettings['shortName']}!", 
                       text_color = 'white', 
                       background_color = '#000000',
                       font = 'Consolas 11 bold',
                       k = 'bannerText'))
                       
    layout.append(row)
    
    
    
    # main panel
    tabs = buildTabList(world, allVisualizers)

    tabBar = sg.TabGroup([tabs],
                         title_color = '#AAAAAA',
                         selected_title_color = '#66FF66',
                         background_color = 'black',
                         tab_background_color = 'black',
                         selected_background_color = '#333333',
                         focus_color = 'black',
                         tab_border_width = 2,
                         border_width = 0,
                         font = 'Consolas 12 bold',
                         expand_x = True,
                         expand_y = True,
                         size=[400,400],
                         k = 'mainTabs')
                         
    layout.append([tabBar])

    #input line
    inputBar = sg.Input(background_color='#333333', 
                        text_color='white',
                        #size=[400,100],
                        expand_x=True,
                        font='Consolas 12',
                        )
    layout.append([inputBar])

    
    win = sg.Window(title, 
                    layout,
                    #finalize = True
                    #text_color = 'white',
                    background_color = 'black',
                    use_custom_titlebar = False,
                    titlebar_text_color = 'white',
                    titlebar_background_color = 'black',
                    size = (1400, 600),
                    location = (0,0)
                    )
    
    
    print("Done building UI.")
    return win
