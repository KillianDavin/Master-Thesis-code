import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import rasterio
import rasterstats
import numpy as np
import rasterio.plot
from zipfile import ZipFile
from rasterio.plot import show_hist

######################################################################################

''' 

This python script is the code used to overlay the country boundaries, ecoregion shapefiles and mapSPAM physical area raster 
files. Leading on from this, the land use characterisation factors and land area shares at the ecoregion level are aggregated and weighted to the national 
level according to the Exiobase country classifications and as described in Section 2.7 
of the method section of the master thesis main body . This python has 4 sections and are as follows: 

Section 1: Ovrelaying Country layer shapefile from the Natural Earth with ecoregion maps of the world from Olson et al. 
Section 2: Reading MapSPAM raster for physical production areas (hectares) for the 42 crops and transforming to EPSG format for overlaying with the shapefile calculated in Section 1
Section 3: Aggregation of MapSPAM crop categories to FAO/EXIOBASE categories and normalisation of crop names with FAO 
Section 4: Calculation of country level CFs by land area weighting of individual ecoregions for the 8 crop categories


'''

#####################################################################################

''' 
Section 1 - Ovrelaying Country layer shapefile from the Natural Earth with ecoregion maps of the world from Olson et al. 

'''

#####################################################################################

### countries shape file ###

### Read in natural earth shapefile using Geopandas library ###

### Read in from local computer - Replace if user is running this scipt with new file location ###

countries_layer = gpd.read_file('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Country_subunits/ne_10m_admin_0_map_subunits.shp')
countries_layer = countries_layer[['NE_ID','ADMIN','geometry']]
countries_layer = gpd.GeoDataFrame(countries_layer)


### ecoregions shape file ###

### Read in ecoregion shapefile using Geopandas library ###

### Read in from local computer - Replace if user is running this scipt with new file location ###

ecoregions_layer = gpd.read_file('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/WWF_ecoregions/wwf_terr_ecos.shp')
ecoregions_layer = gpd.GeoDataFrame(ecoregions_layer[['OBJECTID','ECO_NAME','eco_code','geometry']])


#### Inspecting the 'lake' and 'rock and ice' ecoregions - included as terrestrial habitat in WWF shapefile - removed accordingly in following code #####

ecoregions_layer = ecoregions_layer[ecoregions_layer.eco_code != 'Lake']   # removal of lake habitats from ecoregion shapefile
ecoregions_layer = ecoregions_layer[ecoregions_layer.eco_code != 'Rock and Ice'] #removal of rock and ice from ecoregion shapefile

### Overlaying ecoregion and country layers via the intersection tool in Geopandas to form one layer ###

res_intersection = countries_layer.overlay(ecoregions_layer, how='intersection')
Int_terrestrial_map = res_intersection
Int_terrestrial_map = pd.DataFrame(Int_terrestrial_map)
Crops_Data_frame = pd.DataFrame(Int_terrestrial_map)

#####################################################################################

''' 

Section 2 - Reading MapSPAM raster for physical production areas (hectares) for the 42 crops and transforming to 
            EPSG format for overlaying with the shapefile calculated in Section 1 using python library rasterio.
            Raster stats for each polygon are then calculated using the rasterstats library.   
            
'''

#####################################################################################


### Opening of Raster ZIP files, removing 0 entries from raster series, transform raster file to EPSG format, complete zonal statistics calculations ###

zip_file_directory = 'C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/SPAM files/spam2010v2r0_global_phys_area.geotiff.zip'
with ZipFile(zip_file_directory, 'r') as zip:
    for crop_raster in zip.namelist():
        if crop_raster[-5:] == 'A.tif':   #A = all technologies together, ie complete crop. See MapSPAM ReadME file if unsure to what technologies mean (https://doi.org/10.7910/DVN/PRFF8V)
            crops = zip.extract(crop_raster)
            crops = rasterio.open(crops)
            crops_array = crops.read(1)
            ndval = crops.nodata
            crops_array = crops_array.astype('float64')
            crops_array[crops_array == ndval] = np.nan
            affine = crops.transform
            total_crop_area = rasterstats.zonal_stats(Int_terrestrial_map, crops_array, affine=affine, stats=['sum']) # Sum of crop area in each polygon of 'Int_terrestrial_map' from section 1
            new_list = [i["sum"] for i in total_crop_area]
            Crops_Data_frame[crop_raster[-10:-6]] = new_list
            Crops_Data_frame[crop_raster[-10:-6]] = Crops_Data_frame[crop_raster[-10:-6]].replace(np.nan, 0)    # replacing nan values with 0n according to LCA methodology
            Crops_Data_frame[crop_raster[-10:-6]] = Crops_Data_frame[crop_raster[-10:-6]] / 100   #hectares to km2
            crops.close()



