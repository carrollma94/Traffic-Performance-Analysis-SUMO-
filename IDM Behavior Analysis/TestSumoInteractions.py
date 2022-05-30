import pandas as pd
import os
from SumoConnect import *
from PlotIt import *
import numpy as np
from SensitivityAnalysis import *
from GeneticAlgorithm import *
from PlotGA import *
from RandomSimulations import *
from IDMBehaviorReplication import *

def test():
    ##############################################################################
    # Simulation Location with configuration files needed to run SUMO (parent directory)
    simLoc = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    # File name of sumo configuration file
    cfgFileName = "osm.sumocfg"
    # File name of route file
    rouFileName = "routes.rou.xml"
    # Output file name
    outFileName = "main.output.xml"
    # Additional file name
    addFileName = "additional.xml"
    # Collision file name
    collFileName = "collisions.output.xml"
    # Traffic scale for simulation
    scale = "1"
    # Sample frequency for output data
    freq = "100"
    # Set default values for IDM taken from SUMO documentation
    ###############################################################################
    defParams = {}
    # Minimum gap between following and lead car (meters)
    defParams["minGap"] = 2.5
    # Maximum acceleration of car (m/s^2)
    defParams["accel"] = 2.6
    # Maximum deceleration of car (m/s^2)
    defParams["decel"] = 4.5
    # Emergency deceleration of car (m/s^2)
    defParams["emergencyDecel"] = 9
    # The driver's desired (minimum) time headway
    defParams["tau"] = 1
    # acceleration exponent
    defParams["delta"] = 4


    # Minimum and maximum limits for input CF parameters using multipliers for 50% and 200%
    ###############################################################################
    maxMultiplier = 2.0
    minMultiplier = 0.5
    paramLimits = {}
    # Minimum gap between following and lead car (meters)
    paramLimits["minGap"] = np.array([defParams["minGap"]*minMultiplier, defParams["minGap"]*maxMultiplier])
    # Maximum acceleration of car (m/s^2)
    paramLimits["accel"] = np.array([defParams["accel"]*minMultiplier, defParams["accel"]*maxMultiplier])
    # Maximum deceleration of car (m/s^2)
    paramLimits["decel"] = np.array([defParams["decel"]*minMultiplier, defParams["decel"]*maxMultiplier])
    # Emergency deceleration of car (m/s^2)
    #paramLimits["emergencyDecel"] = np.array([1.5, 10])
    # The driver's desired (minimum) time headway
    paramLimits["tau"] = np.array([defParams["tau"]*minMultiplier, defParams["tau"]*maxMultiplier])
    # acceleration exponent
    paramLimits["delta"] = np.array([defParams["delta"]*minMultiplier, defParams["delta"]*maxMultiplier])
    '''
    # Alter Minimum and maximum limits for tau and accel CF parameters using decision tree constraints 100% IDM
    ###############################################################################
    # Maximum acceleration of car (m/s^2)
    paramLimits["accel"] = np.array([4.585, defParams["accel"]*maxMultiplier])
    # The driver's desired (minimum) time headway
    paramLimits["tau"] = np.array([0.775, defParams["tau"]*maxMultiplier])
    '''
    # Organize input data to run Sensitivity Analysis and Genetic Algorithm
    #################################################################################
    # Create X matrix to combine input parameter limits
    X = np.array([defParams["minGap"], defParams["accel"], defParams["decel"],\
                defParams["emergencyDecel"], defParams["tau"], defParams["delta"]])
    '''
    #
    # create csv of mean density and flow for edge in a simulation
    #
    setVtype(simLoc, rouFileName, idmParams=X, idmRatio=0.0)
    runSUMO(simLoc, cfgFileName, collFileName=collFileName, addFileName=addFileName, begin='0', end='-1', scale='1', noWarnings="true")
    data = outputData(simLoc, outFileName, ignoreZeros=False, cutoff=0.5,\
        paramList = ["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered", "flow", "collisions"],\
        collFileName=None)
    #print(data.data)
    df = pd.DataFrame(columns=["edge", "flow", "density"], index=None)
    for interval in data.data:
        for edge in data.data[interval]:
                flow = data.data[interval][edge]['flow']
                density = data.data[interval][edge]['density']
                df = df.append({"edge": edge, "flow": flow, "density": density}, ignore_index=True)
    print(df)
    df.to_csv(simLoc + "/edge_data_IDM0.0.csv")
    '''
    '''
    # create CSV of random data for alterations of car model parameters
    RandomSimulations(limits=paramLimits, iterations=1000, simLoc=simLoc, cfgFileName=cfgFileName, rouFileName=rouFileName,
                 outFileName=outFileName,collFileName=collFileName, addFileName=addFileName, ratios=[1], scales=[1])
    '''

    '''
    # Change all data to 2 decimal places in the csv files within a specified file location
    twoDecimalPlaces(simLoc + '/IDM Behavior Analysis/GeneticAlgorithm')
    '''
    '''
    # Example of how to Generate combined fitness for default parameter simulation
    idmParams = np.array([defParams["minGap"], defParams["accel"], defParams["decel"], defParams["emergencyDecel"], \
                  defParams["tau"], defParams["delta"]])

    setVtype(simLoc, rouFileName, idmParams, idmRatio=1)
    runSUMO(simLoc, cfgFileName, collFileName, addFileName, begin='0', end='-1', scale='1', noWarnings="true")
    data = outputData(simLoc, outFileName, ignoreZeros=True, collFileName=collFileName)

    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/density'
    fileName = 'density_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params)
    print(stat_data)

    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/flow'
    fileName = 'flow_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/speed'
    fileName = 'speed_1000.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/waitingTime'
    fileName = 'waitingTime.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    performance = {"speed":data.mean["speed"],"flow":data.mean["flow"],'waitingTime':data.mean['waitingTime'],'density':data.mean['density']}
    print(performance)
    fitness = fitnessZScore(performance, 0, stat_data)
    print(fitness)
    df = pd.DataFrame([(defParams["minGap"],defParams["accel"], defParams["decel"],\
                   defParams["emergencyDecel"], defParams["tau"], defParams["delta"],\
                   data.mean['density'],data.mean['sampledSeconds'],data.mean['waitingTime'],\
                   data.mean['occupancy'],data.mean['timeLoss'],data.mean['speed'],\
                   data.mean['entered'],data.mean['flow'],data.mean['collisions'],fitness,1,"Combined")],\
                 columns=['minGap','accel','decel','emergencyDecel','tau','delta','density',\
                          'sampledSeconds','waitingTime','occupancy','timeLoss','speed','entered',\
                          'flow','collisions','fitness','iterations','type'])
    df.to_csv('C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/default fitness.csv', index=False)
    '''


    '''
    # Example of Plotting the density and flow correlations based on edges of a network for different penetration rates
    density = {}
    flow = {}
    for penRate in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]:
        # Set input parameters in xml file for SUMO
        setVtype(simLoc, rouFileName, X, idmRatio=penRate)
        # Run SUMO
        runSUMO(simLoc, cfgFileName, collFileName, addFileName, scale = scale)
        # Collect output data
        outData = outputData(simLoc, outFileName)
        density[penRate] = outData.paramList["density"]
        flow[penRate] = outData.paramList["flow"]

    myDir = simLoc + "/IDM Behavioral Analysis/Distributions/NetworkPenetration_1.0_curve_to_fit"

    PenetrationRatesPlot(density, flow, myDir, cutoff=1)
    '''

    '''
    # Example of how to run Sensitivity Analysis for multiple ratios and scales
    ratios = [1]
    scales = ["1.0"]
    for ratio in ratios:
        for scale in scales:
            outputFolderName = "Penetration Rate Analysis/ratio" + str(ratio) + "/scale_" + scale
            analysis = SensAnalys(paramLimits, defParams=defParams, \
                 outParamList =["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered", "flow", "collisions"], \
                 outFolderName=outputFolderName, \
                 simLoc=simLoc, \
                 cfgFileName=cfgFileName, \
                 rouFileName=rouFileName, \
                 outFileName=outFileName, \
                 addFileName=addFileName, \
                 collFileName=collFileName, \
                 scale = scale, \
                 dataPoints = 50,\
                 ignoreZeros = True,\
                 idmRatio=ratio)
            del(analysis)
    '''



    '''
    # Example of running sensitivity analysis
    SensitivityAnalysis = SensAnalys(paramLimits, defParams=defParams, \
         outParamList =["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered", "flow", "collisions"], \
         outFolderName="Density-Speed-Flow Analysis with Collisions_100", \
         simLoc=simLoc, \
         cfgFileName=cfgFileName, \
         rouFileName=rouFileName, \
         outFileName=outFileName, \
         addFileName=addFileName, \
         collFileName=collFileName, \
         scale = "1", \
         dataPoints = 101,\
         ignoreZeros = True,\
         idmRatio=1)
    
    '''
    '''
    # Examples of how to create statistical data from a GA output files
    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/density'
    fileName = 'density_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params)
    print(stat_data)

    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/flow'
    fileName = 'flow_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/speed'
    fileName = 'speed_1000.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/waitingTime'
    fileName = 'waitingTime.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)
    '''

    '''
    # Example of how to plot the IDM behavior model to show acceleration based on velocity inputs
    # NOTE:UNFINISHED, Results have not be validated
    idm_behavior_analysis(defParams, "Default IDM Behavior", [0,100])
    # Set values for IDM developed from Combined GA Fitness
    ###############################################################################
    idm_params = {}
    # Minimum gap between following and lead car (meters)
    idm_params["minGap"] = 4.05
    # Maximum acceleration of car (m/s^2)
    idm_params["accel"] = 5.58
    # Maximum deceleration of car (m/s^2)
    idm_params["decel"] = 4.67
    # Emergency deceleration of car (m/s^2)
    idm_params["emergencyDecel"] = 9
    # The driver's desired (minimum) time headway
    idm_params["tau"] = 0.93
    # acceleration exponent
    idm_params["delta"] = 5.84
    idm_behavior_analysis(idm_params, "Combined GA Solution IDM Behavior", [0, 100])
    '''


    # Example of how to run GA for combined model
    
    # Generate Stat Data from data set (ours was from a previously ran GA for combined fitness function)
    path = simLoc + '/IDM Behavior Analysis/GeneticAlgorithm/combined'
    fileName = 'combined.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params)
    print(stat_data)
    
    # Run GA
    for idmRatio in [0.25,0.5,0.75,1.0]:
        csvFileName = 'GA-EIDM-' + str(idmRatio) + '.csv'
        optomizeAllParameters(perfMeasure=params, simLoc=simLoc, csvFileName=csvFileName, \
                              rouFileName=rouFileName, cfgFileName=cfgFileName, \
                              paramLimits=paramLimits, defParams=defParams, \
                              idmRatio=idmRatio, collFileName=collFileName, addFileName=addFileName, \
                              begin='0', end='-1', scale='1', noWarnings="true", \
                              stat_data = stat_data)

    #fileName = 'GA-1.0IDM'
    # Plot the GA elites from CSV file that was created
    #plotFromCSV(path=simLoc + '/IDM Behavior Analysis/GeneticAlgorithm', fileName=csvFileName, perfParam = 'combined', increase=False, removeCollisions=True, plot=True)


    return

test()