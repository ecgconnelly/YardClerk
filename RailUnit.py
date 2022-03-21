import json

class RailUnit():
    # Attributes:
    # Reporting mark and number  (unit.initials, unit.unitNumber)
    # Empty weight
    # Load weight
    # Total weight
    # Whether car is loaded
    # Location of each truck
    # Whether unit is locomotive
    # Tag (unit.destinationTag)
    
    """
    rvXMLfilename
    unitType
    currentRoutePrefix
    currentTrackSectionIndex
    startNodeIndex
    distanceTravelledInMeters
    reverseDirection
    loadWeightUSTons
    destinationTag
    unitNumber
    hazmatPlacardIndex
    """
    
    def __init__(self, unitXML = None, **kwargs):
        
        if 'unitDefs' not in RailUnit.__dict__:
            # we need to grab the definitions
            with open('unitdefs.json') as ud:
                j = ud.read()
                RailUnit.unitDefs = json.loads(j)
        try:
            self.rvXMLfilename = unitXML['rvXMLfilename'].split('.xml')[0]
        except Exception as e:
            print('\n\n\n', e)
            print(unitXML)
            input()
            print(unitXML['rvXMLfilename'])
            input()
            raise
       
        self.setPropertiesFromXMLName()
       
        self.unitType = unitXML['unitType']
        self.currentRoutePrefix = (unitXML
            ['currentRoutePrefix']['int'])
            
            
        self.currentTrackSectionIndex = (unitXML
            ['currentTrackSectionIndex']['int'])
            
        for n in self.currentTrackSectionIndex:
            n = int(n)
                
        self.startNodeIndex = (unitXML
            ['startNodeIndex']['int'])
            
            
        self.distanceTravelledInMeters = (unitXML
            ['distanceTravelledInMeters']['float'])
        self.reverseDirection = (unitXML
            ['reverseDirection']['boolean'])
        self.loadWeight = float(unitXML
            ['loadWeightUSTons'])
        self.destinationTag = unitXML['destinationTag']
        self.unitNumber = int(unitXML['unitNumber'])
        self.hazmatPlacardIndex = int(unitXML['hazmatPlacardIndex'])
        
    def isHazmat(self):
        if self.hazmatPlacardIndex != 0:
            return True
        else:
            return False
    def bothTrucks(self):
        return [self.truckInfo(0), self.truckInfo(1)]
        
    def trackKeys(self):
        trucks = self.bothTrucks()
        keys = [trucks[0]['trackKey'], trucks[1]['trackKey']]
        return keys
        
    def truckInfo(self, truckIdx):
        res = {}
        res['routePrefix'] = self.currentRoutePrefix[truckIdx]
        res['trackSection'] = self.currentTrackSectionIndex[truckIdx]
        res['startNode'] = self.startNodeIndex[truckIdx]
        res['distanceMeters'] = self.distanceTravelledInMeters[truckIdx]
        res['reverseDirection'] = self.reverseDirection[truckIdx]
        res['trackKey'] = res['routePrefix'] + '_' + res['trackSection']
        return res
    
    def trackGroupsForUnit(self, groupDef):
        """Given a dictionary of track groups, returns the group names this
        unit has at least one truck on."""
        trucks = self.bothTrucks()
        keys = [trucks[0]['trackKey'], trucks[1]['trackKey']]

        occupiedGroups = []
        for g in groupDef:
            for k in keys:
                #print(f"{g=}")
                #print(f"{k=}")
                #print(f"{keys=}")
                #print(f"{groupDef[g]['sections']=}")
                #input()
                if k in groupDef[g]['sections']:
                    if g not in occupiedGroups:
                        occupiedGroups.append(g)
                        #print('found a match!')
                        #input()
        return occupiedGroups
        
    def trackGroupsForTruck(self, groupDef, truckIndex):
        truck = self.truckInfo(truckIndex)
        key = trucks[truckIndex]['trackKey']
        
        occupiedGroups = []
        for g in groupDef:
            if key in groupDef[g]['sections']:
                if g not in occupiedGroups:
                    occupiedGroups.append(g)
        return occupiedGroups
        
        
    def isOccupyingTrackGroup(self, groupDef, groupName, bothTrucks = False):
        """Given the name of a track group, returns whether this unit is
        occupying that group.  Specifiy bothTrucks = Trus to require that
        both trucks must be in the trackGroup."""
        if not bothTrucks:
            groups = self.trackGroupsForUnit(groupDef)
            if groupName in groups:
                # we are occupying the group
                # we only need one truck this time, report occupancy
                return True
            else:
                return False
        else:
            # we need both trucks, test both individually
            t0groups = self.trackGroupsForTruck(groupDef, 0)
            t1groups = self.trackGroupsForTruck(groupDef, 1)
            
            if groupName in t0groups and groupName in t1groups:
                return True
            else:
                return False
             
            
    def totalWeight(self):
        return self.emptyWeight + self.loadWeight
        
    def isLoco(self):
        if self.unitType == 'US_DieselEngine':
            return True
        return False
    
    def isLoaded(self):
        if self.isLoco():
            return False
        if self.loadWeight < 1:
            return False
        return True
    
    def isEmpty(self):
        if self.isLoco():
            return False
        if self.isLoaded():
            return False
        return True
        
    def run8Route(self):
        if self.currentRoutePrefix[0] != self.currentRoutePrefix[1]:
            return 'Multiple Run8 Routes'
        if self.currentRoutePrefix == ['150', '150']:
            return 'BarstowYermo'
    
    def setPropertiesFromXMLName(self):
        name = self.rvXMLfilename
        for ud in RailUnit.unitDefs:
            if ud['xmlName'] == name:
                self.initials = ud['initials']
                self.emptyWeight = ud['emptyWeight']
                self.lengthFt = ud['lengthFt']
                return
        
        print('XML name: ', self.rvXMLfilename, ' not found')
        raise ValueError
            
