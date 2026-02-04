# ---- This is <S1_query_and_download.py> ----

"""
Query CDSE for Sentinel-1 products.
Download products according to defined specifications.
"""

import pathlib
import sys

from loguru import logger

##from shapely import wkt
##from shapely.geometry import shape

##import numpy as np

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

# Specify download options
download_all_dual_pol    = True
download_minimum_overlap = False
minimum_overlap          = 0.6

# Set loglevel
loglevel = "DEBUG"

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

# Loop over all test sites
for test_site in test_sites:

    logger.info(f'Processing test_site: {test_site}')
    roi_json_path = WORK_DIR / "test_sites" / test_site_dict[test_site]["geojson_epsg4326"]
    start_date    = test_site_dict[test_site]["start_date"]
    end_date      = test_site_dict[test_site]["end_date"]
    start_time    = test_site_dict[test_site]["start_time"]
    end_time      = test_site_dict[test_site]["end_time"]

    logger.debug(f"roi_json_path: {roi_json_path}")
    logger.debug(f"start_date:    {start_date}")
    logger.debug(f"end_date:      {end_date}")
    logger.debug(f"start_time:    {start_time}")
    logger.debug(f"end_time:      {end_time}")


    # Query CDSE for current test site

    # hard-coded: search for S1 GRD data
    sensor           = "Sentinel-1"
    sensor_mode      = None
    product_type     = 'GRD'
    processing_level = None

    response_json = CDSE_sd.search_CDSE_catalogue(
        sensor,
        roi_json_path,
        start_date,
        end_date,
        start_time = start_time,
        end_time = end_time,
        sensor_mode = sensor_mode,
        product_type = product_type,
        processing_level = processing_level,
        max_results = 1000,
        expand_attributes = True,
        loglevel = loglevel,
    )

    product_list = response_json['value']

    # Add product list to dictionary for current test site
    test_site_dict[test_site]["p_list"] = product_list


logger.info("Finished CDSE query for all test sites")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# Loop over all test sites (again)
for test_site in test_sites:

    p_list = test_site_dict[test_site]["p_list"]

    # Get list of product names
    p_names = [ p['Name'] for p in p_list if not "COG" in p['Name'] ]

    # Get separate lists for EW/IW and single/dual-pol
    p_names_IW = [ p for p in p_names if "_IW_" in p ]
    p_names_EW = [ p for p in p_names if "_EW_" in p ]
    p_names_IW_single = [ p for p in p_names_IW if "_1SSH_" in p ]
    p_names_IW_dual   = [ p for p in p_names_IW if "_1SDH_" in p ]
    p_names_EW_single = [ p for p in p_names_EW if "_1SSH_" in p ]
    p_names_EW_dual   = [ p for p in p_names_EW if "_1SDH_" in p ]

    logger.info(f"-----------------------------")
    logger.info(f"RESULTS FOR TEST SITE: {test_site.upper()}")
    logger.info(f"-----------------------------")
    logger.info(f"Total number of products:            {len(p_names)}")
    logger.info(f"    Total number of EW products:     {len(p_names_EW)}")
    logger.info(f"        ... out of which single-pol: {len(p_names_EW_single)}")
    logger.info(f"        ... and dual-pol:            {len(p_names_EW_dual)}")
    logger.info(f"    Total number of IW products:     {len(p_names_IW)}")
    logger.info(f"        ... out of which single-pol: {len(p_names_IW_single)}")
    logger.info(f"        ... and dual-pol:            {len(p_names_IW_dual)}")
    logger.info(f"-----------------------------\n")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

if download_all_dual_pol:

    logger.info("Downloading all dual-pol data for all test sites")

    for test_site in test_sites:

        p_list = test_site_dict[test_site]["p_list"]

        # loop over products and get overlaps
        for p in p_list:
    
            logger.debug(f"{p['Name']}")

            if not 'COG' in p['Name'] and '1SDH' in p['Name']:
                logger.info(f"{p['Name']}")
                logger.info("    Downloading this product")
        
                CDSE_sd.download_product_from_cdse(p, S1_L1_DIR, username, password)

# --------------------------------------------------------------------------- #

if download_minimum_overlap:

    logger.info("Downloading products with minimum ROI overlap (non-COG, dual-pol")

    # Get ROI area as polygon
    search_polygon =  shape(CDSE_json.read_geojson(json_path)['features'][0]['geometry'])

    # loop over products and get overlaps
    for p in product_list:
    
        # get footprint polygon
        footprint_polygon = wkt.loads(p['Footprint'].split(";")[1])

        perc_overlap = CDSE_json.get_polygon_overlap(footprint_polygon, search_polygon)

        logger.debug(f"{p['Name']}")
        logger.debug(f"    Percentage overlap: {np.round(perc_overlap,2)}")


        if not 'COG' in p['Name'] and '1SDH' in p['Name'] and perc_overlap > minimum_overlap:
            logger.info(f"{p['Name']}")
            logger.info("    Downloading this product")
        
            CDSE_sd.download_product_from_cdse(p, S1_L1_DIR, username, password)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# ---- End of <S1_query_and_download.py> ----
