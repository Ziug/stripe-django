#!/usr/bin/env python
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stripe_project.settings')
django.setup()

from site_app.models import Item

# Create test items
items_data = [
    {'name': 'Laptop', 'description': 'High-performance laptop for work and gaming', 'price': 999.99},
    {'name': 'Wireless Mouse', 'description': 'Ergonomic wireless mouse with precision tracking', 'price': 29.99},
    {'name': 'Mechanical Keyboard', 'description': 'RGB mechanical keyboard with blue switches', 'price': 149.99},
    {'name': 'Monitor 27 inch', 'description': '4K Ultra HD monitor with HDR support', 'price': 399.99},
    {'name': 'USB-C Hub', 'description': 'Multi-port USB-C hub with HDMI and USB 3.0', 'price': 79.99},
    {'name': 'Webcam HD', 'description': '1080p HD webcam with auto-focus and noise reduction', 'price': 89.99},
    {'name': 'Headphones', 'description': 'Noise-cancelling wireless headphones', 'price': 199.99},
    {'name': 'Desk Lamp', 'description': 'LED desk lamp with adjustable brightness and color temperature', 'price': 45.99}
]

print("Creating test items...")

for item_data in items_data:
    item, created = Item.objects.get_or_create(name=item_data['name'], defaults=item_data)
    if created:
        print(f'Created: {item.name} - ${item.price}')
    else:
        print(f'Already exists: {item.name} - ${item.price}')

print(f'Total items in database: {Item.objects.count()}')

# Display all items
print("\nAll items in database:")
for item in Item.objects.all():
    print(f"- {item.name}: {item.description} (${item.price})")
