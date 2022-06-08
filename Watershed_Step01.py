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

###
######################################################################################

''' 

This python script is the code used to overlay the water CF shapefile from LC-IMPACT with the Pfister & Bayer watershed shapefile 
(already merged shapefile of country and watershed layers). The file then cleans the BW_per_ton and BW_total excel files 
accompanying the watershed layer provided by pfister & Bayer and readying them for manipulation in further steps. 
The following 4 sections are included: 

Section 1: Convert LC-Impact water raster to EPSG format and complete zonal statistics for each watershed polygon in the pfister & bayer shapefile
Section 2: Treat and normalize Pfister & bayer  BW_per_ton and BW_total excel datasheets for the accompanying shapefile
Section 3: Treatment of missing watershed CFs
Section 4: Constructing proxy water consumption data for missing countries not included in pfister & bayer dataset



Note: BW = Blue water consumption
'''

#####################################################################################
''' 
Section 1: 

Read Pfister & bayer shapefile and LC-IMPACT watershed CFs raster file. 
Convert raster to EPSG format and complete zonal statistics for each watershed polygon in the pfister shapefile. 

'''
#####################################################################################

### Reading of WaterGAP (Stefan Pfister & Bayer 2018) shapefile for global crop watershed consumption maps = Watershed_layer ###

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


### Opening of LC-IMPACT Raster ZIP files, removing 0 entries from raster series, transform raster file to EPSG format, complete zonal statistics calculations ###

dstCrs = {'init': 'EPSG:4326'}

### Opening Tiff file and transforming tiff to geographic referencing system EPSG:4326 ###

with rasterio.open( 'C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/LC_Impact/CF_CORE_plants_noVS_and_animals_inclVS_noCpA_Option3_SW_PDF_perm3.tif') as water_PDF:
    #print(water_PDF.transform)
    transform, width, height = calculate_default_transform(water_PDF.crs, dstCrs, water_PDF.width, water_PDF.height, *water_PDF.bounds)
    #print(transform)
    kwargs = water_PDF.meta.copy()
    kwargs.update({
            'crs': dstCrs,
            'transform': transform,
            'width': width,
             'height': height })

    water_PDF_array = water_PDF.read()
    affine = water_PDF.transform
    #print(water_PDF_array.shape)
    #print(water_PDF.crs)


    with rasterio.open('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/LC_Impact/CF_CORE_plants_noVS_and_animals_inclVS_noCpA_Option3_SW_PDF_perm3.wgs84.tif', 'w', **kwargs) as dst:
        for i in range(1, water_PDF.count + 1):
            reproject(
                source=rasterio.band(water_PDF, i),
                destination=rasterio.band(dst, i),
                #water_PDF_transform=water_PDF.transform,
                water_PDF_crs=water_PDF.crs,
                #dst_transform=transform,
                dstCrs=dstCrs,
                resampling=Resampling.nearest)

            #print(dst.crs)
            dst.close()
            #print(dst.transform)

with rasterio.open('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/LC_Impact/CF_CORE_plants_noVS_and_animals_inclVS_noCpA_Option3_SW_PDF_perm3.wgs84.tif', 'r', **kwargs) as dst:
    dst_array = dst.read(1)
    ndval = dst.nodata
    dst_array = dst_array.astype('float64')
    dst_array[dst_array == ndval] = np.nan
    affine = dst.transform
    print(dst)
    print(dst_array)
    print(type(watershed_layer))

    ### Overlaying LC-IMPACT Tiff on WaterGAP - watershed layer - shapefile ###

    water_cf_factor = rasterstats.zonal_stats(watershed_layer, dst_array, affine = affine, stats=['mean'])   # Average LC-IMPACT watershed CF for polygon in pfister & Bayer shapefile polygons
    print(water_cf_factor[0]['mean'])
    new_list = [i['mean'] for i in water_cf_factor]
    print(new_list)
    print(len(new_list))
    Crops_Data_frame['watershed_CF_factor'] = new_list
    Crops_Data_frame['watershed_CF_factor'] = Crops_Data_frame['watershed_CF_factor']

