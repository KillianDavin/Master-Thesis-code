import pymrio
import pandas as pd


#####################################################################################

''' 

This python script is the code used for the formation of the desired stressor tables S in Exiobase and
for calculation of the environmental pressure footprints of land use 
and blue water consumption for the year 2010 in EXIOBASE as a result of food and agricultural product final demand in Y: 

'''

#####################################################################################

years = range(2010, 2011)
TS_D_cba = pd.DataFrame()
TS_D_pba = pd.DataFrame()
TS_D_imp = pd.DataFrame()
TS_D_exp = pd.DataFrame()

for n, year in enumerate(years):
    print(n, year)
    exio3_folder = "C:/Users/Cillian/PycharmProjects/Master-Thesis/data/Raw/EXIO3"
    exio_meta = pymrio.download_exiobase3(storage_folder=exio3_folder, system="pxp", years=[year])
    year = str(year)
    file_path = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/Raw/EXIO3/IOT_'+ year +'_pxp.zip'
   # print(file_path)
    exiobase3 = pymrio.parse_exiobase3(path= file_path)
    S = pd.DataFrame(exiobase3.satellite.S)
    Y = pd.DataFrame(exiobase3.Y)
    #Y = Y.groupby(level= 0, axis = 1, sort = False).sum(1)   ### All consumption categories included
    idx = pd.IndexSlice  # Slicing of multi index columns for separating out multiindex columns

##################################################################################################################################################################################################################

    '''Segregating the desired final demand categories of agriculture and food production and setting all other final demand entries to 0.0'''

##################################################################################################################################################################################################################

    Desired_final_demand_categories = pd.DataFrame(Y.loc[idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
                    'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
                    'Meat animals nec', 'Animal products nec', 'Raw milk',
                    'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec',
                    'Beverages', 'Sugar', 'Fish products', 'Dairy products',
                    'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec',
                    'products of Vegetable oils and fats', 'Processed rice']],:])

    Y.loc[:,:] = 0.0
    Y.loc[idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
                  'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
                  'Meat animals nec', 'Animal products nec', 'Raw milk',
                  'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec',
                  'Beverages', 'Sugar', 'Fish products', 'Dairy products',
                  'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec',
                  'products of Vegetable oils and fats', 'Processed rice']], :] = Desired_final_demand_categories.values

    print(list(Y.columns))
    print(list(Y.index))
##################################################################################################################################################################################################################

    '''Segregating the household consumption category from the Y tables'''

##################################################################################################################################################################################################################

##################################################################################################################################################################################################################

    '''Segregating required stressors from S tables. Segregation is completed via index referencing of original tables.
       Details on stressors and S table row index, see Appendix F in project literature'''

##################################################################################################################################################################################################################

land_stressors = pd.DataFrame(
    S.iloc[[446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 461, 462, 463, 464, 465],
    :])  # Seperation of land use categories using indexing. Rows obtained from csv file
print(land_stressors)
water_stressors = pd.DataFrame(S.iloc[923:1026])  # Blue water consumption stressor rows
print(water_stressors)
climate_change_stressors = pd.DataFrame(S.iloc[[23, 24, 25, 67, 68, 69, 70, 71, 72, 73, 74, 92, 93, 426, 427, 429,435,437, 438]])  # Climate change stressor rows
eutrophication_stressors = pd.DataFrame(S.iloc[[428,432, 433, 434, 440, 443]])  # Marine and Fresh eutrophication

# Aggregation of fodder crops in exiobase land use categories to LC-IMPACT categories

Annual_crop_df = pd.DataFrame(land_stressors.iloc[[2, 3, 4, 5, 6], :]).sum(0)  # Aggregation of the annual Fodder crop categories in exiobase to a singular LC-IMPACT category for Land Use (This will be characterised by the annual crop CF values for land
print(Annual_crop_df)
Annual_crop_df = pd.DataFrame(
    Annual_crop_df).T  # As python outputs a column vector for a summation operation, the transpose function T is used to return the annual crop dataframe to it's original Dataframe index/column set up with countries and products as the column index and stressor as the row index.
Pasture_crop_df = pd.DataFrame(land_stressors.iloc[[14, 15, 16], :]).sum(
    0)  # Aggregation of Pasture crop land use categories
