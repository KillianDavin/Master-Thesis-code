import pandas as pd
import numpy as np
##########################################################################################################

'''

Aim of this sheet is to aggregate watershed level characterisation factors and irrigated crop data 
to both national level and ROW regional level. This is script 4 of 4 for the water CF construction methodology
 
The following 2 sections are included: 

Section 1: Calculate irrigation crop shares per watershed, per country and calculate the national CFs via weighting of irrigation share
Section 2: Calculate irrigation crop shares per watershed, per ROW continent and calculate the continental CFs via weighting of irrigation shares


'''

##########################################################################################################

#####################################################################################
''' 
Section 1: 

Read in generated tables from the previous 3 python scripts for Watershed_steps, calculate irrigation crop shares per watershed, per country and
calculate the national CFs via weighting of irrigation shares 

'''
#####################################################################################

### Read previously treated and overlayed LC-IMPACT PDFs + watershed consumption data waterGAP + Irrigated mapSPAM crop data #####

Watershed_data = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/water_consumption_FAO_category_PDF_output_dataframe_ver02.csv')
Watershed_data.set_index(['CTRY'], inplace= True)
print(Watershed_data.columns)

### Calculation of total crop area of each crop per country

Total_consumption_per_country = Watershed_data.iloc[:,3:]
print(Total_consumption_per_country)

Total_consumption_per_country = Total_consumption_per_country.groupby(['CTRY']).sum(0)
print(Total_consumption_per_country)

### Calculation of production shares per watershed, per country, based on total production area of each crop in that country ###

Total_share_country_consumption = Watershed_data.iloc[:,3:]
print(Total_share_country_consumption)
Unique_countries = set(Total_share_country_consumption.index.values)
for country in Unique_countries :
    Total_share_country_consumption.loc[country,:] = Total_share_country_consumption.loc[country,:].values / np.array(Total_consumption_per_country.loc[country,:].values)

Consumption_shares = Total_share_country_consumption
Consumption_shares.insert(0,'watershed_CF_factor', value = Watershed_data['watershed_CF_factor'])

### Computation of national level Characterisation factors ###

Consumption_shares = pd.DataFrame(Consumption_shares).replace(np.nan, 0)
print(Consumption_shares)
crop_categories = ['Wheat',
       'Paddy_rice', 'cereal_grains_nec', 'Oil_Seeds', 'sugar',
       'Plant_Based_Fibres', 'Crops_Nec', 'Vegetables, fruit, nuts',
       'Fodder_Crops']
for crop in crop_categories :
    Consumption_shares[crop] = Consumption_shares[crop].values * Consumption_shares['watershed_CF_factor'].values

National_CFs = Consumption_shares
National_CFs = National_CFs.groupby(['CTRY']).sum(0)
National_CFs.drop('watershed_CF_factor', axis = 1)
National_CFs.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/Watershed_aggregated_national_level_characterisation_factors_ver01.csv')


#####################################################################################
''' 
Section 2: 

Calculate irrigation crop shares per watershed, per ROW continent and
calculate the continental CFs via weighting of irrigation shares 

'''
#####################################################################################
#### ROW aggregation ####

Aggregated_Exiobase_regions = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/CF sheets/Exiobase_3rx_data.xlsx')

#### Cleaning Exiobase 3rx country/ROW dataframe for data manipulation #####

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
ROW_Europe.remove('Kosovo') #No irrigated crops data
### ROW Middle East ###

RoW_Middle_East = Exiobase_countries.loc[Exiobase_countries['RoW Middle East'] == 1]
RoW_Middle_East = list(RoW_Middle_East.index)

### ROW America ###

RoW_America = Exiobase_countries.loc[Exiobase_countries['RoW America'] == 1]
RoW_America= list(RoW_America.index)
RoW_America.remove('Netherlands Antilles')     #Netherlands Antilles not included in COuntry/ecoregion/Spam overlayed maps so removed from exiobase ROW region ROW America
RoW_America.remove('Curacao') #No crops in region
RoW_America.remove('Sint Maarten') #No crops in region
RoW_America.remove('Cayman Islands') #No crops in region
RoW_America.remove('Bermuda') #No crops in region

### RoW Asia and Pacific ###

