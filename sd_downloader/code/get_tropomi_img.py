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
import re 


input_folder='./data/tropomi'
save_dir='./img/tropomi'
var_name='nitrogendioxide_tropospheric_column'


def plot_tropomi(input_folder, var_name,save_dir, texas=False):
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    for filename in os.listdir(input_folder):
        if filename.endswith('.nc'):
            file_path = os.path.join(input_folder, filename)
            print(f"Processing file: {file_path}")
            try:
                ds = Dataset(file_path, mode='r')
                print(f"Successfully opened: {file_path}")
            except OSError as e:
                print(f"Cannot open file: {file_path}, Error: {e}")
                continue  
            products_group = ds.groups.get('PRODUCT')
            if not products_group:
                print("No 'PRODUCTS' group found in the dataset.")
                ds.close()
                continue  # Skip to the next file

            if 'longitude' in products_group.variables and 'latitude' in products_group.variables:
                lon = products_group['longitude'][:]
                lat = products_group['latitude'][:]
            # Ensure longitude and latitude have the same shape
            if lon.shape != lat.shape:
                print("Longitude and latitude do not match in shape.")
                ds.close()
                continue  # Skip to the next variable
            def extract_time(filename):
                match = re.search(r'__(\d{8})T(\d{2})(\d{2})(\d{2})', filename)
                if match:
                    year_month_day = int(match.group(1))
                    hour=int(match.group(2))
                    minute =int(match.group(3))
                    second =int(match.group(4))
                    time = f'{year_month_day}\nhour{hour}\nminute{minute}\nsecond{second}'
                    return time
                else:
                    return None
                    
            time=extract_time(filename)
            projection = ccrs.PlateCarree()
            var_name = var_name

            # Extract data for plotting
            data = products_group[var_name][:]
            lon = np.squeeze(lon)
            lat = np.squeeze(lat)
            data = np.squeeze(data)

            # Create the plot
            plt.figure(figsize=(12, 8))
            ax = plt.axes(projection=projection)
            ax.add_feature(cfeature.COASTLINE)
            ax.add_feature(cfeature.BORDERS, linestyle=':')
            ax.add_feature(cfeature.STATES, linestyle=':')
            ax.add_feature(cfeature.LAND, facecolor='lightgray')
            ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
            ax.add_feature(cfeature.LAKES, facecolor='lightblue')
            ax.add_feature(cfeature.RIVERS)
            cmap = 'viridis'
            mesh = ax.pcolormesh(
                lon,
                lat,
                data,
                transform=projection,
                cmap=cmap,
                shading='auto'  # Options: 'auto', 'nearest'
            )

            plt.title(f'{var_name}/n{time}', fontsize=16)
            cbar = plt.colorbar(mesh, orientation='vertical', pad=0.05, aspect=50)
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            save_path = os.path.join(save_dir, f'{var_name}\n{time}.png')
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            print(f"Image saved {hour}{minute}{second}")
            plt.close()

        ds.close()

if __name__ =='__main__':
    plot_tropomi(input_folder=input_folder,var_name=var_name,save_dir=save_dir)

 