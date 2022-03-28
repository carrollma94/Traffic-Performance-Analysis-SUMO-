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
    defParams["accel"] = 2.9
    # Maximum deceleration of car (m/s^2)
    defParams["decel"] = 7.5
    # Emergency deceleration of car (m/s^2)
    defParams["emergencyDecel"] = 9
    # The driver's desired (minimum) time headway
    defParams["tau"] = 1
    # acceleration exponent
    defParams["delta"] = 4

    maxMultiplier = 2.0
    minMultiplier = 0.5

    # Minimum and maximum limits for input CF parameters
    ###############################################################################
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

    # Organize input data to run Sensitivity Analysis and Genetic Algorithm
    #################################################################################
    # Create X matrix to combine input parameter limits
    X = np.array([defParams["minGap"], defParams["accel"], defParams["decel"],\
                defParams["emergencyDecel"], defParams["tau"], defParams["delta"]])



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
    # Test that random data can be created
    RandomSimulations(limits=paramLimits, iterations=1000, simLoc=simLoc, cfgFileName=cfgFileName, rouFileName=rouFileName,
                 outFileName=outFileName,collFileName=collFileName, addFileName=addFileName, ratios=[1], scales=[1])
    '''
    '''
    # Test sensitivity analysis
    outputFolderName = "Sensitivity Analysis Test"
    SensAnalys(paramLimits, defParams=defParams, \
               outParamList=["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered",
                             "flow", "collisions"], \
               outFolderName=outputFolderName, \
               simLoc=simLoc, \
               cfgFileName=cfgFileName, \
               rouFileName=rouFileName, \
               outFileName=outFileName, \
               addFileName=addFileName, \
               collFileName=collFileName, \
               scale='1', \
               dataPoints=10, \
               ignoreZeros=True, \
               idmRatio=1)
    '''
    '''
    # Change all data to 2 decimal places in the csv files within a specified file location
    twoDecimalPlaces('C:\\Users\\Matt\\Sumo\\Gville Test1\\Traffic Analysis\\GeneticAlgorithm')
    '''
    '''
    # Generate combnined fitness for default parameter simulation
    idmRatio = np.array([defParams["minGap"], defParams["accel"], defParams["decel"], defParams["emergencyDecel"], \
                  defParams["tau"], defParams["delta"]])

    setVtype(simLoc, rouFileName, idmRatio, idmRatio=1)
    runSUMO(simLoc, cfgFileName, collFileName, addFileName, begin='0', end='-1', scale='1', noWarnings="true")
    data = outputData(simLoc, outFileName, ignoreZeros=True, collFileName=collFileName)
    print(data.mean)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/density'
    fileName = 'density_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params)
    print(stat_data)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/flow'
    fileName = 'flow_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/speed'
    fileName = 'speed_1000.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/waitingTime'
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
    Plotting the density and flow correlations for different penetration rates
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


    myDir = simLoc + "\\Traffic Analysis\\Distributions\\NetworkPenetration_1.0_curve_to_fit"

    PenetrationRatesPlot(density, flow, myDir, cutoff=1)
    '''
    #histogram(density, bins= 100, xLabel="Density veh/km", yLabel="", title="Density Distribution", \
    #          xMin=0.01, xMax=100, Name="Density Distribution")
    #histogram(sampledSeconds, bins=100, xLabel="Sampled Seconds veh/s", yLabel="", title="Sampled Seconds Distribution", \
    #          xMin=0, xMax=100, Name="Sampled Seconds Distribution")
    #histogram(flow, bins=100, xLabel="Flow veh/hr", yLabel="", title="Flow Distribution", \
    #          xMin=0, xMax=100, Name="Flow Distribution")

    # Run sensitivty analysis
    #########################################################################################
    #SensitivityAnalysis = SensAnalys(paramLimits, defParams=defParams, \
    #     outParamList =["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered", "flow"], \
    #     outFolderName="output_8_18_21", \
    #     simLoc=simLoc, \
    #     cfgFileName=cfgFileName, \
    #     rouFileName=rouFileName, \
    #     outFileName=outFileName, \
    #     addFileName=addFileName, \
    #     collFileName=collFileName, \
    #     scale = "1", \
    #     dataPoints = 11,
    #     ignoreZeros = False)


    ratios = [0.25,0.50,0.75,1.0]
    scales = ["0.5","1.0","2.0"]
    for ratio in ratios:
        for scale in scales:
            outputFolderName = "Penetration Rate Analysis FINAL\\ratio" + str(ratio) + "\\scale_" + scale
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

    #print("Density:", density)    #print("Flow:", flow)
    #print("Entered:", entered)
    #print("Sampled Seconds:", sampledSeconds)
    #print("Mean:", outData.mean)
    #print("Maximum:", outData.maximum)
    '''
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
    

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/density'
    fileName = 'density_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params)
    print(stat_data)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/flow'
    fileName = 'flow_500.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/speed'
    fileName = 'speed_1000.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/waitingTime'
    fileName = 'waitingTime.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm/combined'
    fileName = 'combined.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params, stat_data)
    print(stat_data)

    optomizeAllParameters(perfMeasure=['waitingTime', 'speed', 'flow', 'density'], csvFileName='z_score_combined_1000_IDM_0.25_tau_lower_limit.csv', simLoc=simLoc, \
                          rouFileName=rouFileName, cfgFileName=cfgFileName, \
                          paramLimits=paramLimits, defParams=defParams, \
                          idmRatio=0.25, collFileName=collFileName, addFileName=addFileName, \
                          begin='0', end='-1', scale='1', noWarnings="true", \
                          stat_data = stat_data)

    optomizeAllParameters(perfMeasure=['waitingTime', 'speed', 'flow', 'density'], csvFileName='z_score_combined_1000_IDM_0.75_tau_lower_limit.csv', simLoc=simLoc, \
                          rouFileName=rouFileName, cfgFileName=cfgFileName, \
                          paramLimits=paramLimits, defParams=defParams, \
                          idmRatio=0.75, collFileName=collFileName, addFileName=addFileName, \
                          begin='0', end='-1', scale='1', noWarnings="true", \
                          stat_data = stat_data)
    
    path = 'C:/Users/Matt/Sumo/Gville Test1/Traffic Analysis/GeneticAlgorithm'
    fileName = 'All_except_combined.csv'
    params = ['waitingTime', 'speed', 'flow', 'density']
    stat_data = GenerateStats(path, fileName, params)
    print(stat_data)
    '''

    return

test()