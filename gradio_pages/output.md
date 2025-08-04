# Deep Seafloor Visual Coverage Estimate Dataset

## Overview

This dataset, associated with the study by Bell et al. titled "How Little We’ve Seen: A Visual Coverage Estimate of the Deep Seafloor," provides a compilation of deep seafloor observation locations. The dataset aims to quantify the extent of visual exploration in the deep ocean, offering insights into the current state of deep-sea exploration efforts. The data includes geographic coordinates, depth information, and details about the observation platforms used. This information can be valuable for researchers interested in marine biology, deep-sea ecology, oceanography, and conservation efforts.

## Dataset Description

The dataset is provided as a CSV file: `Bell et al SciAdv How Little We’ve Seen- A Visual Coverage Estimate of the Deep Seafloor- DSV dataset v2.csv`.
Each row in the CSV represents a single observation location. The columns provide details about the location, the observation platform, and other relevant metadata.

### Columns

*   **OBJECTID\_GIS:** A unique identifier for each observation point.
*   **Latitude:** Latitude of the observation location (in decimal degrees). **Note:** The current data has "Contact institution for location" listed. Contact the data providers for specific location details.
*   **Longitude:** Longitude of the observation location (in decimal degrees). **Note:** The current data has "Contact institution for location" listed. Contact the data providers for specific location details.
*   **Institution:** The institution responsible for the observation.
*   **Platform:** The name of the platform used for the observation (e.g., Deep BRUVs drop camera, Maka Nui).
*   **Type:** The type of observation platform (e.g., Lander).
*   **Country:** The country where the observation took place.
*   **Year:** The year the observation was made.
*   **Type\_Original:** The original description of the observation platform type.
*   **Platform\_Original:** The original description of the observation platform.
*   **Jurisdiction:** The jurisdictional zone (e.g., EEZ - Exclusive Economic Zone).
*   **Sovereign:** The sovereign nation with jurisdiction.
*   **DepthToUse:** The depth of the observation in meters (negative values indicate depth below sea level).
*   **DepthZone:** A categorical variable representing the depth range (e.g., Between 200-1000m, Between 1000-2000m).
*   **Decade:** The decade in which the observation was made.
*   **Geomorphology Description:** A description of the seafloor geomorphology at the observation location (e.g., Ridge).

## Data Usage

This dataset can be used to:

*   Map the spatial distribution of deep-sea observations.
*   Analyze the depth distribution of observations.
*   Assess the temporal trends in deep-sea exploration.
*   Identify areas of the deep seafloor that are under-explored.
*   Calculate the visual coverage estimate of the deep seafloor.

### Recommended Citation

When using this dataset, please cite the original research article:

Bell, J. B., et al. (Year). How Little We’ve Seen: A Visual Coverage Estimate of the Deep Seafloor. *Science Advances*, *Volume*, *Issue*, DOI. (Replace with actual publication details)

### Data Access

The dataset is available as a CSV file (`Bell et al SciAdv How Little We’ve Seen- A Visual Coverage Estimate of the Deep Seafloor- DSV dataset v2.csv`). It can be opened and analyzed using any software that supports CSV files, such as Microsoft Excel, Google Sheets, R, or Python.

### Example Analysis (Python)

The following Python code snippet demonstrates how to load and explore the dataset using the `pandas` library:

```python
import pandas as pd

# Load the dataset
data = pd.read_csv("Bell et al SciAdv How Little We’ve Seen- A Visual Coverage Estimate of the Deep Seafloor- DSV dataset v2.csv")

# Print the first 5 rows of the dataset
print(data.head())

# Get summary statistics for the 'DepthToUse' column
print(data['DepthToUse'].describe())

# Count the number of observations in each 'DepthZone'
print(data['DepthZone'].value_counts())
```

## Notes

*   The latitude and longitude data currently indicates "Contact institution for location". Researchers should contact the Bermuda Institute of Ocean Sciences for specific location details if needed.
*   Depth values are negative, representing depth below sea level.
*   The 'Geomorphology Description' provides a general overview of the seafloor terrain.

## Contact

For questions or inquiries related to this dataset, please contact the corresponding author of the original research article or the data providers at the Bermuda Institute of Ocean Sciences.