Pasture_crop_df = pd.DataFrame(Pasture_crop_df).T
Urban_df = pd.DataFrame(land_stressors.iloc[[17], :]).sum(0)  # Aggregation of Urban land use categories
Urban_df = pd.DataFrame(Urban_df).T
Intensive_forestry_df = pd.DataFrame(land_stressors.iloc[[13], :]).sum(
    0)  # Aggregation of Intensive forestry land use stresors to LC-Impact category
Intensive_forestry_df = pd.DataFrame(Intensive_forestry_df).T
Extensive_forestry_df = pd.DataFrame(land_stressors.iloc[[18], :]).sum(
    0)  # Aggregation of Intensive forestry land use stresors to LC-Impact
Extensive_forestry_df = pd.DataFrame(Extensive_forestry_df).T

# Re-creating a combined dataframe for the individual and aggregated land use stressors

Land_aggregated_df = land_stressors
Land_aggregated_df.drop(Land_aggregated_df.index[[2,3,4,5,6,13,14,15,16,17,18]], inplace= True)
Individual_crop_stressor_names = list(Land_aggregated_df.index.values)
landuse_list = (Annual_crop_df, Pasture_crop_df, Urban_df, Extensive_forestry_df, Intensive_forestry_df)
new_land_categories_index = ['Cereal grains Nec', 'Crops Nec','Oil seeds','Paddy rice','Plant-based fibers','Sugar','Vegetables, fruit, nuts','Wheat' ,'Annual crops','Pasture', 'Urban', 'Extensive forestry', 'Intensive forestry']
for i in landuse_list:
    Land_aggregated_df = Land_aggregated_df.append(
        i)  # Appending Land_aggregated_df with each of the aggregated land use categories

Land_aggregated_df.reset_index()
Land_aggregated_df.set_axis(new_land_categories_index, inplace=True)  # Updating the index row labels
print(Land_aggregated_df)

# Combining the aggregated land use stressor categories with the disaggregated land use stressors, and the stressors for the other impact categories being analysed. This is the final compiled stressor matrix.
# Not necessary to add land stressors, but nice to have for future reference if required.

stressor_list = (climate_change_stressors, water_stressors, eutrophication_stressors)
exiobase3.satellite.S = Land_aggregated_df  # Full_stressor_list = All required stressors (aggregated and disaggregated) for footprint calculations
for i in stressor_list:
    exiobase3.satellite.S = exiobase3.satellite.S.append(i)

S = pd.DataFrame(exiobase3.satellite.S)
S.to_csv('S_check.csv')

##################################################################################################################################################################################################################

'''Segregating required stressors from S_Y tables in exactly the same fashion as what was completed above for the S tables'''

##################################################################################################################################################################################################################

S_Y = pd.DataFrame(exiobase3.satellite.S_Y)
land_stressors_S_Y = pd.DataFrame(
    S_Y.iloc[[446, 447, 448, 449, 450, 451, 452, 453, 454, 455, 456, 457, 458, 459, 461, 462, 463, 464, 465],
    :])  # Seperation of land use categories using indexing. Rows obtained from csv file
water_stressors_S_Y = pd.DataFrame(S_Y.iloc[923:1026])  # Blue water consumption stressor rows
climate_change_stressors_S_Y = pd.DataFrame(S_Y.iloc[
                                                [23, 24, 25, 67, 68, 69, 70, 71, 72, 73, 74, 92, 93, 426, 427,
                                                 429,
                                                 435, 437, 438]])  # Global warming stressor rows
eutrophication_stressors_S_Y = pd.DataFrame(
    S_Y.iloc[[428,432, 433, 434, 440, 443]])  # Marine and Fresh eutrophication

# Combining the aggregated land use stressor categories with the disaggregated land use stressors, and the stressors for the other impact categories being analysed. This is the final compiled stressor matrix.

# Aggregation of exiobase land use categories to LC-IMPACT categories_S_Y

Annual_crop_df_S_Y = pd.DataFrame(land_stressors_S_Y.iloc[[ 2, 3, 4, 5, 6], :]).sum(
    0)  # Aggregation of the annual crop categories in exiobase to the singular LC-IMPACT category for Land Use
Annual_crop_df_S_Y = pd.DataFrame(
    Annual_crop_df_S_Y).T  # As python outputs a column vector for a sumation operation, the transpose function T is used to return the annual crop dataframe to it's original Dataframe index/column set up with countries and products as the column index and stressor as the row index.
