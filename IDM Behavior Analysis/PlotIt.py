import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from matplotlib import colors
from matplotlib.ticker import PercentFormatter
from mpl_toolkits import mplot3d
import os
import shutil

class createPlots():
    def __init__(self, data, outFolderName, defParams, idmRatio):
        self.idmRatio = idmRatio
        self.data = data
        self.defParams = defParams
        self.yMax = {}
        self.yMax = self.get_yMax()
        self.xMax = {}
        self.xMax = self.get_xMax()
        self.plots = {}
        self.location = os.path.abspath(os.getcwd())
        self.outFolderName = outFolderName
        self.normalized = {}
        self.normalized = self.normalize()
        self.units = {"density": "(veh/km)", "sampledSeconds": "(s)", "waitingTime": "(s)", "occupancy": "(%)", \
                      "timeLoss": "(s)", "speed": "(m/s)", "entered": "(veh)", "flow": "(veh/hr)", "minGap": "(m)", \
                      "accel": "(m/s^2)", "decel": "(m/s^2)", "emergencyDecel": "(m/s^2)", "tau": "(s)", \
                      "delta": "(accel sensitivity)", "stepping": "(s)", "collisions": ""}

        self.clearOutFolder()
        self.checkDir(self.location)

        # Plot single and combined sensitivity analysis. Save plots in outFolderName
        self.plots = self.plotSingle()
        self.plots = self.plotCombined()

        #self.Plot3D()

        del (self.plots)

        # Call method to save data to csv files
        self.save_to_csv()

    ############################################################################################################
    #
    ############################################################################################################

    def save_to_csv(self):
        for paramType in self.data:
            df = pd.DataFrame()
            df[paramType] = self.data[paramType]["input"]
            for outputParam in self.data[paramType]:
                if outputParam != "input":
                    df[outputParam] = self.data[paramType][outputParam]["mean"]
            df.to_csv(self.location + "\\" + self.outFolderName + "\\" + paramType + ".csv", index=False)
        return

    def get_yMax(self):
        for param in self.data:
            for outData in self.data[param]:
                if outData != "input":
                    for dataType in self.data[param][outData]:
                        tempMax = max(self.data[param][outData][dataType])
                        try:
                            if self.yMax[outData] < tempMax:
                                self.yMax[outData] = tempMax + (tempMax * 0.1)
                        except:
                            self.yMax[outData] = tempMax  + (tempMax * 0.1)
        return self.yMax

    def get_xMax(self):
        for param in self.data:
            tempMax = max(self.data[param]["input"])
            tempMax = tempMax + (tempMax * 0.1)
            try:
                if self.xMax[param] < tempMax:
                    self.xMax[param] = tempMax
            except:
                self.xMax[param] = tempMax
        return self.xMax

    # Create new dictionary for combined plots. normalize data points from 0 to 1 based on min and max x values
    def normalize(self):
        for param in self.data:
            for outData in self.data[param]:
                if outData not in self.normalized:
                    self.normalized[outData] = {}
                if outData == "input":
                    dividor = self.defParams[param]
                    self.normalized[outData][param] = []
                    for data in self.data[param][outData]:
                        self.normalized[outData][param].append(float("{:.2f}".format((data) / dividor)))
                else:
                    self.normalized[outData][param] = self.data[param][outData]["mean"]
        return self.normalized

    def clearOutFolder(self):
        folder = self.location + "\\" + self.outFolderName
        if os.path.exists(folder):
            shutil.rmtree(folder)
        return

    #
    def plotSingle(self):
        idmRatio = str(self.idmRatio)
        for param in self.data:
            self.plots[param] = {}
            for outData in self.data[param]:
                if outData != "input":
                    title = "Traffic Data Correlation(" + param + " - " + outData + ") IDM-" + idmRatio
                    for dataType in self.data[param][outData]:
                        try:
                            self.plots[param][outData] = self.add(self.plots[param][outData], \
                                                                  self.data[param]["input"], \
                                                                  self.data[param][outData][dataType], \
                                                                  dataType, \
                                                                  outData, \
                                                                  xMax=self.xMax[param], \
                                                                  yMax=self.yMax[outData], \
                                                                  title=title)
                        except:
                            self.plots[param][outData] = self.plot(self.data[param]["input"], \
                                                                   self.data[param][outData][dataType], \
                                                                   param, \
                                                                   outData, \
                                                                   dataType, \
                                                                   xMax=self.xMax[param], \
                                                                   yMax=self.yMax[outData], \
                                                                   title=title)
                            self.plots[param][outData] = self.add(self.plots[param][outData], \
                                                                 self.defParams[param], \
                                                                 self.defParams[outData], \
                                                                 "Default " + param, \
                                                                 outData, \
                                                                 xMax=self.xMax[param], \
                                                                 yMax=self.yMax[outData], \
                                                                 title=title, \
                                                                 marker=True)
                    plt.clf()
                    plt.close()
        return self.plots

    def plotCombined(self):
        idmRatio = str(self.idmRatio)
        maxX = 0
        for outData in self.normalized:
            if outData != "input":
                for param in self.normalized[outData]:
                    title = "Sensitivity Analysis of Traffic " + outData + " IDM-" + idmRatio
                    if maxX < self.xMax[param]/self.defParams[param]:
                        maxX = self.xMax[param]/self.defParams[param]
                    try:
                        self.plots[outData] = self.add(self.plots[outData], \
                                                       self.normalized["input"][param], \
                                                       self.normalized[outData][param], \
                                                       param, \
                                                       outData, \
                                                       xMax=maxX, \
                                                       yMax=self.yMax[outData], \
                                                       title=title, \
                                                       addXLabel = False)
                    except:
                        self.plots[outData] = self.plot(self.normalized["input"][param], \
                                                      self.normalized[outData][param], \
                                                      param, \
                                                      outData, \
                                                      param, \
                                                      xMax=maxX, \
                                                      yMax=self.yMax[outData], \
                                                      title=title, \
                                                      addXLabel = False)
            plt.clf()
            plt.close()
        return self.plots

    def checkDir(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)
        return

    def plot(self, x, y, xLabel, yLabel, label, xMax, yMax, title, addXLabel = True):
        dir = self.location + "\\" + self.outFolderName + "\\" + yLabel
        self.checkDir(dir)
        fileLoc = dir + "\\" + title + ".png"
        plt.plot(x, y, label=label)
        plt.title(title)
        if addXLabel == True:
            plt.xlabel(xLabel + self.units[xLabel])
        else:
            plt.xlabel("Ratio of Default Parameters")
        plt.ylabel(yLabel + self.units[yLabel])
        plt.ylim([0, yMax])
        plt.xlim([-0.1, xMax])
        plt.legend()
        plt.savefig(fileLoc, dpi = 500, bbox_inches='tight', transparent = "true")
        return plt

    def add(self, plt, x, y, label, yLabel, xMax, yMax, title, marker = False):
        dir = self.location + "\\" + self.outFolderName + "\\" + yLabel
        self.checkDir(dir)
        fileLoc = dir + "\\" + title + ".png"
        if marker == True:
            plt.plot(x, y, label=label, marker="o")
        else:
            plt.plot(x, y, label=label)
        plt.xlim([-0.1, xMax])
        plt.ylim([0, yMax])
        plt.legend()
        plt.savefig(fileLoc, dpi = 500, bbox_inches='tight', transparent = "true")
        return plt

    def Plot3D(self):
        for param in self.data:
            dir = self.location + "\\" + self.outFolderName + "\\3D Plots"
            self.checkDir(dir)
            title = "3D Plot Correlation ("  + param + "-Flow-Density)"
            fileLoc = dir + "\\" + title + ".png"
            fig = plt.figure()
            ax = plt.axes(projection='3d')
            x = np.array(self.data[param]["density"]["mean"])
            y = np.array(self.data[param]["input"])
            z = np.array(self.data[param]["flow"]["mean"])
            ax.scatter3D(x, y, z);
            '''
            #
            # Code for Mesh (UNFINISHED)
            ##################################
            X, Y, Z = np.meshgrid(x, y, z)
            print(self.data[param]["density"]["mean"])
            print(self.data[param]["input"])
            dim1 = int(max(self.data[param]["density"]["mean"]))
            dim2 = int(max(self.data[param]["input"]))
            print(dim1)
            print(dim2)
            X = np.reshape(x, (dim1, dim2))
            Y = np.reshape(y, (dim1, dim2))
            Z = np.reshape(z, (dim1, dim2))
            p = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap='viridis', edgecolor='none')
            fig.colorbar(p, ax=ax)
            '''
            plt.title(title)
            ax.set_xlabel("Density")
            ax.set_ylabel(param)
            ax.set_zlabel("Flow");
            plt.savefig(fileLoc, dpi=500, bbox_inches='tight', transparent="true")
            plt.clf()
            plt.close()
        return

