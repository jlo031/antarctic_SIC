# ---- This is <S1_classify_image.py> ----

"""
Extract training data, train classifier, and classify image.
"""

import sys
import pathlib

from loguru import logger

import numpy as np
import matplotlib.pyplot as plt
from osgeo import gdal

import GLIA_classifier.gaussian_linear_IA_classifier as GLIA

from config.load_config import *

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# S1 input image 
S1_base      = "S1A_EW_GRDM_1SDH_20250421T134349_20250421T134449_058855_074B5A_17D9"

# Currently fixed parameters
labels_path  = pathlib.Path("config/labels.txt").resolve()
ML           = "5x5"
overwrite    = True
loglevel     = "DEBUG"

# Define class colors
class_colors = [
    [0.0,0.0,1.0],
    [0.0,0.5,0.8],
    [1.0,1.0,0.0],
    [0.7,0.7,0.0],
    [1.0,1.0,1.0],
    [0.0,1.0,0.0],
    [1.0,1.0,1.0]
]

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

logger.remove()
logger.add(sink=sys.stdout, level=loglevel)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

logger.info(f"Processing image: {S1_base}")

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

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# Build paths to training and image data
training_path   = S1_TRAIN_DIR / f"ML_{ML}" / f"{S1_base}_rgb_training_mask.img"
HH_path         = S1_FEAT_DIR / f"ML_{ML}" / f"{S1_base}" / "Sigma0_HH_dB.img"
HV_path         = S1_FEAT_DIR / f"ML_{ML}" / f"{S1_base}" / "Sigma0_HV_dB.img"
IA_path         = S1_FEAT_DIR / f"ML_{ML}" / f"{S1_base}" / "IA.img"
swath_mask_path = S1_FEAT_DIR / f"ML_{ML}" / f"{S1_base}" / "swath_mask.img"

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# Load data and extract training
training_mask = gdal.Open(training_path).ReadAsArray()
swath_mask    = gdal.Open(swath_mask_path).ReadAsArray()
IA            = gdal.Open(IA_path).ReadAsArray()
HH            = gdal.Open(HH_path).ReadAsArray()
HV            = gdal.Open(HV_path).ReadAsArray()

# Extract training data
HH_train = HH[training_mask!=0]
HV_train = HV[training_mask!=0]
IA_train = IA[training_mask!=0]
sm_train = swath_mask[training_mask!=0]
y_train  = training_mask[training_mask!=0]

# Combine to X_train
X_train = np.stack((HH_train, HV_train),1)

# Get min and max training IA for linear fit
IA_train_min  = int(np.floor(IA_train.min()))
IA_train_max  = int(np.ceil(IA_train.max()))
IA_linear_fit = np.linspace(IA_train_min, IA_train_max, IA_train_max-IA_train_min+1)

# Get unique class labels
unique_classes = np.unique(y_train)

logger.debug(f"Classes in training set: {unique_classes}")
logger.debug(f"Dimensions of training feature vector: {X_train.shape}")
logger.debug(f"Dimensions of training label vector:   {y_train.shape}")

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# Train a Gaussian clf and/or GLIA clf

logger.info("Training Gaussian classifier")
clf1 = GLIA.gaussian_clf()
clf1.fit(X_train, y_train)

logger.info("Training GLIA classifier")
clf2 = GLIA.GLIA_clf()
clf2.fit(X_train, y_train, IA_train)

# -------------------------------------------- #

# Stack full iamge data to feature vector X

logger.info("Stacking channels to feature vectors")
X_vec = np.stack((HH.ravel(), HV.ravel()),1)
IA_vec = IA.ravel()

# -------------------------------------------- #

# Predict labels

# Initialize full label vectors
y_pred1 = np.zeros((len(X_vec),))
y_pred2 = np.zeros((len(X_vec),))

# Split in the middle and only predict half of the image at the time
middle_index = X_vec.shape[0] //2 

logger.info("Predicting labels for Gaussian classifier")
y_pred1[:middle_index], p1 = clf1.predict(X_vec[:middle_index,:])
y_pred1[middle_index:], p1 = clf1.predict(X_vec[middle_index:,:])

logger.info("Predicting labels for GLIA classifier")
y_pred2[:middle_index], p2 = clf2.predict(X_vec[:middle_index,:], IA_vec[:middle_index])
y_pred2[middle_index:], p2 = clf2.predict(X_vec[middle_index:,:], IA_vec[middle_index:])


# -------------------------------------------- #

# Reshape into image dimensions

logger.info("Reshaping results to image dimensions")
y_pred_img1 = y_pred1.reshape(HH.shape)
y_pred_img2 = y_pred2.reshape(HH.shape)

y_pred_img1[swath_mask==0] = 0
y_pred_img2[swath_mask==0] = 0

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# OVERLAY PRE-SELECTED ICE-WATER MASK FROM LABELME

