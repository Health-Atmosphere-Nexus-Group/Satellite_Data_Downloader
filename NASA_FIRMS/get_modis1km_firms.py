'''
Author: Zhengyi Cui
Email: Zhengyi.Cui@uth.tmc.edu
Date: 2024-12-16 18:50:15

LANCE Near Real Time (NRT)
USA_contiguous_and_Hawaii
Modis C6.1 1km
https://https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/modis-c6.1/USA_contiguous_and_Hawaii/
This code will donwload all the data from the above link to the local directory
'''

import subprocess
import logging
import os

################################ Replace with your own Token here ################################
EDL_TOKEN = 
BASE_URL = "https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/modis-c6.1/USA_contiguous_and_Hawaii/"
SAVE_DIR = "./data/modis"
LOG_DIR = './log/download_modis_data.log'

def main():
    if not os.path.exists(LOG_DIR):
        os.makedirs(os.path.dirname(LOG_DIR), exist_ok=True)

    logger = logging.getLogger('download_modis_data')
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        c_handler = logging.StreamHandler()
        f_handler = logging.FileHandler(LOG_DIR, mode='a')
        c_handler.setLevel(logging.INFO)
        f_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        c_handler.setFormatter(formatter)
        f_handler.setFormatter(formatter)
        logger.addHandler(c_handler)
        logger.addHandler(f_handler)


    if not os.path.exists(SAVE_DIR):
        try:
            os.makedirs(SAVE_DIR)
            logger.info(f"Created directory: {SAVE_DIR}")
        except Exception as e:
            logger.error(f"Failed to create directory {SAVE_DIR}: {e}")
            raise

    cmd = [
        "wget",  # Update to your wget path
        "-e", "robots=off",
        "-m",
        "-np",
        "-R", ".html,.tmp",
        "-nH",
        "--cut-dirs=3",
        BASE_URL,
        "--header", f"Authorization: Bearer {EDL_TOKEN}",
        "-P", SAVE_DIR
    ]

    # Execute the wget command
    logger.info("Starting MODIS data download...")
    try:
        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("MODIS data download completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Download failed with error:\n{e.stderr}")
    except Exception as ex:
        logger.error(f"Unexpected error occurred: {ex}")

if __name__ == '__main__':
    main()
