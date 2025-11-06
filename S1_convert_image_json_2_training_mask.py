# ---- This is <S1_convert_image_json_2_training_mask.py> ----

"""
Convert S1 input image training json file to training mask.
"""

import pathlib
import sys
import argparse

from loguru import logger

import labelme_utils.json_conversion as lm_json

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
    p.add_argument("labels", help = "path to labels txt file")
    p.add_argument("-ML", default="5x5", help = "multilook window size (default=5x5)")
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
    S1_base      = args.S1_base
    labels_path  = pathlib.Path(args.labels).resolve()
    ML           = args.ML
    overwrite    = args.overwrite
    loglevel     = args.loglevel

    logger.info(f"Processing image: {S1_base}")

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

    # Build path th RGB training folder (for ML setting)
    rgb_folder      = S1_RGB_DIR / f"ML_{ML}"
    training_folder = S1_TRAIN_DIR / f"ML_{ML}"

    # Build full paths to json and training mask
    json_path     = rgb_folder / f"{S1_base}_rgb.json"
    rgb_path      = rgb_folder / f"{S1_base}_rgb.tif"
    training_path = training_folder / f"{S1_base}_rgb_training_mask.img"

    if not labels_path.is_file():
        logger.error(f"Could not find labels_path: {labels_path}")
        return

    if not json_path.is_file():
        if rgb_path.is_file():
            logger.warning(f"Could not find json_path:         {json_path}")
            logger.warning(f"But found corresponding rgb_path: {rgb_path}")
        else:
            logger.error(f"Could not find json_path:              {json_path}")
            logger.error(f"Could not find corresponding rgb_path: {rgb_path}")
        return

    logger.info(f"Processing json_path: {json_path}")

    # Make sure training_folder exists
    training_folder.mkdir(parents=True, exist_ok=True)

    lm_json.convert_json_file_2_mask(
        json_path,
        labels_path,
        training_folder,
        output_format = 'ENVI',
        overwrite = overwrite,
        loglevel = loglevel,
    )

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    main()
    
# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# ---- End of <S1_convert_image_json_2_training_mask.py> ----
