#!/bin/bash

# Path to json config file
json_config_file="config/config.json"

# Path to image_list_file
img_list_file="config/full_L1_image_list.txt"

# Extract paths using jq
DATA_DIR=$(jq -r '.DATA_DIR' "$json_config_file")
satellite_data=$(jq -r '.sub_dirs.satellite_data' "$json_config_file")
S1=$(jq -r '.sub_dirs.sat_data_subdirs.S1' "$json_config_file")
L1=$(jq -r '.sub_dirs.sat_data_subdirs.S1_subdirs.L1' "$json_config_file")

# Concatenate paths
S1_L1_DIR="$DATA_DIR/$satellite_data/$S1/$L1"

# Delete output file if it exists
if [ -f "$img_list_file" ]; then
    rm "$img_list_file"
fi

if [ -d "$S1_L1_DIR" ]; then
    for file in "$S1_L1_DIR"/*; do
        filename=$(basename "$file")
	echo "${filename%.*}" >> "$img_list_file"
    done
    echo "File list written to '$img_list_file'"
else
    echo "Directory "$S1_L1_DIR" does not exist"
fi