class PenetrationRatesPlot():
    def __init__(self, density, flow, myDir, cutoff=1):
        self.xLabel = "Density (veh/km)"
        self.yLabel = "Flow (veh/hr)"
        self.title = "Flow and Density Correlation for Edges in Network"
        clearOutFolder(myDir)
        if len(density) > 1:
            self.pltCombined = True
        else:
            self.pltCombined = False
        densMax = 0
        flowMax = 0
        for penRate in density:
            tempMax = np.quantile(density[penRate], cutoff)
            if tempMax > densMax:
                densMax = tempMax
        for penRate in flow:
            tempMax = np.quantile(flow[penRate], cutoff)
            if tempMax > flowMax:
                flowMax = tempMax
        for penRate in density:
            x = density[penRate]
            y = flow[penRate]
            penetration = str(penRate*100)
            label = " " + penetration + "% Penetration"
            title = self.title + label
            myPlot = plot(x, y, myDir, self.xLabel, self.yLabel, title, densMax, flowMax)
            #myPlot = logFit(myPlot, x, y, myDir, title, densMax, flowMax)
            myPlot.clf()
            myPlot.close()
        for penRate in density:
            x = density[penRate]
            y = flow[penRate]
            penetration = str(penRate * 100)
            label = " " + penetration + "% Penetration"
            title = self.title + label
            if self.pltCombined == True:
                if penRate <= 0:
                    combinedPlot = plot(x, y, myDir, self.xLabel, self.yLabel, self.title, densMax, flowMax, label=label)
                else:
                    combinedPlot = add(combinedPlot, x, y, myDir, label, self.title)
        try:
            combinedPlot.clf()
            combinedPlot.close()
        except:
            print("ONLY ONE PENETRATION RATE OR COMBINED PLOT = FALSE")

