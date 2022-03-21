from RailUnit import RailUnit



class Train():
    
        
    
    def isWestFacing(self, trackGroups):
        """Determines whether the train object has its lead unit at the 
        west end.  If this is true, the object is in correct left-right order
        for display on the visualizer."""
        
        # find the first and last units in the train 
        # that occupy a known track group
        group = None
        first = None
        last = None
        
        count = self.countUnits()
        
        # get the first unit on a group
        for idx in range(0, count):
            unit = self.units[idx]
            groups = unit.trackGroupsForUnit(trackGroups)
            if len(groups):
                first = unit
                group = groups[0]
                break
        
        # get the last unit on the same group
        for idx in range(-1, (count*-1)-1, -1):
            unit = self.units[idx]
            groups = unit.trackGroupsForUnit(trackGroups)
            if group in groups:
                last = unit
                break
        
        if group is not None:
            #print(f"{self.symbol()} is on {group}")
            firstKeys = first.trackKeys()
            lastKeys = last.trackKeys()
            
            groupKeys = trackGroups[group]['sections']
            
            
            # try to use the leadmost truck on the head end and the 
            # rearmost truck on the rear end
            # but we need to handle the case where those trucks are not
            # actually occupying the track groups
            firstIdealTruck = bool(first.reverseDirection[0])
            lastIdealTruck = bool(not(last.reverseDirection[0]))
            try:
                leadKey = first.trackKeys()[firstIdealTruck]
                leadIdx = list(groupKeys).index(firstKeys[firstIdealTruck])
                leadDist = first.distanceTravelledInMeters[firstIdealTruck]
                leadStartNode = first.startNodeIndex[firstIdealTruck]
            except:
                leadKey = first.trackKeys()[1-firstIdealTruck]
                leadIdx = list(groupKeys).index(firstKeys[1-firstIdealTruck])
                leadDist = first.distanceTravelledInMeters[1-firstIdealTruck]
                leadStartNode = first.startNodeIndex[1-firstIdealTruck]
            
            try:
                trailKey = last.trackKeys()[lastIdealTruck]
                trailIdx = list(groupKeys).index(lastKeys[lastIdealTruck])
                trailDist = last.distanceTravelledInMeters[lastIdealTruck]
                trailStartNode = last.startNodeIndex[lastIdealTruck]
            except:
                trailKey = last.trackKeys()[1-lastIdealTruck]
                trailIdx = list(groupKeys).index(lastKeys[1-lastIdealTruck])
                trailDist = last.distanceTravelledInMeters[1-lastIdealTruck]
                trailStartNode = last.startNodeIndex[1-lastIdealTruck]
            
            #print(f"{leadIdx=}, {trailIdx=}")
            
            if leadIdx < trailIdx:
                #print("West facing!")
                return True
            elif leadIdx > trailIdx:
                #print("East facing!")
                return False
            elif self.countCars() == 1 and self.countLocos() == 0:
                #print("This train has one car and no locos, don't worry!")
                return True # by default, it doesn't really matter in this case
            elif leadIdx == trailIdx:
                #print(f"We only have one section to go on, doing it the hard way...")
                #print(f"{leadDist=}")
                #print(f"{trailDist=}")
                if leadDist == trailDist:
                    print(f"Can't orient train {self.symbol} on {group}, no distance")
                    return None
                if leadStartNode != trailStartNode:
                    print(f"Can't orient train {self.symbol} on {group}, different start nodes")
                    return None
                elif leadDist < trailDist:
                    # this means the lead truck is closest to the section start node
                    # if the start node is also the left node, we're facing west
                    leftNode = trackGroups[group]['sections'][leadKey]['leftNode']
                    if leftNode is None:
                        print(f"Can't orient train {self.symbol} on {group}, unknown section orientation")
                        return None
                    if leadStartNode == leftNode:
                        #print("West facing (short)!")
                        return True
                    else:
                        #print("East facing (short)!")
                        return False
                    
                    
                
                
        
    
    def trackGroups(self, groupDef):
        groups = []
        for u in self.units:
            ugr = u.trackGroupsForUnit(groupDef)
            groups = list(set(groups+ugr))
        
        return groups
            
    def leadLoco(self):
        lead = self.leadUnit()
        if lead.isLoco():
            return lead
        else:
            return None
    
    def leadUnit(self):
        return self.units[0]
    
    def lastUnit(self):
        return self.units[-1]

    
    def symbol(self):
        lead = self.units[0]
        return lead.destinationTag
    
    def run8Route(self):
        routes = []
        for u in self.units:
            uroute = u.run8Route()
            if uroute not in routes:
                routes.append(uroute)
        
        if routes == ['BarstowYermo']:
            return 'BarstowYermo'
        
        if 'multiple' in routes:
            return multiple
        
        return 'unknown'
        
        
    def countCars(self):
        count = 0
        for u in self.units:
            if u.isLoco():
                continue
            count += 1
        return count
        
    def countLocos(self):
        count = 0
        for u in self.units:
            if u.unitType != 'US_DieselEngine':
                continue
            count += 1
        return count
        
    def countUnits(self):
        return self.countLocos() + self.countCars()
        
        
    def length(self):
        length = 0
        for u in self.units:
            length += u.lengthFt
        return length
        
    def carTons(self):
        weight = 0
        for u in self.units:
            if u.unitType == 'US_DieselEngine':
                continue
            weight += u.emptyWeight
            weight += u.loadWeight
        return weight
        
    def __init__(self, TrainLoader = None, **kwargs):
        """Takes a TrainLoader object (likely obtained from the world XML 
        file) and creates the corresponding Train object."""
        
        self.trainID = TrainLoader['trainID']
        self.TrainWasAI = TrainLoader['TrainWasAI']
        self.unitLoaderList = TrainLoader['unitLoaderList']
        
        self.buildUnitList()
        
    
    def buildUnitList(self):
        if type(self.unitLoaderList['RailVehicleStateClass']) is list:
            loneUnit = False
            units = self.unitLoaderList['RailVehicleStateClass']
        else:
            loneUnit = True
            units = [self.unitLoaderList['RailVehicleStateClass']]
        
        
        # list of the actual unit objects, not XML
        self.units = []

        for unit in units:
            try:
                thisUnit = RailUnit(unit) # build the RailUnit object
            except:
                print('\n\n\n\ntried to interpret the following as xml: ', unit)
                print('\n\nunits: ', units)
                input()
            self.units.append(thisUnit)

