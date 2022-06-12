import xml.etree.ElementTree as ET
import math
import numpy as np
import pandas as pd
import subprocess
import random
import sumolib
import platform
import os

def AddIterations(myCSV):
    df = pd.read_csv(myCSV)
    df["Iterations"] = ''
    df.to_csv(myCSV, index=False)
    return

def twoDecimalPlaces(folderLocation):
    for root, subdirectories, files in os.walk(folderLocation):
        for subdirectory in subdirectories:
            twoDecimalPlaces(folderLocation + '/' + subdirectory)
        for file in files:
            try:
                if file.endswith('.csv'):
                    print(file)
                    csv = folderLocation + "/" + file
                    df = pd.read_csv(csv)
                    print(df)
                    df = np.round(df, decimals=2)
                    print(df)
                    df.to_csv(csv, index=False)
            except:
                print("Already Changed")
    return


def runSUMO(simLoc, cfgFileName, collFileName = None, addFileName = None, begin = '0', end = '-1', scale = '1', noWarnings = "true"):
    location = simLoc + '/' + cfgFileName
    additional = simLoc + '/' + addFileName
    collision = simLoc + '/' + collFileName
    if platform.system() is "Windows":
        sumo = "sumo.exe"
    else:
        sumo = "sumo"
    if addFileName != None and collFileName != None:
        SUMO_run = subprocess.Popen([sumo, "-c", location, \
                                     "--additional-files", additional, \
                                     "--collision-output", collision, \
                                     "--begin", begin, \
                                     "--end", end, \
                                     "--scale", scale, \
                                     "--no-warnings", noWarnings,\
                                     "--step-length", "1"], \
                                     stdout=subprocess.PIPE)
    elif collFileName == None:
        SUMO_run = subprocess.Popen([sumo, "-c", location, \
                                     "--additional-files", additional, \
                                     "--scale", scale, \
                                     "--begin", begin, \
                                     "--end", end, \
                                     "--no-warnings", noWarnings,\
                                     "--step-length", "1"], \
                                     stdout=subprocess.PIPE)
    elif addFileName == None:
        SUMO_run = subprocess.Popen([sumo, "-c", location, \
                                     "--collision-output", collision, \
                                     "--scale", scale, \
                                     "--begin", begin, \
                                     "--end", end, \
                                     "--no-warnings", noWarnings, \
                                     "--step-length", "1"], \
                                     stdout=subprocess.PIPE)
    SUMO_run.wait()
    return

def setVtype(simLoc, rouFileName, idmParams, idmRatio=1):
    print(simLoc + '/' + rouFileName)
    idmID = "autonomous_vehicle"
    kraussID = "human_driver"
    carFollowModel = 'EIDM'
    # insert variables from X array into vtype parameters of rou.xml file
    tree = ET.parse(simLoc + '\\' + rouFileName)
    root = tree.getroot()
    # Recreate vType elements for IDM and krauss
    # Create IDM vType elements and set parameter attributes
    for vType in root.iter("vType"):
        if vType.attrib["id"] == idmID:
            vType.set("id", idmID)
            vType.set("vClass", "passenger")
            vType.set('carFollowModel', carFollowModel)
            vType.set('minGap', str(idmParams[0]))
            vType.set('accel', str(idmParams[1]))
            vType.set('decel', str(idmParams[2]))
            vType.set('emergencyDecel', str(idmParams[3]))
            vType.set('tau', str(idmParams[4]))
            vType.set('delta', str(idmParams[5]))
            #vType.set('stepping', str(idmParams[6]))

    # TODO: add way to set krauss parameters if desired

    tree.write(simLoc + '/' + rouFileName)

    # Iterate through all vehicles and set their vType based on idmRatio
    for vehicle in root.iter('vehicle'):
        num = random.random()
        if num <= idmRatio:
            vehicle.set("type", idmID)
        else:
            vehicle.set("type", kraussID)

    tree.write(simLoc + '/' + rouFileName)
    return

def setSampleFreq(simLoc, addFileName, freq):
    tree = ET.parse(simLoc + '/' + addFileName)
    root = tree.getroot()
    for vType in root.iter('edgeData'):
        vType.set('freq', freq)
    tree.write(simLoc + '/' + addFileName)

# Function to delete empty roads
def delEmptyRoads(data, simLoc, netFileName):
    tree = ET.parse(simLoc + '/' + netFileName)
    root = tree.getroot()
    for edge in root.iter('edge'):
        if edge.attrib["id"] in data.emptyRoads:
            root.remove(edge)
    tree.write(simLoc + '/' + "newNetFile.net.xml")
    tree = None
    return

# Data object for output data
# Contains all output data in dictionary and dictionaries of
# mean, standard deviation, minimum, and maximum values
# keys are used to reference the calculated data
# (i.e. 'density, 'collisions', etc.)
class outputData():
    def __init__(self, simLoc, outFileName, ignoreZeros=False, cutoff=0.5,\
        paramList = ["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered", "flow", "collisions"],\
        collFileName=None):
        # Get values from output xml and change to csv files with desired columns
        # create mean, standard deviation, minimum, and maximum attributes
        self.simLoc = simLoc
        self.outFileName = outFileName
        self.collFileName = collFileName
        self.cutoff=cutoff
        self.ignoreZeros=ignoreZeros
        if collFileName==None and "collisions" in paramList:
            paramList.remove("collisions")
        self.params = paramList
        self.sampleFreq = self.sampleTime(simLoc, outFileName)
        self.mean = {}
        self.stdDev = {}
        self.minimum = {}
        self.maximum = {}
        self.data = {}
        self.paramList = {}
        self.Q1 = {}
        self.Q3 = {}
        self.median = {}
        self.data = self.extractData(simLoc, outFileName, self.params, self.data)
        self.emptyRoads = self.findEmptyRoads()
        for param in self.params:
            if param != "collisions":
                self.mean[param] = self.paramMean(param)
                self.stdDev[param] = self.paramStdDev(param)
                self.minimum[param] = self.paramMin(param)
                self.maximum[param] = self.paramMax(param)
                self.paramList[param] = self.listIt(param, self.data)
                self.Q1[param] = self.paramQuart1(param)
                self.Q3[param] = self.paramQuart3(param)
                self.median[param] = self.paramMedian(param)
            else:
                self.mean[param] = self.countCollision()

    def countCollision(self):
        count = 0
        if self.collFileName != None:
            tree = ET.parse(self.simLoc + '/' + self.collFileName)
            root = tree.getroot()
            if root.find("collision")!=None:
                for collision in root.iter("collision"):
                    count += 1
        return count

    def listIt(self, param, data):
        x = []
        for interval in data:
            for edge in data[interval]:
                if param in data[interval][edge]:
                    value = data[interval][edge][param]
                    x.append(value)
        return x

    def sampleTime(self, simLoc, outFileName):
        tree = ET.parse(simLoc + '/' + outFileName)
        root = tree.getroot()
        for edgeData in root.iter('interval'):
            sampleTime = edgeData.attrib['end']
        return sampleTime

    def extractData(self, simLoc, outFileName, paramList, outData):
        # get data from xml output file
        tree = ET.parse(simLoc + "//" + outFileName)
        root = tree.getroot()
        count = 0
        for interval in root.iter("interval"):
            if interval not in outData:
                outData[count] = {}
            for edge in root.iter("edge"):
                if edge.attrib["id"] not in outData[count]:
                    outData[count][edge.attrib["id"]] = {}
                for param in paramList:
                    if self.ignoreZeros == False:
                        outData[count][edge.attrib["id"]][param] = self.storeAttribute(outData, param, edge)
                    else:
                        if "density" in edge.attrib:
                            if float(edge.attrib["density"]) >= self.cutoff:
                                outData[count][edge.attrib["id"]][param] = self.storeAttribute(outData, param, edge)
            count =+ 1
            # outData = {edgeID: {laneID: {dataType1: value, dataType2: value...}}}
        return outData

    def storeAttribute(self, outData, param, edge):
        if param in edge.attrib:
            data = float("{:.2f}".format(float(edge.attrib[param])))
        else:
            if param == "flow":
                data = float("{:.2f}".format(float(edge.attrib["entered"]) * 3600.00 / float(self.sampleFreq)))
            else:
                data = 0
        return data

    # Function to find roads with 0 entered
    def findEmptyRoads(self):
        if self.ignoreZeros == False:
            self.emptyRoads = []
            busyRoads = []
            roads = []
            for interval in self.data:
                for edge in self.data[interval]:
                    if edge not in roads:
                        try:
                            roads.append(edge)
                        except:
                            roads = edge
                    if self.data[interval][edge]["density"] >= self.cutoff:
                        try:
                            busyRoads.append(edge)
                        except:
                            busyRoads = edge
            for road in roads:
                if road not in busyRoads:
                    try:
                        self.emptyRoads.append(road)
                    except:
                        self.emptyRoads = road
        else:
            self.emptyRoads = None
        return self.emptyRoads

    #################################################################################
    #
    # Functions for parameter calculations
    #
    #################################################################################
    # Function to calculate mean density
    def paramMean(self, key):
        count = 0
        param = 0
        for interval in self.data:
            for edge in self.data[interval]:
                if key in self.data[interval][edge]:
                    count += 1
                    param += self.data[interval][edge][key]
        if count != 0:
            mean = float("{:.2f}".format(param/count))
        else:
            mean = 0
        return mean
    # Function to calculate standard deviation of density
    def paramStdDev(self, key):
        count = 0
        difference = 0
        for interval in self.data:
            for edge in self.data[interval]:
                if key in self.data[interval][edge]:
                    count += 1
                    difference += abs(self.data[interval][edge][key] - self.mean[key])
        if count != 0:
            stdDev = float("{:.2f}".format(math.sqrt(difference/count)))
        else:
            stdDev = 0
        return stdDev
    # Function to calculate minimum density
    def paramMin(self, key):
        minimum = None
        for interval in self.data:
            for edge in self.data[interval]:
                if key in self.data[interval][edge]:
                    param = self.data[interval][edge][key]
                    if minimum is None:
                        minimum = param
                    elif param < minimum:
                        minimum = param
        float("{:.2f}".format(float(minimum)))
        return minimum
    # Function to calculate maximum density
    def paramMax(self, key):
        maximum = None
        for interval in self.data:
            for edge in self.data[interval]:
                if key in self.data[interval][edge]:
                    param = self.data[interval][edge][key]
                    if maximum is None:
                        maximum = param
                    elif param > maximum:
                        maximum = param
        float("{:.2f}".format(float(maximum)))
        return maximum
    # Function to calculate first quartile
    def paramQuart1(self, key):
        params = self.paramList[key]
        params.sort()
        if params:
            Q1 = np.quantile(params, .25)
        else:
            Q1 = 0
        float("{:.2f}".format(float(Q1)))
        return Q1
    # Function to calculate third quartile
    def paramQuart3(self, key):
        params = self.paramList[key]
        params.sort()
        if params:
            Q3 = np.quantile(params, .75)
        else:
            Q3 = 0
        float("{:.2f}".format(float(Q3)))
        return Q3
    # Function to calculate median
    def paramMedian(self, key):
        params = self.paramList[key]
        params.sort()
        if params:
            med = np.quantile(params, .50)
        else:
            med = 0
        float("{:.2f}".format(float(med)))
        return med





