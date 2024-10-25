'''
Author: zhengyi cui
Date: 2024-10-17 20:09:44
LastEditTime: 2024-10-22 01:13:58
E-mail address: Zhengyi.Cui@uth.tmc.edu

Copyright (c) 2024 by ${Zhengyi.Cui@uth.tmc.edu}, All Rights Reserved. 

###################key URLs########################
hrrr info: https://rapidrefresh.noaa.gov/hrrr/
Herbie intro page: https://rapidrefresh.noaa.gov/hrrr/
data format: GRIB2
'''




from herbie import Herbie
import herbie 
import time
from datetime import timedelta
from datetime import datetime
import logging
import os


save_dir = './data/hrrr'
start_date = datetime(2023, 4, 9)
end_date = datetime(2023, 4, 9)

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


def get_data_HRRR(dates, meteorology_index, save_dir):
    try:
        herbie.misc.HerbieLogo2(white_line=False)
        logger.info('Starting HRRR download by Herbie')
        for date in dates:
            for hour in range(0, 24):
                logger.info(f'Downloading data for {date}/{hour}')

                H = Herbie(
                    model='hrrr',
                    product='sfc',
                    fxx=hour,
                    date=date,
                    priority='aws'
                )

                for i in meteorology_index:
                    try:
                        H.download(i, overwrite=True, save_dir=save_dir, errors='raise')
                        logger.info(f'Successfully downloaded {date}/{hour}/{i}')
                    except Exception as e:
                        logger.error(f'Failed to download {date}/{hour}/{i} due to {e}')
                        continue
            logger.info(f'Downloading data for {date} completed')
    except Exception as e:
        logger.critical(f'Failed to download data due to {e}') 


if __name__ == "__main__":
    logger = setup_logging()
    dates = generate_dates(start_date, end_date)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    get_data_HRRR(dates,meterology_index,save_dir)