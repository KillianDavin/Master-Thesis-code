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

''' 

This python script is the code used to convert the 160 Water dataset  crop categories and 42 mapSPAM crop categories   
to the standardised FAO/Exiobase aggregated crop categories. In the final sections, the total water consumption 
per crop, per watershed, per country is calculated using the mapSPAM Tonnes of crop produced per polygon/watershed area for the year 2010 and the 
pfister & bayer data for blue water consumption per tonne of crop produced or total blue water consumption of a crop, 
per watershed per country in some instances for the year 2000. 
  
The following 3 sections are included: 

Section 1: Normalization of water dataset crop categories and MapSPAM crop categories to EXIOBASE crop categories
Section 2: Treatment of blue water consumption mismatches between MapSPAM and pfister & bayer water dataset
Section 3:  Calculation of total irrigated blue water consumption for 2010 after merging BW_per_ton and Mapspam production data (tonnes)

'''

#####################################################################################

#####################################################################################
''' 
Section 1: 

Normalization of water dataset crop categories and MapSPAM crop categories to EXIOBASE crop categories

'''
#####################################################################################


### Read Data in from Watershed_step01.py computation step ###

Crop_BW_Ton = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Watershed data/Per_Ton_BW_Consumption_mergerd_watershed_layers.csv')

Total_BW = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/Watershed data/Total_BW_Consumption_mergerd_watershed_layers.csv')

### Read in FAO_Exiobase crop categorisation info/codes ###

FAO_codes = pd.ExcelFile('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/FAO_EXIOBASE codes/Copy of List_Primary production_FAO-CPA-EXIOBASE.xlsx')
for n in FAO_codes .sheet_names:
    if n == 'Correspondance_FAO-CPA-EXIOBASE':
        FAO_codes = FAO_codes.parse(sheet_name = n)

### Normalisation of crop names across FAO-WaterGAP-MapSPAM for manipulation in future steps #########

''' Crop names used in WaterGAP were maintained and FAO-MapSPAM were normalised accordingly. 
  Crops not covered in WaterGAP were removed from the FAO crop aggregated categories. These crops are as follows: 
  Popcorn, Fruit_pome_nes, brazil nuts, karite nuts, Tung nuts, Jojoba seed, Tallowtree seed, Hempseed, 
  Cottonlint, chicoryroot, Mate,Pyrethrum dried, Cassava leaves, peppermint, leeks and other alliaceous veg, 
    melons other, mushrooms + truffles., Tea nes '''

''' Note: MapSPAM has slightly different categorisation to Exiobase. It includes Nuts in the Cros_Nec category 
  while FAO includes this in Vegetables, Fruits, Nuts. Sugar Nes is also included in Crops_Nec in MapSPAM 
   but included in Sugar, Sugar Beet category in FAO. Reconcilliation steps required at later stage '''

######################################################################################################

Paddy_Rice = ['Ricepaddy']
Wheat = ['Wheat']
cereal_grains_nec = list(FAO_codes.iloc[2:16,0])
cereal_grains_nec[11] = 'Canaryseed'
cereal_grains_nec[12] = 'Mixedgrain'
cereal_grains_nec[13] = 'Cerealsnes'