def clearOutFolder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    return

def checkDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)
    return

def plot(x, y, myDir, xLabel, yLabel, title, xMax, yMax, label=None):
    checkDir(myDir)
    fileLoc = myDir + "\\" + title + ".png"
    if label != None:
        plt.plot(x, y, 'o', label=label, markersize=1)
        plt.legend()
    else:
        plt.plot(x, y, 'o', markersize=1)
    plt.title(title)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    #plt.xlim([0, xMax])
    #plt.ylim([0, yMax])
    plt.savefig(fileLoc, dpi = 500, bbox_inches='tight', transparent = "true")
    return plt

def logFit(plt, x, y, myDir, title, xMax, yMax):
    checkDir(myDir)
    fileLoc = myDir + "\\" + title + ".png"
    plt.xlim([0, xMax])
    plt.ylim([0, yMax])
    delete = []
    for idx, item in enumerate(x):
        print(item)
        if item <= 0:
            print(idx)
            delete.append(idx)
    for idx in reversed(delete):
        del x[idx]
        del y[idx]
    print(x)
    print(y)
    x_data = np.array(x)
    y_data = np.array(y)
    log_x = np.log10(x_data)
    #log_y = np.log(y_data)
    curve_fit = np.polyfit(log_x, y_data, 1)
    new_log_y = curve_fit[0] * log_x + curve_fit[1]
    plt.plot(x_data, new_log_y)
    plt.savefig(fileLoc, dpi=500, bbox_inches='tight', transparent="true")
    return plt

def add(plt, x, y, dir, label, title):
    checkDir(dir)
    fileLoc = dir + "\\" + title + ".png"
    plt.plot(x, y, 'o', label=label, markersize=1)
    plt.legend()
    plt.savefig(fileLoc, dpi = 500, bbox_inches='tight', transparent = "true")
    return plt

def histogram(x, bins = 100, xLabel="", yLabel="", title="", setRange=False, xMin=-0, xMax=50, Name="", location=""):
    Name = location + Name + ".png"
    newX = []
    for value in x:
        if value <= xMax and value >= xMin:
            newX.append(value)
    x = newX

    fig, ax = plt.subplots(1, sharey=True, tight_layout=True)
    ax.set_title(title)
    ax.hist(x, bins=bins)
    plt.xlabel(xLabel)
    plt.ylabel(yLabel)
    if setRange == True:
        plt.xlim([xMin, xMax])
    plt.savefig(Name, dpi = 500, bbox_inches='tight', transparent = "true")
    plt.clf()
    plt.close()
    return