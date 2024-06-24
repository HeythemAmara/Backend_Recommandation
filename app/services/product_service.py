import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_180_csv_data(df):

    result = []
    for _, row in df.iterrows():
        product_data = {
            "modele": row['modele'],
            "marque": row['marque'],
            "ram": row['ram'],
            "stockage": row['stockage'],
            "couleur": row['couleur'],
            "options": row['options'],
            "reference_global": row['reference_global'],
            "reference_detail": row['reference_detail'],
            "ad_title": row['ad_title'],
            "ad_url": [row['ad_url']],
            "shop": [row['shop']],
            "ad_stocks": [row['ad_stocks']],
            "max_price": row['ad_price'],
            "min_price": row['ad_price'],
            "date_scrapy": [row['date_scrapy']],
            "all_prices": [row['ad_price']]
        }

        # Check if the product already exists in the result list
        existing_product = next((p for p in result if p["modele"] == product_data["modele"]
                                 and p["marque"] == product_data["marque"]
                                 and p["ram"] == product_data["ram"]
                                 and p["stockage"] == product_data["stockage"]
                                 and p["couleur"] == product_data["couleur"]
                                 and p["options"] == product_data["options"]), None)

        if existing_product:
            existing_product["ad_url"].append(product_data["ad_url"][0])
            existing_product["shop"].append(product_data["shop"][0])
            existing_product["ad_stocks"].append(product_data["ad_stocks"][0])
            existing_product["date_scrapy"].append(product_data["date_scrapy"][0])
            existing_product["all_prices"].append(product_data["all_prices"][0])
            existing_product["max_price"] = max(existing_product["max_price"], product_data["max_price"])
            existing_product["min_price"] = min(existing_product["min_price"], product_data["min_price"])
        else:
            result.append(product_data)

        if len(result) == 180:
            return result

    return result
