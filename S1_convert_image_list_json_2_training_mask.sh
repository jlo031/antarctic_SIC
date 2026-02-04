#!/bin/bash

img_list="image_lists/test_site_1_full_image_list_2025.txt"
labels_file="config/labels.txt"
n_img=`cat ${img_list} | wc -l`
counter=0

echo " "
echo "Converting json to training masks for all scenes from image list"
echo "Image list has ${n_img} entries"


for f in `cat ${img_list}`; do

    # Increase counter
    let counter+=1

    echo " "
    echo "Processing image ${counter}/${n_img} "
    echo "Processing ${f}"
    echo " "

    conda run -n labelme python S1_convert_image_json_2_training_mask.py ${f} ${labels_file}

done 
