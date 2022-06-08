import io
from zipfile import ZipFile
import pandas as pd
import geopandas as gpd
import numpy as np
import matplotlib.pyplot as plt
import rasterio
import rasterstats
import numpy as np
import rasterio.plot
from zipfile import ZipFile
from rasterio.plot import show_hist
from rasterio.warp import calculate_default_transform, reproject, Resampling

######################################################################################

''' This python script is the code used to calculate total production of irrigated crops in Tonnes from the MapSPam model per Watershed layer. 
This is done by overlaying MapSPAM raster on top of Watershed shapefile (Pfister & Bayer 2018) and calculating zonal statistics i.e. total production  
mass (tonnes) per watershed layer/polygon.  
'''

#####################################################################################

### Open and clean pfister & bayer 2018 shapefile ###

zip_file_directory = 'C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Watershed data/WS_ctry.zip'
with ZipFile(zip_file_directory, 'r') as zip:
    for shapefile in zip.namelist():
        if shapefile [-4:] == '.shp':
            print(shapefile)
            watershed_file = zip.extract(shapefile)
            print(watershed_file)
            watershed_layer = gpd.read_file('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Watershed data/WaterGap_Countries.shp')
            print(watershed_layer.crs)
            print(watershed_layer.head(2))
            print(watershed_layer.shape)

watershed_layer = gpd.GeoDataFrame(watershed_layer, geometry = 'geometry')
Crops_Data_frame = pd.DataFrame(watershed_layer)

######################

'''Open and clean global production of irrigated crops MapSPAM raster file. 
Overlay raster on watershed layer, calculating zonal stats thereafter.'''

######################

zip_file_directory = 'C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/SPAM files/spam2010v2r0_global_prod.geotiff.zip'
with ZipFile(zip_file_directory, 'r') as zip:
    for crop_raster in zip.namelist():
        if crop_raster[-5:] == 'I.tif':
            crops = zip.extract(crop_raster)
            crops = rasterio.open(crops)
            crops_array = crops.read(1)
            ndval = crops.nodata
            crops_array = crops_array.astype('float64')
            crops_array[crops_array == ndval] = np.nan
            affine = crops.transform
            print(crops)
            total_crop_production = rasterstats.zonal_stats(watershed_layer, crops_array, affine=affine, stats=['sum'])
            print(type(total_crop_production))
            print(len(total_crop_production))
            print(len(watershed_layer))
            print(total_crop_production[0]['sum'])
            new_list = [i["sum"] for i in total_crop_production]
            print(new_list)
            print(len(new_list))
            Crops_Data_frame[crop_raster[-10:-6]] = new_list
            Crops_Data_frame[crop_raster[-10:-6]] = Crops_Data_frame[crop_raster[-10:-6]].replace(np.nan, 0)
            Crops_Data_frame[crop_raster[-10:-6]] = Crops_Data_frame[crop_raster[-10:-6]] * 10**6        # change units: mT to Tonnes
            print(Crops_Data_frame)
            crops.close()

### Aggregation of MapSPAM crop categories to FAO/EXIOBASE categories. Normalisation of names with FAO and WaterGAP ####

''' Notes: Olives contained within oil seeds crops category in MAPSpam but in Vegetables sub category in FAO/Exiobase
Crops_Nec production volumes contain nuts and sugar nes'''

########################################################################################################################
Crops_Data_frame.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/CHECk_IRRIGATED_CROPS.csv')

Paddy_rice = ['RICE']
Wheat = ['WHEA']
Cereal_grains_Nec = ['MAIZ', 'BARL', 'PMIL', 'SMIL', 'SORG', 'OCER' ]
Fruit = ['BANA','PLNT','TROF','TEMF','CNUT']
Nuts = []
Vegetables = ['VEGE']  #Crops should be in
Roots_and_tubers = ['POTA', 'SWPO', 'YAMS', 'CASS', 'ORTS']
Pulses = ['BEAN','CHIC', 'COWP', 'PIGE', 'LENT', 'OPUL']
Sugar = ['SUGC', 'SUGB']   #sugar nes not in SPAM individually
Oil_seeds = ['SOYB','GROU', 'OILP', 'SUNF', 'RAPE','SESA','OOIL'] #olives contained within oil seed crops
Plant_based_fibres = ['OFIB', 'COTT']   #Cotton just contained within Plant based fbres but not Oil seeds to avoid double counting
Crops_nec = ['ACOF', 'RCOF', 'COCO', 'TEAS','TOBA', 'REST' ]  #includes nuts category and Sugar Nes
Crops_nec_misc = ['REST']
Crops_nec_commodity = ['ACOF', 'RCOF', 'COCO', 'TEAS','TOBA']

categories = [Wheat, Paddy_rice,Cereal_grains_Nec, Fruit, Vegetables, Roots_and_tubers, Pulses, Sugar, Oil_seeds, Plant_based_fibres, Crops_nec, Crops_nec_misc, Crops_nec_commodity ]
categories_str = ['Wheat','Paddy_rice','cereal_grains_nec' , 'Fruit',  'Vegetables' , 'Roots_and_Tubers', 'Pulses', 'sugar', 'Oil_Seeds', 'Plant_Based_Fibres', 'Crops_Nec', 'Crops_nec_misc', 'Crops_nec_commodity' ]
Production_df = pd.DataFrame()
count = 0
for category in categories:
    New_df = pd.DataFrame(Crops_Data_frame[category]).sum(1)
    New_df = pd.DataFrame(New_df)
    Production_df[categories_str[count]] = New_df.iloc[:,0]
    count += 1
    print(Production_df)
Production_df.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/overlayed_layers_SPAM_production_irrigated_watersheds_to_FAO_categories.csv')
