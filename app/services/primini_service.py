import logging
from app.models.brand_dict import BRAND_DICT, Colors
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clean_price(price_str):
    """Convert price string to float by removing unwanted characters."""
    try:
        return float(price_str.replace('DT', '').replace(' ', '').strip())
    except ValueError:
        return None


def process_fournisseur(fournisseur_str):
    """Process fournisseur field into shop and ad_titles lists."""
    shop_list = []
    ad_titles_list = []
    count = 1  # ! TO REMOVE
    for entry in fournisseur_str.split(','):
        if count == 1:  # ! TO REMOVE
            parts = entry.split(':')
            count = 2  # ! TO REMOVE
            if len(parts) == 2:
                shop_list.append(parts[0].strip())
                ad_titles_list.append(parts[1].strip())
            else:
                logger.error(f"Invalid fournisseur entry: {entry}")
        else:  # ! TO REMOVE
            count = 1  # ! TO REMOVE
    return shop_list, ad_titles_list


def identify_brand(titre_article):
    """Identify brand from titre_article."""
    for word in titre_article.lower().split():
        if word in BRAND_DICT:
            return word
    return ""


def identify_color(titre_article):
    """Identify color from titre_article."""
    for color_fr, color_en in Colors.items():
        if color_fr in titre_article.lower() or color_en in titre_article.lower():
            return color_en
    return ""


def extract_modele(titre_article, couleur, marque):
    """Extract modele from titre_article by removing couleur, marque, and specific words."""
    words_to_remove = ['smartphone', 'téléphone']
    modele = titre_article.lower()

    # Remove couleur (both French and English terms)
    for color_fr, color_en in Colors.items():
        modele = modele.replace(color_fr, '').replace(color_en, '')

    # Remove marque
    modele = modele.replace(marque.lower(), '')

    # Remove words to remove
    for word in words_to_remove:
        modele = modele.replace(word, '')

    # Remove words that begin with a number and end with g, go, or gb
    modele = re.sub(r'\b\d+\s*(g|go|gb)\b', '', modele)

    # Remove extra spaces and capitalize
    modele = ' '.join(modele.split()).title()

    return modele


def get_primini_data(df, max_rows=None):
    result = []
    for _, row in df.iterrows():
        prix_detail_list = [clean_price(price) for price in row['prix_detail'].split(',')]
        if None in prix_detail_list:
            continue  # Skip rows with invalid price conversion

        min_price = clean_price(row['price'])
        if min_price is None:
            continue  # Skip rows with invalid min_price conversion

        max_price = max(prix_detail_list)

        shop_list, ad_titles_list = process_fournisseur(row['fournisseur'])
        stocks_list = row['stocks'].split(',')

        brand_found = identify_brand(row['titre_article'])
        color_found = identify_color(row['titre_article'])

        modele = extract_modele(row['titre_article'], color_found, brand_found)

        product_data = {
            "titre_article": row['titre_article'],
            "ad_href": row['ad_href'],
            "ad_image": row['ad_image'],
            "description_article": row['description_article'],
            "prix_detail": prix_detail_list,
            "min_price": min_price,
            "max_price": max_price,
            "shop": shop_list,
            "ad_titles": ad_titles_list,
            "stocks": stocks_list,
            "marque": brand_found,
            "couleur": color_found,
            "modele": modele
        }

        result.append(product_data)
        if max_rows and len(result) >= max_rows:
            return result
    return result


def get_specific_range_primini_data(start, lists):
    # Calculate the actual range based on the total available data
    actual_start = max(0, start * 180)
    actual_end = min(len(lists), start * 180 + 180)
    max_rows = actual_end - actual_start
    return get_primini_data(lists[actual_start:], max_rows=max_rows)
