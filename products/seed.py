from decimal import Decimal
from products.models import Product

def run():
    data = [
        ("Calming Lavender Spray","Natural calming spray for pets.","9.99"),
        ("Dental Chew Sticks","Daily chew sticks for dental support.","6.50"),
        ("Joint Support Treats","Glucosamine-based treats for joints.","12.99"),
        ("Hypoallergenic Shampoo","Gentle shampoo for sensitive skin.","8.49"),
        ("Mindful Pet Journal (PDF)","Downloadable journal for pet routines.","4.99"),
        ("Organic Paw Balm","Protective balm for paws and nose.","7.25"),
        ("Digestive Support Powder","Probiotic powder for digestion.","10.75"),
        ("Eco Toy Rope","Durable eco-friendly rope toy.","5.99"),
        ("Herbal Ear Cleaner","Mild herbal ear cleaning solution.","9.50"),
        ("Herbal Chill Drops","Herbal drops for relaxation.","11.49"),
    ]

    created = 0
    for name, desc, price in data:
        _, was_created = Product.objects.get_or_create(
            name=name,
            defaults={"description": desc, "price": Decimal(price)},
        )
        if was_created:
            created += 1

    print(f"Seed complete. Created {created} products. Total: {Product.objects.count()}")
