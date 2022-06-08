import pymrio
import pandas as pd
years = range(2010, 2011)


#####################################################################################

''' 

This python script is the code used to calculate the biodiversity footprints post disaggregation of the LC-IMPACT CFs
using the stressor table S, calculated in the Footprints_step_01 and due to the final demand for agriculture and food 
products only. 

'''

#####################################################################################


iso3_to_full_names_dict = {'AT': 'Austria', 'BE':'Belgium', 'BG':'Bulgaria','CZ':'Czech Republic', 'CY':'Cyprus', 'DE':'Germany', 'DK':'Denmark', 'EE':'Estonia',
                            'ES':'Spain','FR':'France','FI':'Finland','GR':'Greece', 'HU':'Hungary', 'HR':'Croatia', 'IE':'Ireland','IT':'Italy' ,'LT':'Lithuania', 'LV':'Latvia', 'LU': 'Luxembourg',
                           'MT':'Malta', 'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'SE':'Sweden', 'SK':'Slovakia', 'SI':'Slovenia','RO': 'Romania',
                           'GB': 'Great Britain', 'US':'United States', 'CN':'China', 'CA': 'Canada', 'JP': 'Japan', 'IN': 'India', 'ID': 'Indonesia',
                           'KR': 'South Korea', 'RU': 'Russia', 'NO': 'Norway', 'CH': 'Switzerland', 'TW':'Taiwan','TR':'Turkey','ZA':'South Africa', 'BR': 'Brazil',
                           'MX':'Mexico', 'AU': 'Australia', 'WA': 'RoW_Asia_and_Pacific', 'WF': 'RoW_Africa', 'WL': 'RoW_America', 'WM':'RoW_Middle_East', 'WE':'RoW_Europe'}


#####################################################################################

''' Loading in the LC-Impact characterisation factors and the tailored & opitimised Land and water characterisation factors calculated in previous steps 
Land_CF_tables represent the disaggegrated PDFs for the various crop/land use types, Water_CF_tables represent the water impacts for the disaggregated crop types, 
 while LC '''


##########################################################################################################################################################

Land_CF_tables = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/Final_sheets_for_Exiobase/land_characterization_factors_with_ROW_regions_ver02.csv')
Land_CF_tables.set_index('Land Type', inplace = True)
Land_CF_tables = Land_CF_tables* (
        10 ** 6)  # conversion from m2 to km2 for land Characterisations, index 0-6 are the land CFs in the table

LC_Impact_CF_tables = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/CF sheets/Land_characterisation_thesis/Full_CF_table_continental_proxy_approach.csv')
LC_Impact_CF_tables.set_index('Stressor name', inplace = True)
LC_Impact_CF_tables.rename(index = {'Permanent crops ': 'Permanent crops', 'Pasture ':'Pasture', 'Urban ':'Urban', 'Extensive forestry ': 'Extensive forestry', 'Intensive forestry ': 'Intensive forestry'}, inplace= True)
LC_Impact_CF_tables.rename(columns = iso3_to_full_names_dict, inplace = True)
LC_Impact_CF_tables.iloc[0:6,2:] = LC_Impact_CF_tables.iloc[0:6,2:].values * 10 ** 6  # conversion from m2 to km2 for land Characterisations, index 0-6 are the land CFs in the table
LC_Impact_CF_tables.iloc[22:24, :] = LC_Impact_CF_tables.iloc[22:24,:]*(10**6) #coversion from m3 to Mm3 for Water consumption as per exiobase, index 22 and 23 are the water CFs in the table
countries_Exiobase3 = list(LC_Impact_CF_tables.columns.values)
countries_Exiobase3.pop(0)
countries_Exiobase3.pop(0)
Water_CF_tables = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/Final_sheets_for_Exiobase/Watershed_aggregated_national_and_ROW_level_characterisation_factors_ver03.csv')
Water_CF_tables.set_index('Crop Type', inplace = True)
Water_CF_tables = Water_CF_tables.astype(float)
Water_CF_tables = Water_CF_tables * 10**6  # conversion from Mm3 to m3


