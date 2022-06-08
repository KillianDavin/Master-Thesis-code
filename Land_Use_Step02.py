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

 
This python script is the code used to aggregate the land use and PDF values at the ecoregion level calculated in
Land_Use_Step01 up to the Rest of the World (ROW) level classifications of Exiobase.


'''

#####################################################################################

'''

Section 1: Cleaning of EXIOBASE-ROW regions excel file, LC-IMPACT ecoregion CF excel file and 
           Crops_Data_frame dataframe calculated in section 2 of Land_Use_Step_01. MapSPAM crps are aggregated to EXIOBASE categories
           again in the same process completed in Land_Use_Step01
'''

###################################################################################

### Load Exiobase list of regions data from excel sheet Exiobase 3rx || load overlayed Country, ecoregion and spam dataframe calculated in section 2 of Land_Use_Step01 || load LC-IMPACT land characterisation factor dataframe

Aggregated_Exiobase_regions = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/CF sheets/Exiobase_3rx_data.xlsx')
Crops_Data_frame = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/overlayed_layers_SPAM_physical_crop_area_all_technologies_ecoregions.csv')
Land_CF_updated = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/CF sheets/Land_characterisation_thesis/CFs_land_Use_average.xlsx')

for n in Land_CF_updated.sheet_names:
    if n == 'occupation average ecoregion':
        Average_CF_df = Land_CF_updated.parse(sheet_name=n)

##### Cleaning LC-IMPACT land use CF excel file for data manipulation ##################

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

print(Average_CF_df)

#### Cleaning Exiobase 3rx country/ROW dataframe for data manipulation #####

spam_countries = set(Crops_Data_frame['ADMIN'].values)
for n in Aggregated_Exiobase_regions.sheet_names:
    if n == 'Countries':
        Exiobase_countries = Aggregated_Exiobase_regions.parse(sheet_name = n)
        Aggregated_Exiobase_regions.close()
columns_exio = list(Exiobase_countries.columns)
columns_exio.pop(0)
Exiobase_countries = pd.DataFrame(Exiobase_countries.iloc[:,1:].values, index = Exiobase_countries.iloc[:,0].values, columns= columns_exio)

### ROW Europe ####

ROW_Europe = Exiobase_countries.loc[Exiobase_countries['RoW Europe'] == 1]
ROW_Europe = list(ROW_Europe.index)

### ROW Middle East ###

RoW_Middle_East = Exiobase_countries.loc[Exiobase_countries['RoW Middle East'] == 1]
RoW_Middle_East = list(RoW_Middle_East.index)

### ROW America ###

RoW_America = Exiobase_countries.loc[Exiobase_countries['RoW America'] == 1]
RoW_America= list(RoW_America.index)
RoW_America.remove('Netherlands Antilles')     #Netherlands Antilles not included in COuntry/ecoregion/Spam overlayed maps so removed from exiobase ROW region ROW America

### RoW Asia and Pacific ###

RoW_Asia_and_Pacific = Exiobase_countries.loc[Exiobase_countries['RoW Asia and Pacific'] == 1]
RoW_Asia_and_Pacific = list(RoW_Asia_and_Pacific.index)
RoW_Asia_and_Pacific.remove('Nauru')  #Nauru not included in COuntry/ecoregion/Spam overlayed maps so removed from exiobase ROW region ROW Asia and Pacific

### RoW Africa ###

RoW_Africa = Exiobase_countries.loc[Exiobase_countries['RoW Africa'] == 1]
RoW_Africa = list(RoW_Africa.index)
RoW_Africa.remove('Zanzibar')  #Zanzibar not included in COuntry/ecoregion/Spam overlayed maps so removed from exiobase ROW region ROW Africa

### Preparation of Crops data into the FAO/Exiobase crop categories of ['Rice','Wheat','Cereal grains Nec' ,'Vegetables, fruit, nuts', 'Roots_and_tubers', 'Pulses', 'Sugar', 'Oil_seeds', 'Plant_based_fibres', 'Crops_nec' ] #####

Rice = ['RICE']
Wheat = ['WHEA']
Cereal_grains_Nec = ['MAIZ', 'BARL', 'PMIL', 'SMIL', 'SORG', 'OCER' ]
Fruit = ['BANA','PLNT','TROF','TEMF','CNUT']
Nuts = []
Vegetables = ['VEGE']  #Crops should be in
Roots_and_tubers = ['POTA', 'SWPO', 'YAMS', 'CASS', 'ORTS']
Pulses = ['BEAN','CHIC', 'COWP', 'PIGE', 'LENT', 'OPUL']
Sugar = ['SUGC', 'SUGB']   #sugar nes not in SPAM individually
Oil_seeds = ['SOYB','GROU', 'OILP', 'SUNF', 'RAPE','SESA','OOIL', 'COTT'] #olives contained within oil seed crops
Plant_based_fibres = ['OFIB']
Crops_nec = ['ACOF', 'RCOF', 'COCO', 'TEAS','TOBA', 'REST' ]  #includes nuts category and Sugar Nes
Crops_nec_misc = ['REST']
Crops_nec_commodity = ['ACOF', 'RCOF', 'COCO', 'TEAS','TOBA']

categories = [Rice,Wheat,Cereal_grains_Nec, Fruit, Vegetables, Roots_and_tubers, Pulses, Sugar, Oil_seeds, Plant_based_fibres, Crops_nec, Crops_nec_misc, Crops_nec_commodity ]
categories_str = ['Paddy Rice','Wheat','Cereal grains Nec' , 'Fruit',  'Vegetables' , 'Roots_and_tubers', 'Pulses', 'Sugar', 'Oil_seeds', 'Plant_based_fibres', 'Crops_nec', 'Crops_nec_misc', 'Crops_nec_commodity' ]
Production_df = pd.DataFrame(Crops_Data_frame.iloc[:,0:6])
count = 0
for category in categories:
    New_df = pd.DataFrame(Crops_Data_frame[category].values.sum(1))
    New_df = pd.DataFrame(New_df)
    Production_df[categories_str[count]] = New_df.iloc[:,0]
    count += 1
    print(Production_df)
Production_df['Vegetables, fruit, nuts'] = Production_df['Fruit'].values + Production_df['Pulses'].values + Production_df['Roots_and_tubers'].values + Production_df['Vegetables'].values  #missing nuts and olives
del Production_df['Fruit']
del Production_df['Pulses']
del Production_df['Roots_and_tubers']
del Production_df['Vegetables']
del Production_df['Unnamed: 0']
del Production_df['Crops_nec_misc']
del Production_df['Crops_nec_commodity']
column_headings = list(Production_df.columns)
ecocodes = list(Average_CF_df.index)

### Removing ecocodes not present in intersected country/terrestrial production layer or ecoregions where no crops are grown ###

ecocodes.remove('NT1318')   # NT1318 not present in ecoregion/country/spam overlayed map so it is removed here
ecocodes2 = Production_df['eco_code'].values

#### Removing ecocode rows not present in LC-IMPACT ####
missing_ecocodes = list(set(ecocodes)- set(ecocodes2))
missing_ecocodes = list(set(ecocodes2)- set(ecocodes))
print(missing_ecocodes)
missing_ecocodes = ['AT1301', 'NT0110', 'NA0301', 'NT0403', 'OC0204', 'OC0102', 'OC0107', 'AN1101', 'AT0720', 'AN1104', 'NT1311', 'AN1103', 'NT0123', 'OC0703', 'AN1102', 'OC0111']  #Ecoregions not covered in LC-IMPACT and that have no crops located within their boarders according to the SPAM model.

Production_df.set_index(['eco_code'], inplace= True)
Production_df.insert(loc = 0,column = 'eco_code',value = Production_df.index.values)
for ecocode in missing_ecocodes:
    Production_df.drop(ecocode, inplace= True)  # removed ecocodes not present in LC-IMPACt and have no crops grown within its ecoregion area

#####################################################################################

'''

