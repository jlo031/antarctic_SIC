 # ---- This is <download_osisaf_data.py> ----

"""
Download PM data from OSISAF thredds server
"""

import pathlib

from loguru import logger

import osisaf_thredds_download.download as osi_download

from config.load_config import *

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# search parameters
year_list  = [2025]
month_list = [1,2,3,4,5,6,7,8,9,10,11,12]
month_list = [10,11,12]
hemisphere = 'SH'
sensor     = 'amsr2'

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

logger.debug(f"DATA_DIR:    {DATA_DIR}")
logger.debug(f"SAT_DIR:     {SAT_DIR}")
logger.debug(f"IN_SITU_DIR: {IN_SITU_DIR}")
logger.debug(f"MISC_DIR:    {MISC_DIR}")
logger.debug(f"S1_DIR:      {S1_DIR}")
logger.debug(f"S2_DIR:      {S2_DIR}")
logger.debug(f"OSISAF_DIR:  {OSISAF_DIR}")
logger.debug(f"S1_L1_DIR:   {S1_L1_DIR}")
logger.debug(f"S1_FEAT_DIR: {S1_FEAT_DIR}")
logger.debug(f"S1_GEO_DIR:  {S1_GEO_DIR}")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

for year in year_list:
   
    for month in month_list:
       
        logger.info(f"Processing: {year}-{month}")
       
        osi_download.download_osisaf_full_month_daily_SIC(year, month, hemisphere, sensor, OSISAF_DIR)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <download_osisaf_data.py> ----
