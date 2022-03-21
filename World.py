import collections
import copy
import json
from os import walk

import xmltodict


from Train import Train 


# WorldState.trains: list of all trains in the world
# WorldState.units: list of all units in the world
# WorldState.trackGroups: all the defined trackGroup objects
# WorldState.yardSettings: all the settings for this yard
#### ['humpTags']
#### ['displayName']



class Track():
        """ Defines a Track object.  Generally units either exist on a Track,
        or they are in an unknown location / nowhere.  Allows registration of 
        Visualizers so that all associated Visualizers can be redrawn when 
        units are moved in or out of the track.
        
        Attributes:
            subyardName
            trackName
            units: list of Unit objects
            length
            status
            visualizers: list of visualizers showing this track
            
        
        Methods:
        
            populateFromWorld(world):
                takes a world object and sets self.units to match the given world
                
                
                
            addUnits(units, leftEnd = False) 
                adds a correctly oriented list of units
                returns nothing
                
                units: list of Unit objects, element 0 is always at left
                leftEnd: if true, add the new units to the left end of this Track
                
                
            
            removeUnits(count, leftEnd = False)
                removes a number of units
                returns a list of the removed units, properly oriented
                (suitable for adding to another track)
                
                count: the number of units to remove
                leftEnd: if true, removes units from the left end
                
            redrawVisualizers()
                iterates over self.visualizers and calls redraw() on each
        """
    
        def __init__(self, world, subyardName, trackName, units = [],
                     length = 0, status = None):
                            
            self.subyardName = subyardName
            self.trackName = trackName
            self.units = units
            self.length = length
            self.status = status
            self.visualizers = []
            self.pointers = [] # pointer/cursor for car selections
            
            
            # call setVisTag() after setting the subyard name
            self.setVisTag(world)
            
            self.populateFromWorld(world)
        
        
        def isOverLength(self, world):
            if sum([u.lengthFt for u in self.units]) > self.length:
                return True
            else:
                return False
                
                
        def setVisTag(self, world):
            subyard = world.yardSettings['subyards'][self.subyardName]
            track = subyard[self.trackName]
            try:
                self.visTag = track['visTag']
            except KeyError:
                # if the track has no visualizer tag defined
                self.visTag = None
            
        def populateFromWorld(self, world):
            """ 
            Takes a world object and sets self.units to match
            """
            units = []
            
            for train in world.trains:
                onGroups = train.trackGroups(world.trackGroups)

                if self.trackName in onGroups:
                    # train is on this track
                    
                    # don't be affected by subsequent changes to the Train obj
                    trainUnits = copy.deepcopy(train.units)
                    
                    if not train.isWestFacing(world.trackGroups):
                        # this train is facing east and needs to be flipped
                        # for display and inventory purposes
                        trainUnits.reverse()
                    
                    # maybe there are multiple cuts in this track
                    units += trainUnits
            
            self.units = units
            
        def registerVisualizer(self, visualizer):
            if visualizer not in self.visualizers:
                self.visualizers.append(visualizer)
                
        def deregisterVisualizer(self, visualizer):
            if visualizer in self.visualizers:
                self.visualizers.remove(visualizer)
            
        def redrawVisualizers(self):
            for vis in self.visualizers:
                vis.redraw()

class Job():
    def __init__(self, world, jobID, jobName, jobType, jobNotes = None):
        self.world = world
        self.steps = [] # start with empty job
        self.jobID = jobID
        self.jobName = jobName
        self.jobType = jobType
        
        if jobNotes is None:
            self.jobNotes = ''
        else:
            self.jobNotes = jobNotes
        
    
    def execute(self):
        for step in self.steps:
            step.execute()
    
    def undo(self):
        for step in reversed(self.steps):
            step.undo()
        
        self.world.redrawAllVisualizers()
            
    def undoLast(self):
        lastStep = self.steps[-1]
        lastStep.undo()
        self.steps.remove(lastStep)
        self.world.redrawAllVisualizers()
        
        
            
    def addHumpStep(self, trackName):
        # hump the rightmost unit on selected track
        # iterate one by one until track is empty
        # create undo stack for each humped unit
        ops = []
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
            
            op = Operation(self.world, source, dest,
                           count, sourceIndex, destIndex)
                                 
            op.execute()
            
            ops.append(op)
        
        # done humping, put all those operations into a JobStep
        step = JobStep(operations = ops)
        
        # put the step we just created into the Job we're working on
        self.steps.append(step)
        
        # show the results
        self.world.redrawAllVisualizers()


class JobStep():
    """
    Object representing a group of Operations to be accomplished together.
    """
    
    def __init__(self, operations):
        self.operations = operations
    
    
    def execute(self):
        for op in self.operations:
            op.execute()
    
    def undo(self):
        for op in reversed(self.operations):
            op.execute(undo = True)
        