Section 2: Normalization of country names from Natural Earth to EXIOBASE country names and calculation of 
           ROW continental CFs by crop land area weighting at a continental level 
           
'''

###################################################################################
### Prep of Dataframes for matrix multiplication. Index names need to be the same for required dataframes. ###
### The country names from the Natural Earth shapefile are transformed to match those of the Exiobase country classification names below ###

ROW_Regions = [ROW_Europe, RoW_Asia_and_Pacific, RoW_America, RoW_Africa, RoW_Middle_East]
RoW_America.remove('Bermuda')  # Bermudas one ecoregion was removed in the last section as there was no crops grown in the region. Therefore Bermuda removed from ROW region ROW America.
ROW_Regions_str = ['RoW_Europe', 'RoW_Asia_and_Pacific', 'RoW_America', 'RoW_Africa','RoW_Middle_East']
Total_production_per_country = Production_df.groupby(['ADMIN']).sum(0)
Total_production_per_country.rename(index={'Republic of Serbia':'Serbia', 'North Macedonia':'Macedonia', 'Brunei':'Brunei Darussalam', 'Hong Kong S.A.R.':'Hong Kong',
                                           'Macao S.A.R':'Macao', 'Kyrgyzstan':'Kyrgyz Republic', 'Federated States of Micronesia': 'Micronesia, Fed. Sts.', 'East Timor':'Timor-Leste',
                                           'The Bahamas':'Bahamas', 'Curaçao': 'Curacao','Saint Kitts and Nevis':'St. Kitts and Nevis','Saint Lucia':'St. Lucia', 'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines',
                                           'Republic of the Congo': 'Congo Republic', 'Ivory Coast': "Cote d'Ivoire", 'Democratic Republic of the Congo': 'DR Congo', 'eSwatini':'Swaziland',
                                           'United Republic of Tanzania': 'Tanzania', 'São Tomé and Principe': 'Sao Tome and Principe'},inplace=True)

Total_production_per_country.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/checkxx.csv')  ###checked - Total production is calculated correctly

### Calculation of total production area for the 5 ROW regions ###

ROW_df = pd.DataFrame()
count = 0
for region in ROW_Regions:
    regional_df = pd.DataFrame((Total_production_per_country.loc[region,:].values.sum(0)))
    regional_df = regional_df.T
    ROW_df = ROW_df.append(pd.DataFrame(regional_df))

ROW_df.set_index([ROW_Regions_str], inplace = True)
ROW_df = pd.DataFrame(ROW_df.iloc[:,4:])
ROW_df.set_axis(['Paddy Rice', 'Wheat','Cereal grains Nec', 'Sugar',
                              'Oil_seeds', 'Plant_based_fibres','Crops_nec', 'Vegetables, fruit, nuts'], axis = 1, inplace= True)


### Calculation of production shares per ecoregion, per country, based on total production area of the ROW regions they are pertained to.

Production_df.set_index(['ADMIN'], inplace= True)
Production_df.rename(index = {'Republic of Serbia':'Serbia', 'North Macedonia':'Macedonia', 'Brunei':'Brunei Darussalam', 'Hong Kong S.A.R.':'Hong Kong',
                                           'Macao S.A.R':'Macao', 'Kyrgyzstan':'Kyrgyz Republic', 'Federated States of Micronesia': 'Micronesia, Fed. Sts.', 'East Timor':'Timor-Leste',
                                           'The Bahamas':'Bahamas', 'Curaçao': 'Curacao','Saint Kitts and Nevis':'St. Kitts and Nevis','Saint Lucia':'St. Lucia', 'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines',
                                           'Republic of the Congo': 'Congo Republic', 'Ivory Coast': "Cote d'Ivoire", 'Democratic Republic of the Congo': 'DR Congo', 'eSwatini':'Swaziland',
                                           'United Republic of Tanzania': 'Tanzania', 'São Tomé and Principe': 'Sao Tome and Principe'},inplace=True)


count = 0
for region in ROW_Regions:

    for crop in ['Paddy Rice', 'Wheat','Cereal grains Nec', 'Sugar',
                              'Oil_seeds', 'Plant_based_fibres','Crops_nec', 'Vegetables, fruit, nuts']:
        Production_df.loc[region,crop] = Production_df.loc[region,crop].values /  ROW_df.loc[ROW_Regions_str[count],crop]  #array divided by a scalar elementwise according to Pandas
    count += 1
Production_shares = Production_df
Production_shares = pd.DataFrame(Production_shares).replace(np.nan, 0)  # replacemnt of NAN from 0 division during production share calculation
Production_shares['ADMIN'] = list(Production_shares.index)
Production_shares.set_index('eco_code',  inplace=True)
Annual_crops = ['Paddy Rice', 'Wheat','Cereal grains Nec', 'Sugar', 'Oil_seeds', 'Plant_based_fibres','Crops_nec']
Permanent_crops = ['Vegetables, fruit, nuts']

### Production shares check, and calculations are ok!

### Calculation of the aggregated ROW region characterisation factors for the 8 crop categories ###

New_Charc_factors_df = pd.DataFrame()
for land_type in [Annual_crops,Permanent_crops] :
    for ecocode in ecocodes:
        if land_type == Annual_crops:
            Production_shares.loc[ecocode,Annual_crops] = Production_shares.loc[ecocode,Annual_crops].values * Average_CF_df.loc[ecocode, ('Annual crops','Median')]
        else:
            Production_shares.loc[ecocode,Permanent_crops] = Production_shares.loc[ecocode,Permanent_crops] * Average_CF_df.loc[ecocode, ('Permanent crops','Median')]

New_Land_CF = Production_shares.groupby(['ADMIN']).sum(0)
del New_Land_CF['NE_ID']
del New_Land_CF['OBJECTID']
del New_Land_CF['ECO_NAME']

ROW_CF_df = pd.DataFrame()
count = 0
for region in ROW_Regions:
    regional_df = pd.DataFrame((New_Land_CF.loc[region,:].sum(0)))
    regional_df = regional_df.T
    ROW_CF_df = ROW_CF_df.append(pd.DataFrame(regional_df))

ROW_CF_df.set_index([ROW_Regions_str], inplace = True)

## ROW_CF_df calculation checked for validity - calculation calculated as intended

### Joining of country level CF factors dataframe with the ROW CF factor dataframe ###

Country_CFs = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/Final_sheets_for_Exiobase/land_characterization_factors_ver02.csv')
Country_CFs.set_index(['ADMIN'], inplace= True)
Country_CFs.rename(index = {'Republic of Serbia':'Serbia', 'North Macedonia':'Macedonia', 'Brunei':'Brunei Darussalam', 'Hong Kong S.A.R.':'Hong Kong',
                                           'Macao S.A.R':'Macao', 'Kyrgyzstan':'Kyrgyz Republic', 'Federated States of Micronesia': 'Micronesia, Fed. Sts.', 'East Timor':'Timor-Leste',
                                           'The Bahamas':'Bahamas', 'Curaçao': 'Curacao','Saint Kitts and Nevis':'St. Kitts and Nevis','Saint Lucia':'St. Lucia', 'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines',
                                           'Republic of the Congo': 'Congo Republic', 'Ivory Coast': "Cote d'Ivoire", 'Democratic Republic of the Congo': 'DR Congo', 'eSwatini':'Swaziland',
                                           'United Republic of Tanzania': 'Tanzania', 'São Tomé and Principe': 'Sao Tome and Principe', 'Czechia':'Czech Republic', 'United States of America': 'United States',
                            'United Kingdom':'Great Britain' },inplace=True)

Country_CFs = pd.DataFrame(Country_CFs.iloc[:,:])
Country_CFs = Country_CFs.append(ROW_CF_df)
Country_CFs = Country_CFs.T
Country_CFs.rename(index = {'Oil_seeds': 'Oil seeds', 'Plant_based_fibres':'Plant-based fibers', 'Paddy Rice': 'Paddy rice',
                            'Crops_nec': 'Crops Nec'}, inplace = True)

### Final dataframe including all country and continental land CFs


Country_CFs.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/land_characterization_factors_with_ROW_regions_ver02.csv')

#######################################