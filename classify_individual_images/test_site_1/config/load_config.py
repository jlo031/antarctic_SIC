 # ---- This is <load_config.py> ----

"""
Load project config directory structure from json file
"""

import json
from pathlib import Path

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

with open("config/config.json", "r") as f:
    config = json.load(f)

# Project work dir
WORK_DIR = Path(config["WORK_DIR"])

# Main project dir
DATA_DIR = Path(config["DATA_DIR"])

# Sub-dirs
SAT_DIR     = DATA_DIR / config["sub_dirs"]["satellite_data"]
IN_SITU_DIR = DATA_DIR / config["sub_dirs"]["in_situ_data"]
MISC_DIR    = DATA_DIR / config["sub_dirs"]["misc"]

# Satellite sub-dirs
S1_DIR     = SAT_DIR / config["sub_dirs"]["sat_data_subdirs"]["S1"]
S2_DIR     = SAT_DIR / config["sub_dirs"]["sat_data_subdirs"]["S2"]
OSISAF_DIR = SAT_DIR / config["sub_dirs"]["sat_data_subdirs"]["OSISAF"]

# S1 sub-dirs
S1_L1_DIR    = S1_DIR / config["sub_dirs"]["sat_data_subdirs"]["S1_subdirs"]["L1"]
S1_FEAT_DIR  = S1_DIR / config["sub_dirs"]["sat_data_subdirs"]["S1_subdirs"]["FEAT"]
S1_GEO_DIR   = S1_DIR / config["sub_dirs"]["sat_data_subdirs"]["S1_subdirs"]["GEO"]
S1_RGB_DIR   = S1_DIR / config["sub_dirs"]["sat_data_subdirs"]["S1_subdirs"]["RGB"]
S1_TRAIN_DIR = S1_DIR / config["sub_dirs"]["sat_data_subdirs"]["S1_subdirs"]["TRAIN"]

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Create directories if needed

DATA_DIR.mkdir(parents=True, exist_ok=True)

SAT_DIR.mkdir(parents=True, exist_ok=True)
IN_SITU_DIR.mkdir(parents=True, exist_ok=True)
MISC_DIR.mkdir(parents=True, exist_ok=True)

S1_DIR.mkdir(parents=True, exist_ok=True)
S2_DIR.mkdir(parents=True, exist_ok=True)
OSISAF_DIR.mkdir(parents=True, exist_ok=True)

S1_L1_DIR.mkdir(parents=True, exist_ok=True)
S1_FEAT_DIR.mkdir(parents=True, exist_ok=True)
S1_GEO_DIR.mkdir(parents=True, exist_ok=True)
S1_RGB_DIR.mkdir(parents=True, exist_ok=True)
S1_TRAIN_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <load_config.py> ----
