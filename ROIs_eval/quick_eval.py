from osgeo import gdal
import numpy as np
import matplotlib.pyplot as plt

img = gdal.Open("tmp/S1_HHHV_20250719_test_site_1_eval_1.tif").ReadAsArray()

HV = img[1,:,:]

l = np.zeros(HV.shape)


# 4
l[HV>-24] = 1

#l[:,0:50] = 1
fig, axes = plt.subplots(1,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HV)
axes[1].imshow(l)
axes[0].set_title("-24")
print(f"-24: {l.mean()*100}")




# 1
l[HV>-28] = 1
fig, axes = plt.subplots(1,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HV)
axes[1].imshow(l)
axes[0].set_title("-28")
print(f"-28: {l.mean()*100}")


# 2
l[HV>-30] = 1
fig, axes = plt.subplots(1,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HV)
axes[1].imshow(l)
axes[0].set_title("-30")
print(f"-30: {l.mean()*100}")


# 3
l[HV>-32] = 1
fig, axes = plt.subplots(1,2,sharex=True, sharey=True)
axes = axes.ravel()
axes[0].imshow(HV)
axes[1].imshow(l)
axes[0].set_title("-32")
print(f"-32: {l.mean()*100}")


plt.show()




plt.show()