print(Crops_Data_frame.shape)
Total_BW_Consumption = pd.DataFrame(Crops_Data_frame.iloc[154:12262,:]).reset_index()
print(Total_BW_Consumption.shape)

#####################################################################################
''' 
Section 2: 

Read Pfister & bayer accompanying BW_per_ton and BW_total datasheets for the shapefile dataframe. 
Normalize country names in pfister excel sheets to the EXIOBASE country names

'''
#####################################################################################


### Opening of accomopanying Blue water crop data excel of the WaterGap shapefile (Total BW consumption excel sheet and BW consumption per ton of crop produced)  ###

watershed_BW_data = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Watershed data/watershed_WF_crops.xlsx')
for n in watershed_BW_data.sheet_names:
    if n[-9:] == 'BlueWater' or n[-10:] == 'BW_per_ton':
        vars()[n] = watershed_BW_data.parse(sheet_name = n)
        print(watershed_BW_data.sheet_names)
watershed_BW_data.close()

### Cleaning Excel Files ###

BW_df = pd.DataFrame(total_BlueWater)
total_BlueWater = pd.DataFrame(total_BlueWater).reset_index()
Total_BW_Consumption = pd.concat([Total_BW_Consumption,total_BlueWater.reindex(Total_BW_Consumption.index)], axis = 1)
Per_Ton_BW_Consumption = pd.DataFrame(Crops_Data_frame.iloc[154:12262,:]).reset_index()
Bw_per_ton = pd.DataFrame(BW_per_ton).reset_index()
Per_Ton_BW_Consumption = pd.concat([Per_Ton_BW_Consumption, BW_per_ton], axis = 1)
Per_Ton_BW_Consumption.set_index(['CTRY'],inplace= True)
Total_BW_Consumption.set_index(['CTRY'],inplace= True)
Total_BW_Consumption.rename(index={"Cote d'Ivory":'Ivory Coast',
                                           'Falkland Is.':'Falkland Islands', 'United Arab Emirate': 'United Arab Emirates', 'East Timor':'Timor-Leste',
                                           'St. Vincent & the G':'St. Vincent and the Grenadines', 'Solomon Is.': 'Solomon Islands', 'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines'
                                           , 'Trinidad & Tobago': "Trinidad and Tobago", 'Central African Rep': 'Central African Republic', 'Congo, DRC': 'Congo DRC', 'Virgin Is.': 'Virgin Islands',
                                           'British Virgin Is.': 'British Virgin Islands', 'Sao Tome & Principe': 'Sao Tome and Principe', 'Faroe Is.': 'Faroe Islands', 'Bosnia & Herzegovin': 'Bosnia and Herzegovina'},inplace=True)
Per_Ton_BW_Consumption.rename(index={"Cote d'Ivory":'Ivory Coast',
                                           'Falkland Is.':'Falkland Islands', 'United Arab Emirate': 'United Arab Emirates', 'East Timor':'Timor-Leste',
                                           'St. Vincent & the G':'St. Vincent and the Grenadines', 'Solomon Is.': 'Solomon Islands', 'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines'
                                           , 'Trinidad & Tobago': "Trinidad and Tobago", 'Central African Rep': 'Central African Republic', 'Congo, DRC': 'Congo DRC', 'Virgin Is.': 'Virgin Islands',
                                           'British Virgin Is.': 'British Virgin Islands', 'Sao Tome & Principe': 'Sao Tome and Principe', 'Faroe Is.': 'Faroe Islands', 'Bosnia & Herzegovin': 'Bosnia and Herzegovina'},inplace=True)


