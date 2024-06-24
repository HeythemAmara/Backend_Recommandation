import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def api_filters(df):
    if df.empty:
        logger.info("No aggregated data available for API preparation.")
        return {}

    # Initialize variables to store the maximum and minimum ad price
    max_ad_price = df['ad_price'].max()
    min_ad_price = df['ad_price'].min()

    # Extract unique lists for RAM, stockage, couleur, shop, and marque
    unique_ram_go = df[(df['ram'] != '') & (~df['ram'].isna())]['ram'].unique().tolist()
    unique_ram_go = [x for x in unique_ram_go if x.endswith('go')]

    # Sort RAM by extracting the numeric part and converting it to int
    unique_ram_go.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))

    unique_stockage_gb = df[(df['stockage'] != '') & (~df['stockage'].isna())]['stockage'].unique().tolist()
    unique_stockage_gb = [x for x in unique_stockage_gb if x.endswith('gb')]

    unique_stockage_gb.sort(key=lambda x: int(''.join(filter(str.isdigit, x))))

    unique_couleur = df[df['couleur'] != ''].dropna()['couleur'].unique().tolist()
    unique_couleur.sort()  # Sort colors alphabetically

    unique_stocks = df[df['ad_stocks'] != ''].dropna()['ad_stocks'].unique().tolist()
    unique_stocks = [x for x in unique_stocks if x != 'RETIRED']
    unique_stocks.sort()  # Sort colors alphabetically

    unique_shops = df[df['shop'] != ''].dropna()['shop'].unique().tolist()
    unique_shops.sort()  # Sort shops alphabetically

    # Custom sort for marque based on your specification
    unique_marques = df[df['marque'] != ''].dropna()['marque'].unique().tolist()
    custom_order = ['Samsung', 'Apple', 'Huawei', 'Infinix', 'Oppo', 'Xiaomi']
    sorted_marques = []
    for marque in unique_marques:
        if marque in custom_order:
            sorted_marques.append(marque)
        else:
            sorted_marques.append(marque)

    # Prepare the data for the API response
    api_response = {
        "max_ad_price": max_ad_price,
        "min_ad_price": min_ad_price,
        "ram": unique_ram_go,
        "stockage": unique_stockage_gb,
        "ad_stocks": unique_stocks,
        "couleur": unique_couleur,
        "shop": unique_shops,
        "marque": sorted_marques
    }

    return api_response


def api_primini_filters(product_data):
    # Extract the unique filters from the product data
    unique_stocks = set()
    unique_couleur = set()
    unique_shops = set()
    sorted_marques = set()

    for product in product_data:
        # Skip empty values
        if product['stocks']:
            unique_stocks.update(filter(None, product['stocks']))
        if product['couleur']:
            unique_couleur.add(product['couleur'])
        if product['shop']:
            unique_shops.update(filter(None, product['shop']))
        if product['marque']:
            sorted_marques.add(product['marque'])

    sorted_marques = sorted(sorted_marques)

    # Determine the minimum and maximum prices
    max_ad_price = max(product['max_price'] for product in product_data)
    min_ad_price = min(product['min_price'] for product in product_data)

    # Prepare the data for the API response
    result = {
        "max_ad_price": max_ad_price,
        "min_ad_price": min_ad_price,
        "ram": [],
        "stockage": [],
        "ad_stocks": list(unique_stocks),
        "couleur": list(unique_couleur),
        "shop": list(unique_shops),
        "marque": sorted_marques
    }

    return result


def api_filters_update(df, filters):
    if df.empty:
        logger.info("No data available for filtering.")
        return []

    filtered_df = df.copy()

    # Apply price range filter
    min_price, max_price = filters['priceRange']
    filtered_df = filtered_df[(filtered_df['ad_price'] >= min_price) & (filtered_df['ad_price'] <= max_price)]

    # Apply status filter
    if filters['status']:
        filtered_df = filtered_df[filtered_df['ad_stocks'].isin(filters['status'])]

    # Apply offer filter
    if filters['offer']:
        filtered_df = filtered_df[filtered_df['offer'].isin(filters['offer'])]

    # Apply RAM filter
    if filters['ram']:
        filtered_df = filtered_df[filtered_df['ram'].isin(filters['ram'])]

    # Apply stockage filter
    if filters['stockage']:
        filtered_df = filtered_df[filtered_df['stockage'].isin(filters['stockage'])]

    # Apply shop filter
    if filters['shop']:
        filtered_df = filtered_df[filtered_df['shop'].isin(filters['shop'])]

    # Apply marque filter
    if filters['marque']:
        filtered_df = filtered_df[filtered_df['marque'].isin(filters['marque'])]

    # Apply color filter
    if filters['color']:
        filtered_df = filtered_df[filtered_df['couleur'].isin(filters['color'])]

    return filtered_df


def filter_by_price(item, price_range):
    return price_range[0] <= item['min_price'] <= price_range[1]


def filter_by_status(item, status_filter):
    return not status_filter or any(stock in item['stocks'] for stock in status_filter)


def filter_by_shop(item, shop_filter):
    return not shop_filter or any(shop in item['shop'] for shop in shop_filter)


def filter_by_marque(item, marque_filter):
    return not marque_filter or item['marque'] in marque_filter


def filter_by_color(item, color_filter):
    return not color_filter or item['couleur'] in color_filter


def api_filters_primini_update(rawdata, filters):
    price_range = filters.get("priceRange", [0, float("inf")])
    status_filter = filters.get("status", [])
    shop_filter = filters.get("shop", [])
    marque_filter = filters.get("marque", [])
    color_filter = filters.get("color", [])

    filtered_data = []

    for item in rawdata:
        if not filter_by_price(item, price_range):
            continue
        if not filter_by_status(item, status_filter):
            continue
        if not filter_by_shop(item, shop_filter):
            continue
        if not filter_by_marque(item, marque_filter):
            continue
        if not filter_by_color(item, color_filter):
            continue

        filtered_data.append(item)
        if len(filtered_data) >= 180:
            return filtered_data

    return filtered_data
