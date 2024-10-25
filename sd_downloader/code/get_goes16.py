'''
Author: zhengyi cui
Date: 2024-10-17 20:09:44
LastEditTime: 2024-10-22 01:13:58
E-mail address: Zhengyi.Cui@uth.tmc.edu

Copyright (c) 2024 by ${Zhengyi.Cui@uth.tmc.edu}, All Rights Reserved. 


###################key URLs########################
goes-16 info: https://eospso.nasa.gov/missions/geostationary-operational-environmental-satellite-16#:~:text=GOES%2D16%20has%20provided%20continuous,climatic%2C%20solar%20and%20space%20data.
aws database info: https://registry.opendata.aws/noaa-goes/

data format: NetCDF
'''


import os
from datetime import datetime, timedelta
from tqdm import tqdm
import s3fs
import logging



save_dir='./data/goes_16'
start_date = datetime(2023, 7, 7)
end_date = datetime(2023, 7, 7)
aws_path= f'noaa-goes16/ABI-L2-AODC/{year}/{day_of_year}/{hour}/'

#generate a date list
def generate_dates(start_date, end_date):
    current_date = start_date
    date_list = []
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += timedelta(days=1)
    return date_list



def get_goes16_aod(start_date, end_date,save_dir):
    logger = logging.getLogger('get_goes16_aod')
    logger.setLevel(logging.INFO)
    
    # Prevent adding multiple handlers if the function is called multiple times
    if not logger.handlers:
        # Create handlers
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(f'./log/get_goes16_aod{start_date}_{end_date}.log')
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)
        
        # Create formatters and add to handlers
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        f_handler.setFormatter(formatter)
        
        # Add handlers to the logger
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
        print(dates)
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

    for current_date in tqdm(dates, desc="Downloading GOES-16 AOD Data"):
        year = current_date.strftime('%Y')
        day_of_year = current_date.strftime('%j') 
        
        for hour in range(0,24):
            s3_path = aws_path
            logger.info(f"Processing date: {current_date.strftime('%Y-%m-%d')} | S3 path: {s3_path}")
            
            try:
                files = fs.ls(s3_path)
                if not files:
                    logger.warning(f"No files found for {current_date.strftime('%Y-%m-%d')} at 0z")
                    continue
                else:
                    logger.info(f"Found {len(files)} files for {current_date.strftime('%Y-%m-%d')} at 0z")
                
                for file in files:
                    filename = os.path.basename(file)
                    save_path = os.path.join(save_directory, filename)
                    if os.path.exists(save_path):
                        logger.info(f"File {filename} already exists, skipping download.")
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
    get_goes16_aod(start_date, end_date,save_dir)