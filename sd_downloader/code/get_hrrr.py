'''
Author: zhengyi cui
Date: 2024-10-17 20:09:44
LastEditTime: 2024-10-27 9:56:58
E-mail address: Zhengyi.Cui@uth.tmc.edu

Copyright (c) 2024 by ${Zhengyi.Cui@uth.tmc.edu}, All Rights Reserved. 

###################key URLs########################
hrrr info: https://rapidrefresh.noaa.gov/hrrr/
Herbie intro page: https://rapidrefresh.noaa.gov/hrrr/
data format: GRIB2
'''




from herbie import FastHerbie
import herbie 
import time
from datetime import timedelta
from datetime import datetime
import logging
import os
import pandas as pd 

save_dir = './data/hrrr'
start_date = datetime(2023, 4, 10)
end_date = datetime(2023, 4, 12)


meterology_index=[
':TMP:2 m',#Temperature at 2 m above ground
':PRES:surface:',#Surface pressure
':UGRD:10 mb:',#U-wind at 10 m above ground
':VGRD:10 mb:',#V-wind at 10 m above ground
':UGRD:250 mb:'#U-wind at 250 hPa pressure level
':VGRD:250 mb:',#V-wind at 250 hPa pressure level:
':HPBL:surface:', #Planetary boundary layer height
':RH: 2 m',#Relative humidity at 2 m above ground
':RHPW:entire atmosphere:',#Relative humidity entire atmosphere
':TCDC:entire atmosphere:',#total cloud cover entire atmosphere
':TCDC:boundary layer cloud layer:', #total cloud cover 
':HCDC:',#high cloud layer
':LCDC:', #low cloud layer
':MCDC:', #middle cloud layer
':VIS:surface:', #Visibility at surface
':VEG:surface:',#Vegetation at surface
':MSTAV:0 m underground:', #Moisture availability at 0 m underground
':SFCR:surface:', #Surface roughness at surface
':CAPE:surface:' #Convective available potential energy at surface

]


def setup_logging(log_file='./log/hrrr.log'):
    logger = logging.getLogger('HRRR_Download')
    logger.setLevel(logging.DEBUG) 
    fh = logging.FileHandler(log_file)
    fh.setLevel(logging.DEBUG) 
    ch = logging.StreamHandler()
    ch.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger


def generate_dates(start_date, end_date):
    current_date = start_date
    date_list = []
    while current_date <= end_date:
        date_str = current_date.strftime('%Y-%m-%d')
        date_list.append(date_str)
        current_date += timedelta(days=1)
    return date_list


def get_data_HRRR(dates, meteorology_index, save_dir, logger):

    fxx = [0]

    try:
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            logger.debug(f'Created save directory: {save_dir}')

        logger.info('Starting HRRR data download using FastHerbie')

        for data_type in meteorology_index:
            logger.info(f'Start Downloading data type: {data_type}')
            for date_str in dates:
                try:
                    logger.info(f'Downloading {data_type} for date: {date_str}')
                    

                    date_range = pd.date_range(start=date_str, periods=24, freq='1h')
                    # print(date_range)
                    FH = FastHerbie(DATES=date_range, model='hrrr', fxx=fxx)
                    
                    FH.download(data_type, save_dir=save_dir, overwrite=True)
                    
                    logger.info(f'Successfully downloaded {data_type} for date: {date_str}')
                except Exception as e:
                    logger.error(f'Failed to download {data_type} for date {date_str}: {e}')
                    continue 

            logger.info(f'Finished downloading data type: {data_type}')

        logger.info(f'All HRRR data on {dates} downloads completed successfully.')
    except Exception as e:
        logger.critical(f'Critical error during HRRR data download: {e}')



if __name__ == "__main__":
    logger = setup_logging()
    dates = generate_dates(start_date, end_date)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    get_data_HRRR(dates,meterology_index,save_dir,logger)
