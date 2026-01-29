#!/bin/bash

img_list="image_lists/test_site_1_full_image_list_2025.txt"
n_img=`cat ${img_list} | wc -l`
counter=0

echo " "
echo "Pre-processing all scenes from image list"
echo "Image list has ${n_img} entries"

for f in `cat ${img_list}`; do

    # Increase counter
    let counter+=1

    echo " "
    echo "Processing image ${counter}/${n_img} "
    echo "Processing ${f}"
    echo " "

    conda run -n SAR_PM_SIC python S1_preprocess_image.py ${f} -make_RGB -get_lat_lon

done 
