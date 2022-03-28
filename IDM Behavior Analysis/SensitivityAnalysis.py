'''
Purpose:
# Run sumo for parameter input values to determine sensitivity of parameter to desired outputs
# Create dictionary of lists for input and output values
# Save plots of input Parameter changes and output parameter results
Author: Matthew James Carroll
'''
import xml.etree.ElementTree as ET
from SumoConnect import *
from PlotIt import *
import numpy as np

# Sensitivity Analysis class to run SUMO, retrieve output data, and plot data
##########################################################################################
class SensAnalys():
    def __init__(self, paramLimits, defParams = None, \
               outParamList = ["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered", "flow", "collisions"], \
               outFolderName="output", \
               simLoc='C:\\Users\\Matt\\SUMO\\Gville Test1', \
               cfgFileName="osm.sumocfg", \
               rouFileName="routes.rou.xml", \
               outFileName="main.output.xml", \
               addFileName="additional.xml", \
               collFileName=None, \
               plot = False, \
               scale = "1", \
               dataPoints = 10,
               ignoreZeros = False,
               idmRatio = 1):
        print("Running Sensitivity Analysis...")
        # Set default values for IDM taken from SUMO documentation
        ###############################################################################
        if defParams == None:
            self.defParams = {}
            # Minimum gap between following and lead car (meters)
            self.defParams["minGap"] = 2.5
            # Maximum acceleration of car (m/s^2)
            self.defParams["accel"] = 2.9
            # Maximum deceleration of car (m/s^2)
            self.defParams["decel"] = 7.5
            # Emergency deceleration of car (m/s^2)
            self.defParams["emergencyDecel"] = 9.0
            # The driver's desired (minimum) time headway
            self.defParams["tau"] = 1.0
            # acceleration exponent
            self.defParams["delta"] = 4.0
        else:
            self.defParams = defParams

        # Redefine input variables as part of class
        ###############################################################################
        self.ignoreZeros = ignoreZeros
        self.idmRatio = idmRatio
        self.paramLimits = paramLimits
        self.outParamList = outParamList
        self.outFolderName = "SensitivityAnalysis\\" + outFolderName
        self.simLoc = simLoc
        self.cfgFileName = cfgFileName
        self.rouFileName = rouFileName
        self.outFileName = outFileName
        self.addFileName = addFileName
        self.collFileName = collFileName
        self.plot = plot
        self.scale = scale
        self.dataPoints = dataPoints

        # Run sumo and store output data of default params
        self.defParams = self.runDefParams()

        # Change min and max param data to evenly distributed list of data points
        ###################################################################################
        self.params = {}
        self.params = self.createDataPoints()
        # Create dictionary for output
        ###################################################################################
        self.outputDict = {}

        # Call function to create output dictionary of input and output data points
        ###################################################################################
        self.outputDict = self.runSensAnalys()
        print(self.outputDict)
        # Call myPlot class to save plots in output folder
        ###################################################################################


        self.plots = createPlots(self.outputDict, self.outFolderName, self.defParams, self.idmRatio, self.plot)
        del(self.plots)
    # Run SUMO with default parameters
    ################################################################################################
    def runDefParams(self):
        X = self.setParam()
        outputData = self.runIt(X)
        for outputParam in self.outParamList:
            self.defParams[outputParam] = outputData.mean[outputParam]
        return self.defParams

    # Function to create a data points distributed based on max and min value for a parameter and the desired data points
    ################################################################################################
    def createDataPoints(self):
        for param in self.paramLimits:
            increment = (self.paramLimits[param][1] - self.paramLimits[param][0]) / (self.dataPoints - 1)
            number = self.paramLimits[param][0]
            self.params[param] = []
            while number <= self.paramLimits[param][1]:
                self.params[param].append(float("{:.5f}".format(number)))
                number = number + increment
        return self.params

    # Function to run SUMO for each parameter change thgen put input and output data in a dictionary
    ########################################################################################
    def runSensAnalys(self):
        # Create dictionary for output data for each input param type
        for paramType in self.params:
            self.outputDict[paramType] = {}
            self.outputDict[paramType]["input"] = self.params[paramType]
            for outputParam in self.outParamList:
                self.outputDict[paramType][outputParam] = {}
        # Run SUMO for each parameter type and each parameter value in list
        for paramType in self.params:
            for param in self.params[paramType]:
                # Check what param type is being altered then call function to set parameters in "rou" file
                if paramType == 'minGap':
                    X = self.setParam(minGap=param)
                    print(paramType, param)
                elif paramType == 'accel':
                    X = self.setParam(accel=param)
                    print(paramType, param)
                elif paramType == 'decel':
                    X = self.setParam(decel=param)
                    print(paramType, param)
                elif paramType == 'emergencyDecel':
                    X = self.setParam(emergencyDecel=param)
                    print(paramType, param)
                elif paramType == 'tau':
                    X = self.setParam(tau=param)
                    print(paramType, param)
                elif paramType == 'delta':
                    X = self.setParam(delta=param)
                    print(paramType, param)
                elif paramType == 'stepping':
                    X = self.setParam(stepping=param)
                    print(paramType, param)
                outputData = self.runIt(X)
                print(outputData.mean)
                # Store mean of each output parameter
                for outputParam in self.outParamList:
                    if outputParam == "collisions":
                        try:
                            self.outputDict[paramType][outputParam]["mean"].append(outputData.mean[outputParam])
                        except:
                            self.outputDict[paramType][outputParam]["mean"] = []
                            self.outputDict[paramType][outputParam]["mean"].append(outputData.mean[outputParam])
                    else:
                        try:
                            self.outputDict[paramType][outputParam]["mean"].append(outputData.mean[outputParam])
                            self.outputDict[paramType][outputParam]["median"].append(outputData.median[outputParam])
                            self.outputDict[paramType][outputParam]["Q1"].append(outputData.Q1[outputParam])
                            self.outputDict[paramType][outputParam]["Q3"].append(outputData.Q3[outputParam])
                        except:
                            self.outputDict[paramType][outputParam]["mean"] = []
                            self.outputDict[paramType][outputParam]["median"] = []
                            self.outputDict[paramType][outputParam]["Q1"] = []
                            self.outputDict[paramType][outputParam]["Q3"] = []
                            self.outputDict[paramType][outputParam]["mean"].append(outputData.mean[outputParam])
                            self.outputDict[paramType][outputParam]["median"].append(outputData.median[outputParam])
                            self.outputDict[paramType][outputParam]["Q1"].append(outputData.Q1[outputParam])
                            self.outputDict[paramType][outputParam]["Q3"].append(outputData.Q3[outputParam])

        return self.outputDict

    # Function to change the input parameters into a list
    #################################################################################################
    def setParam(self, \
                 minGap=None, \
                 accel=None, \
                 decel=None, \
                 emergencyDecel=None, \
                 tau=None, \
                 delta=None, \
                 stepping=None):
        print("in setParam")
        if minGap == None:
            minGap = self.defParams["minGap"]
        if accel == None:
            accel = self.defParams["accel"]
        if decel == None:
            decel = self.defParams["decel"]
        if emergencyDecel == None:
            emergencyDecel = self.defParams["emergencyDecel"]
        if tau == None:
            tau = self.defParams["tau"]
        if delta == None:
            delta = self.defParams["delta"]
        X = np.array([minGap, accel, decel, emergencyDecel, tau, delta, stepping])
        return X

    # Function to Set vtype parameters, run SUMO, then retrieve output data
    ###################################################################################################
    def runIt(self, X):
        setVtype(self.simLoc, self.rouFileName, X, self.idmRatio)
        runSUMO(self.simLoc, self.cfgFileName, self.collFileName, self.addFileName, scale = self.scale)
        data = outputData(self.simLoc, self.outFileName, self.ignoreZeros, paramList=self.outParamList, collFileName=self.collFileName)
        return data

