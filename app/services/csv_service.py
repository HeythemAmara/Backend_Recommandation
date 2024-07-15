import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_scrapping_csv_data():
    csv_dir = os.path.join(os.getcwd(), "data/scrapping")
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    all_data = []

    for file in csv_files:
        file_path = os.path.join(csv_dir, file)
        #logger.info(f"Reading file: {file_path}")
        df = pd.read_csv(file_path)

        # Rename columns
        df.columns = [col.split('.')[-1] for col in df.columns]

        # Replace NaN values with None
        df = df.where(pd.notnull(df), '')

        # Filter out rows where ad_stocks is 'retired'
        df = df[df['ad_stocks'] != 'retired']

        #logger.info(f"File {file_path} read successfully with {len(df)} records.")
        all_data.extend(df.to_dict('records'))

    if not all_data:
        logger.info("No data to process")
        return []

    # Convert list of dicts to DataFrame for further processing
    df_all = pd.DataFrame(all_data)
    #logger.info("DataFrame created")

    df_all = df_all.sort_values(by='date_scrapy', ascending=False)

    df_aggregated_date = df_all.groupby([
        'reference_detail',
        'ad_title',
        'ad_url',
        'shop',
        'modele',
        'marque',
        'ram',
        'stockage',
        'couleur',
        'options'
    ]).agg({
        'reference_global': 'first',
        'ad_price': 'first',
        'ad_stocks': 'first',
        'date_scrapy': 'max'
    }).reset_index()
    return df_aggregated_date


def read_primini_csv_data():
    csv_dir = os.path.join(os.getcwd(), "data/scrapping_Primini")
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    all_data = []

    for file in csv_files:
        file_path = os.path.join(csv_dir, file)
        df = pd.read_csv(file_path)
        df = df.where(pd.notnull(df), '')
        all_data.extend(df.to_dict('records'))

    if not all_data:
        logger.info("No data to process")
        return []

    # Convert list of dicts to DataFrame for further processing
    df_all = pd.DataFrame(all_data)
    return df_all