cereal_grains_nec.pop(2)  #Popcorn not covered in water data
Fruit = list(FAO_codes.iloc[16:54,0])
Fruit[5], Fruit[6], Fruit[7], Fruit[8] = 'Tangerinesmandarinsclem' , 'Lemonsandlimes', 'Grapefruit_incpomelos', 'Citrusfruitnes'
Fruit[13], Fruit[15],Fruit[16], Fruit[17]  = 'Sourcherries', 'peachetc','Plumsandsloes', 'Stonefruitnes'
Fruit[25], Fruit[28], Fruit[34] = 'BerriesNes', 'Mangoesmangosteensguavas', 'Kiwifruit'
Fruit[36], Fruit[37] = 'Fruittropicalfreshnes', 'FruitFreshNes'
Fruit.pop(18) #'Fruit, pome nes not covered in water data
Nuts = list(FAO_codes.iloc[54:64,0])
Nuts[1], Nuts[2], Nuts[3], Nuts[4] = 'Cashewnutswithshell','chstnut', 'Almondswithshell', 'Walnutswithshell'
Nuts[6], Nuts[7], Nuts[8], Nuts[9] = 'Kolanuts', 'Hazelnutswithshell', 'Arecanuts', 'Nutsnes'
Nuts.pop(0)  #Brazil nuts not covered in water data
Pulses = list(FAO_codes.iloc[64:77,0])
Pulses[0], Pulses[1], Pulses[2], Pulses[3] = 'Beansdry', 'Broadbeanshorsebeansdry', 'Peasdry', 'Chickpeas'
Pulses[4], Pulses[5], Pulses[7], Pulses[10], Pulses[11], Pulses[12] = 'Cowpeasdry' ,'Pigeonpeas', 'Bambarabeans', 'Pulsesnes', 'Beansgreen', 'Stringbeans'
Roots_and_Tubers = list(FAO_codes.iloc[77:84,0])
Roots_and_Tubers[1], Roots_and_Tubers[3], Roots_and_Tubers[4], Roots_and_Tubers[6] = 'Sweetpotatoes', 'Yautia_cocoyam', 'Taro_cocoyam', 'RootsandTubersnes'
Oil_Seeds = list(FAO_codes.iloc[110:129,0])
Oil_Seeds[1], Oil_Seeds[2], Oil_Seeds[4], Oil_Seeds[5], Oil_Seeds[9] = 'Groundnutswithshell', 'Oilpalmfruit', 'Castoroilseed', 'Sunflowerseed', 'Safflowerseed'
Oil_Seeds[10], Oil_Seeds[11], Oil_Seeds[12], Oil_Seeds[13], Oil_Seeds[15], Oil_Seeds[18]  = 'Sesameseed', 'Mustardseed', 'Poppyseed', 'Melonseed', 'Seedcotton', 'OilseedsNes'
Oil_Seeds.pop(3)  #karite nuts
Oil_Seeds.pop(6) #Tung nuts
Oil_Seeds.pop(6) #Jojoba seed
Oil_Seeds.pop(11) #Tallowtree seed
Oil_Seeds.pop(13) #Hempseed
sugar = list(FAO_codes.iloc[129:132,0])
sugar[0], sugar[1], sugar[2] = 'Sugarcane', 'Sugarbeet', 'Sugarcropsnes'
sugar.pop(2)  #Sugarcropsnes dealt with later as it is merged with crops nec in SPAM. Total water consumption from WaterGAP model for year 2000 is used for Sugarcropsnes
Plant_Based_Fibres = list(FAO_codes.iloc[132:143,0])
Plant_Based_Fibres[1], Plant_Based_Fibres[2], Plant_Based_Fibres[4] = 'Flaxfibreandtow', 'HempTowWaste',  'OtherBastfibres'
Plant_Based_Fibres[7], Plant_Based_Fibres[8], Plant_Based_Fibres[10] = 'AgaveFibresNes', 'ManilaFibre_Abaca', 'FibreCropsNes'
Plant_Based_Fibres[0] = 'Seedcotton'
Plant_Based_Fibres.pop(9) # No data for Coir
Crops_Nec = list(FAO_codes.iloc[143:163,0])
Crops_Nec[7], Crops_Nec[8] = 'Pepper_Piperspp',  'Chilliesandpeppersdry'
Crops_Nec[10], Crops_Nec[12], Crops_Nec[13], Crops_Nec[15] = 'Cinnamon_canella', 'Nutmegmaceandcardamoms', 'Anisebadianfennelcorian', 'Spicesnes',
Crops_Nec[19] = 'Naturalrubber'
Crops_Nec.pop(0) # chicory roots - no data
Crops_Nec.pop(0) # coffee - diff category

#Remove 'Coffeegreen', 'Cocoabeans', 'Tea', 'Tobaccounmanufactured' as can be quantified seperately as commodities

Crops_Nec.pop(0) #cocoa - diff category
Crops_Nec.pop(0) #teas - diff category
Crops_Nec.pop(0) # Mate - no data
Crops_Nec.pop(0) # Tea nes - no data
Crops_Nec.pop(10) # Peppermint - no data
Crops_Nec.pop(10) # 'Pyrethrum, dried' - no data
Crops_Nec.pop(10) #Tobacco - diff category

Crops_commodity = list(FAO_codes.iloc[[144,145,146,161],0])
Crops_commodity[0], Crops_commodity[1], Crops_commodity[3] = 'Coffeegreen', 'Cocoabeans', 'Tobaccounmanufactured'
Vegetables = list(FAO_codes.iloc[84:110,0])
Vegetables[1], Vegetables[4], Vegetables[8], Vegetables[9], Vegetables[10]= 'Cabbagesandotherbrassicas', 'Lettuceandchicory', 'Cauliflowersandbroccoli', 'Pumpkinssquashandgourds', 'Cucumbersandgherkins'
Vegetables[11], Vegetables[12], Vegetables[13], Vegetables[14], Vegetables[17],Vegetables[18], = 'Eggplants_aubergines', 'Chilliesandpeppersgreen', 'Onions_incshallotsgreen', 'Onionsdry', 'Peasgreen', 'Leguminousvegetablesnes'
Vegetables[19], Vegetables[21], Vegetables[23] = 'Carrotsandturnips', 'Maizegreen', 'Vegetablesfreshnes',
print(Vegetables)
Vegetables.pop(6) #casavaleaves - no data
Vegetables.pop(15) #leeks and other alliaceous veg - no data
Vegetables.pop(20) #mushroom + truffles - no data
Vegetables.pop(22) #Melones other + cantouloupe - no data
n = [Wheat,Paddy_Rice, cereal_grains_nec, Fruit, Nuts, Pulses, Roots_and_Tubers, Oil_Seeds, sugar, Plant_Based_Fibres, Crops_commodity, Vegetables]
str_n = ['Wheat', 'Paddy_rice', 'cereal_grains_nec', 'Fruit', 'Nuts', 'Pulses', 'Roots_and_Tubers', 'Oil_Seeds','sugar','Plant_Based_Fibres', 'Crops_commodity', 'Vegetables']  # Nuts not included here. Total water consumed for nuts included later
count = 0
New_df = pd.DataFrame()
Water_df = pd.DataFrame(Crop_BW_Ton)
Water_df = pd.DataFrame(Water_df.iloc[:,0:6])

