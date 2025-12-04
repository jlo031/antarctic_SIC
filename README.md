# antarctic_SIC
Cripts and workflow for comparison of Antarctic SIC from PM and SAR.


## SAR workflow

### (1) Download images over selected test sites and time periods:
Requirements: https://github.com/jlo031/CDSE

*S1_query_and_download.py*

### (2) Pre-process all S1 images in L1_DIR:
Requirements: https://github.com/jlo031/S1_processing

- extract features
- make RGBs for labelme
- 
*S1_preprocess_image.py*
*S1_preprocess_image_list.sh (for batch processing)*

### (3) Label ice types and open water for each image:
Requirements: https://github.com/jlo031/labelme_utils

*S1_convert_image_json_2_training_mask.py*
*S1_convert_image_list_json_2_training_mask.py* (for batch processing)

### (4) Train and classify images:
Requirements: https://github.com/jlo031/GLIA

*S1_train_and_classify_image.py*