Pasture_crop_df_S_Y = pd.DataFrame(land_stressors_S_Y.iloc[[14, 15, 16], :]).sum(
    0)  # Aggregation of Pasture crop land use categories
Pasture_crop_df_S_Y = pd.DataFrame(Pasture_crop_df_S_Y).T
Urban_df_S_Y = pd.DataFrame(land_stressors_S_Y.iloc[[17], :]).sum(0)  # Aggregation of Urban land use categories
Urban_df_S_Y = pd.DataFrame(Urban_df_S_Y).T
Intensive_forestry_df_S_Y = pd.DataFrame(land_stressors_S_Y.iloc[[13], :]).sum(
    0)  # Aggregation of Intensive forestry land use stresors to LC-Impact category
Intensive_forestry_df_S_Y = pd.DataFrame(Intensive_forestry_df_S_Y).T
Extensive_forestry_df_S_Y = pd.DataFrame(land_stressors_S_Y.iloc[[18], :]).sum(
    0)  # Aggregation of Intensive forestry land use stresors to LC-Impact
Extensive_forestry_df_S_Y = pd.DataFrame(Extensive_forestry_df_S_Y).T

# Re-creating a combined dataframe for the aggregated land use stressors_F_Y
Land_aggregated_df_S_Y = land_stressors_S_Y
Land_aggregated_df_S_Y.drop(Land_aggregated_df_S_Y.index[[2,3,4,5,6,13,14,15,16,17,18]], inplace= True)
landuse_list = (
    Annual_crop_df_S_Y, Pasture_crop_df_S_Y, Urban_df_S_Y, Extensive_forestry_df_S_Y,
    Intensive_forestry_df_S_Y)
new_land_categories_index = ['Cereal grains Nec', 'Crops Nec','Oil seeds','Paddy rice','Plant-based fibers','Sugar','Vegetables, fruit, nuts','Wheat' ,'Annual crops','Pasture', 'Urban', 'Extensive forestry', 'Intensive forestry']
for i in landuse_list:
    Land_aggregated_df_S_Y = Land_aggregated_df_S_Y.append(
        i)  # Appending Land_aggregated_df with each of the aggregated land use categories

Land_aggregated_df_S_Y.reset_index()
Land_aggregated_df_S_Y.set_axis(new_land_categories_index, inplace=True)  # Updating the index row labels

# Combining the aggregated land use stressor categories with the disaggregated land use stressors, and the stressors for the other impact categories being analysed. This is the final compiled stressor matrix for F_Y.

stressor_list_S_Y = (
    climate_change_stressors_S_Y, water_stressors_S_Y, eutrophication_stressors_S_Y)
exiobase3.satellite.S_Y = Land_aggregated_df_S_Y  # Full_stressor_list = All required stressors (aggregated and disaggregated) for footprint calculations
for i in stressor_list_S_Y:
    exiobase3.satellite.S_Y = exiobase3.satellite.S_Y.append(i)

S_Y = pd.DataFrame(exiobase3.satellite.S_Y)

##################################################################################################################################################################################################################

'''With a new Y table, S table and S_Y table, all other tables are reset to the co-efficients
for the recalculation of new x,F,Z,M tables. Resetting of coefficients with pymrio resets all tables in EXIOBASE other than the
A and L matrices'''

##################################################################################################################################################################################################################
exiobase3.reset_all_to_coefficients()
print(exiobase3.A)  # 9800x9800
exiobase3.L = pymrio.calc_L(exiobase3.A)
print(exiobase3.L)  # 9800x9800

print(exiobase3.x)  # 0
print(exiobase3.satellite.F)  # 0
print(exiobase3.Z)  # 0
print(exiobase3.satellite.M)  # 0
exiobase3.Y = pd.DataFrame(Y)  # Setting Y tables to Y tables formed in the first section of the code
exiobase3.satellite.S = pd.DataFrame(S)  # Setting S tables to S tables formed in the second section of the code
exiobase3.satellite.S_Y = pd.DataFrame(
    S_Y)  # Setting S_Y tables to S_Y tables formed in third section of the code
Y = exiobase3.Y
exiobase3.x = pymrio.calc_x_from_L(exiobase3.L, exiobase3.Y.sum(
    1))  # Using PYMRIO functionality to calculate x from L and Y tables
