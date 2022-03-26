'''
PURPOSE:
This file is used to take the elite set of IDM parameters and
validate that the conditions are acceptable given the IDM behavior
AUTHOR:
Matthew Carroll
DATE:
1/18/2022
'''
from SumoConnect import *
import traci
import sumolib
import math
import pandas as pd
import os

# Class to start SUMO simulation
class validation_model:
    def __init__(self, config_path, csv_path):
        self.config_path = config_path
        self.csv_path = csv_path
        # TODO: open/create csv file and create pandas dataframe
        self.data = None
        start_sumo(self)
        # TODO: add method to get speed limit
        self.speed_limit = get_speed_limit()

    # Method to start/restart the simulation
    def start_sumo(self):
        # create path for sumo tools
        if 'SUMO_HOME' in os.environ:
            tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
            sys.path.append(tools)
        else:
            sys.exit("please declare environment variable 'SUMO_HOME'")
        # Create command to start SUMO
        sumoBinary = "sumo"
        sumoCmd = [sumoBinary, "-c", self.config_path, "--start"]
        # start simulation using traci and set step
        self.traci.start(sumoCmd)
        self.step = 0
        return

    # TODO: finish method to get speed limit
    def get_speed_limit():

        return self

    def create_df(self):
        # Check if csv exist, if not create empty df else make df from csv
        if not os.path.exists(self.csv_path):
            self.data = pd.DataFrame
        else:
            self.data = pd.read_csv(self.csv_path)
        return

    # TODO: Save important data to csv (vehicle speeds, gaps, etc.)
    def data_write(self):

        # TODO: iterate through the vehicles in simulation, grab data for each

        # TODO: write data to csv and save it
        return

    def driving_behavior(self, type, duration, speed_variation, duty_cycle, avg_speed, threshold = 0):

        # TODO: check if combination of speed_variation and avg_speed will be greater than threshold above the speed limit (throw error)

        if type.lower() in ["sine", "sin"]:
            # TODO: get current speed of vehicle to calculate instataneous phase for sin function for smooth transition
            phi = 0
            step = avg_speed
            omega = 2 * math.pi / duty_cycle
            A = speed_variation
            for i in range(duration-1):
                self.step += 1
                x = A * math.sin(omega * step - phi) + step
                # TODO: apply speed to lead vehicle for next step
                traci.simulationStep()
                # Save important data to csv (call function)
                csv_write(self)
        # TODO: Create equation to give vehicle sawtooth behavior
        elif type.lower() in ["saw", "sawtooth"]:
            for i in range(duration - 1):

                self.step += 1
        return

    def end_simulation(self):
        traci.close(False)
        return