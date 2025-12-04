# antarctic_SIC
Scripts and workflow for comparison of Antarctic SIC from PM and SAR.

## Requirements
Working python (anaconda/miniconda) and SNAP installation.
Package requirements for each processing step are listed below.
Follow installation guides provided in the individual packages.

Except for *labelme*, most packages can be installed in the same environment. Follow installation guides 


## SAR workflow

### (0) Set up configuration
Edit *config.json* in the *config* folder for your system.
Unless you know exactly what you are doing, it is recommended to only adjust the "WORK_DIR" and "DATA_DIR" variables.
Normally, you do not need to edit *load_config.py*.


### (1) Download images over selected test sites and time periods:
Requirements: https://github.com/jlo031/CDSE

*S1_query_and_download.py*

Define the time period for each test site directly in the script.
Run to find and dowload S1 products into the *S1_L1_DIR*.


### (2) Pre-process all S1 images in L1_DIR:
Requirements: https://github.com/jlo031/S1_processing

*S1_preprocess_image.py*
*S1_preprocess_image_list.sh (for batch processing)*

### (3) Label ice types and open water for each image:
Requirements: https://github.com/jlo031/labelme_utils

*S1_convert_image_json_2_training_mask.py*
*S1_convert_image_list_json_2_training_mask.py* (for batch processing)

### (4) Train and classify images:
Requirements: https://github.com/jlo031/GLIA

*S1_train_and_classify_image.py*

! CURRENTLY IN DEVELOPMENT ! 
