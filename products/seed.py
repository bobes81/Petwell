from decimal import Decimal
from products.models import Category, Product

def run():
    categories = [
        ("supplements", "Supplements"),
        ("toys", "Toys"),
        ("care", "Care"),
        ("wellness", "Wellness"),
    ]

    cat_objs = {}
    for name, friendly in categories:
        obj, _ = Category.objects.get_or_create(name=name, defaults={"friendly_name": friendly})
        cat_objs[name] = obj

    items = [
        ("Calming Herbal Drops", "supplements", "Gentle calming drops for pets.", "9.99"),
        ("Omega-3 Pet Oil", "supplements", "Supports coat and joint health.", "12.99"),
        ("Natural Paw Balm", "care", "Soothing balm for dry paws.", "7.50"),
        ("Eco Grooming Brush", "care", "Soft brush for sensitive coats.", "8.99"),
        ("Mindful Chew Toy", "toys", "Durable chew toy for enrichment.", "6.49"),
        ("Puzzle Feeder Bowl", "toys", "Slow feeding and mental stimulation.", "14.99"),
        ("Lavender Pet Spray", "wellness", "Fresh calming scent for bedding.", "5.99"),
        ("Gentle Shampoo", "care", "Mild wash for sensitive skin.", "10.49"),
    ]

    created = 0
    for name, cat, desc, price in items:
        obj, was_created = Product.objects.get_or_create(
            name=name,
            defaults={
                "category": cat_objs[cat],
                "description": desc,
                "price": Decimal(price),
                "sku": name.upper().replace(" ", "-")[:32],
            },
        )
        if was_created:
            created += 1

    print(f"Seed complete. Created {created} products.")