#####################################################################################

''' 

Section 3 - Aggregation of MapSPAM crop categories to FAO/EXIOBASE categories and normalisation of crop names with FAO   

'''

#####################################################################################


''' 
Notes: Olives contained within oil seeds crops category in MAPSpam but in Vegetables sub category in FAO/Exiobase
       Crops_Nec production includes nuts and sugar nes in MapSPAM but are included in EXIOBASE categories 'Vegetables, fruits & nuts' and 'Sugar' respectively

Notes: Vegetables, fruits & nuts missing land area for nuts and olives due to aggregation in MapSpam with crops_nec category
       Sugar category missing Sugar Nes 
       MapSPAM's Crops_nec category includes nuts and sugar nes and therefore overestimates land areas in certain ecoregions'''

########################################################################################################################
### MapSPAM crop names - See (https://doi.org/10.5194/essd-12-3545-2020) for more detail ###

### Aggregating MapSPAM categories to those of EXIOBASE ###

Rice = ['RICE']
Wheat = ['WHEA']
Cereal_grains_Nec = ['MAIZ', 'BARL', 'PMIL', 'SMIL', 'SORG', 'OCER' ]
Fruit = ['BANA','PLNT','TROF','TEMF','CNUT']
Nuts = []
Vegetables = ['VEGE']  #Crops should be in
Roots_and_tubers = ['POTA', 'SWPO', 'YAMS', 'CASS', 'ORTS']
Pulses = ['BEAN','CHIC', 'COWP', 'PIGE', 'LENT', 'OPUL']
Sugar = ['SUGC', 'SUGB']   #sugar nes not in SPAM individually
Oil_seeds = ['SOYB','GROU', 'OILP', 'SUNF', 'RAPE','SESA','OOIL','COTT'] #olives contained within oil seed crops
Plant_based_fibres = ['OFIB']
Crops_nec = ['ACOF', 'RCOF', 'COCO', 'TEAS','TOBA', 'REST' ]  #includes nuts category and Sugar Nes
Crops_nec_misc = ['REST']
Crops_nec_commodity = ['ACOF', 'RCOF', 'COCO', 'TEAS','TOBA']

categories = [Rice, Wheat, Cereal_grains_Nec, Fruit, Vegetables, Roots_and_tubers, Pulses, Sugar, Oil_seeds, Plant_based_fibres, Crops_nec, Crops_nec_misc, Crops_nec_commodity ]
categories_str = ['Paddy Rice','Wheat','Cereal grains Nec' , 'Fruit',  'Vegetables' , 'Roots_and_tubers', 'Pulses', 'Sugar', 'Oil_seeds', 'Plant_based_fibres', 'Crops_nec', 'Crops_nec_misc', 'Crops_nec_commodity' ]
Production_df = pd.DataFrame(Crops_Data_frame.iloc[:,0:6 ])
count = 0
for category in categories:
    New_df = pd.DataFrame(Crops_Data_frame[category].values.sum(1))
    New_df = pd.DataFrame(New_df)
    Production_df[categories_str[count]] = New_df.iloc[:,0].values
    count += 1

Production_df['Vegetables, fruit, nuts'] = Production_df['Fruit'].values + Production_df['Pulses'].values + Production_df['Roots_and_tubers'].values + Production_df['Vegetables'].values  #missing nuts and olives
del Production_df['Fruit']
del Production_df['Pulses']
del Production_df['Roots_and_tubers']
del Production_df['Vegetables']
del Production_df['Unnamed: 0']
del Production_df['Crops_nec_misc']
del Production_df['Crops_nec_commodity']
column_headings = list(Production_df.columns)


#####################################################################################

''' 

Section 4: Calculation of country level CFs by land area weighting of individual ecoregions for the 8 crop categories   

'''

#####################################################################################

### Calculation of total crop area of each crop per country

Total_production_per_country = Production_df.groupby(['ADMIN']).sum(0)
Total_production_per_country.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/total_production_area_per_country.csv')
Total_production_per_country = Total_production_per_country.loc[:, ['Paddy Rice', 'Wheat',
       'Cereal grains Nec', 'Sugar', 'Oil_seeds', 'Plant_based_fibres',
       'Crops_nec', 'Vegetables, fruit, nuts']]

### Calculation of production shares per ecoregion, per country, based on total production area of each crop in that country ###