idx = pd.IndexSlice  # Slicing of multi index columns for separating out multiindex columns

#####################################################################################################################################################################

'''The next section deals with characterizing the stressor table S, with the CF factors from table 'Land_CF_tables'.
   The S table is broken out into smaller S_impact tables to match the [ various impact categories for characterization.
   The table is reformed after characterization as Char_table with units PDF per elementary flow.
   This section also calculates the characterized footprint of F_Y, which is the footprint related to household consumption or
   the impacts required for the consumption to take place.Multiplication is done via index location and for loops at different
   levels, according to indexs in the Stressor tables S_, F_Y, and Land_CF_tables. '''

############################################################################################################################################################################################
exiobase3 = pymrio.load_all('C:/Users/Cillian/PycharmProjects/Master-Thesis/data/interim/EXIO3')   # Loading tables saved from Footprints_Step_01
exiobase3.satellite.S = pd.DataFrame(exiobase3.satellite.S)
exiobase3.satellite.S_Y = pd.DataFrame(exiobase3.satellite.S_Y)
exiobase3.satellite.S.rename(columns = iso3_to_full_names_dict, level = 0, inplace =True)
exiobase3.satellite.S_Y.rename(columns = iso3_to_full_names_dict, level = 0, inplace =True)

for crop_type in ['Cereal grains Nec', 'Crops Nec', 'Oil seeds', 'Paddy rice', 'Plant-based fibers', 'Sugar', 'Vegetables, fruit, nuts', 'Wheat' ]:

    for country in countries_Exiobase3:
        print(country)
        print(exiobase3.satellite.S.loc[crop_type, idx[country, :]])
        exiobase3.satellite.S.loc[crop_type, idx[country, :]] = exiobase3.satellite.S.loc[crop_type, idx[country, :]].values * Land_CF_tables.loc[crop_type, country]
        exiobase3.satellite.S_Y.loc[crop_type, idx[country, :]] = exiobase3.satellite.S_Y.loc[crop_type, idx[country, :]].values * Land_CF_tables.loc[crop_type, country]

for land_type in ['Annual crops', 'Pasture', 'Urban','Extensive forestry', 'Intensive forestry']:

    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[land_type, idx[country, :]] = exiobase3.satellite.S.loc[land_type, idx[country, :]].values * LC_Impact_CF_tables.loc[land_type,country]
        exiobase3.satellite.S_Y.loc[land_type, idx[country, :]] = exiobase3.satellite.S_Y.loc[land_type, idx[country, :]].values * LC_Impact_CF_tables.loc[land_type,country]

for water_consumption in ['Water Consumption Blue - Agriculture - wheat', 'Water Consumption Blue - Agriculture - rice', 'Water Consumption Blue - Agriculture - other cereals',
                          'Water Consumption Blue - Agriculture - oil crops', 'Water Consumption Blue - Agriculture - sugar crops', 'Water Consumption Blue - Agriculture - fibres',
                          'Water Consumption Blue - Agriculture - other crops', 'Water Consumption Blue - Agriculture - fodder crops']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[water_consumption, idx[country, :]]  = exiobase3.satellite.S.loc[water_consumption, idx[country, :]].values * Water_CF_tables.loc[water_consumption,country]
        exiobase3.satellite.S_Y.loc[water_consumption, idx[country, :]]  = exiobase3.satellite.S_Y.loc[water_consumption, idx[country, :]].values * Water_CF_tables.loc[water_consumption,country]

for water_consumption in ['Water Consumption Blue - Agriculture - vegetables','Water Consumption Blue - Agriculture - fruits', 'Water Consumption Blue - Agriculture - nuts', 'Water Consumption Blue - Agriculture - pulses','Water Consumption Blue - Agriculture - roots and tubers']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[water_consumption, idx[country, :]] = exiobase3.satellite.S.loc[water_consumption, idx[country, :]].values * Water_CF_tables.loc['Water Consumption Blue - Agriculture - Vegetables, fruit, nuts',country]
        exiobase3.satellite.S_Y.loc[water_consumption, idx[country, :]] = exiobase3.satellite.S_Y.loc[water_consumption, idx[country, :]].values * Water_CF_tables.loc['Water Consumption Blue - Agriculture - Vegetables, fruit, nuts',country]

