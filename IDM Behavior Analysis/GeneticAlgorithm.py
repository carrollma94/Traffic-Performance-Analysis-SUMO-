'''
Purpose:
This program is used to find optimal parameters for a car following model using SUMO traffic simulation software.
Upper and lower bound limits are set for the parameters of an Intelligent Driving Model (IDM)
Genetetic Algorithm is used to alter parameters and insert them into route files of a simulation directory
SUMO is ran where the output traffic density and collision counts are minimized through a fitness function
Results are saved as CSV and analyze graphically

Author: Matthew James Carroll
Date: 6/9/2021
'''
import numpy as np
import os
import shutil
import pandas as pd
from SumoConnect import *
from geneticalgorithm import geneticalgorithm as ga


def clearOutFolder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    return

def deleteFile(file):
    if os.path.exists(file):
        os.remove(file)
    return

def checkDir(myDir):
    if not os.path.exists(myDir):
        os.makedirs(myDir)
    return

# Function to find optimal parameters for car following behavior of intelligent driver model (IDM)
# Input parameters: simLoc (location of simulation files) and varbound (matrix of car following parameters with min and max values)

def optomizeAllParameters(perfMeasure, csvFileName, simLoc, rouFileName, cfgFileName, paramLimits, defParams, \
                          outFileName="main.output.xml", idmRatio=1, collFileName=None, addFileName=None, begin='0', \
                          end='-1', scale='1', noWarnings="true", stat_data = {}, weight = {}):
    # Set stat_datas for density and collision
    if weight == {}:
        weight["density"] = 1
        weight["flow"] = 1
        weight["speed"] = 1
        weight["waitingTime"] = 1

    # Add data to CSV files
    # Get the current working directory
    cwd = os.getcwd()
    if type(perfMeasure) is list:
        myDir = cwd + "/GeneticAlgorithm/combined"
    else:
        myDir = cwd + "/GeneticAlgorithm/" + perfMeasure
    checkDir(myDir)
    csvFile = myDir + "/" + csvFileName

    # Calculate fitness function
    def fitnessFuncDec(performance, collisions):
        if collisions == 0:
            fitness = performance[perf]
        elif collisions > 0:
            fitness = 1
        return fitness

    # Calculate fitness function
    def fitnessFuncInc(performance, collisions):
        if collisions == 0:
            fitness = 1/performance[perf]
        elif collisions > 0:
            fitness = 1
        return fitness

    def fitnessNormalize(performance, collisions, stat_data):
        if collisions == 0:
            fitness = 0
            for perf in performance:
                perfMax = stat_data[perf][1]
                perfMin = stat_data[perf][0]
                if perf in ['speed', 'flow']:
                    fitness = fitness + weight[perf]*((1/len(performance))*((perfMax-perfMin)-(performance[perf]-perfMin))/(perfMax-perfMin))
                elif perf in ['waitingTime', 'density']:
                    fitness = fitness + weight[perf]*((1/len(performance))*(performance[perf]-perfMin)/(perfMax-perfMin))
        elif collisions > 0:
            fitness = 1
        return fitness

    def fitnessZScore(performance, collisions, stat_data):
        if collisions == 0:
            fitness = 0
            for perf in performance:
                perfMean = stat_data[perf][2]
                perfSTD = stat_data[perf][3]
                if perf in ['speed', 'flow']:
                    newFit = weight[perf]*((1/len(performance))*(perfMean-performance[perf])/(perfSTD))
                    fitness = fitness + newFit
                elif perf in ['waitingTime', 'density']:
                    newFit = weight[perf]*((1/len(performance))*(performance[perf]-perfMean)/(perfSTD))
                    fitness = fitness + newFit
        elif collisions > 0:
            fitness = 4
        return fitness

    def f(X):
        X = np.insert(X, 3, defParams["emergencyDecel"])
        X = np.around(X, 2)
        # Call function to insert parameters into vtype of *.rou.xml
        setVtype(simLoc, rouFileName, X, idmRatio)
        # Call function to run Sumo and generate output xml files
        runSUMO(simLoc, cfgFileName, collFileName, addFileName, begin, end, scale, noWarnings)

        # Call function to retrieve output data
        data = outputData(simLoc, outFileName, ignoreZeros=True, cutoff=0.5,\
        paramList=paramList, collFileName=collFileName)

        columns = ["minGap", "accel", "decel", "emergencyDecel", "tau", "delta", \
                   "density", "sampledSeconds", "waitingTime", \
                   "occupancy", "timeLoss", "speed", "entered", \
                   "flow", "collisions", "fitness"]

        # Check if CSV already exists, if so open it, otherwise create empty dataframe
        if os.path.isfile(csvFile):
            csvData = pd.read_csv(csvFile)
        else:
            csvData = pd.DataFrame(columns=columns)

        # Call function to calcualte collision value to be used
        collisions = data.mean["collisions"]

        # Call function to grab output performance measure value to be used

        # Call fitness function
        if type(perfMeasure) is list:
            performance = {}
            for perf in perfMeasure:
                performance[perf] = data.mean[perf]
            #fitness = fitnessNormalize(performance, collisions, stat_data)
            fitness = fitnessZScore(performance, collisions, stat_data)
        else:
            performance = data.mean[perfMeasure]
            if perfMeasure in ["density", 'waitingTime']:
                fitness = fitnessFuncDec(performance, collisions)
            elif perfMeasure in ["flow", "speed"]:
                fitness = 1/fitnessFuncInc(performance, collisions)
        row = X
        for param in paramList:
            row = np.append(row, data.mean[param])
        row = np.append(row, np.around(fitness, 2))
        print(row)
        csvData = csvData.append(pd.DataFrame([row], columns=columns), ignore_index = False)
        # Delete old CSV file then write new CSV file
        # deleteFile(csvFile)
        csvData.to_csv(csvFile, index=False)
        return fitness

    # List of parameters to add to CSV and grab from SUMO output file
    paramList = ["density", "sampledSeconds", "waitingTime", "occupancy", \
                 "timeLoss", "speed", "entered", "flow", "collisions"]

    varbound = np.array([paramLimits["minGap"], paramLimits["accel"], paramLimits["decel"], \
                  paramLimits["tau"], paramLimits["delta"]])

    # Set GA parameters
    algorithm_param = {'max_num_iteration': 500, \
                       'population_size': 10, \
                       'mutation_probability': 0.5, \
                       'elit_ratio': .1, \
                       'crossover_probability': 0.5, \
                       'parents_portion': .1, \
                       'crossover_type': 'uniform', \
                       'max_iteration_without_improv': None}

    model = ga(function=f, dimension=len(varbound), variable_type='real', variable_boundaries=varbound, function_timeout=6000, algorithm_parameters=algorithm_param)

    model.run()
    convergence = model.report
    output = model.output_dict
    optimalParam = output['variable']
    optimalFitness = output['function']


    return convergence, optimalParam, optimalFitness

def fitnessZScore(performance, collisions, stat_data, weight={}):
    if weight == {}:
        weight["density"] = 1
        weight["flow"] = 1
        weight["speed"] = 1
        weight["waitingTime"] = 1
    if collisions == 0:
        fitness = 0
        for perf in performance:
            perfMean = stat_data[perf][2]
            perfSTD = stat_data[perf][3]
            if perf in ['speed', 'flow']:
                newFit = weight[perf]*((1/len(performance))*(perfMean-performance[perf])/(perfSTD))
                fitness = fitness + newFit
            elif perf in ['waitingTime', 'density']:
                newFit = weight[perf]*((1/len(performance))*(performance[perf]-perfMean)/(perfSTD))
                fitness = fitness + newFit
    elif collisions > 0:
        fitness = 4
    return fitness