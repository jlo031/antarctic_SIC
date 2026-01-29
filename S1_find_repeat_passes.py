# ---- This is <S1_find_repeat_passes.py> ----

"""
Query CDSE to find repeat passes over test site ROI.
Relative orbit number is read from provided example image.
All repeat passes of that relative orbit for 2025 are found and downloaded.
"""

import pathlib
import sys

from loguru import logger

import CDSE.utils as CDSE_utils
import CDSE.json_utils as CDSE_json
import CDSE.search_and_download as CDSE_sd

from config.load_config import *

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

# Build path to test site config json file (dictionary in json format with information on test sites [files and dates])
path_to_test_site_config_json = WORK_DIR / "test_sites" / "test_sites_and_dates.json"

# Set loglevel
loglevel = "DEBUG"

# Select test site and provide example image for relative orbit
test_site = 'site_1'
example_image = "S1A_EW_GRDM_1SDH_20250807T134346_20250807T134446_060430_078315_C255"    # DONE
##example_image = "S1A_EW_GRDM_1SDH_20250812T135154_20250812T135254_060503_0785F9_877B"    # DONE


### Select test site and provide example image for relative orbit
##test_site = 'site_2'
##example_image = "S1A_EW_GRDM_1SDH_20250304T152136_20250304T152236_058156_072F25_3ECE"    #DONE
##example_image = "S1A_EW_GRDM_1SDH_20250311T151330_20250311T151430_058258_07333C_5635"

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

logger.remove()
logger.add(sink=sys.stdout, level=loglevel)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# Read test site dict
with open(path_to_test_site_config_json, "r") as f:
    test_site_dict = json.load(f)

# Get individual test sites
test_sites = test_site_dict.keys()

logger.info(f"Found {len(test_sites)} test sites: {list(test_sites)}")

# Read CDSE user credentials from '.env'
username, password = CDSE_utils.get_user_and_passwd()

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# GET RELATIVE ORBIT PARAMETERS AND SENSOR PLATFORM FROM INPUT DATA

# S1A/B/C ?
platform = example_image[0:3]

# Search for example image in CDSE data base
logger.info("Searching CDSE for example image to retrieve relative orbit number")

example_result_json = CDSE_sd.search_CDSE_catalogue_by_name(example_image)
example_result      = example_result_json['value'] 

# Find relative orbit of example image
for attribute in example_result[0]['Attributes']:
    if attribute["Name"] == "relativeOrbitNumber":
        relative_orbit = attribute["Value"]

logger.info(f"Sentinel platform is:                             {platform}")
logger.info(f"Relative orbit number for given example image is: {relative_orbit}")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# QUERY CDSE FOR REPEAT PASSES FOR ALL OF 2025

logger.info(f'Processing test_site: {test_site}')

# Use any overlap for test site 1
# Use only overlap with centroid for test site 2
if test_site == "site_1":
    roi_json_path = WORK_DIR / "test_sites" / test_site_dict[test_site]["centroid_geojson_epsg4326"]
elif test_site == "site_2":
    roi_json_path = WORK_DIR / "test_sites" / test_site_dict[test_site]["centroid_geojson_epsg4326"]
else:
    logger.warning("Implement test site!!")


# hard-coded: search for S1 GRD data for repeat passes in all of 2025
sensor           = "Sentinel-1"
sensor_mode      = None
product_type     = 'GRD'
processing_level = None
start_date       = "2025-01-01"
end_date         = "2026-01-01"
start_time       = "00:00:00"
end_time         = "00:00:00"

logger.debug(f"roi_json_path: {roi_json_path}")
logger.debug(f"start_date:    {start_date}")
logger.debug(f"end_date:      {end_date}")
logger.debug(f"start_time:    {start_time}")
logger.debug(f"end_time:      {end_time}")


response_json = CDSE_sd.search_CDSE_catalogue(
    sensor,
    roi_json_path,
    start_date,
    end_date,
    start_time = start_time,
    end_time = end_time,
    sensor_mode = sensor_mode,
    relative_orbit = relative_orbit,
    product_type = product_type,
    processing_level = processing_level,
    max_results = 1000,
    expand_attributes = True,
    loglevel = loglevel,
)

product_list = response_json['value']

logger.info("Finished CDSE query for all test sites")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# DOWNLOAD REPEAT PASSES FROM SAME PLATFORM WITHOUT COG PRODUCTS

repeat_pass_list = []

# loop over products and get overlaps
for p in product_list:
    
    logger.debug(f"{p['Name']}")

    if not 'COG' in p['Name'] and '1SDH' in p['Name'] and platform in p['Name']:
        logger.info(f"{p['Name']}")
        repeat_pass_list.append(f"{p['Name']}")
        logger.info("    Downloading this product")
        
        CDSE_sd.download_product_from_cdse(p, S1_L1_DIR, username, password)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# WRITE FILE LIST TO TXT FILE

repeat_pass_list.sort()

with open(f"test_{test_site}_orbit_{relative_orbit:03d}_image_list_2025.txt", "w") as f:
    for item in repeat_pass_list:
        f.write(f"{item}\n")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# ---- End of <S1_query_and_download.py> ----