exiobase3.Z = pymrio.calc_Z(exiobase3.A,
                            exiobase3.x)  # Using PYMRIO functionality to calculate Z from A and x tables

exiobase3.satellite.F_Y = pd.DataFrame(pymrio.calc_F_Y(exiobase3.satellite.S_Y, pd.DataFrame(exiobase3.Y.sum(0)).T))
exiobase3.satellite.F = pd.DataFrame(pymrio.calc_F(exiobase3.satellite.S, exiobase3.x))
exiobase3.M = pd.DataFrame(pymrio.calc_M(exiobase3.satellite.S, exiobase3.L))
exiobase3.Y = pd.DataFrame(Y.groupby(level=0, axis=1, sort=False).sum(1))  ### All consumption categories included
##################################################################################################################################################################################################################

'''Following re-calc of all relevant tables, the PYMRIO calc_accounts function is used
to calculate pressure footprint accounts D_cba, D_pba, D_imp and D_exp. The function returns a tupple where
new_accounts[0] = D_cba, new_accounts[1] = D_pba, new_accounts[2] = D_imp, new_accounts[3] = D_exp.'''

##################################################################################################################################################################################################################
new_accounts = pymrio.calc_accounts(exiobase3.satellite.S, exiobase3.L, exiobase3.Y)
exiobase3.satellite.D_cba = new_accounts[0]
D_cba = pd.DataFrame(exiobase3.satellite.D_cba)

D_cba = pd.DataFrame(
    D_cba.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
            'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
            'Meat animals nec', 'Animal products nec', 'Raw milk',
            'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec',
            'Beverages', 'Sugar', 'Fish products', 'Dairy products',
            'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec',
            'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand
myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Pressure Footprint/EXIO3/PF_D_cba_' + year + '_LCIA_disaggregated_All_Y_categories_agrifood_final_demand.csv'
D_cba.to_csv(myfile)

myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Pressure Footprint/EXIO3/PF_D_pba_' + year + '_LCIA_disaggregated_All_Y_categories_agrifood_final_demand.csv'

exiobase3.satellite.D_pba = new_accounts[1]
print(exiobase3.satellite.D_pba.shape)
D_pba = pd.DataFrame(exiobase3.satellite.D_pba)
D_pba = pd.DataFrame(
    D_pba.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
            'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
            'Meat animals nec', 'Animal products nec', 'Raw milk',
            'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec',
            'Beverages', 'Sugar', 'Fish products', 'Dairy products',
            'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec',
            'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand

D_pba.to_csv(myfile)

exiobase3.satellite.D_imp = new_accounts[2]
D_imp = pd.DataFrame(exiobase3.satellite.D_imp)
D_imp = pd.DataFrame(
    D_imp.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
            'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
            'Meat animals nec', 'Animal products nec', 'Raw milk',
            'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec',
            'Beverages', 'Sugar', 'Fish products', 'Dairy products',
            'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec',
            'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand
myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Pressure Footprint/EXIO3/PF_D_imp_' + year + '_LCIA_disaggregated_All_Y_categories_agrifood_final_demand.csv'
D_imp.to_csv(myfile)

exiobase3.satellite.D_exp = new_accounts[3]
D_exp = pd.DataFrame(exiobase3.satellite.D_exp)
D_exp = pd.DataFrame(
    D_exp.loc[:, idx[:, ['Paddy rice', 'Wheat', 'Cereal grains nec', 'Vegetables, fruit, nuts', 'Oil seeds',
            'Sugar cane, sugar beet', 'Plant-based fibers', 'Crops nec', 'Cattle', 'Pigs', 'Poultry',
            'Meat animals nec', 'Animal products nec', 'Raw milk',
            'Fish and other fishing products; services incidental of fishing (05)', 'Food products nec',
            'Beverages', 'Sugar', 'Fish products', 'Dairy products',
            'Products of meat cattle', 'Products of meat pigs', 'Products of meat poultry', 'Meat products nec',
            'products of Vegetable oils and fats', 'Processed rice']]])  # Seggregating final consumer household demand

myfile = 'C:/Users/Cillian/PycharmProjects/Master-Thesis/data/processed/Pressure Footprint/EXIO3/PF_D_exp_' + year + '_LCIA_disaggregated_All_Y_categories_agrifood_final_demand.csv'
D_exp.to_csv(myfile)