#####################################################################################
''' 
Section 3: 

Read in national water stress CF excel file from LC-IMPACT. National PDFs to be used as proxies for missing watershed CFs
where mapSPAM have indicated irrigated crop production to take place but LC-IMPACT have not provided a watershed CF. 

'''
#####################################################################################
#################################################

'''Reading National aggregated Water stress PDFS from LC-IMPACT, 
to be used for missing watershed PDFs within national boundaries'''

#################################################

LC_impact_national_CF = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/CF sheets/Autumn project 2021/CFs_water_consumption_ecosystems_20150917.xlsx')

for n in LC_impact_national_CF.sheet_names:
    if n == 'Country level':
        Country_level_CF = LC_impact_national_CF.parse(sheet_name=n)
        Columns = Country_level_CF.iloc[1,1:].values
        index = Country_level_CF.iloc[2:,0]
        Country_level_CF = pd.DataFrame(Country_level_CF.iloc[2:,1:].values, index = index, columns= Columns)
        Missing_countries_LC_water_impact = list(set(Total_BW_Consumption.index) - set(index))
        Missing_countries_LC_water_impact2 = list(set(index) - set(Total_BW_Consumption.index))
        print(Missing_countries_LC_water_impact)
        print(Missing_countries_LC_water_impact2)
index = list(index)
index.remove('Cook Islands')
index.remove('Kiribati')
index.remove('French Polynesia')

#################################################

'''Replacing nan PDF values within overlayed Watershed shapefile and LC-IMPACT raster 
with National aggregated PDFs from LC-IMPACT'''

#################################################

new_df = []
for country in index:

    New_df = Total_BW_Consumption.loc[[country],'watershed_CF_factor']
    New_df2 = Per_Ton_BW_Consumption.loc[[country],'watershed_CF_factor']
    New_df = pd.DataFrame(New_df)
    New_df2 = pd.DataFrame(New_df2)
    print(New_df)
    New_df['watershed_CF_factor'] = New_df['watershed_CF_factor'].replace(np.nan, Country_level_CF.loc[country,'CF core \n[PDF·yr/m3]'])
    New_df2['watershed_CF_factor'] = New_df2['watershed_CF_factor'].replace(np.nan, Country_level_CF.loc[country,'CF core \n[PDF·yr/m3]'])
    print(New_df)
    Total_BW_Consumption.loc[country,'watershed_CF_factor'] = New_df['watershed_CF_factor'].values
    Per_Ton_BW_Consumption.loc[country,'watershed_CF_factor'] = New_df['watershed_CF_factor'].values

Total_BW_Consumption.to_csv(
    'C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Watershed data/Total_BW_Consumption_mergerd_watershed_layers.csv')
Per_Ton_BW_Consumption.to_csv(
    'C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Watershed data/Per_Ton_BW_Consumption_mergerd_watershed_layers.csv')


#####################################################################################
''' 
Section 4: 

Constructing proxy water consumption data for missing countries not included in pfister & bayer dataset but included in EXIOBASE. 

'''
#####################################################################################


#####  Adding Missing Countries in WaterGAP model but included in EXIOBASE ROW via Proxy accounts/country data ###

''' Note: The following countries are not included in WaterGAP and need treatment: 
'Kosovo', 'Sint Maarten', 'Nauru', 'Seychelles', 'Hong Kong', 'Netherlands Antilles', 
'Curacao', 'Bermuda', 'Zanzibar', 'Palau', 'Micronesia, Fed. Sts.', 'Marshall Islands', 'Macao', 
'Maldives', 'Tuvalu', 'Cayman Islands', 'Palestine', 'South Sudan, 'Cook Islands', 'French Polynesia', 'Kiribati''  

However: according to MapSPAM to following countries either have no crops or no irrigated crops: 
Nauru, Seychelles, Hong Kong, Neth.Antilles, Curacao, Bermuda, Palau, Micronesia, Marshal Islands, Macao, 
Maldives, Tuvalu, Cayman Islands, Kosovo, Sint Maarten , 
'Cook Islands', 'French Polynesia', 'Kiribati and therefore are removed from the analysis'   

South Sudan is recognised in MapSPAM as the only missing region in WaterGAP with irrigated crops and below is the 
proxy formation for this country. '''