### water consumption that is not agricultural ####

Get_index_S = list(exiobase3.satellite.S.iloc[45:135,:].index.values)
print(Get_index_S)

for water_consumption_type in Get_index_S:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[water_consumption_type, idx[country, :]] = exiobase3.satellite.S.loc[water_consumption_type, idx[country, :]].values * LC_Impact_CF_tables.loc['Water consumption - core ', country]
        exiobase3.satellite.S_Y.loc[water_consumption_type, idx[country, :]] = exiobase3.satellite.S_Y.loc[water_consumption_type, idx[country, :]].values * LC_Impact_CF_tables.loc['Water consumption - core ', country]

### Eutrophication ###

for eutrophication_pollution in ['P - agriculture - water', 'P - waste - water']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[eutrophication_pollution, idx[country, :]] = exiobase3.satellite.S.loc[eutrophication_pollution, idx[country, :]] * LC_Impact_CF_tables.loc['P emission to water ', country]
        exiobase3.satellite.S_Y.loc[eutrophication_pollution, idx[country, :]] = exiobase3.satellite.S_Y.loc[eutrophication_pollution, idx[country, :]] * LC_Impact_CF_tables.loc['P emission to water ', country]

for eutrophication_pollution in ['P - agriculture - soil', 'Pxx - agriculture - soil']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[eutrophication_pollution, idx[country, :]] = exiobase3.satellite.S.loc[eutrophication_pollution, idx[country, :]] * LC_Impact_CF_tables.loc['P emission to soil ', country]
        exiobase3.satellite.S_Y.loc[eutrophication_pollution, idx[country, :]] = exiobase3.satellite.S_Y.loc[eutrophication_pollution, idx[country, :]] * LC_Impact_CF_tables.loc['P emission to soil ', country]

for eutrophication_pollution in ['N - agriculture - water', 'N - waste - water']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[eutrophication_pollution, idx[country, :]] = exiobase3.satellite.S.loc[eutrophication_pollution, idx[country, :]] * LC_Impact_CF_tables.loc['N emissions to freshwater', country]
        exiobase3.satellite.S_Y.loc[eutrophication_pollution, idx[country, :]] = exiobase3.satellite.S_Y.loc[eutrophication_pollution, idx[country, :]] * LC_Impact_CF_tables.loc['N emissions to freshwater', country]

### Climate Change ###

