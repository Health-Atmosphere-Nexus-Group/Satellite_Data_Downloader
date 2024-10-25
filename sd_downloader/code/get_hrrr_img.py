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

input_folder='./data/hrrr/hrrr/20230409'
save_dir='./img/hrrr'

def plot_grib2_with_cartopy(input_folder,save_dir,texas=False):

    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    for filename in os.listdir(input_folder):
        if filename.endswith('.grib2'):
            file_path = os.path.join(input_folder, filename)
            try:
                ds = xr.open_dataset(file_path, engine='cfgrib')
            except (ValueError, KeyError) as e:
                print('find data keys')
                ds = xr.open_dataset(
                file_path,
                engine='cfgrib',
                filter_by_keys={'stepType': 'instant', 'typeOfLevel': 'surface'})
                pass                

            variables = list(ds.data_vars)
            if not variables:
                print("No variables found in the dataset.")
                ds.close()
                return
            variable = variables[0]  


            if 'time' in ds.coords:
                time = ds['time'].values
                try:
                    time = xr.conventions.decode_cf_datetime(ds['time'], ds['time'].attrs.get('units'))
                    time_str = str(time)
                except:
                    time_str = str(time)
            else:
                time_str = 'unknow time'

            if ('longitude' in ds.coords) and ('latitude' in ds.coords):
                lon = ds['longitude']
                lat = ds['latitude']
            elif ('lon' in ds.coords) and ('lat' in ds.coords):
                lon = ds['lon']
                lat = ds['lat']
            elif ('longitude' in ds.variables) and ('latitude' in ds.variables):
                lon = ds['longitude']
                lat = ds['latitude']
            elif ('lon' in ds.variables) and ('lat' in ds.variables):
                lon = ds['lon']
                lat = ds['lat']
            else:
                print("No longitude and latitude found in the dataset.")
                ds.close()
                return
            if lon.shape != lat.shape:
                print("Longitude and latitude do not match.")
                ds.close()
                return

            projection = ccrs.PlateCarree()

            data = ds[variable]

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

            if texas:
                min_lon, max_lon = 253.35,   266.49
                min_lat, max_lat = 25.84, 36.50
                ds_subset = ds.where(
                (ds['longitude'] >= min_lon) & (ds['longitude'] <= max_lon) &
                (ds['latitude'] >= min_lat) & (ds['latitude'] <= max_lat),
                drop=True)

                lon = ds_subset['longitude'].values
                lat = ds_subset['latitude'].values
                data = ds_subset[variable].values


            data_plot = ax.pcolormesh(
                lon,
                lat,
                data,
                transform=projection,
                cmap=cmap,
                shading='auto'  # 'auto' or 'nearest'
            
            )

            plt.title(f'{time_str} / {variable}', fontsize=16)
            cbar = plt.colorbar(data_plot, orientation='vertical', pad=0.05, aspect=50)
            cbar.set_label(variable)
            gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False

        
            save_path = os.path.join(save_dir, f'{variable}_{time_str}.png')
            plt.savefig(save_path, bbox_inches='tight', dpi=300)
            print(f"img saved {save_path}")

            plt.close()

if __name__ =='__main__':
    plot_grib2_with_cartopy(input_folder=input_folder,save_dir=save_dir)

 