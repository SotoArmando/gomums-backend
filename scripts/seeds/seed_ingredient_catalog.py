"""
Seed ingredient catalog from CSV files in the 'excel docs' folder.

Usage:
    python seed_ingredient_catalog.py

This reads the "Common Household Ingredients" section from each CSV file
and inserts them into the ingredient_catalog table.
"""
import csv
import re
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DATABASE_HOST", "localhost"),
    "port": int(os.getenv("DATABASE_PORT", 5432)),
    "database": os.getenv("DATABASE_NAME", "gomums"),
    "user": os.getenv("DATABASE_USER", "postgres"),
    "password": os.getenv("DATABASE_PASSWORD", ""),
}

# ── Category mapping ─────────────────────────────────────────────
# We auto-categorize ingredients based on keywords in their name.

CATEGORY_RULES = [
    # Proteins
    (r"beef|pork|chicken|turkey|bacon|sausage|hot dog|frankfurter|deli ham|longaniza|salami|ground meat",
     "proteins"),
    (r"fish|shrimp|camar|tilapia|catfish|salmon|tuna|sardina|atún|pescado",
     "seafood"),
    # Dairy
    (r"milk|leche|cheese|queso|butter|mantequilla|cream|crema|yogur|sour cream|cottage|evaporad|condensad",
     "dairy"),
    # Oils & Vinegars
    (r"oil|aceite|vinegar|vinagre",
     "oils & vinegars"),
    # Grains & Pasta
    (r"rice|arroz|flour|harina|oat|avena|pasta|spagueti|spaghetti|macaroni|codito|penne|cornmeal|bread|pan |tortilla|bun|cracker|galleta",
     "grains & pasta"),
    # Beans & Legumes
    (r"bean|habichuela|lentil|chickpea|garbanzo|guandul|pigeon pea",
     "beans & legumes"),
    # Vegetables
    (r"potato|papa|batata|sweet potato|yuca|cassava|ñame|yam|auyama|squash|tayota|chayote|carrot|zanahoria|celery|broccoli|cauliflower|cabbage|repollo|spinach|espinaca|kale|lettuce|lechuga|cucumber|pepino|zucchini|pepper|ají|pimiento|morón|cubanela|jalapeño|green bean|vainita|corn |maíz|mushroom|onion|ceboll|garlic|ajo|ginger|jengibre|tomato|tomate|eggplant|berenjena|beet|remolacha|okra|molondron|watercress|berro|romaine",
     "vegetables"),
    # Herbs & Spices
    (r"cilantro|culantro|parsley|perejil|basil|albahaca|dill|oregano|orégano|cumin|comino|paprika|chili powder|pepper.*ground|pimienta|cinnamon|canela|clove|clavo|nutmeg|nuez moscada|garlic powder|sazón|achiote|annatto|sofrito|seasoning|salt |sal ",
     "herbs & spices"),
    # Fruits
    (r"apple|manzana|banana|orange|naranja|lemon|limón|lime|grape|strawberr|blueberr|watermelon|peach|pear|cantaloupe|avocado|aguacate|papaya|lechosa|pineapple|piña|mango|guava|guayaba|passion fruit|chinola|coconut|coco|cherry|cereza|acerola",
     "fruits"),
    # Canned & Sauces
    (r"canned|enlatad|tomato sauce|salsa de tomate|tomato paste|pasta de tomate|diced tomato|ketchup|mustard|mostaza|mayonnaise|mayonesa|hot sauce|salsa picante|soy sauce|salsa de soya|worcestershire|ranch|bbq|broth|caldo|bouillon|cubito",
     "canned & sauces"),
    # Condiments & Sweeteners
    (r"sugar|azúcar|honey|miel|maple|peanut butter|olive|aceituna|caper|alcaparra|raisin|pasa|peanut|maní|coconut.*shredded|coco rallado|coconut milk|leche de coco|baking powder|baking soda|vinegar|chocolate|café|coffee|tea |té ",
     "pantry & baking"),
    # Beverages
    (r"juice|jugo|water|agua|wine|vino|beer|cerveza|soda|soft drink|cappuccino",
     "beverages"),
]


def categorize(name: str) -> str:
    """Determine the category of an ingredient by its name."""
    lower = name.lower()
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, lower):
            return category
    return "other"


def parse_price(price_str: str) -> float:
    """Parse a price string like '90.00 RD$' or '3.50 $' into a float."""
    if not price_str or not price_str.strip():
        return 0.0
    # Remove currency symbols, commas, and whitespace
    cleaned = re.sub(r"[A-Za-z$\s]", "", price_str.replace(",", ""))
    try:
        return float(cleaned)
    except ValueError:
        return 0.0


