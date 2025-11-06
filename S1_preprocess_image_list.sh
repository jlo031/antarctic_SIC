#!/bin/bash
for f in `cat S1_image_list`; do

    echo " "
    echo "Processing ${f}"
    echo " "

    conda run -n S1_processing python S1_preprocess_single_image.py $f

done 