#################################################################################################################################

LC_impact_national_CF = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/CF sheets/Autumn project 2021/CFs_water_consumption_ecosystems_20150917.xlsx')
Production_quantities_country = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/overlayed_layers_national_boundary_irrigated_production_area.csv')
Total_BW_Consumption.set_index(['CTRY'],inplace= True)
Per_Ton_BW_Consumption.set_index(['CTRY'],inplace= True)
Production_quantities_country.set_index(['ADMIN'], inplace = True)

for n in LC_impact_national_CF.sheet_names:
    if n == 'Country level':
        Country_level_CF = LC_impact_national_CF.parse(sheet_name=n)
        Columns = Country_level_CF.iloc[1,1:].values
        index = Country_level_CF.iloc[2:,0]
        Country_level_CF = pd.DataFrame(Country_level_CF.iloc[2:,1:].values, index = index, columns= Columns)
        Missing_countries_LC_water_impact = list(set(Total_BW_Consumption.index) - set(index))
        Missing_countries_LC_water_impact2 = list(set(index) - set(Total_BW_Consumption.index))
        print(Missing_countries_LC_water_impact)
        print(Missing_countries_LC_water_impact2)

Total_BW_Consumption.rename(index={'Ivory Coast': "Cote d'Ivoire",
                                           'Turks & Caicos Is.':'Turks and Caicos Islands', 'Antigua & Barbuda': 'Antigua and Barbuda', 'Brunei':'Brunei Darussalam',
                                           'Congo':'Congo Republic', 'The Bahamas': 'Bahamas', 'Cape Verde':'Cabo Verde'
                                           , 'St. Kitts & Nevis': 'St. Kitts and Nevis', 'Kyrgyzstan': 'Kyrgyz Republic', 'Congo DRC':'DR Congo', 'Virgin Is.': 'Virgin Islands',
                                           'The Gambia': 'Gambia', 'Sao Tome & Principe': 'Sao Tome and Principe', 'Faroe Is.': 'Faroe Islands', 'Bosnia & Herzegovin': 'Bosnia and Herzegovina'},inplace=True)



### Average of interpolating South Sudan neighbouring countries ###

South_Sudan_BW_proxy = pd.DataFrame(Total_BW_Consumption.loc[['Ethiopia', 'Sudan', 'Central African Republic', 'Uganda', 'DR Congo']])
South_Sudan_length = len(South_Sudan_BW_proxy.index)
South_Sudan_BW_proxy = pd.DataFrame(South_Sudan_BW_proxy.iloc[:,4:].join(South_Sudan_BW_proxy.iloc[:,2]).sum(0) / South_Sudan_length).T

missing_watershed_names = ['South Sudan']
Missing_water_consumption_dataframe = pd.DataFrame()
for i in (South_Sudan_BW_proxy) :
    Missing_water_consumption_dataframe = Missing_water_consumption_dataframe.append(i)