for CO2_stressor in ['CO2 - combustion - air','CO2 - non combustion - Cement production - air','CO2 - non combustion - Lime production - air', 'CO2 - waste - biogenic - air','CO2 - waste - fossil - air', 'CO2 - agriculture - peat decay - air']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[CO2_stressor, idx[country, :]] = exiobase3.satellite.S.loc[CO2_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Carbon dioxide (fossil) - core', country]
        exiobase3.satellite.S_Y.loc[CO2_stressor, idx[country, :]] = exiobase3.satellite.S_Y.loc[CO2_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Carbon dioxide (fossil) - core', country]

Get_index_S = list(exiobase3.satellite.S.iloc[16:24, :].index.values)
non_combustion_methane_stressors = ['CH4 - waste - air', 'CH4 - agriculture - air']
non_combustion_methane_stressors.extend(Get_index_S)
for Fossil_CH4_stressor in ['CH4 - combustion - air']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[Fossil_CH4_stressor, idx[country, :]] = exiobase3.satellite.S.loc[Fossil_CH4_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Fossil methane - core', country]
        exiobase3.satellite.S_Y.loc[Fossil_CH4_stressor, idx[country, :]] = exiobase3.satellite.S_Y.loc[Fossil_CH4_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Fossil methane - core', country]

for CH4_stressor in (non_combustion_methane_stressors) :
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[CH4_stressor, idx[country, :]] = exiobase3.satellite.S.loc[CH4_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Methane - core', country]
        exiobase3.satellite.S_Y.loc[CH4_stressor, idx[country, :]] = exiobase3.satellite.S_Y.loc[CH4_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Methane - core', country]

for N2O_stressor in ['N2O - combustion - air', 'N2O - agriculture - air']:
    for country in countries_Exiobase3:
        exiobase3.satellite.S.loc[N2O_stressor, idx[country, :]] = exiobase3.satellite.S.loc[N2O_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Nitrous oxide - core', country]
        exiobase3.satellite.S_Y.loc[N2O_stressor, idx[country, :]] = exiobase3.satellite.S.loc[N2O_stressor, idx[country, :]] * LC_Impact_CF_tables.loc['Nitrous oxide - core', country]

#Recombining the relevant stressor table for manipulation in footprint calculations
Get_index_S = list(exiobase3.satellite.S.iloc[45:135,:].index.values)
Land_categories = ['Cereal grains Nec', 'Crops Nec', 'Oil seeds', 'Paddy rice', 'Plant-based fibers', 'Sugar', 'Vegetables, fruit, nuts', 'Wheat', 'Annual crops', 'Pasture', 'Urban','Extensive forestry', 'Intensive forestry' ]
Water_categories = ['Water Consumption Blue - Agriculture - wheat', 'Water Consumption Blue - Agriculture - rice', 'Water Consumption Blue - Agriculture - other cereals',
                'Water Consumption Blue - Agriculture - oil crops', 'Water Consumption Blue - Agriculture - sugar crops', 'Water Consumption Blue - Agriculture - fibres',
                'Water Consumption Blue - Agriculture - other crops', 'Water Consumption Blue - Agriculture - fodder crops', 'Water Consumption Blue - Agriculture - vegetables',
                'Water Consumption Blue - Agriculture - fruits', 'Water Consumption Blue - Agriculture - nuts', 'Water Consumption Blue - Agriculture - pulses', 'Water Consumption Blue - Agriculture - roots and tubers']
Water_categories.extend(Get_index_S)
Climate_categories = ['CO2 - combustion - air','CO2 - non combustion - Cement production - air','CO2 - non combustion - Lime production - air', 'CO2 - waste - biogenic - air','CO2 - waste - fossil - air', 'CO2 - agriculture - peat decay - air',
                  'CH4 - combustion - air', 'N2O - combustion - air', 'N2O - agriculture - air'  ]
Climate_categories.extend(non_combustion_methane_stressors)

Eutrophication_categories = ['P - agriculture - water', 'P - waste - water', 'P - agriculture - soil', 'Pxx - agriculture - soil', 'N - agriculture - water', 'N - waste - water'  ]


new_df = pd.DataFrame()
new_df2 = pd.DataFrame()
for stressor_category in (Land_categories, Water_categories, Climate_categories, Eutrophication_categories):
    new_df = new_df.append(exiobase3.satellite.S.loc[stressor_category,:])
    print(new_df)
    new_df2 = new_df2.append(exiobase3.satellite.S_Y.loc[stressor_category,:])

exiobase3.satellite.S = pd.DataFrame(new_df)
exiobase3.satellite.S_Y = pd.DataFrame(new_df2)

exiobase3.satellite.S.to_csv("C:/Users/Cillian/PycharmProjects/Master-Thesis/data/Raw/EXIO3/check_S.csv")
exiobase3.satellite.S_Y.to_csv("C:/Users/Cillian/PycharmProjects/Master-Thesis/data/Raw/EXIO3/check_S_Y.csv")
#exiobase3.Y = exiobase3.Y.groupby(level= 0, axis = 1, sort = False).sum(1)   ### All consumption categories included
###########################################################################################################################################################################

exiobase3.rename_regions({'AT': 'Austria', 'BE':'Belgium', 'BG':'Bulgaria','CZ':'Czech Republic', 'CY':'Cyprus', 'DE':'Germany', 'DK':'Denmark', 'EE':'Estonia',
                        'ES':'Spain','FR':'France','FI':'Finland','GR':'Greece', 'HU':'Hungary', 'HR':'Croatia', 'IE':'Ireland','IT':'Italy' ,'LT':'Lithuania', 'LV':'Latvia', 'LU': 'Luxembourg',
                       'MT':'Malta', 'NL': 'Netherlands', 'PL': 'Poland', 'PT': 'Portugal', 'SE':'Sweden', 'SK':'Slovakia', 'SI':'Slovenia','RO': 'Romania',
                       'GB': 'Great Britain', 'US':'United States', 'CN':'China', 'CA': 'Canada', 'JP': 'Japan', 'IN': 'India', 'ID': 'Indonesia',
                       'KR': 'South Korea', 'RU': 'Russia', 'NO': 'Norway', 'CH': 'Switzerland', 'TW':'Taiwan','TR':'Turkey','ZA':'South Africa', 'BR': 'Brazil',
                       'MX':'Mexico', 'AU': 'Australia', 'WA': 'RoW_Asia_and_Pacific', 'WF': 'RoW_Africa', 'WL': 'RoW_America', 'WM':'RoW_Middle_East', 'WE':'RoW_Europe'})

new_accounts = pymrio.calc_accounts(exiobase3.satellite.S, exiobase3.L, exiobase3.Y)  # Note here, we input Char_table_S rather than S for the calculation of the Biodiversity accounts

D_cba_biod = pd.DataFrame(new_accounts[0])
print(D_cba_biod.shape)
D_cba_biod = pd.DataFrame(D_cba_biod)

D_cba_biod = pd.DataFrame(
    D_cba_biod.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
                      'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
                      'Meat animals nec', 'Animal products nec', 'Raw milk',
                      'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec','Beverages', 'Sugar', 'Fish products', 'Dairy products',
                      'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec', 'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand
myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Biodiversity Footprint/EXIO3/BF_D_cba_2010_LCIA_disaggregted_Y_categories_agrifood_final_demand_continental_proxy_approach.csv'
D_cba_biod.to_csv(myfile)




exiobase3.satellite.D_pba = new_accounts[1]
print(exiobase3.satellite.D_pba.shape)
D_pba = pd.DataFrame(exiobase3.satellite.D_pba)
D_pba = pd.DataFrame(
    D_pba.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
                      'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
                      'Meat animals nec', 'Animal products nec', 'Raw milk',
                      'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec','Beverages', 'Sugar', 'Fish products', 'Dairy products',
                      'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec', 'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand

myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Biodiversity Footprint/EXIO3/BF_D_pba_2010_LCIA_disaggregated_Y_categories_agrifood_final_demand_continental_proxy_approach.csv'
D_pba.to_csv(myfile)

exiobase3.satellite.D_imp = new_accounts[2]
D_imp = pd.DataFrame(exiobase3.satellite.D_imp)
D_imp = pd.DataFrame(
    D_imp.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
                      'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
                      'Meat animals nec', 'Animal products nec', 'Raw milk',
                      'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec','Beverages', 'Sugar', 'Fish products', 'Dairy products',
                      'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec', 'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand
myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Biodiversity Footprint/EXIO3/BF_D_imp_2010_LCIA_disaggregated_Y_categories_agrifood_final_demand_continental_proxy_approach.csv'
D_imp.to_csv(myfile)

exiobase3.satellite.D_exp = new_accounts[3]
D_exp = pd.DataFrame(exiobase3.satellite.D_exp)
D_exp = pd.DataFrame(
    D_exp.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
                      'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
                      'Meat animals nec', 'Animal products nec', 'Raw milk',
                      'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec','Beverages', 'Sugar', 'Fish products', 'Dairy products',
                      'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec', 'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand

myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Biodiversity Footprint/EXIO3/BF_D_exp_2010_LCIA_disaggregated_Y_categories_agrifood_final_demand_continental_proxy_approach.csv'
D_exp.to_csv(myfile)


del exiobase3
