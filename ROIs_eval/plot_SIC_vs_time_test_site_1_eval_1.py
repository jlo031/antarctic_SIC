import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime


# Read the dates from "dates.txt"
with open("data/dates.txt", "r") as file:
    dates = file.read().splitlines()
    
# Convert the dates to a pandas datetime format
dates = pd.to_datetime(dates, format='%Y%m%d')

# Read the values from "OSISAF_SIC_test_site_1_eval_1.txt"
with open("data/OSISAF_SIC_test_site_1_eval_1.txt", "r") as file:
    OSISAF_SIC = file.read().splitlines()
    
# Convert values to float (assuming they are numerical)
OSISAF_SIC = [float(xx) for xx in OSISAF_SIC]

# Check if the lengths of dates and values match
if len(dates) != len(values):
    raise ValueError("The number of dates and values do not match!")
    
# Create a DataFrame for easier plotting
data = pd.DataFrame({'Date': dates, 'OSISAF_SIC': OSISAF_SIC})

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(data['Date'], data['OSISAF_SIC'], marker='o', linestyle='-', color='b')
plt.title('Test Site 1, Eval 1, SIC 2025')
plt.xlabel('Date')
plt.ylabel('SIC (%)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()













import matplotlib.pyplot as plt
from datetime import datetime

# Read the dates from "dates.txt"
with open("data/dates.txt", "r") as file:
    dates = file.read().splitlines()

# Convert the dates to datetime objects
dates = [datetime.strptime(date, '%Y%m%d') for date in dates]

# Read the values from "OSISAF_SIC_test_site_1_eval_1.txt"
with open("data/OSISAF_SIC_test_site_1_eval_1.txt", "r") as file:
    OSISAF_SIC = file.read().splitlines()

# Convert values to float (assuming they are numerical)
OSISAF_SIC = [float(xx) for xx in OSISAF_SIC]

# Check if the lengths of dates and values match
if len(dates) != len(OSISAF_SIC):
    raise ValueError("The number of dates and values do not match!")

# Plot the data
plt.figure(figsize=(10, 6))
plt.plot(dates, OSISAF_SIC, marker='o', linestyle='-', color='b')
plt.plot(dates, S1_SIC, marker='o', linestyle='-', color='r')
plt.title('Test Site 1, Eval 1, SIC 2025')
plt.xlabel('Date')
plt.ylabel('SIC (%)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()




# -------------------------------------------------------------------------- #

# NO PANDAS
# READ ALL FROM SAME FILE


import matplotlib.pyplot as plt
from datetime import datetime

# File path
file_path = "data/test_site_1_eval_1_all_SIC.txt"  # Replace with the path to your file

# Initialize lists to store dates and values
dates = []
OSISAF_SIC = []
S1_SIC = []
QC = []

# Read the file line by line
with open(file_path, "r") as file:
    for line in file:
        # Split each line into date and value
        date_str, value1_str, value2_str, QC_str = line.split()
        
        # Convert date to datetime object and value to float
        date = datetime.strptime(date_str, '%Y%m%d')
        value1 = float(value1_str)
        value2 = float(value2_str)

        
        # Append to lists
        dates.append(date)
        OSISAF_SIC.append(value1)
        S1_SIC.append(value2)
        QC.append(QC_str)

# Plot the data
plt.figure(figsize=(12, 5))
plt.plot(dates, OSISAF_SIC, marker='o', linestyle='--', color='b')
plt.plot(dates, S1_SIC, marker='o', linestyle='--', color='r')
plt.title('Test Site 1, Eval 1, SIC 2025')
plt.xlabel('Date')
plt.ylabel('SIC (%)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.legend(['OSISAF SIC', 'Sentinel-1 SIC'])
plt.show()




plt.figure(figsize=(12, 5))

plt.plot(dates, OSISAF_SIC, marker='o', linestyle='--', color='b')
plt.plot(dates, S1_SIC, marker='o', linestyle='--', color='r')

plt.title('Test Site 1, Eval 1, SIC 2025', fontsize=16, fontweight='bold')  # Bold and larger title

plt.ylabel('SIC (%)', fontsize=16, fontweight='bold')  # Bold and larger y-axis label
plt.grid(True)

plt.xticks(rotation=45, fontsize=16, fontweight='bold')  # Larger tick labels (bold not supported for ticks)
plt.yticks(fontsize=16, fontweight='bold')  # Bold and larger y-tick labels

plt.legend(['OSISAF SIC', 'Sentinel-1 SIC'], loc='upper left', prop={'weight': 'bold', 'size': 14})  # Bold and larger legend text

plt.tight_layout()


plt.savefig("SIC_time_series_2025_test_site_1_eval_1.png", transparent=True, dpi=300)
plt.show()








# -------------------------------------------------------------------------- #
