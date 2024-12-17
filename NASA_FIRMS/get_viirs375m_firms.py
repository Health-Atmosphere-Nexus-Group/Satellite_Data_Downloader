'''
Author: Zhengyi Cui
Email: Zhengyi.Cui@uth.tmc.edu
Date: 2024-12-10 17:08:07

LANCE Near Real Time (NRT)
Central_America
NOAA-21 VIIRS 375m C2
https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/noaa-21-viirs-c2/Central_America/
This code will donwload all the data from the above link to the local directory
'''
import subprocess
import logging
import os

################################ Takeplace your own Token here ################################
EDL_TOKEN = 
BASE_URL = "https://nrt3.modaps.eosdis.nasa.gov/archive/FIRMS/noaa-21-viirs-c2/Central_America/"
SAVE_DIR = "./data/viirs"
LOG_DIR = './log/download_viirs_data.log'

def main():
    if not os.path.exists(LOG_DIR):
        os.makedirs(os.path.dirname(LOG_DIR), exist_ok=True)
    logger = logging.getLogger('download_viirs_data')
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
        
    #cmd = f"wget -e robots=off -m -np -R .html,.tmp -nH --cut-dirs=3 {BASE_URL} --header 'Authorization: Bearer

    cmd = [
        "wget",
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

    logger.info("Starting VIIRS data download with wget...")
    try:
        result = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info("Download completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Download failed with error:\n{e.stderr}")
    except Exception as ex:
        logger.error(f"Unexpected error: {ex}")


if __name__ == '__main__':
    main()