### Getting average water consumption per tonne of crop produced for all the FAO crop categories contained in an EXIOBASE agrregated crop category.
## Transformation of Watergap data to aggregated FAO sectors ###

for FAO_category in n :
    New_df= pd.DataFrame(Crop_BW_Ton[FAO_category].values)
    New_df = New_df.mean(1)
    Water_df[str_n[count]] = New_df
    count += 1

print(Water_df)
Water_df.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/water_df_check.csv')
Water_df.set_index('CTRY', inplace= True)

#####################################################################################
''' 
Section 2: 

Treatment of blue water consumption mismatches between MapSPAM and pfister & bayer water dataset. Also we
treat the mismatches of crop categories between MapSPAM and EXIOBASE here. 

'''

######################################################################################################

'''Any watershed polygon that has 0 BW/ton data for the different crop categories is given the country average BW/ton value. 
   This is to cover data gaps at a later stage, where the MAP SPAM model locates crop production in a polygon  but 
   the water-gap model has not identified water consumption in the same polygon for the year 2000. '''

######################################################################################################

Water_df = pd.DataFrame(Water_df)
print(Water_df)
Countries_water_gap = set(list(Water_df.index.values))
new_df = pd.DataFrame()

for country in Countries_water_gap:
    count = 0
    for FAO_category in str_n:
        length_of_dataframe = len(Water_df.loc[[country]].index)
        if length_of_dataframe == 1 :
            new_df = Water_df.loc[country, FAO_category]

        else:

            new_df = Water_df.loc[country,FAO_category]
            index = list(new_df.index.values)
            new_df = pd.DataFrame(new_df.values, index = index , columns = [str_n[count]])
            new_df[FAO_category] = new_df[FAO_category].replace(0, new_df[FAO_category].mean())
            Water_df.loc[country, FAO_category] = new_df[FAO_category].values

        count +=1

for FAO_category in str_n:
    Water_df[str_n] = Water_df[str_n].replace(0, Water_df[str_n].mean())


Water_df.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/water_df_check2.csv')

######################################################################################################

### Reconcilliation of Nuts and Sugar Nec. ##################################################

'''As detailed individual production data for the Nuts and Sugar Nec crops cannot be obtained from MapSPAM, Total water consumption 
 for these crops for the year 2000 according to the WaterGAP model was used. Also no fodder crop details available in 
 MapSPAM but available in WaterGAP. Fodder crop total consumption for the year 2000 was used. For the crop Nes category, 
 total water consumption for spices for year 2000 is added in following step to individual per_ton BW cons. and 
  production data for Tea, coffee, cocoa and tobacco, to form recombined Crop_Nes category without Nuts'''

'''Note: Nuts contained in Crops nes category in MapSPAM, therefore the Crops Nes category needs to be disaggregated via 
         the WaterGap data and reaggregated once again while excluding the Nuts categories'''

Crop_Nec_df = pd.DataFrame(Total_BW[Crops_Nec])
Crop_Nec_df = pd.DataFrame(Crop_Nec_df.sum(1).values, columns = ['Crop_Nec_Total Water Usage '])
Nuts_df = pd.DataFrame(Total_BW[Nuts])
print(Nuts_df)
Nuts_df = pd.DataFrame(Nuts_df.sum(1).values, columns = ['Nuts_Total_Water_Usage'])
Sugar_nes_df = pd.DataFrame(Total_BW['Sugarcropsnes'].values, columns = ['sugarnes'])
print(Sugar_nes_df)
Fodder_crops = ['Fodder', 'Fodder.1','Fodder.2', 'Fodder.3','Fodder.4','Fodder.5','Fodder.6','Fodder.7','Fodder.8','Fodder.9','Fodder.10','Fodder.11', 'Fodder.12','Fodder.13','Fodder.14','Fodder.15']
Fodder_crops = pd.DataFrame(Total_BW[Fodder_crops])
Fodder_crops = pd.DataFrame(Fodder_crops.sum(1).values, columns = ['Fodder_Crops'])


