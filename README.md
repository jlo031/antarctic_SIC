# 🧊 `antarctic_SIC`: Scripts & Workflow

Scripts and workflow for comparison of **Antarctic Sea Ice Concentration (SIC)** data derived from **Passive Microwave (PM)** and **Synthetic Aperture Radar (SAR)** imagery.

---

## 🛠️ Requirements & Installation

For the full workflow, you require a working **Python** (Anaconda/Miniconda) and **SNAP** installation.

### Python Environment Setup

Specific package requirements are listed for each step in the workflow. Except for `labelme`, most packages can be installed within a single environment.

You can follow the individual installation guides on the GitHub pages for each package, or use the following steps to install the environment:

1.  **Create and activate the environment:**
    ```bash
    # Create new environment with gdal
    conda create -y -n SAR_PM_SIC gdal

    # Activate the environment
    conda activate SAR_PM_SIC
    ```

2.  **Install required packages from conda-forge:**
    ```bash
    conda install -y -c conda-forge loguru requests lxml geojson geomet python-dotenv scipy scikit-learn pillow
    ```

3.  **Install personal packages from GitHub via pip:**
    ```bash
    pip install git+[https://github.com/jlo031/CDSE](https://github.com/jlo031/CDSE)
    pip install git+[https://github.com/jlo031/GLIA](https://github.com/jlo031/GLIA)
    pip install git+[https://github.com/jlo031/S1_processing.git](https://github.com/jlo031/S1_processing.git)
    ```

### Environment Variables (`.env` file)

The download option of the `CDSE` package and the SNAP `gpt` call of the `S1_processing` package require **environment variables**.

Store these variables in a local `.env` file in your working directory. The file contents should look like this:

```dotenv
CDSE_USER="your-CDSE-user-name"
CDSE_PASSWORD="your-CDSE-password"
GPT="/path/to/your/snap/bin/gpt"
```

---

## ⚙️ Configuration Setup

The general folder structure is defined in the **`config.json`** file and read using `load_config.py`.

> * You should only need to edit the **`config.json`**.
> * **Recommendation:** Only adjust the `"WORK_DIR"` and `"DATA_DIR"` variables and leave the dependent folder structure untouched, unless you know exactly what you are doing.

---

## 🚀 SAR Workflow Steps

### (1) Download S1 Images

This script finds and downloads Sentinel-1 (S1) products over selected test sites and time periods, placing them into the configured `S1_L1_DIR`.

* **Script:** `S1_query_and_download.py`
* **Action:** Define/adjust the time period for each test site **directly in the script**.
* **Requirement:** [CDSE](https://github.com/jlo031/CDSE)

### (2) Pre-process S1 Images

Pre-process all S1 images currently stored in the `S1_L1_DIR`.

* **Script (Single Image):** `S1_preprocess_image.py`
* **Script (Batch Processing):** `S1_preprocess_image_list.sh`
* **Requirement:** [S1\_processing](https://github.com/jlo031/S1_processing)

### (3) Label Ice Types

Label ice types (ice and water) in individual images.

* **Script:** `label_ice_types.sh`
* **Requirement:** [labelme\_utils](https://github.com/jlo031/labelme_utils)

### (4) Convert Label Files (json) to Label Masks

Convert the labels from the previous steps to full-sized label masks.

* **Script (Single Image):** `S1_convert_image_json_2_training_mask.py`
* **Script (Batch Processing):** `S1_convert_image_list_json_2_training_mask.py`
* **Requirement:** [labelme\_utils](https://github.com/jlo031/labelme_utils)

### (5) Train and classify images:

* **Script S1_train_and_classify_image.py**
* **! CURRENTLY IN DEVELOPMENT !**
* **Requirement: https://github.com/jlo031/GLIA**