RoW_Asia_and_Pacific = Exiobase_countries.loc[Exiobase_countries['RoW Asia and Pacific'] == 1]
RoW_Asia_and_Pacific = list(RoW_Asia_and_Pacific.index)
RoW_Asia_and_Pacific.remove('Nauru')  #Nauru not included in COuntry/ecoregion/Spam overlayed maps so removed from exiobase ROW region ROW Asia and Pacific
RoW_Asia_and_Pacific.remove('Palau') #No crops in region
RoW_Asia_and_Pacific.remove('Hong Kong') #No crops in region
RoW_Asia_and_Pacific.remove('Maldives') #No crops in region
RoW_Asia_and_Pacific.remove('Tuvalu') #No crops in region
RoW_Asia_and_Pacific.remove('Marshall Islands') #No crops in region
RoW_Asia_and_Pacific.remove('Micronesia, Fed. Sts.') #No irrigated crops data
RoW_Asia_and_Pacific.remove('French Polynesia') #No irrigated crops data
RoW_Asia_and_Pacific.remove('Kiribati') #No irrigated crops data
RoW_Asia_and_Pacific.remove('Cook Islands') #No crops in region
RoW_Asia_and_Pacific.remove('Macao') #No crops in region
print(RoW_Asia_and_Pacific)

### RoW Africa ###

RoW_Africa = Exiobase_countries.loc[Exiobase_countries['RoW Africa'] == 1]
RoW_Africa = list(RoW_Africa.index)
RoW_Africa.remove('Zanzibar') #Not a country
RoW_Africa.remove('Seychelles') #No crops in region
ROW_Regions_str = ['ROW_Europe', 'RoW_Asia_and_Pacific', 'RoW_America', 'RoW_Africa','RoW_Middle_East']
Total_consumption_per_ROW_region = Watershed_data.iloc[:,3:]
Palestine = Total_consumption_per_ROW_region.loc['Gaza Strip'].sum(0) + Total_consumption_per_ROW_region.loc['West Bank'].sum(0)  #Palestine listed as West Bank and Gaza in WaterGAP and MapSPAM. Total Palestinian crop consumption is the sum of both regions

### Calculation of total crop area of each crop per ROW region ###

Total_consumption_per_ROW_region.rename(index={'Republic of Serbia':'Serbia', 'North Macedonia':'Macedonia', 'Brunei':'Brunei Darussalam', 'Hong Kong S.A.R.':'Hong Kong',
                                           'Macao S.A.R':'Macao', 'Kyrgyzstan':'Kyrgyz Republic', 'Federated States of Micronesia': 'Micronesia, Fed. Sts.', 'East Timor':'Timor-Leste',
                                           'The Bahamas':'Bahamas', 'Curaçao': 'Curacao','Saint Kitts and Nevis':'St. Kitts and Nevis','Saint Lucia':'St. Lucia', 'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines',
                                           'Congo': 'Congo Republic', 'Ivory Coast': "Cote d'Ivoire", 'Congo DRC': 'DR Congo', 'eSwatini':'Swaziland',
                                           'United Republic of Tanzania': 'Tanzania', 'São Tomé and Principe': 'Sao Tome and Principe', 'Antigua & Barbuda': 'Antigua and Barbuda',
                                               'St. Kitts & Nevis': 'St. Kitts and Nevis', 'Turks & Caicos Is.':'Turks and Caicos Islands', 'The Gambia': 'Gambia', 'Cape Verde': 'Cabo Verde'},inplace=True)
Total_consumption_per_ROW_region = Total_consumption_per_ROW_region.groupby(['CTRY']).sum(0)
Total_consumption_per_ROW_region.loc['Palestine'] = Palestine.values
Total_ROW_consumption = pd.DataFrame()
for ROW in (ROW_Europe, RoW_Asia_and_Pacific, RoW_America, RoW_Africa, RoW_Middle_East):
    New_df = pd.DataFrame(Total_consumption_per_ROW_region.loc[ROW,:]).sum(0)
    New_df = pd.DataFrame(New_df).T
    Total_ROW_consumption = Total_ROW_consumption.append(New_df)

Total_ROW_consumption.set_index([ROW_Regions_str], inplace = True)

print(Total_ROW_consumption)
### Calculation of consumption shares per watershed,per country, per ROW region ###