##training_path = S1_TRAIN_DIR / f"ML_{ML}" / f"{S1_base}_rgb_training_mask.img"

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

sub = 5

fig, axes = plt.subplots(2,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HH[::sub,::sub], vmin=-30, vmax=-5, cmap="gray")
axes[1].imshow(HV[::sub,::sub], vmin=-35, vmax=-10, cmap="gray")
axes[2].imshow(training_mask[::sub,::sub])
axes[3].imshow(swath_mask[::sub,::sub])

# -------------------------------------------- #

fig, axes = plt.subplots(1,2)
axes = axes.ravel()
for cl in unique_classes:
    axes[0].plot(IA_train[y_train==cl], HH_train[y_train==cl], ".", color=class_colors[cl-1])
    axes[1].plot(IA_train[y_train==cl], HV_train[y_train==cl], ".", color=class_colors[cl-1])
    
# -------------------------------------------- #

fig, axes = plt.subplots(1,2)
axes = axes.ravel()
for cl in unique_classes:
    axes[0].plot(IA_train[y_train==cl], HH_train[y_train==cl], ".", color=class_colors[cl-1])
    axes[1].plot(IA_train[y_train==cl], HV_train[y_train==cl], ".", color=class_colors[cl-1])
    HH_linear_fit = clf2.a[cl-1,0] + clf2.b[cl-1,0] * IA_linear_fit
    HV_linear_fit = clf2.a[cl-1,1] + clf2.b[cl-1,1] * IA_linear_fit
    axes[0].plot(IA_linear_fit, HH_linear_fit, color=class_colors[cl-1])
    axes[1].plot(IA_linear_fit, HV_linear_fit, color=class_colors[cl-1])

# -------------------------------------------- #

sub = 2

fig, axes = plt.subplots(2,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HH[::sub,::sub], vmin=-30, vmax=-5, cmap="gray")
axes[1].imshow(HV[::sub,::sub], vmin=-35, vmax=-10, cmap="gray")
axes[2].imshow(y_pred_img1[::sub,::sub])
axes[3].imshow(y_pred_img2[::sub,::sub])

# -------------------------------------------- #

plt.show()

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# SORT OUT FINAL LABELS

ice_tmp     = 99
water_tmp   = 98
no_data_tmp = 97

ice_final     = 1
water_final   = 0
no_data_final = 99

final_labels = np.zeros(HH.shape)

final_labels[y_pred_img1==1] = water_tmp
final_labels[y_pred_img1==2] = water_tmp
final_labels[y_pred_img1==3] = ice_tmp
final_labels[y_pred_img1==4] = ice_tmp
final_labels[y_pred_img1==5] = ice_tmp
final_labels[y_pred_img1==5] = ice_tmp
final_labels[y_pred_img1==6] = ice_tmp
final_labels[y_pred_img1==8] = ice_tmp

final_labels[final_labels==ice_tmp]     = ice_final
final_labels[final_labels==water_tmp]   = water_final

unique_final_labels = np.unique(final_labels)
logger.info(f"Unique final labels are: {unique_final_labels}")

plt.imshow(final_labels)
plt.show()

final_labels[HV==0] = no_data_final

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

# write final labels to file

labels_path = S1_DIR / "ice_water_labels" / f"{S1_base}_ice_water_labels.img"

# delete output file if it exists
if labels_path.is_file() and overwrite:
    logger.info('Removing existing output file')
    os.remove(labels_path.as_posix())
    os.remove(os.path.splitext(labels_path.as_posix())[0]+'.hdr')

# get dimensions
Ny, Nx = final_labels.shape

# set number of bands and data type
bands = 1
data_type =gdal.GDT_Byte
    
# get driver
output = gdal.GetDriverByName('Envi').Create(
    labels_path.as_posix(),
    Nx,
    Ny,
    bands,
    data_type
)

# write to file
output.GetRasterBand(1).WriteArray(final_labels)
output.FlushCache()

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

import geocoding.generic_geocoding as gen_geo
import geocoding.geocoding_utils as geo_utils

feat_folder = S1_FEAT_DIR / f"ML_{ML}" / f"{S1_base}"

target_epsg   = 3031
pixel_spacing = 200

lat_path         = feat_folder / "lat.img"
lon_path         = feat_folder / "lon.img"
output_tiff_path = S1_GEO_DIR / f"{S1_base}__ice_water_labels__epsg_{target_epsg}__pixelspacing_{pixel_spacing}.tiff"

gen_geo.geocode_image_from_lat_lon(
    labels_path,
    lat_path,
    lon_path,
    output_tiff_path,
    target_epsg,
    pixel_spacing,
    tie_points= 21,
    srcnodata = 99,
    dstnodata = 99,
    order = 3,
    resampling = 'near',
    keep_gcp_file = False,
    overwrite = overwrite,
    loglevel = loglevel,
)


# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <S1_training_mask.py> ----