#####################################################################################
''' 
Section 3: 

Calculation of total irrigated blue water consumption for 2010 after merging BW_per_ton and Mapspam production data (tonnes)

'''

######################################################################################################

### Read in Tonnes of Crops produced per watershed area. Calculated in Watershed_Step02  ###

Production_df = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/overlayed_layers_SPAM_production_irrigated_watersheds_to_FAO_categories.csv')
Production_df = Production_df.iloc[154:,:]    # To match excel file length and index supplied with WaterGAP shapefile 'watershed_WF_crops.xlsx'

#### Calculation of total water consumption per FAO crop category, using BW_per_ton data from WaterGAP and tons produced from MapSPAM ###

FAO_categories_str = ['Wheat', 'Paddy_rice','cereal_grains_nec', 'Fruit', 'Pulses', 'Roots_and_Tubers', 'Oil_Seeds', 'sugar', 'Plant_Based_Fibres', 'Vegetables']

Water_consumption_df = pd.DataFrame(Water_df.iloc[:,0:6])


for FAO_category in FAO_categories_str :
    Water_consumption_df[FAO_category] = Water_df[FAO_category].values * Production_df[FAO_category].values
    print(Water_consumption_df)
Water_consumption_df['Crops_Nec'] = (Production_df['Crops_nec_commodity'].values * Water_df['Crops_commodity'].values) + Crop_Nec_df['Crop_Nec_Total Water Usage '].values
Water_consumption_df['Nuts'] = Nuts_df['Nuts_Total_Water_Usage'].values
Water_consumption_df['Vegetables, fruit, nuts'] = Water_consumption_df['Fruit'].values + Water_consumption_df['Pulses'].values + Water_consumption_df['Roots_and_Tubers'].values + Water_consumption_df['Vegetables'].values + Water_consumption_df['Nuts'].values
Water_consumption_df['Fodder_Crops'] = Fodder_crops['Fodder_Crops'].values
Water_consumption_df.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/water_consumption_FAO_category_PDF_output_dataframe_trial.csv')

print(Water_consumption_df.shape)
print(Sugar_nes_df.shape)

Water_consumption_df['sugar'] = Water_consumption_df['sugar'].values + Sugar_nes_df['sugarnes'].values
del Water_consumption_df['index']
#del Water_consumption_df['Unnamed: 0']
del Water_consumption_df['Fruit']
del Water_consumption_df['Pulses']
del Water_consumption_df['Roots_and_Tubers']
del Water_consumption_df['Vegetables']
del Water_consumption_df['Nuts']
print(Water_consumption_df)

### Adding South Sudan proxy, missing from WaterGAP model but found to have irrigated crop data in MapSPAM and is contained in Exiobase ###

'''
Proxy Water consumption data for South Sudan is assumed based on neighbouring country interpolation. 
The neighbouring countries bordering South Sudans, total water consumption data per crops, was averaged and applied to South Sudan 
as a rough approximation of water consumption in the region
'''

####

South_Sudan = pd.read_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/proxy_BW_cons_and_watershed_cfs_for_missing_countries.csv')
South_Sudan = pd.DataFrame(South_Sudan.iloc[0,:]).T
South_Sudan.set_index(['CTRY'], inplace = True)
SS_df = pd.DataFrame(index = South_Sudan.index)
count = 0
for FAO_category in n :
    New_df= pd.DataFrame(South_Sudan[FAO_category].values)
    New_df = New_df.sum(1)
    SS_df[str_n[count]] = New_df.values
    count += 1
SS_df.insert(0,'FID', value= 0)
SS_df.insert(0,'watershed_CF_factor', value = South_Sudan['watershed_CF_factor'].values)
SS_df.insert(0,'geometry', value= 0)
SS_df.insert(0,'CTRY', value= South_Sudan.index)
SS_df['Crops_Nec'] = SS_df['Crops_commodity']
SS_df['Vegetables, fruit, nuts'] = SS_df['Fruit'] + SS_df['Pulses'] + SS_df['Roots_and_Tubers'] + SS_df['Vegetables'] + SS_df['Nuts']
SS_df['Fodder_Crops'] = 0
del SS_df['Fruit']
del SS_df['Pulses']
del SS_df['Roots_and_Tubers']
del SS_df['Vegetables']
del SS_df['Nuts']
del SS_df['Crops_commodity']
del SS_df['CTRY']
print(SS_df)
Water_consumption_df = Water_consumption_df.append(SS_df)

Water_consumption_df.to_csv('C:/Users/Cillian/OneDrive - NTNU/Documents/NTNU project documents/ArcGIS_shapefiles_MT2022/GIS_layers_output/water_consumption_FAO_category_PDF_output_dataframe_ver02.csv')