Missing_water_consumption_dataframe['CTRY'] = missing_watershed_names
Missing_water_consumption_dataframe.set_index(['CTRY'], inplace= True)
column_names = list(Missing_water_consumption_dataframe.columns)
column_names = ['watershed_CF_factor','Wheat', 'Ricepaddy', 'Barley', 'Maize', 'Rye', 'Oats', 'Millet', 'Sorghum', 'Buckwheat', 'Quinoa', 'Fonio', 'Triticale', 'Canaryseed', 'Mixedgrain', 'Cerealsnes', 'Potatoes', 'Sweetpotatoes', 'Cassava', 'Yautia_cocoyam', 'Taro_cocoyam', 'Yams', 'RootsandTubersnes', 'Sugarcane', 'Sugarbeet', 'Sugarcropsnes', 'Beansdry', 'Broadbeanshorsebeansdry', 'Peasdry', 'Chickpeas', 'Cowpeasdry', 'Pigeonpeas', 'Lentils', 'Bambarabeans', 'Vetches', 'Lupins', 'Pulsesnes', 'NODATA', 'Cashewnutswithshell', 'chstnut', 'Almondswithshell', 'Walnutswithshell', 'Pistachios', 'Kolanuts', 'Hazelnutswithshell', 'Arecanuts', 'Nutsnes', 'Soybeans', 'Groundnutswithshell', 'Coconuts', 'Oilpalmfruit', 'Olives', 'NODATA.1', 'Castoroilseed', 'Sunflowerseed', 'Rapeseed', 'NODATA.2', 'NODATA.3', 'Safflowerseed', 'Sesameseed', 'Mustardseed', 'Poppyseed', 'Melonseed', 'NODATA.4', 'KapokseedinShell', 'Seedcotton', 'Linseed', 'NODATA.5', 'OilseedsNes', 'Fodder', 'Artichokes', 'Asparagus', 'Lettuceandchicory', 'Spinach', 'Tomatoes', 'Cauliflowersandbroccoli', 'Pumpkinssquashandgourds', 'Cucumbersandgherkins', 'Eggplants_aubergines', 'Chilliesandpeppersgreen', 'Onions_incshallotsgreen', 'Onionsdry', 'Garlic', 'NODATA.6', 'Beansgreen', 'Peasgreen', 'Leguminousvegetablesnes', 'Stringbeans', 'Carrotsandturnips', 'Okra', 'Maizegreen', 'NODATA.7', 'NODATA.8', 'Carobs', 'Vegetablesfreshnes', 'Bananas', 'Plantains', 'Oranges', 'Tangerinesmandarinsclem', 'Lemonsandlimes', 'Grapefruit_incpomelos', 'Citrusfruitnes', 'Apples', 'Pears', 'Quinces', 'Apricots', 'Sourcherries', 'Cherries', 'peachetc', 'Plumsandsloes', 'Stonefruitnes', 'Strawberries', 'Raspberries', 'Gooseberries', 'Currants', 'Blueberries', 'Cranberries', 'BerriesNes', 'Grapes', 'Watermelons', 'Othermelons_inccantaloupes', 'Figs', 'Mangoesmangosteensguavas', 'Avocados', 'Pineapples', 'Dates', 'Persimmons', 'Cashewapple', 'Kiwifruit', 'Papayas', 'Fruittropicalfreshnes', 'FruitFreshNes', 'Fodder.1', 'Fodder.2', 'Fodder.3', 'Fodder.4', 'Fodder.5', 'Fodder.6', 'Fodder.7', 'Fodder.8', 'Cabbagesandotherbrassicas', 'Fodder.9', 'Fodder.10', 'Fodder.11', 'Fodder.12', 'Fodder.13', 'Fodder.14', 'Fodder.15', 'Coffeegreen', 'Cocoabeans', 'NODATA.9', 'NODATA.10', 'Tea', 'Hops', 'Pepper_Piperspp', 'Chilliesandpeppersdry', 'Vanilla', 'Cinnamon_canella', 'Cloves', 'Nutmegmaceandcardamoms', 'Anisebadianfennelcorian', 'Ginger', 'Spicesnes', 'NODATA.11', 'NODATA.12', 'Flaxfibreandtow', 'HempTowWaste', 'Jute', 'OtherBastfibres', 'Ramie', 'Sisal', 'AgaveFibresNes', 'ManilaFibre_Abaca', 'FibreCropsNes', 'Tobaccounmanufactured', 'Naturalrubber']
Missing_water_consumption_dataframe = Missing_water_consumption_dataframe.reindex(columns =column_names)
Missing_water_consumption_dataframe.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/proxy_BW_cons_and_watershed_cfs_for_missing_countries.csv')