class Operation():
    """
    Object to represent moving a single block of cars from one track to another.
    
    A job is made up of multiple operations.
    """
    
    def __init__(self, world, sourceTrackName, destinationTrackName, 
                 count, sourceIndex, destinationIndex):
        # moves the given number of cars from source to destination
        # pulls #count cars from source track, starting at sourceIndex,
        # and inserts to destination track at destinationIndex
        self.world = world
        self.sourceTrack = world.getTrackObject(sourceTrackName)
        self.destinationTrack = world.getTrackObject(destinationTrackName)
        self.count = count
        self.sourceIndex = sourceIndex
        self.destinationIndex = destinationIndex
        
        
        
    def execute(self, undo = False):
        
        if undo:
            sourceTrack = self.destinationTrack
            sourceIndex = self.destinationIndex
            destinationTrack = self.sourceTrack
            destinationIndex = self.sourceIndex
        else:
            sourceTrack = self.sourceTrack
            sourceIndex = self.sourceIndex
            destinationTrack = self.destinationTrack
            destinationIndex = self.destinationIndex
        
        # split the source into left remaining, 
        # moving, and right remaining chunks
        sourceUnits = sourceTrack.units
        
        sourceLeft = sourceUnits[:sourceIndex]

        movedUnits = sourceUnits[sourceIndex:sourceIndex + self.count]

        sourceRight = sourceUnits[sourceIndex+self.count:]
        
        # update the source track to reflect what remains
        sourceTrack.units = sourceLeft + sourceRight
        afterMarks = [f"{unit.initials} {unit.unitNumber}" for unit in sourceTrack.units]
        #sg.popup(afterMarks, title = ' source track after move')
        
        # split the destination into left and right chunks
        # insert the moved units
        destLeft = destinationTrack.units[:destinationIndex]
        destRight = destinationTrack.units[destinationIndex:]
        
        # update the destination track
        destinationTrack.units = destLeft + movedUnits + destRight


    