def extract_unit(name: str) -> str:
    """Extract the unit from the ingredient name, e.g., '(1 kg)' -> '1 kg'."""
    match = re.search(r"\(([^)]+)\)", name)
    if match:
        return match.group(1)
    return "unit"


def extract_clean_name(name: str) -> str:
    """Get the ingredient name without the unit portion."""
    # Remove the parenthetical unit
    clean = re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()
    return clean


def split_local_name(name: str, region: str) -> tuple:
    """
    Split 'Habichuelas Rojas / Red Beans' into (english_name, local_name).
    For Kansas (English region), no split needed.
    """
    if " / " in name:
        parts = name.split(" / ", 1)
        if region == "Dominican Republic":
            # Format: Local / English
            return parts[1].strip(), parts[0].strip()
        else:
            # Format: English / Local
            return parts[0].strip(), parts[1].strip()
    return name, None


def read_csv_ingredients(filepath: str) -> list:
    """
    Read a CSV file and extract rows from the 'Common Household Ingredients' section.
    Returns a list of dicts with name, unit, price, price_low, price_high.
    """
    ingredients = []
    in_section = False

    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0].strip():
                continue

            item = row[0].strip()

            # Detect section header
            if item == "Common Household Ingredients":
                in_section = True
                continue

            # If we hit another section header after our section, stop
            if in_section and len(row) >= 2 and not row[1].strip() and not row[2].strip() if len(row) > 2 else False:
                # This is a new section header (no prices)
                break

            if in_section:
                price_str = row[1].strip() if len(row) > 1 else ""
                low_str = row[2].strip() if len(row) > 2 else ""
                high_str = row[3].strip() if len(row) > 3 else ""

                if not price_str:
                    continue  # Skip empty rows or sub-headers

                ingredients.append({
                    "raw_name": item,
                    "price": parse_price(price_str),
                    "price_low": parse_price(low_str) if low_str else None,
                    "price_high": parse_price(high_str) if high_str else None,
                })

    return ingredients


# ── Region configs ────────────────────────────────────────────────

REGION_CONFIGS = {
    "Dominican Republic.csv": {
        "region": "Dominican Republic",
        "currency": "RD$",
        "language": "es",
    },
    "Kansas.csv": {
        "region": "Kansas",
        "currency": "USD",
        "language": "en",
    },
}


def seed_ingredient_catalog():
    """Read CSVs and insert ingredients into the database."""
    csv_dir = os.path.join(os.path.dirname(__file__), "..", "..", "excel docs")

    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    total_inserted = 0

    for filename, config in REGION_CONFIGS.items():
        filepath = os.path.join(csv_dir, filename)
        if not os.path.exists(filepath):
            print(f"⚠️  File not found: {filepath}")
            continue

        region = config["region"]
        currency = config["currency"]
        language = config["language"]

        print(f"\n📂 Processing {filename} ({region})...")

        raw_ingredients = read_csv_ingredients(filepath)
        if not raw_ingredients:
            print(f"  ⚠️  No 'Common Household Ingredients' section found in {filename}")
            continue

        print(f"  Found {len(raw_ingredients)} ingredients")

        for ing in raw_ingredients:
            raw_name = ing["raw_name"]
            unit = extract_unit(raw_name)
            clean_name = extract_clean_name(raw_name)
            english_name, local_name = split_local_name(clean_name, region)
            category = categorize(raw_name)

            try:
                cursor.execute("""
                    INSERT INTO ingredient_catalog (
                        id, name, name_local, category, unit,
                        price, price_low, price_high, currency, region, language, source
                    )
                    VALUES (gen_random_uuid(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (LOWER(name), LOWER(region)) DO UPDATE
                    SET price = EXCLUDED.price,
                        price_low = EXCLUDED.price_low,
                        price_high = EXCLUDED.price_high,
                        name_local = EXCLUDED.name_local,
                        category = EXCLUDED.category,
                        unit = EXCLUDED.unit,
                        currency = EXCLUDED.currency,
                        language = EXCLUDED.language,
                        source = EXCLUDED.source,
                        updated_at = NOW()
                """, (
                    english_name,
                    local_name,
                    category,
                    unit,
                    ing["price"],
                    ing["price_low"],
                    ing["price_high"],
                    currency,
                    region,
                    language,
                    "csv_import",
                ))
                total_inserted += 1
            except Exception as e:
                print(f"  ❌ Error inserting '{english_name}': {e}")
                conn.rollback()
                continue

        conn.commit()
        print(f"  ✅ {len(raw_ingredients)} ingredients loaded for {region}")

    cursor.close()
    conn.close()

    print(f"\n🎉 Done! Total ingredients processed: {total_inserted}")


if __name__ == "__main__":
    seed_ingredient_catalog()
