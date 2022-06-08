# Master-Thesis-code
The following repository contains the published code for the accompanying master thesis from Killian Davin. 
The repository contains 6 python scripts for the construction of spatially explicit, crop-specific characterisation factors (CFs) for agriculture from LC-Impact. 

The following 2 python scripts are executed to calculate land occupation CFs for 8 specific crops for the national and continental regions of EXIOBASE.
For successful execution, the scripts must be executed in sequential order 

- Land_Use_Step01.py   -        Overlaying of shapefiles and raster files and calc of national CFs
- Land_Use_Step02.py   -        Calculation of continental CFs

The following 4 python scripts were for the construction of the crop-specific water stress CFs from LC-Impact. Again, the scipts must be 
exectuted in a sequential fashion. 

- Watershed_Step01.py   -        Overlaying of water CF shapefile from LC-IMPACT with the Pfister & Bayer (2018) watershed shapefile
- Watershed_Step02.py   -        Calculation of total production of irrigated crops in Tonnes from the MapSPAM model per watershed layer
- Watershed_Step03.py   -        Calculation of total blue water consumption per crop per watershed layer
- Watershed_Step04.py   -        CF construction  


The python scripts for the biodiversity impact calculations via MRIO modelling are listed velow and need to be executed in sequence. 

- Footprints_Step01.py   -       Construction of desired stressor table S and pressure footprint calculation
- Footprints_Step02.py   -       Calculation of biodiversity footprints
