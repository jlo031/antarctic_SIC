
gdal_translate -projwin 2911.3239646634697 99.70287567767575 2961.1754076269785 49.851437751086735 -of GTiff "NETCDF:"""/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/OSISAF/ice_conc_sh_polstere-100_amsr2_202501301200.nc""":ice_conc" /home/581/jl0818/work/antarctic_SIC/ROIs_eval/OUTPUT.tif


# WORKS!!!
gdal_translate -projwin 2911.3239646634697 99.70287567767575 2961.1754076269785 49.851437751086735 -of GTiff "NETCDF:"""/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/OSISAF/ice_conc_sh_polstere-100_amsr2_202507261200.nc""":ice_conc" /home/581/jl0818/work/antarctic_SIC/ROIs_eval/tmp/OSISAF_SIC_20250726.tif


gdal_translate -projwin 2911.3239646634697 99.70287567767575 2961.1754076269785 49.851437751086735 -of GTiff "NETCDF:"""/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/OSISAF/ice_conc_sh_polstere-100_amsr2_202507261200.nc""":ice_conc" /home/581/jl0818/work/antarctic_SIC/ROIs_eval/TEST_20250726.tif

gdal_translate -projwin 2911.3239646634697 99.70287567767575 2961.1754076269785 49.851437751086735 -of GTiff "NETCDF:"""/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/OSISAF/ice_conc_sh_polstere-100_amsr2_202507261200.nc""":ice_conc" /home/581/jl0818/work/antarctic_SIC/ROIs_eval/TEST_20250726.tif

gdal_translate -projwin 2911.3239646634697 99.70287567767575 2961.1754076269785 49.851437751086735 -of GTiff "NETCDF:"""/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/OSISAF/ice_conc_sh_polstere-100_amsr2_202507261200.nc""":ice_conc" /home/581/jl0818/work/antarctic_SIC/ROIs_eval/TEST_20250726.tif


gdal_translate -of GTiff NETCDF:"/g/data/jk72/jl0818/DATA/SIC_comparison/satellite_data/OSISAF/ice_conc_sh_polstere-100_amsr2_202507261200.nc":ice_conc /home/581/jl0818/work/antarctic_SIC/ROIs_eval/TEST2_20250726_raw.tif

gdalwarp -t_srs EPSG:3031 -tr 10000 10000 -r bilinear /home/581/jl0818/work/antarctic_SIC/ROIs_eval/TEST2_20250726_raw.tif /home/581/jl0818/work/antarctic_SIC/ROIs_eval/TEST2_20250726_rawepsg_3031.tif
