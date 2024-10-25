'''
Author: zhengyi cui
Date: 2024-10-17 20:09:44
LastEditTime: 2024-10-22 01:13:58
E-mail address: Zhengyi.Cui@uth.tmc.edu

Copyright (c) 2024 by ${Zhengyi.Cui@uth.tmc.edu}, All Rights Reserved. 

'''

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy.feature as cfeature
import os 
import pandas as pd 
import numpy as np
import metpy  
from netCDF4 import Dataset
from sklearn.datasets import make_classification
import re 
import xarray as xr


input_folder='./data/goes_16'
output_folder='./img/goes_16'


def calculate_degrees(file_id):
    
    # Read in GOES ABI fixed grid projection variables and constants
    x_coordinate_1d = file_id.variables['x'][:]  # E/W scanning angle in radians
    y_coordinate_1d = file_id.variables['y'][:]  # N/S elevation angle in radians
    projection_info = file_id.variables['goes_imager_projection']
    lon_origin = projection_info.longitude_of_projection_origin
    H = projection_info.perspective_point_height+projection_info.semi_major_axis
    r_eq = projection_info.semi_major_axis
    r_pol = projection_info.semi_minor_axis
    
    # Create 2D coordinate matrices from 1D coordinate vectors
    x_coordinate_2d, y_coordinate_2d = np.meshgrid(x_coordinate_1d, y_coordinate_1d)
    
    # Equations to calculate latitude and longitude
    lambda_0 = (lon_origin*np.pi)/180.0  
    a_var = np.power(np.sin(x_coordinate_2d),2.0) + (np.power(np.cos(x_coordinate_2d),2.0)*(np.power(np.cos(y_coordinate_2d),2.0)+(((r_eq*r_eq)/(r_pol*r_pol))*np.power(np.sin(y_coordinate_2d),2.0))))
    b_var = -2.0*H*np.cos(x_coordinate_2d)*np.cos(y_coordinate_2d)
    c_var = (H**2.0)-(r_eq**2.0)
    r_s = (-1.0*b_var - np.sqrt((b_var**2)-(4.0*a_var*c_var)))/(2.0*a_var)
    s_x = r_s*np.cos(x_coordinate_2d)*np.cos(y_coordinate_2d)
    s_y = - r_s*np.sin(x_coordinate_2d)
    s_z = r_s*np.cos(x_coordinate_2d)*np.sin(y_coordinate_2d)
    
    # Ignore numpy errors for sqrt of negative number; occurs for GOES-16 ABI CONUS sector data
    np.seterr(all='ignore')
    
    abi_lat = (180.0/np.pi)*(np.arctan(((r_eq*r_eq)/(r_pol*r_pol))*((s_z/np.sqrt(((H-s_x)*(H-s_x))+(s_y*s_y))))))
    abi_lon = (lambda_0 - np.arctan(s_y/(H-s_x)))*(180.0/np.pi)
    
    return abi_lat, abi_lon


def plot_aod(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.endswith('.nc'):
            file_path = os.path.join(input_folder, filename)
            xr_data=xr.open_dataset(file_path)
            file_id = Dataset(file_path)
            lat, lon = calculate_degrees(file_id)

           
            aod = file_id.variables['AOD'][:]
            time=xr_data.coords['t'].values
            ds_new = xr.Dataset(
                {
                    'AOD': (['y', 'x'], aod)
                },
                coords={
                    'lat': (['y', 'x'], lat),
                    'lon': (['y', 'x'], lon)
                }
            )

    
            fig, ax = plt.subplots(figsize=(10, 6), subplot_kw={'projection': ccrs.PlateCarree()})
            plot = ax.contourf(ds_new['lon'], ds_new['lat'], ds_new['AOD'], transform=ccrs.PlateCarree())
            ax.add_feature(cfeature.COASTLINE.with_scale('50m'), linewidth=2)
            ax.add_feature(cfeature.STATES.with_scale('50m'), linestyle=':', edgecolor='black')
            ax.add_feature(cfeature.BORDERS.with_scale('50m'), linewidth=2, edgecolor='black')
            plt.colorbar(plot, ax=ax, shrink=0.5, label='AOD Level')
            plt.title(f'GOES-16 AOD {time}')

        
            output_path = os.path.join(output_folder, f"{os.path.splitext(filename)[0]}.png")
            plt.savefig(output_path)
    print('Done')


if __name__ == '__main__':
    plot_aod(input_folder=input_folder,output_folder=output_folder)