Total_share_of_country_production = pd.DataFrame(Production_df.loc[:, ['Paddy Rice', 'Wheat',
       'Cereal grains Nec', 'Sugar', 'Oil_seeds', 'Plant_based_fibres',
       'Crops_nec', 'Vegetables, fruit, nuts']].values, index = Production_df['ADMIN'].values, columns = ['Rice', 'Wheat',
       'Cereal grains Nec', 'Sugar', 'Oil_seeds', 'Plant_based_fibres',
       'Crops_nec', 'Vegetables, fruit, nuts'])
Unique_countries = set(Production_df['ADMIN'].values)
for country in Unique_countries :
    vector = np.array(Total_production_per_country.loc[country,:].values)
    Total_share_of_country_production.loc[country,:] = np.divide(np.array(Total_share_of_country_production.loc[country,:].values),vector)

Production_shares = Production_df

Production_shares.loc[:,['Paddy Rice', 'Wheat',
       'Cereal grains Nec', 'Sugar', 'Oil_seeds', 'Plant_based_fibres',
       'Crops_nec', 'Vegetables, fruit, nuts']] = Total_share_of_country_production.iloc[:,:].values

Production_shares = pd.DataFrame(Production_shares).replace(np.nan, 0)
Production_shares.set_index('eco_code',  inplace=True)
Production_shares.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/Land_shares_per_crop_per_country_per_polygon.csv')


##### Opening LC-IMPACT land use CF data and cleaning LC-IMPACT land use CF excel file for data manipulation ##################

### Read in from local computer - Replace if user is running this scipt with new file location ###

Land_CF_updated = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/CF sheets/Land_characterisation_thesis/CFs_land_Use_average.xlsx')

for n in Land_CF_updated.sheet_names:
    if n == 'occupation average ecoregion':
        Average_CF_df = Land_CF_updated.parse(sheet_name=n)

new_index = Average_CF_df.iloc[3:,0].values
land_types = ['Annual crops', 'Permanent crops', 'Pasture', 'Urban', 'Extensive forestry', 'Intensive forestry']
column_index1 = []
for i in range(len(land_types)):
    column_index1 += [land_types[i]]*3

column_index2 = Average_CF_df.iloc[1,1:].values
Average_CF_df = pd.DataFrame(Average_CF_df.iloc[3:,1:].values, index = new_index, columns = [column_index1, column_index2])
Average_CF_df = Average_CF_df.astype(float)
Average_CF_df = pd.DataFrame(Average_CF_df).replace(np.nan, 0)
Average_CF_df = Average_CF_df.rename_axis(['eco_code'])
Average_CF_df = Average_CF_df.rename_axis(['Land type', 'Confidence interval'], axis = 1)
Land_CF_updated.close()

#### Removing ecocode rows not present in LC-IMPACT and where no crops are grown  ####

Annual_crops = ['Paddy Rice', 'Wheat','Cereal grains Nec', 'Sugar', 'Oil_seeds', 'Plant_based_fibres','Crops_nec']
Permanent_crops = ['Vegetables, fruit, nuts']
ecocodes = list(Average_CF_df.index)
ecocodes.remove('NT1318') #Not in Natural Earth Ecoregions shapefile from Olson et al.
missing_ecocodes = ['AT1301', 'NT0110', 'NA0301', 'NT0403', 'OC0204', 'OC0102', 'OC0107',
                    'AN1101', 'AT0720', 'AN1104', 'NT1311', 'AN1103', 'NT0123',
                    'OC0703', 'AN1102', 'OC0111']  #Ecoregions not covered in LC-IMPACT and that have no crops located within their boarders according to the SPAM model.

for ecocode in missing_ecocodes:
    Production_shares.drop(ecocode, inplace= True)  # removed ecocodes not present in LC-IMPACt and have no crops grown within its ecoregion area

### Calculation of the country level characterisation factors for the 8 crop categories ###

for land_type in [Annual_crops,Permanent_crops] :
    for ecocode in ecocodes:
        if land_type == Annual_crops:
            Production_shares.loc[ecocode,Annual_crops] = Production_shares.loc[ecocode,Annual_crops] * Average_CF_df.loc[ecocode, ('Annual crops','Median')]
        else:
            Production_shares.loc[ecocode,Permanent_crops] = Production_shares.loc[ecocode,Permanent_crops] * Average_CF_df.loc[ecocode, ('Permanent crops','Median')]

print(Production_shares.shape)

### checked production shares database, characterisation factor output database and all are correct and calculated as predicted ###
Production_shares.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/agri_CF_check.csv')


New_Land_CF = Production_shares.groupby(['ADMIN']).sum(0)
del New_Land_CF['NE_ID']
del New_Land_CF['OBJECTID']
del New_Land_CF['ECO_NAME']

### Outputed national CFs for land use ###

New_Land_CF.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/land_characterization_factors_ver02.csv')

