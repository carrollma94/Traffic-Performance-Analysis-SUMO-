from SumoConnect import *
import os
import pandas as pd
import random

class RandomSimulations():
    def __init__(self, limits, iterations, simLoc, cfgFileName, rouFileName, outFileName,
                 collFileName = None, addFileName = None, ratios = [1], scales = [1]):
        self.limits = limits
        self.iterations = iterations
        self.simLoc = simLoc
        self.cfgFileName = cfgFileName
        self.rouFileName = rouFileName
        self.outFileName=outFileName
        self.collFileName = collFileName
        self.addFileName = addFileName
        self.ratios = ratios
        self.scales = scales
        self.runSimulations()

    def runSimulations(self):
        for ratio in self.ratios:
            for scale in self.scales:
                scale = str(scale)
                df = pd.DataFrame(columns=['minGap','accel','decel','emergencyDecel','tau'
                    ,'delta','density','sampledSeconds','waitingTime'
                    ,'occupancy','timeLoss','speed','entered','flow','collisions'])
                for iteration in range(0,self.iterations):

                    idmParams = []
                    idmParams.append(round(random.uniform(self.limits['minGap'][0], self.limits['minGap'][1]), 2))
                    idmParams.append(round(random.uniform(self.limits['accel'][0], self.limits['accel'][1]), 2))
                    idmParams.append(round(random.uniform(self.limits['decel'][0], self.limits['decel'][1]), 2))
                    idmParams.append(9.0)
                    idmParams.append(round(random.uniform(self.limits['tau'][0], self.limits['tau'][1]), 2))
                    idmParams.append(round(random.uniform(self.limits['delta'][0], self.limits['delta'][1]), 2))
                    setVtype(self.simLoc, self.rouFileName, idmParams, idmRatio=ratio)

                    # Run SUMO
                    runSUMO(self.simLoc, self.cfgFileName, self.collFileName, self.addFileName,
                            begin='0', end='-1', scale=scale,noWarnings="true")
                    # Import data into dictionary
                    data = outputData(self.simLoc, self.outFileName, ignoreZeros=True, cutoff=0.5,\
                    paramList = ["density", "sampledSeconds", "waitingTime", "occupancy", "timeLoss", "speed", "entered", "flow", "collisions"],\
                    collFileName=self.collFileName)

                    # convert dictionary to string of means
                    row = idmParams
                    row.append(data.mean['density'])
                    row.append(data.mean['sampledSeconds'])
                    row.append(data.mean['waitingTime'])
                    row.append(data.mean['occupancy'])
                    row.append(data.mean['timeLoss'])
                    row.append(data.mean['speed'])
                    row.append(data.mean['entered'])
                    row.append(data.mean['flow'])
                    row.append(data.mean['collisions'])

                    # Add data to df
                    df.loc[len(df)] = row

                #Save df as csv
                df.to_csv(self.simLoc + "\\Traffic Analysis\\Random Data\\Random Data_scale-" + scale + "_ratio-" + \
                          str(ratio) + "_iterations-" + str(self.iterations) + ".csv",
                          index=False)

        return