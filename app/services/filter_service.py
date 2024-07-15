import logging
from collections import Counter

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
    stock_counter = Counter()
    couleur_counter = Counter()
    shop_counter = Counter()
    marque_counter = Counter()

    # Extract the unique filters and count occurrences
    for product in product_data:
        if product['stocks']:
            stock_counter.update(filter(None, product['stocks']))
        if product['couleur']:
            couleur_counter[product['couleur']] += 1
        if product['shop']:
            shop_counter.update(filter(None, product['shop']))
        if product['marque']:
            marque_counter[product['marque']] += 1

    # Determine the minimum and maximum prices
    max_ad_price = max(product['max_price'] for product in product_data)
    min_ad_price = min(product['min_price'] for product in product_data)

    # Convert counters to the required format
    def counter_to_list(counter):
        return sorted([{"name": name, "count": count} for name, count in counter.items()], key=lambda x: x["name"])

    result = {
        "max_price": max_ad_price,
        "min_price": min_ad_price,
        "stocks": counter_to_list(stock_counter),
        "couleur": counter_to_list(couleur_counter),
        "shop": counter_to_list(shop_counter),
        "marque": counter_to_list(marque_counter)
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
    status_filter = filters.get("stocks", [])
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


def is_within_price_range(product, price_min, price_max):
    return (price_min <= product['min_price'] <= price_max or
            price_min <= product['max_price'] <= price_max)


def has_required_stock(product, stock_filter):
    return not stock_filter or any(stock in stock_filter for stock in product['stocks'])


def has_required_shop(product, shop_filter):
    return not shop_filter or any(shop in shop_filter for shop in product['shop'])


def has_required_marque(product, marque_filter):
    return not marque_filter or product['marque'] in marque_filter


def has_required_color(product, color_filter):
    return not color_filter or product['couleur'] in color_filter


def filter_products(product_data, givf):
    # Extract filters from givf
    price_min, price_max = givf.get("priceRange", [0, float("inf")])
    stock_filter = set(givf.get("stocks", []))
    shop_filter = set(givf.get("shop", []))
    marque_filter = set(givf.get("marque", []))
    color_filter = set(givf.get("color", []))

    # Filter product data based on givf
    filtered_products = []
    for product in product_data:
        if not is_within_price_range(product, price_min, price_max):
            continue
        if not has_required_stock(product, stock_filter):
            continue
        if not has_required_shop(product, shop_filter):
            continue
        if not has_required_marque(product, marque_filter):
            continue
        if not has_required_color(product, color_filter):
            continue
        filtered_products.append(product)

    return filtered_products


def convert_to_list(thelist):
    oldfnameslist = []
    for oldfnames in thelist:
        oldfnameslist.append(oldfnames["name"])
    return oldfnameslist


def update_counts_with_filters(product_data, givf, oldf, exif):
    # Filter products based on givf
    filtered_products = filter_products(product_data, givf)

    # Initialize counters
    couleur_counter = Counter()
    shop_counter = Counter()
    marque_counter = Counter()
    stock_counter = Counter()

    # Count occurrences in filtered data
    for product in filtered_products:
        if product['stocks']:
            stock_counter.update(filter(None, product['stocks']))
        if product['couleur']:
            couleur_counter[product['couleur']] += 1
        if product['shop']:
            shop_counter.update(filter(None, product['shop']))
        if product['marque']:
            marque_counter[product['marque']] += 1

    # Convert counters to the required format
    def counter_to_list(counter, exif_list):
        exif_names = {item["name"] for item in exif_list}
        result_list = [{"name": name, "count": counter.get(name, 0)} for name in exif_names]
        return result_list

    # Update exif with new counts
    if convert_to_list(oldf["stocks"]) != givf["stocks"]:
        print("stocks\t true")
        exif["stocks"] = counter_to_list(stock_counter, exif["stocks"])
    if convert_to_list(oldf["couleur"]) != givf["color"]:
        print("color\t true")
        exif["couleur"] = counter_to_list(couleur_counter, exif["couleur"])
    if convert_to_list(oldf["shop"]) != givf["shop"]:
        print("shop\t true")
        exif["shop"] = counter_to_list(shop_counter, exif["shop"])
    if convert_to_list(oldf["marque"]) != givf["marque"]:
        print("marque\t true")
        exif["marque"] = counter_to_list(marque_counter, exif["marque"])

    return exif
