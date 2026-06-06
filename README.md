# Banking on Biodiversity

This repository contains code produced during research-assistant work on the
project "Banking on Biodiversity" and specifically for researcher Stefano Tarroni (https://www.stefanotarroni.com). The code builds survey and spatial data
inputs for analysis of community seed banks, candidate villages, household
panels, agricultural outcomes, and environmental covariates in Uganda.

In the notes below, `CSB` means community seed bank.

The repository is organized as a reproducibility guide rather than a single
push-button pipeline. Most notebooks currently use local file paths, so anyone
rerunning the project should first update the path variables at the top of each
notebook or script.

## Data and Software Requirements

The raw data are not stored in this repository. To reproduce the workflow, you
need access to the local data folders used by the notebooks, including:

- Uganda LSMS / UNPS wave-level `.dta` files.
- Community seed bank (CSB) and candidate village coordinate files.
- Household observation ID and harmonized LSMS files.
- Spatial rasters and shapefiles, including CHIRPS/CHIRTS exports, land-cover
  rasters, SPAM crop rasters, population density, GAEZ crop suitability, and
  buffer shapefiles.
- Intermediate Excel/CSV files exported from Google Earth Engine or earlier
  notebooks.

Main software used:

- Python / Jupyter with `pandas`, `numpy`, `pyreadstat`, `openpyxl`,
  `pyarrow`, `geopandas`, `rasterio`, `rioxarray`, `rasterstats`, `xarray`,
  and `rapidfuzz`.
- Google Earth Engine Code Editor for the scripts in `GEE/`.
- Stata for the scripts in `STATA/`.

Before running, replace hard-coded paths such as `C:/Users/Carl/Desktop/...` or
`Path("/")` with the correct root folder on your computer.

## Logic Tree

The project can be read as the following data-building tree.

```text
Raw inputs
|-- Uganda LSMS / UNPS wave files
|-- Community seed bank and candidate village coordinates
|-- Spatial rasters, shapefiles, and Google Earth Engine assets
|-- Consumption, price, and balance-table input files
|
|-- 1. Explore raw data and identify variables
|   |-- Trial and Error/Wavematching.ipynb
|   |-- Trial and Error/LSMS working file.ipynb
|   |-- Trial and Error/lsms_loader.py
|   `-- Various Code/Wave_variable_inventory.ipynb
|
|-- 2. Standardize LSMS sections across waves
|   |-- Panel Building/household rosterization.ipynb
|   |-- Panel Building/Panelbuilder (GSEC).ipynb
|   |-- Panel Building/Panelbuilder (AGSEC).ipynb
|   `-- Panel Building/Panelbuilder (CSEC).ipynb
|
|-- 3. Merge standardized survey sections into household/agricultural panels
|   |-- Panel Building/Merging Sections.ipynb
|   |-- Panel Building/AG HH CROP LEVEL.ipynb
|   `-- Panel Building/hh id obs.ipynb
|
|-- 4. Build spatial and environmental covariates
|   |-- GEE/AWA_seasonal_rainfall
|   |-- GEE/Rainfall_anomaly
|   |-- GEE/Seasonal_temp_CHIRTS
|   |-- GEE/adjusted_crop_suitability_index
|   |-- Various Code/Landcover_loop.ipynb
|   |-- Various Code/SPAM_crop_loop.ipynb
|   |-- Various Code/Crop Suitability.ipynb
|   |-- Various Code/Density reshape.ipynb
|   |-- Various Code/village matching.ipynb
|   `-- Various Code/Prices.ipynb
|
|-- 5. Build analysis-ready village/site panels
|   |-- Panel Building/reg_ready_villages.ipynb
|   `-- Panel Building/covariate_balance_panel.ipynb
|
`-- 6. Final Stata summaries and balance checks
    |-- STATA/Balancetable_PSW
    |-- STATA/HH_consumption_wavewise
    `-- STATA/Standard_errors_consumption
```

## Recommended Run Order

### 1. Inventory and exploration

Start here if you are reproducing the project from raw LSMS files.

| File | What it does | Main output |
| --- | --- | --- |
| `Trial and Error/Wavematching.ipynb` | Explores how files and variables line up across LSMS waves. Builds a cross-wave variable catalog and tests stacking sections. | `variable_catalog_all_waves.xlsx`, `AGSEC1_stacked_preview.xlsx` |
| `Trial and Error/LSMS working file.ipynb` | Early working notebook for reading wave 1 household, community, and agriculture sections. It prototypes household-, person-, community-, parcel-, plot-, crop-, livestock-, and extension-service extracts. | Multiple wave 1 CSV extracts |
| `Trial and Error/lsms_loader.py` | Helper functions for reading a variable specification, finding `.dta` files, selecting requested columns, and adding standard household/person/community keys. | Python helper module |
| `Various Code/Wave_variable_inventory.ipynb` | Variable-inventory script for one wave at a time. Despite the `.ipynb` extension, this file is plain Python text and may need indentation/path cleanup before running. | `wave*_variable_inventory.xlsx` |

### 2. Standardize LSMS survey sections

These notebooks convert raw wave-specific files into standardized section files
that can be merged later.

| File | What it does | Main output |
| --- | --- | --- |
| `Panel Building/household rosterization.ipynb` | Creates a roster-style `GSEC15A` file from `GSEC2` for a wave where the roster needs to be reconstructed. | `GSEC15A_wave*_from_GSEC2.csv`, preview Excel, parquet |
| `Panel Building/Panelbuilder (GSEC).ipynb` | Standardizes household sections across waves, including consumption, assets, enterprise, shocks, transport, roster, and related household modules. Contains special cleaning for sections such as GSEC17, GSEC15B, GSEC11, GSEC12, GSEC18, and GSEC15A. | `GSEC*_standardized.csv`, `.parquet`, preview Excel files |
| `Panel Building/Panelbuilder (AGSEC).ipynb` | Standardizes agriculture sections across waves, including crop, plot, parcel, input, labor, and extension-service modules. | `AGSEC*_standardized.csv`, `.parquet`, preview Excel files |
| `Panel Building/Panelbuilder (CSEC).ipynb` | Standardizes community sections across waves. Includes special handling for community identifiers and NGO/community modules. | `CSEC*_standardized.csv`, `.parquet`, preview Excel files |

### 3. Merge standardized survey sections

After the standardized files exist, use these notebooks to build wider panels.

| File | What it does | Main output |
| --- | --- | --- |
| `Panel Building/Merging Sections.ipynb` | Merges standardized household sections into a household-wave panel. It reshapes repeated sections wide, handles duplicate checks, recodes binary variables, and creates an AGSEC10 wide file. | `hh_panel_roster_9_10_11_12_13_17_18.xlsx`, `.parquet`, `AGSEC10_wide.csv` |
| `Panel Building/AG HH CROP LEVEL.ipynb` | Builds household-crop-level and household-visit-level agricultural panels from standardized agriculture files. It harmonizes crop codes, converts visit numbers to seasons/years, handles coffee variants, creates crop-level wide variables, and aggregates AGSEC3 inputs. | `AG_crop_panel_long_fixed.*`, `AG_crop_panel_wide_hh_id_obs.*`, `AG3_inputs_aggregated.xlsx` |
| `Panel Building/hh id obs.ipynb` | Matches household observation IDs between two sheets and separates matched from unmatched records. | `hh_id_obs_merge_matched_only.xlsx`, `hh_id_obs_merge_unmatched.xlsx` |

### 4. Build spatial and environmental covariates

These scripts create the spatial inputs that are later merged into the village
and site panels.

| File | What it does | Main output |
| --- | --- | --- |
| `GEE/AWA_seasonal_rainfall` | Earth Engine script that calculates area-weighted mean seasonal CHIRPS rainfall for buffered points over 2000-2010. Edit the asset, ID field, buffer size, and export folder before running. | Seasonal rainfall CSV export |
| `GEE/Rainfall_anomaly` | Earth Engine script that builds a seasonal rainfall panel and rainfall anomalies for candidate locations over 2009-2020. | `candidates_seasonal_rainfall_anomaly_2009_2020` CSV export |
| `GEE/Seasonal_temp_CHIRTS` | Earth Engine script that calculates seasonal mean CHIRTS temperature in buffers for CSB locations over 2000-2010. | `CSB_20KM_seasonal_mean_temperature_CHIRTS_wide_2000_2010` CSV export |
| `GEE/adjusted_crop_suitability_index` | Earth Engine script that recodes GAEZ crop suitability classes into approximate suitability scores and averages them by CSB location. | `GAEZ_crop_suitability_meanSI_30km_Rainfed_lowinput_CSB` CSV export |
| `Various Code/Crop Suitability.ipynb` | Clips and stacks GAEZ crop suitability rasters, then writes a band-name list for Earth Engine upload/use. | `GAEZ_V5_IX30AS_stacked.tif`, band-name text file |
| `Various Code/Density reshape.ipynb` | Reshapes population-density files into a wide table by year. | `population_density_wide.csv`, `.xlsx` |
| `Various Code/Landcover_loop.ipynb` | Clips land-cover rasters and calculates zonal land-cover shares for CSB, candidate, household, and ring buffers. | Land-cover `.gpkg` and `.xlsx` outputs |
| `Various Code/SPAM_crop_loop.ipynb` | Calculates zonal statistics from SPAM crop rasters for CSB, candidate, household, and ring buffers across several years. | SPAM crop-stat CSV and `.gpkg` outputs |
| `Various Code/village matching.ipynb` | Fuzzy matches 11k village/admin records to UBOS records. | `11kadmins_matched.xlsx` |
| `Various Code/Prices.ipynb` | Converts long market-price data into a wide price table. | `market_prices_wide.xlsx` |

### 5. Build regression-ready village and site panels

These notebooks connect the survey panels to the spatial covariates.

| File | What it does | Main output |
| --- | --- | --- |
| `Panel Building/reg_ready_villages.ipynb` | Builds candidate-village and CSB panels by merging household panels, AGSEC10 extension-service variables, AGSEC3 input variables, rainfall, density, and ID crosswalks. | `Village_candidates_panel_v2.xlsx`, `CSB_panel_v2.xlsx` |
| `Panel Building/covariate_balance_panel.ipynb` | Builds a site-level balance panel for CSB and candidate sites. It merges treatment timing, rainfall, temperature, population density, distance to town, elevation, land cover, poverty, and baseline variables, then creates unweighted balance outputs. | `balance_panel_site_level_v2.*`, `balance_table_unweighted_v2.*` |

### 6. Stata post-processing

The files in `STATA/` are Stata scripts without `.do` extensions. They can be
renamed to `.do` or opened directly in Stata.

| File | What it does | Main output |
| --- | --- | --- |
| `STATA/Balancetable_PSW` | Builds unweighted and propensity-score-weighted balance tables. It estimates logit/probit propensity scores, checks common support, exports density plots, calculates ATT weights, and summarizes normalized differences. | Weighted/unweighted balance tables and propensity-score plot |
| `STATA/HH_consumption_wavewise` | Collapses seasonal household consumption to wave-level totals, checks coordinate consistency, and reshapes consumption/household size wide by wave for GIS use. | `totcons_USD_by_wave_XY.xlsx`, `wide_cons_w1_w7.xlsx` |
| `STATA/Standard_errors_consumption` | Calculates wave-specific averages and standard errors for consumption and household size. | `csb_cons_SE_fixed.xlsx` |

## Folder Guide

| Folder | Role |
| --- | --- |
| `Panel Building/` | Main production notebooks for standardized LSMS sections, household/agricultural panels, village panels, and covariate balance data. |
| `GEE/` | Google Earth Engine JavaScript scripts for rainfall, temperature, and crop-suitability covariates. |
| `Various Code/` | Supporting spatial, matching, density, price, and raster-processing notebooks. |
| `STATA/` | Stata scripts for final balance-table and consumption summaries. |
| `Trial and Error/` | Exploratory notebooks and helper code used to understand the raw LSMS files and develop the final panel-building approach. |

## Reproduction Notes

1. Clone the repository.
2. Place raw and intermediate data in a consistent local folder structure.
3. Update root paths in each notebook or script.
4. Run the inventory/exploration notebooks only if you need to rebuild the
   variable mapping from raw LSMS files.
5. Run the section builders before the merge notebooks.
6. Run the Earth Engine and spatial notebooks before building the final
   candidate/CSB village panels.
7. Run the Stata scripts after the balance-panel and consumption inputs have
   been created.

The most important dependency chain is:

```text
Panelbuilder notebooks
-> Merging Sections and AG HH CROP LEVEL
-> GEE/spatial covariate outputs
-> reg_ready_villages
-> covariate_balance_panel
-> STATA balance and summary scripts
```

## Current Limitations

- Several files use absolute local paths and will not run until those paths are
  edited.
- Some notebooks are exploratory and contain manual checks or one-off cells.
- `Various Code/Wave_variable_inventory.ipynb` is stored with a notebook
  extension but is plain Python text.
- Raw data and large intermediate data products are not included in the
  repository.
