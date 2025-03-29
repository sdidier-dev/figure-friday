import os
import pandas as pd

# Define the path to the dataset
assets_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '.', 'assets'))
if os.getenv('DASH_URL_BASE_PATHNAME', 'prod') == 'dev':
    dataset = f'{assets_dir}/banknotesData.csv'
else:
    plotly_dataset_repo = 'https://raw.githubusercontent.com/plotly/Figure-Friday/main/2025'
    dataset = plotly_dataset_repo + '/week-12/banknotesData.csv'

# Load the dataset
df = pd.read_csv(dataset)

# We'll add more data processing as we explore the dataset
# For now, just ensure the dataset is loaded properly
print(f"Dataset loaded with {len(df)} rows and {len(df.columns)} columns")