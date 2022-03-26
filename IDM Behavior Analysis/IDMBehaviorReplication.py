import pandas as pd
import os
from mpl_toolkits import mplot3d
import numpy as np
import matplotlib.pyplot as plt
import math

class idm_behavior_analysis():
    '''
    Purpose: Creates mesh plot of acceleration values based
    on idm parameters and limits of velocity changes
    :param idm_params: dictionary of all IDM params
    key=parameter name => value
    :param speed_limits: list containing the minimum
    and maximum speeds
    '''
    def __init__(self, idm_params, plot_name, speed_limits = [0,100]):
        self.idm_params=idm_params
        self.file_location = os.getcwd() + "/IDM Behavior Plots/" + plot_name
        # create linspace for both velocity inputs
        self.x = np.linspace(speed_limits[0], speed_limits[1], speed_limits[1] * 10)
        self.y = np.linspace(speed_limits[0], speed_limits[1], speed_limits[1] * 10)
        self.v_max = speed_limits[1]
        # create meshgrid for the maximum velocity (v_max) and the current velocity (v_0)
        self.v, self.v_des = np.meshgrid(self.x, self.y)
        self.equation()
        self.create_plot()
        self.create_csv()

    def equation(self):
        # Implement IDM behavior model equation to calculate the acceleration
        self.acceleration = self.idm_params['accel']*(1-(self.v/self.v_max)**self.idm_params['delta']-((self.idm_params['minGap'] + self.idm_params['tau'] * self.v \
                        + (self.v*(self.v-self.v_des))/(2*math.sqrt(self.idm_params['accel']*self.idm_params['decel'])))/self.idm_params['minGap'])**2)
        self.acceleration = np.where(self.acceleration < -self.idm_params['emergencyDecel'], -self.idm_params['emergencyDecel'], self.acceleration)
        return

    def create_plot(self):
        fig = plt.figure()
        ax = plt.axes(projection='3d')
        ax.contour3D(self.v, self.v_des, self.acceleration, 50, cmap='binary')
        ax.set_xlabel('IDM Velocity')
        ax.set_ylabel('Desired Velocity')
        ax.set_zlabel('Acceleration')
        fig.savefig(self.file_location)
        return

    def create_csv(self):
        #TODO: add method to create csv, may be unnecessary
        return