ROW_consumption_shares = Watershed_data.iloc[:,3:]
ROW_consumption_shares.loc['Palestine'] = Palestine.values
ROW_consumption_shares.rename(index={'Republic of Serbia':'Serbia', 'North Macedonia':'Macedonia', 'Brunei':'Brunei Darussalam', 'Hong Kong S.A.R.':'Hong Kong',
                                           'Macao S.A.R':'Macao', 'Kyrgyzstan':'Kyrgyz Republic', 'Federated States of Micronesia': 'Micronesia, Fed. Sts.', 'East Timor':'Timor-Leste',
                                           'The Bahamas':'Bahamas', 'Curaçao': 'Curacao','Saint Kitts and Nevis':'St. Kitts and Nevis','Saint Lucia':'St. Lucia', 'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines',
                                           'Congo': 'Congo Republic', 'Ivory Coast': "Cote d'Ivoire", 'Congo DRC': 'DR Congo', 'eSwatini':'Swaziland',
                                           'United Republic of Tanzania': 'Tanzania', 'São Tomé and Principe': 'Sao Tome and Principe', 'Antigua & Barbuda': 'Antigua and Barbuda',
                                               'St. Kitts & Nevis': 'St. Kitts and Nevis', 'Turks & Caicos Is.':'Turks and Caicos Islands', 'The Gambia': 'Gambia', 'Cape Verde': 'Cabo Verde'},inplace=True)

count = 0
for ROW in (ROW_Europe, RoW_Asia_and_Pacific, RoW_America, RoW_Africa, RoW_Middle_East):
    ROW_consumption_shares.loc[ROW,:] = ROW_consumption_shares.loc[ROW,:].values / np.array(Total_ROW_consumption.loc[ROW_Regions_str[count],:].values)
    count += 1

### Calculation of ROW watershed aggregated CF factors ###

Watershed_CFs = list(Watershed_data['watershed_CF_factor'].values)
Palestine_length = Watershed_data.loc['Gaza Strip'] + Watershed_data.loc['West Bank']
Palestine_length = len(Palestine_length.index)
Palestine_CFs = ( Watershed_data.loc['Gaza Strip', 'watershed_CF_factor'].values.sum(0) + Watershed_data.loc['West Bank','watershed_CF_factor'].values.sum(0)) / Palestine_length   #Palestine Watershed CF is the average CF of the various watersheds in both regions. The CF is applied for all crop categories


Watershed_CFs.append(Palestine_CFs)

ROW_consumption_shares.insert(0,column ='watershed_CF_factor', value = Watershed_CFs)

''' Malta given European aggregated PDF factors for polygons (National or polygon PDFs not available in LC-IMPACT) 
Timor-Leste given Oceania continent PDF as no PDFs exisiting in LC-IMPACT or polygons. BE AWARE  These were inserted manually in C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/water_consumption_FAO_category_PDF_output_dataframe_ver02.csv  '''

ROW_consumption_shares['watershed_CF_factor'] = ROW_consumption_shares['watershed_CF_factor'].replace(np.nan,0)  ## checked all nan watersheds are areas with no production or water consumption according to MapSPam and Watergap.
print(list(ROW_consumption_shares['watershed_CF_factor'].values))
Palestine_data_entry = [Palestine_CFs]*10
Palestine_data_entry = pd.DataFrame(Palestine_data_entry).T
Palestine_data_entry = pd.DataFrame(Palestine_data_entry.values, index = ['Palestine'], columns = National_CFs.columns)
print(Palestine_data_entry)
ROW_aggregated_CF = ROW_consumption_shares.iloc[:,1:]
New_df = pd.DataFrame()
for ROW in (ROW_Europe, RoW_Asia_and_Pacific, RoW_America, RoW_Africa, RoW_Middle_East):

    ROW_aggregated_CF.loc[ROW, :] = pd.DataFrame(ROW_aggregated_CF.loc[ROW,:]).multiply(ROW_consumption_shares.loc[ROW, 'watershed_CF_factor'], axis=0)
    print(ROW_aggregated_CF.loc[ROW, :])
    ROW_aggregated = pd.DataFrame(ROW_aggregated_CF.loc[ROW,:].sum(0)).T
    New_df = New_df.append(pd.DataFrame(ROW_aggregated))

New_df.set_index([ROW_Regions_str], inplace = True)
ROW_aggregated_CF = New_df
print(ROW_aggregated_CF)
National_CFs  = National_CFs.append(Palestine_data_entry)
National_and_ROW_CFs = National_CFs.append(ROW_aggregated_CF)

