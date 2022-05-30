import traci
import traci.constants as tc
import sumolib
import numpy as np
from SumoConnect import *
import os, sys
import matplotlib.pyplot as plt


def performanceAnalys(simLoc = "C:/Users/Matt/Sumo/Gville Test1/", netFileName = "osm.net.xml", cfgFileName = "osm.sumocfg",\
                      outFolderName = "performance_outputs/", sampleTime = 360, simulationTime = 3600, scale = 1, ignoreZeros = True):
    # Folder to save plots and screenshots
    folder = simLoc + outFolderName
    # array to store edge names
    netEdges = []
    # create dictionary for time step and data
    edgeData = {}

    # create path for sumo tools
    if 'SUMO_HOME' in os.environ:
        tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
        sys.path.append(tools)
    else:
        sys.exit("please declare environment variable 'SUMO_HOME'")

    # variables to run sumo through traci
    sumoBinary = "sumo-gui"
    cfgFile = simLoc + cfgFileName
    sumoCmd = [sumoBinary, "-c", cfgFile, "--start", "--scale", str(scale), "--quit-on-end"]

    # collect edge names using sumolib
    for edge in sumolib.xml.parse(simLoc + netFileName, ['edge']):
        netEdges.append(edge.id)
        edgeData[edge.id] = {}

    # start simulation using traci and set step
    traci.start(sumoCmd)
    step = 0

    # run simulation by step until simulation time reaches 3600
    while step < simulationTime + 1:
        traci.simulationStep()

        # check if step is divisible by sample time
        if step%sampleTime == 0:
            # For each edge in network get peformance data
            for edge in edgeData:
                edgeData[edge][step] = {}

                # Get density using traci
                vehNum = traci.edge.getLastStepVehicleNumber(edge)
                density = vehNum / traci.lane.getLength(edge + "_0") * 1000
                edgeData[edge][step]["density"] = float(density)
                #print("density: " + str(density))

                # Get travel time using traci
                travelTime = traci.edge.getTraveltime(edge)
                edgeData[edge][step]["travel_time"] = float(travelTime)
                #print("travel_time: " + str(travelTime))

                # Get mean speed using traci
                meanSpeed = traci.edge.getLastStepMeanSpeed(edge)
                edgeData[edge][step]["mean_speed"] = float(meanSpeed)
                #print("mean_speed: " + str(meanSpeed))

                # Get occupancy using traci
                occupancy = traci.edge.getLastStepOccupancy(edge)
                edgeData[edge][step]["occupancy"] = float(occupancy)
                #print("occupancy: " + str(occupancy))

                # Get waiting time using traci
                waitingTime = traci.edge.getWaitingTime(edge)
                edgeData[edge][step]["waiting_time"] = float(waitingTime)
                #print("waiting_time: " + str(waitingTime))

            traci.gui.screenshot(viewID="View #0", filename="screenshot_" + str(step) + ".png")

        step += 1

    traci.close(False)

    data = {}
    means = {}
    steps = []
    for edge in edgeData:
        for step in edgeData[edge]:
            steps.append(step)
            for dataType in edgeData[edge][step]:
                if dataType not in data:
                    data[dataType] = {}
                if step not in data[dataType]:
                    data[dataType][step] = []
                if ignoreZeros == True:
                    if edgeData[edge][step][dataType] > 0.0:
                        data[dataType][step].append(edgeData[edge][step][dataType])
                else:
                    data[dataType][step].append(edgeData[edge][step][dataType])
    for dataType in data:
        means[dataType] = []
        for step in data[dataType]:
            try:
                means[dataType].append(sum(data[dataType][step])/len(data[dataType][step]))
            except:
                means[dataType].append(0)
    #print(means)
    #print(data)

    for dataType in data:
        for step in data[dataType]:
            dir = folder + dataType
            try:
                xMax = float(max(data[dataType][step]))
            except:
                xMax = 0
            plt = histogram(dir, data[dataType][step], xLabel=dataType, title = dataType + " distribution " + str(step), xMax=xMax)
            plt.clf()
            plt.close()

    return

def checkDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return

def plot(dir, units, x, y, xLabel, yLabel, label, xMax, yMax, title):
    checkDir(dir)
    fileLoc = dir + "/" + title + ".png"
    plt.plot(x, y, label=label)
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    plt.ylim([0, yMax])
    plt.xlim([-0.1, xMax])
    plt.legend()
    plt.savefig(fileLoc, dpi=500, bbox_inches='tight', transparent="true")
    return plt

def add(dir, plt, x, y, label, yLabel, xMax, yMax, title, marker = False):
    checkDir(dir)
    fileLoc = dir + "/" + title + ".png"
    if marker == True:
        plt.plot(x, y, label=label, marker="o")
    else:
        plt.plot(x, y, label=label)
    plt.xlim([0, xMax])
    plt.ylim([0, yMax])
    plt.legend()
    plt.savefig(fileLoc, dpi = 500, bbox_inches='tight', transparent = "true")
    return plt

def histogram(dir, x, bins = 250, xLabel="", yLabel="", title="", setRange=False, xMin=-0, xMax=50):
    checkDir(dir)
    Name = dir + "/" + title + ".png"
    newX = []
    for value in x:
        newValue = float(value)
        if newValue <= xMax and newValue >= xMin:
            newX.append(newValue)
    x = newX

    fig, ax = plt.subplots(1, sharey=True, tight_layout=True)
    ax.set_title(title)
    ax.hist(x, bins=bins)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    if setRange == True:
        plt.xlim([xMin, xMax])
    plt.savefig(Name, dpi = 500, bbox_inches='tight', transparent = "true")
    return plt

performanceAnalys()