# ---- This is <S1_geocode_image.py> ----

"""
Geocode S1 input image.
Folder structure is read from config folder.

    Default features to geocode: Sigma0_HH_dB, Sigma0_HV_dB
    Optional features to geopcode: RGB, labels
"""

import pathlib
import sys
import argparse

from loguru import logger

import S1_processing.utils as S1_utils
import S1_processing.S1_feature_extraction as S1_feat

import geocoding.generic_geocoding as gen_geo
import geocoding.geocoding_utils as geo_utils

from config.load_config import *

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

def set_loglevel(level: str):
    level = level.upper()
    if level not in ["TRACE", "DEBUG", "INFO", "SUCCESS" "WARNING", "ERROR", "CRITICAL"]:
        raise ValueError(f"Invalid log level: {level}")
    logger.remove()
    logger.add(sink=sys.stdout, level=level)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

def main():

    p = argparse.ArgumentParser(formatter_class = argparse.RawDescriptionHelpFormatter, description =__doc__)
    
    p.add_argument("S1_base", help = "S1 basename")
    p.add_argument("-ML", default="5x5", help = "multilook window size (default=5x5)")
    p.add_argument("-make_geo_RGB", action = "store_true", help = "make geocoded RGB image")
    p.add_argument("-target_epsg", default="3031", help = "set target epsg code (default=3031)")
    p.add_argument("-pixel_spacing", default="100", help = "set target pixel spacing (default=100)")
    p.add_argument("-make_geo_RGB_only", action = "store_true", help = "remove single channel geocoded images and keep only stacked RGB")
    p.add_argument("-overwrite", action = "store_true", help = "overwrite existing files")
    p.add_argument('-loglevel', choices = ["TRACE", "DEBUG", "INFO", "SUCCESS" "WARNING", "ERROR", "CRITICAL"], default = "INFO", help = "loglevel setting (default=INFO)")

    args = p.parse_args()

    # set loglevel
    try:
        set_loglevel(args.loglevel)
    except ValueError as e:
        print(e)
        return

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

    logger.debug(f"args: {args}")

    # Parse inputs
    S1_base           = args.S1_base
    ML                = args.ML
    make_geo_RGB      = args.make_geo_RGB
    target_epsg       = args.target_epsg
    pixel_spacing     = args.pixel_spacing
    make_geo_RGB_only = args.make_geo_RGB_only
    overwrite         = args.overwrite
    loglevel          = args.loglevel

    logger.info(f"Processing image:     {S1_base}")

    # Set GPT variable from local .env file
    GPT = S1_utils.get_GPT_path('local')
    logger.info(f"GPT: {GPT}")

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

    # Build path to S1 zip or safe and check that it exists
    S1_zip  = S1_L1_DIR / f"{S1_base}.zip"
    S1_safe = S1_L1_DIR / f"{S1_base}.SAFE"
    if S1_zip.is_file():
        S1_safe_zip = S1_zip
    elif S1_safe.is_dir():
        S1_safe_zip = S1_safe
    else:
        logger.error(f"Could not find S1_zip:  {S1_zip}")
        logger.error(f"Could not find S1_safe: {S1_safe}")
        return
    logger.info(f"S1_safe_zip: {S1_safe_zip}")

    # Build path to feature folder and RGB folder (for ML setting)
    feat_folder = S1_FEAT_DIR / f"ML_{ML}" / f"{S1_base}"
    rgb_folder  =  S1_RGB_DIR / f"ML_{ML}"

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

    if make_geo_RGB_only:

        logger.info("Geocoding input image, only creating geocoded stacked intensities")

        # Path to final geocoded RGB file
        output_tif_path = S1_GEO_DIR / f"{S1_base}__intensities__epsg_{target_epsg}__pixelspacing_{pixel_spacing}.tiff"

        logger.debug(f"output_tif_path: {output_tif_path}")

        if output_tif_path.is_file() and not overwrite:
            logger.info(f"Geocoded RGB file already exists: {output_tif_path}")
            return

        else:
            logger.info("Preparing to geocode HH and HV, stack, clean up")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

    # Get lat/lon if needed

    logger.info("Computing lat/lon bands for GCP extraction")

    S1_feat.get_S1_lat_lon(
        S1_safe_zip, 
        feat_folder,
        GPT,
        loglevel = loglevel,
        overwrite = overwrite
    )

# --------------------------------------------------------------------------- #

    features_2_geocode = [ 'Sigma0_HH_dB', 'Sigma0_HV_dB' ]

    for feature_2_geocode in features_2_geocode:

        logger.info(f"Geocoding feature: {feature_2_geocode}")

        img_path         = feat_folder / f"{feature_2_geocode}.img"
        lat_path         = feat_folder / "lat.img"
        lon_path         = feat_folder / "lon.img"
        output_tiff_path = S1_GEO_DIR / f"{S1_base}__{feature_2_geocode}__epsg_{target_epsg}__pixelspacing_{pixel_spacing}.tiff"


        logger.debug(f"img_path: {img_path}")
        logger.debug(f"lat_path: {lat_path}")
        logger.debug(f"lon_path: {lon_path}")
        logger.debug(f"output_tiff_path: {output_tiff_path}")

        gen_geo.geocode_image_from_lat_lon(
            img_path,
            lat_path,
            lon_path,
            output_tiff_path,
            target_epsg,
            pixel_spacing,
            tie_points= 21,
            srcnodata = 0,
            dstnodata = 0,
            order = 3,
            resampling = 'near',
            keep_gcp_file = False,
            overwrite = overwrite,
            loglevel = loglevel,
        )

# --------------------------------------------------------------------------- #

    # Make geocoded RGB

    if make_geo_RGB or make_geo_RGB_only:

        logger.info("Stacking HH and HV to geocoded RGB for QGIS")

        input_tif_path1 = S1_GEO_DIR / f"{S1_base}__Sigma0_HH_dB__epsg_{target_epsg}__pixelspacing_{pixel_spacing}.tiff"
        input_tif_path2 = S1_GEO_DIR / f"{S1_base}__Sigma0_HV_dB__epsg_{target_epsg}__pixelspacing_{pixel_spacing}.tiff"
        output_tif_path = S1_GEO_DIR / f"{S1_base}__intensities__epsg_{target_epsg}__pixelspacing_{pixel_spacing}.tiff"

        geo_utils.stack_geocoded_images(
            input_tif_path1,
            input_tif_path2,
            output_tif_path,
            no_data_value = 0,
            overwrite = overwrite,
            loglevel = loglevel,
        )

        if make_geo_RGB_only:

            logger.info("Cleaning up: Deleting geocoded HH and HV files")
            input_tif_path1.unlink()
            input_tif_path2.unlink()

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    main()
    
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# ---- End of <S1_geocode_image.py> ----
