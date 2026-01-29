#!/bin/bash

# Paths to the folders to be cleaned up
FEAT_FOLDER_PATH="/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/Sentinel-1/features/ML_5x5"
RGB_FOLDER_PATH="/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/Sentinel-1/RGB/ML_5x5"
GEO_FOLDER_PATH="/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/Sentinel-1/geocoded"

# Path to the text file containing the list of directory names
IMAGE_LIST_FILE_1="/home/581/jl0818/work/antarctic_SIC/image_lists/test_site_1_orbit_056_image_list_2025.txt"
IMAGE_LIST_FILE_2="/home/581/jl0818/work/antarctic_SIC/image_lists/test_site_1_orbit_158_image_list_2025.txt"
IMAGE_LIST_FILE_3="/home/581/jl0818/work/antarctic_SIC/image_lists/test_site_2_orbit_086_image_list_2025.txt"
IMAGE_LIST_FILE_4="/home/581/jl0818/work/antarctic_SIC/image_lists/test_site_2_orbit_159_image_list_2025.txt"

COMBINED_IMAGE_LIST_FILE="/home/581/jl0818/work/antarctic_SIC/image_lists/combined_image_list_2025.txt"

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

rm -rf $COMBINED_IMAGE_LIST_FILE
touch $COMBINED_IMAGE_LIST_FILE
cat $IMAGE_LIST_FILE_1 $IMAGE_LIST_FILE_2 $IMAGE_LIST_FILE_3 $IMAGE_LIST_FILE_4 > $COMBINED_IMAGE_LIST_FILE

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# CLEAN UP FEATURE FOLDER

# Loop through all directories in the folder
for dir in "$FEAT_FOLDER_PATH"/*/; do

    # Get the directory name without the path
    DIR_NAME=$(basename "$dir")

    # Check if the directory name is in the image_list.txt file
    if ! (grep -qx "$DIR_NAME".SAFE "$COMBINED_IMAGE_LIST_FILE"); then

        echo "Directory '$DIR_NAME' is not in either list. Deleting..."
        rm -rf "$dir" # Delete the directory

    else
        echo "Directory '$DIR_NAME' is in the list. Keeping it."
    fi

done

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# CLEAN UP RGB FOLDER

# Loop through all files in the folder
for file in "$RGB_FOLDER_PATH"/*; do

    # Check if the file ends with "rgb.json" or "rgb.tif"
    if [[ "$file" == *_rgb.json || "$file" == *_rgb.tif ]]; then

        # Remove the ending ".rgb.json" or ".rgb.tif" to get the base file name
        BASE_NAME=$(basename "$file" | sed -E 's/\_(rgb\.json|rgb\.tif)$//')

        # Check if the base file name is in either of the text files
        if ! (grep -qx "$BASE_NAME".SAFE "$COMBINED_IMAGE_LIST_FILE"); then

            echo "File '$file' is not in either list. Deleting..."
            rm -f "$file" # Delete the file

        else
            echo "File '$file' is in the list. Keeping it."
        fi

    else
        echo "File '$file' does not match the pattern. Skipping."
    fi

done

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# CLEAN UP GEO FOLDER

# Loop through all files in the folder
for file in "$GEO_FOLDER_PATH"/*; do

    # Check if the file ends with "rgb.json" or "rgb.tif"
    if [[ "$file" == *__intensities__epsg_3031__pixelspacing_200.tiff ]]; then

        # Remove the ending ".rgb.json" or ".rgb.tif" to get the base file name
        BASE_NAME=$(basename "$file" | sed 's/__intensities__epsg_3031__pixelspacing_200\.tiff$//')

        # Check if the base file name is in either of the text files
        if ! (grep -qx "$BASE_NAME".SAFE "$COMBINED_IMAGE_LIST_FILE"); then

            echo "File '$file' is not in either list. Deleting..."
            rm -f "$file" # Delete the file

        else
            echo "File '$file' is in the list. Keeping it."
        fi

    else
        echo "File '$file' does not match the pattern. Skipping."
    fi

done

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #
