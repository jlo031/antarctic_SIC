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
S1_base      = "S1A_EW_GRDM_1SDH_20250103T134351_20250103T134451_057280_070C0E_3D46"

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

# write final labels to file

final_labels = y_pred_img1

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






# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #


training_path   = S1_TRAIN_DIR / f"ML_{ML}" / f"{S1_base}_rgb_training_mask.img"



















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

    class_colors = [
        [0.0,0.0,1.0],
        [0.0,0.5,0.8],
        [1.0,1.0,0.0],
        [0.7,0.7,0.0],
        [1.0,1.0,1.0],
        [0.0,1.0,0.0],
        [1.0,1.0,1.0]
    ]

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

    # Get min and max training IA for linear fit
    IA_train_min  = int(np.floor(IA_train.min()))
    IA_train_max  = int(np.ceil(IA_train.max()))
    IA_linear_fit = np.linspace(IA_train_min, IA_train_max, IA_train_max-IA_train_min+1)

    # Get unique class labels
    unique_classes = np.unique(y_train)

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #

    X_train = np.stack((HH_train, HV_train),1)

    clf1 = GLIA.gaussian_clf()
    clf2 = GLIA.GLIA_clf()

    clf1.fit(X_train, y_train)
    clf2.fit(X_train, y_train, IA_train)


    # Stack full iamge data to feature vector X
    X_vec = np.stack((HH.ravel(), HV.ravel()),1)
    IA_vec = IA.ravel()

    y_pred1, p1 = clf1.predict(X_vec)
    y_pred2, p2 = clf2.predict(X_vec, IA_vec)

    y_pred_img1 = y_pred1.reshape(HH.shape)
    y_pred_img2 = y_pred2.reshape(HH.shape)

    y_pred_img1[swath_mask==0] = 0
    y_pred_img2[swath_mask==0] = 0

# --------------------------------------------------------------------------- #
# --------------------------------------------------------------------------- #



# END HERE #

# S1 scene to process

S1_base = "S1A_EW_GRDM_1SDH_20250807T134446_20250807T134522_060430_078315_2E29"
S1_base = "S1A_EW_GRDM_1SDH_20250814T133614_20250814T133710_060532_078718_29BF"
S1_base = "S1A_EW_GRDM_1SDH_20250824T135254_20250824T135337_060678_078CDC_E5C7"
S1_base = "S1A_EW_GRDM_1SDH_20250910T140036_20250910T140136_060926_0796B9_F0EF"
S1_base = "S1A_EW_GRDM_1SDH_20251006T134447_20251006T134523_061305_07A5F3_CC49"
S1_base = "S1A_EW_GRDM_1SDH_20251009T140915_20251009T141007_061349_07A7BD_2EE0"
S1_base = "S1A_EW_GRDM_1SDH_20251020T132824_20251020T132857_061509_07AE24_885C"
S1_base = "S1A_EW_GRDM_1SDH_20251021T140915_20251021T141006_061524_07AEC5_98AC"
S1_base = "S1A_EW_GRDM_1SDH_20251025T133614_20251025T133711_061582_07B115_0053"
S1_base = "S1A_EW_GRDM_1SDH_20251028T140036_20251028T140136_061626_07B2E1_76DA"
S1_base = "S1A_EW_GRDM_1SDH_20251030T134446_20251030T134523_061655_07B407_92A4"
S1_base = "S1A_EW_GRDM_1SDH_20250301T145621_20250301T145726_058112_072D50_F0F9"

# Set S1 processing parameters
ML              = '5x5'
loglevel        = 'INFO'
overwrite       = True
training_format = "ENVI"

# path to labels file
labels_path = WORK_DIR / "config" / "labels.txt"


# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

sub = 5

fig, axes = plt.subplots(2,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HH[::sub,::sub], vmin=-30, vmax=-5, cmap="gray")
axes[1].imshow(HV[::sub,::sub], vmin=-35, vmax=-10, cmap="gray")
axes[2].imshow(training_mask[::sub,::sub])
axes[3].imshow(swath_mask[::sub,::sub])

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

fig, axes = plt.subplots(1,2)
axes = axes.ravel()
for cl in unique_classes:
    axes[0].plot(IA_train[y_train==cl], HH_train[y_train==cl], ".", color=class_colors[cl-1])
    axes[1].plot(IA_train[y_train==cl], HV_train[y_train==cl], ".", color=class_colors[cl-1])


plt.show()

# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #



X_train = np.stack((HH_train, HV_train),1)

clf1 = GLIA.gaussian_clf()
clf2 = GLIA.GLIA_clf()

clf1.fit(X_train, y_train)
clf2.fit(X_train, y_train, IA_train)



fig, axes = plt.subplots(1,2)
axes = axes.ravel()
for cl in unique_classes:
    axes[0].plot(IA_train[y_train==cl], HH_train[y_train==cl], ".", color=class_colors[cl-1])
    axes[1].plot(IA_train[y_train==cl], HV_train[y_train==cl], ".", color=class_colors[cl-1])
    HH_linear_fit = clf2.a[cl-1,0] + clf2.b[cl-1,0] * IA_linear_fit
    HV_linear_fit = clf2.a[cl-1,1] + clf2.b[cl-1,1] * IA_linear_fit
    axes[0].plot(IA_linear_fit, HH_linear_fit, color=class_colors[cl-1])
    axes[1].plot(IA_linear_fit, HV_linear_fit, color=class_colors[cl-1])

plt.show()





# Stack full iamge data to feature vector X
X_vec = np.stack((HH.ravel(), HV.ravel()),1)
IA_vec = IA.ravel()

y_pred1, p1 = clf1.predict(X_vec)
y_pred2, p2 = clf2.predict(X_vec, IA_vec)

y_pred_img1 = y_pred1.reshape(HH.shape)
y_pred_img2 = y_pred2.reshape(HH.shape)

y_pred_img1[swath_mask==0] = 0
y_pred_img2[swath_mask==0] = 0



sub = 2

fig, axes = plt.subplots(2,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HH[::sub,::sub], vmin=-30, vmax=-5, cmap="gray")
axes[1].imshow(HV[::sub,::sub], vmin=-35, vmax=-10, cmap="gray")
axes[2].imshow(y_pred_img1[::sub,::sub])
axes[3].imshow(y_pred_img2[::sub,::sub])


# -------------------------------------------------------------------------- #
# -------------------------------------------------------------------------- #

# ---- End of <S1_training_mask.py> ----