class WorldState():
    
    
    # instance attributes:
        # track groups:
            # definition
            # cuts occupying that group, oriented
            # L, W, count total and for each dest
        # trains
        # list of destination tags with total length and weight
    
    def __init__(self, worldName, stateFilenames, yardName):
        self.worldName = worldName
        self.stateFilenames = stateFilenames
        self.yardName = yardName
        
        # analyze track groups
        # populate self.trackGroups
        self.analyzeTrackGroups()
        
        
        # analyze world files
        # populate self.trains, self.units
        self.analyzeWorldFiles()
        
        
        # load yard settings file
        self.loadYardSettings()
        
        for unit in self.units:
            if not unit.isLoco():
                # this is a car
                unit.nextTrain = self.getNextTrain(unit.destinationTag)
                co = self.isTagCustomerOrder(unit.destinationTag)
            else:
                # this is a loco
                co = False
            
            unit.isCustomerOrder = co
                
        
        
        # build track objects 
        # this depends on trackGroups, trains, units, yardSettings
        self.buildTrackObjects()
    
    
    def redrawAllVisualizers(self):
        for track in self.trackObjects:
            self.trackObjects[track].redrawVisualizers()
            
            
    def buildTrackObjects(self):
        # set up dict of Track objects
        # key by the Track name (from yard.json)
        
        print("Building track objects...")
        
        trackObjects = {}
        
        subyards = self.yardSettings['subyards']
        
        
        for subyard in subyards:
            for track in subyards[subyard]:
                # iterate over all the designated tracks
                trackName = track
                subyardName = subyard
                length = subyards[subyard][track]['length']
                if length is None:
                    length = 0
                    
                # here, self IS a world object
                thisTrack = Track(self, subyardName, trackName,
                                  length = length)
                  
                trackObjects[trackName] = thisTrack
                
                
                
                # Track.__init__():
                """ def __init__(self, world, subyardName, trackName, units = [],
                     length = 0, status = None, visualizers = []):"""

        self.trackObjects = trackObjects
        
        
        print("Done building track objects.")
        
    def getUnitsFiltered(self, filters = []):
        """ Returns a list of units that satisfy the filters passed in.
        filters should be a list of dicts, like the examples below:
        
        To filter by current track:
            {onTrack:['R1', 'R3']}
            {notOnTrack:['R4']}
        
        To filter by hump tag:
            {humpTag:['BEL']}
            {notHumpTag:['PAS']}
        
        """
        pass
    
        
    def loadYardSettings(self):
        print("Loading yard settings from file...")
        
        # open the settings file
        filepath = f'./yardConfigs/{self.yardName}/{self.yardName}.json'
        
        with open(filepath) as f:
            filestr = f.read()
            self.yardSettings = json.loads(filestr)
        
        # if this is a hump yard, tokenize the hump destination strings
        if "humpTags" in self.yardSettings:
            for track in self.yardSettings['humpTags']:
                self.yardSettings['humpTags'][track] = self.yardSettings['humpTags'][track].split()
                
        
        
        

        print("Done loading yard settings.")

    
    def getNextTrain(self, destinationTag):
        

        try:
            for token in destinationTag.split():
                for tag in self.yardSettings['nextTrain']:
                    if tag.upper() == token.upper():
                        # matched
                        return self.yardSettings['nextTrain'][tag]
        except AttributeError:
            return None
         
        #if we look at all the tags and don't find a match, give up
        return None
        
    def isTagCustomerOrder(self, destinationTag):
        # if we have an off-route tag, this is not a CO
        try:
            for token in destinationTag.split():
                if token in self.yardSettings['offRouteTags']:
                    return False # not a CO
        except AttributeError:
            # this isn't a real tag, so it's not a CO
            return False
        
        return True # didn't find an off-route tag, probably CO

    def getTrackObject(self, trackName):
        """ Given a track name, returns the associated Track object.
        Intended for use with visualizers."""
        
        for track in self.trackObjects:
            if track == trackName:
                return self.trackObjects[track]
        return None
        
    def isTrackOverLength(self, trackName):
        trackObj = self.getTrackObject(trackName)
        return trackObj.isOverLength(world = self)
        
    def listOverLengthTracks(self, subyard = None):
        overs = []
        
        if subyard == None:
            subs = self.yardSettings['subyards'].keys()
        else:
            subs = [subyard]
        
        for sy in subs:
            # iterate over all relevant subyards
            for track in self.yardSettings['subyards'][sy]:
                over = self.isTrackOverLength(track)
                if over:
                    overs.append(track)
        
        return overs
            
        
    def getHumpColor(self, destinationTag):
        humpTag = self.getHumpTag(destinationTag)
        
        colorDict = self.yardSettings['filterColors']['humpColors']
        if humpTag in colorDict:
            return colorDict[humpTag]
        else:
            return colorDict['default']
            
            
    def getHumpTag(self, destinationTag):
        
        # return None if there's no hump set up
        if "humpTags" not in self.yardSettings:
            return None
        
        humpTag = 'SLUFF'
        
        humpTracks = self.yardSettings['humpTags']
        
        for track in humpTracks:
            trackTags = humpTracks[track]
            try:
                for token in destinationTag.split():
                    if token in trackTags:
                        humpTag = token
                        break
            except AttributeError:
                # maybe the unit isn't tagged
                humpTag = 'SLUFF'
                
        return humpTag
        
    def getHumpTrack(self, destinationTag):
        
        # return None if there's no hump set up
        if "humpTags" not in self.yardSettings:
            return None

        humpTracks = self.yardSettings['humpTags']

        for track in humpTracks:
            trackTags = humpTracks[track]
            try:
                for token in destinationTag.split():
                    if token in trackTags:
                        humpTrack = track
                        break
            except AttributeError:
                # maybe the unit isn't tagged
                humpTrack = self.getHumpTrack('SLUFF')
        try:        
            return humpTrack
        except:
            return self.getHumpTrack('SLUFF')
        
        
        
        
        
        
    def getXMLFiles(self, path):
        files = []
        
        for (dirpath, dirnames, filenames) in walk(path):
            files.extend(filenames)
        
        for f in files:
            if not(f.endswith('.xml')):
                files.remove(f)
        
        return files
        
    def trainsFromLoaders(self, loaders):
        trains = []
        for ldr in loaders:
            train = Train(ldr)
            trains.append(train)
        return trains
        
    def trainLoadersFromFile(self, filepath):
        print(f"Loading file {filepath}")
        allTrainLoaders = []
        with open(filepath) as f:
            fstr = f.read()
            fdict = xmltodict.parse(fstr)
            
            trainLoaders = fdict['ScnLoader']['trainList']['TrainLoader']
            # there may be one or multiple trains per file
            # if there is one train, trainLoaders is an OrderedDict
            # otherwise trainLoaders is a list
            
             
            if type(trainLoaders) is list:
                # there are multiple trains in this file
                # insert them all into configTrains
                for t in trainLoaders:
                    allTrainLoaders.append(t)
            elif type(trainLoaders) is collections.OrderedDict:
                # there is only one train in this file
                # insert it into configTrains
                allTrainLoaders.append(trainLoaders)
            else:
                raise Exception(f"Couldn't parse yard config file {filepath}")
        return allTrainLoaders

    def analyzeTrackGroups(self):
        print("Analyzing yard configuration...")
        
        # get list of all XML files in the yard directory
        yardDir = 'yardConfigs/' + self.yardName
        print(f"Getting XML files in ./yardConfigs/{yardDir}")
        
        xmlFileNames = self.getXMLFiles(yardDir)
        print(f"Found {len(xmlFileNames)} XML files.")


        # open all the XML files and convert to dicts
        configTrainLoaders = []
        for fn in xmlFileNames:
            filepath = f'./yardConfigs/{self.yardName}/{fn}'
            loaders = self.trainLoadersFromFile(filepath)
            configTrainLoaders += loaders
            
        print("Yard configuration files successfully loaded.")
        
        
        # build all train objects from the loaded files        
        print("Building yard configuration train objects...")
        
        
        configTrains = self.trainsFromLoaders(configTrainLoaders)
        
        
        print("Done building yard configuration train objects.")
        
        
        
        print("Analyzing yard configuration train objects...")     
        # build dict of track groups for this yard
        trackGroups = {}
        
        for train in configTrains:
            group = {} #dictionary for this particular group
            # one train defines a group
            
            
            # group name is the tag of the lead unit
            groupName = train.symbol()
            
            # assume the lead unit is always at the end 
            # we want to display on the left
            
            # iterate over units in the train
            # if we find a unit tagged lastOne, ignore all remaining units
            # starting from the lead unit, 
            # add track segments to the group's list
            group['sections'] = {}
            for unit in train.units:
                #what sections is this unit occupying?
                unitSections = unit.trackKeys()
                
                for us in unitSections: #only two sections per unit, at most
                    if us not in group['sections']:
                        thisSection = {}
                        thisSection['leftNode'] = None # default for now
                        group['sections'][us] = thisSection
                        #print(f'Registered section {us}')
                        #input()
                
                # now all sections this unit occupies have been entered
                
                # try to figure out which way this section points
                try:
                    if unitSections[0] != unitSections[1]:
                        # trucks are on different sections, don't bother
                        #print("Can't orient, trucks on different sections")
                        raise Exception('exitOK')
                        
                    section = unitSections[0]
                    if group['sections'][section]['leftNode'] is not None:
                        #print("Section already oriented")
                        raise Exception('exitOK')
                    
                    
                                            
                        
                    # we can only orient if both trucks start from the same node
                    # otherwise we would need to know the section length
                    if unit.startNodeIndex[0] != unit.startNodeIndex[1]:
                        #print("Can't orient, trucks have different start nodes")
                        raise Exception('exitOK')
                        
                    if unit.reverseDirection[0] != unit.reverseDirection[1]:
                        #print("Can't orient, this unit doesn't know which way it's facing")
                        raise Exception('exitOK')
                        
                    # if we're here, we're ok to orient
                    #print(f"Orienting section {section}")
                    
                    d0 = unit.distanceTravelledInMeters[0]
                    d1 = unit.distanceTravelledInMeters[1]
                    unitReversed = unit.reverseDirection[0]
                    
                    if d0 < d1:
                        if unitReversed == 'false':
                            leftNode = 0
                        else:
                            leftNode = 1
                    else:
                        if unitReversed == 'false':
                            leftNode = 1
                        else:
                            leftNode = 0
                    
                    group['sections'][section]['leftNode'] = leftNode
                                
                except Exception as e:
                    if 'exitOK' in e.args:
                        pass
                    
                    elif type(e) is KeyError:
                        print(f"Key error while orienting section {section}")
                        print(f"{group=}")
                        raise KeyError(e)
                    else:
                        print(f'Unknown exception while orienting section {section}.')
                        raise Exception(e)      
                
                if 'lastOne' in unit.destinationTag:
                    #ignore the rest of this train 
                    #(train goes onto track we don't want in this group)
                     
                    #print(f'Car is tagged lastOne, ignoring the rest of {train.symbol()}')
                    break
                        
            trackGroups[groupName] = group
            
        self.trackGroups = trackGroups
        print("Done analyzing yard configuration train objects.")
    
    
            
            
        
    
    def analyzeWorldFiles(self):
        print("Analyzing world state files...")
        
        loaders = []
        for f in self.stateFilenames:
            loaders += self.trainLoadersFromFile(f)
            
        print(f"Found {len(loaders)} trains in {len(self.stateFilenames)} files")
        
        self.trains = self.trainsFromLoaders(loaders)
        
        print("Done building train objects.")
        
        self.units = []
        for t in self.trains:
            for u in t.units:
                self.units.append(u)
        
        
        print("Done analyzing world state files.")
