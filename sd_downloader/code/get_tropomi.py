'''
Author: zhengyi cui
Date: 2024-10-17 20:09:44
LastEditTime: 2024-10-22 01:13:58
E-mail address: Zhengyi.Cui@uth.tmc.edu

Copyright (c) 2024 by ${Zhengyi.Cui@uth.tmc.edu}, All Rights Reserved. 


###################key URLs########################
# Sentinel-5p Reprocessed Data (RPRO) NetCDF format.
# aws s3 ls --no-sign-request s3://meeo-s5p/RPRO/L2__NO2___/{year}/{month}/{day}/

# Sentinel-5p Off Line Data (OFFL) NetCDF format.
# aws s3 ls --no-sign-request s3://meeo-s5p/OFFL/

# Ozone data: s3://meeo-s5p/RPRO/L2__O3____/{year}/{month}/{day}/

#Obit track & time ASCENDING
#https://worldview.earthdata.nasa.gov/?v=-168.02751212738684,-22.676864438916184,-13.704768322917204,93.17676277808877&l=Reference_Labels_15m(hidden),Reference_Features_15m(hidden),Coastlines_15m,OrbitTracks_Sentinel-5P_Ascending,VIIRS_NOAA21_CorrectedReflectance_TrueColor(hidden),VIIRS_NOAA20_CorrectedReflectance_TrueColor(hidden),VIIRS_SNPP_CorrectedReflectance_TrueColor(hidden),MODIS_Aqua_CorrectedReflectance_TrueColor(hidden),MODIS_Terra_CorrectedReflectance_TrueColor&lg=true&t=2024-10-22-T05%3A13%3A07Z

data format: NetCDF
'''
import os
from datetime import datetime, timedelta
from tqdm import tqdm
import s3fs
import logging
import re


save_dir='./data/tropomi'
start_date = datetime(2023, 10, 15)
end_date = datetime(2023, 10, 15)



def generate_dates(start_date, end_date):
    current_date = start_date
    date_list = []
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list

def extract_hour(filename):

    match = re.search(r'T(\d{2})(\d{2})(\d{2})', filename)
    if match:
        hour = int(match.group(1))
        return hour
    else:
        return None



def get_tropomi_data(start_date, end_date,save_dir):
    logger = logging.getLogger('get_tropomi_data')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(f'./log/get_tropomi_data.log')
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        f_handler.setFormatter(formatter)
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)
    save_directory = save_dir
    if not os.path.exists(save_directory):
        try:
            os.makedirs(save_directory)
            logger.info(f"Created directory: {save_directory}")
        except Exception as e:
            logger.error(f"Failed to create directory {save_directory}: {e}")
            return

    try:
        dates = generate_dates(start_date, end_date)
        logger.info(f"Generated {len(dates)} dates from {start_date} to {end_date}.")
    except Exception as e:
        logger.error(f"Failed to generate dates between {start_date} and {end_date}: {e}")
        return

    try:
        fs = s3fs.S3FileSystem(anon=True)
        logger.info("Initialized anonymous S3FileSystem.")
    except Exception as e:
        logger.error(f"Failed to initialize S3FileSystem: {e}")
        return

    for current_date in (tqdm(dates, desc="Downloading TROPOMI Data")):

        year = current_date.strftime('%Y')
        month = current_date.strftime('%m')
        day = current_date.strftime('%d')



        s3_path = aws_path = f's3://meeo-s5p/NRTI/L2__NO2___/{year}/{month}/{day}/'



        logger.info(f"Processing date: {current_date.strftime('%Y-%m-%d')} | S3 path: {s3_path}")
        print(f"Trying to access: {s3_path}")
        try:
            files = fs.ls(s3_path)
            print(files)
            if not files:
                logger.warning(f"No files found for {current_date.strftime('%Y-%m-%d')} at 0z")
                continue
            else:
                logger.info(f"Found {len(files)} files for {current_date.strftime('%Y-%m-%d')} at 0z")
            for file in files:
                #get the real filename
                filename = os.path.basename(file)

                hour = extract_hour(filename)
                if hour is None:
                    logger.warning(f"Filename {filename} does not match expected pattern, skipping.")
                    continue


                ##select time range
                if 18 <= hour < 20:

                    save_path = os.path.join(save_directory, filename)
                    if os.path.exists(save_path):
                        logger.info(f"File {filename} already exists, skipping download.")
                        continue
                    else:
              
                        logger.info(f"Downloading file: {filename}")
                        fs.get(file, save_path)
                        logger.info(f"Downloaded file to: {save_path}")
                else:
                    logger.info(f"File {filename} is outside the desired time range (18-20), skipping.")
                    continue

                try:
                    with fs.open(file, 'rb') as f_in:
                        with open(save_path, 'wb') as f_out:
                            f_out.write(f_in.read())
                    logger.info(f"Downloaded {filename}")
                except Exception as e_file:
                    logger.error(f"Failed to download {filename}: {e_file}")
                    continue
        except Exception as e:
            logger.error(f"Failed to access {s3_path}: {e}")
            continue


if __name__ == "__main__":
   get_tropomi_data(start_date, end_date,save_dir)