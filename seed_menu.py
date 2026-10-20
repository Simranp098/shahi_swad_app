import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from orders.models import Category, MenuItem

def seed_database():
    print("🧹 Cleaning old menu data...")
    MenuItem.objects.all().delete()
    Category.objects.all().delete()

    menu_structure = [
        {
            "category": "Veg Main Course",
            "order": 1,
            "items": [
                {"name": "Mix Veg", "food_type": "VEG", "price": 180},
                {"name": "Veg Kadhai", "food_type": "VEG", "price": 200},
                {"name": "Veg Tawa", "food_type": "VEG", "price": 220},
                {"name": "Veg Kolhapuri", "food_type": "VEG", "price": 160},
                {"name": "Veg Chatpata", "food_type": "VEG", "price": 220},
                {"name": "Veg Bhurji", "food_type": "VEG", "price": 200},
                {"name": "Veg Maratha", "food_type": "VEG", "price": 180},
                {"name": "Veg Patiyala", "food_type": "VEG", "price": 280},
                {"name": "Sai Bhaji", "food_type": "VEG", "price": 140},
                {"name": "Surya Masala", "food_type": "VEG", "price": 160},
                {"name": "Methi Masala", "food_type": "VEG", "price": 160},
                {"name": "Bhindi Masala", "food_type": "VEG", "price": 150},
                {"name": "Paneer Masala", "food_type": "VEG", "price": 200},
                {"name": "Paneer Tikka Masala", "food_type": "VEG", "price": 240},
                {"name": "Paneer Butter Masala", "food_type": "VEG", "price": 260},
                {"name": "Palak Paneer", "food_type": "VEG", "price": 180},
                {"name": "Paneer Bhurji", "food_type": "VEG", "price": 160},
                {"name": "Paneer Kolhapuri", "food_type": "VEG", "price": 220},
                {"name": "Paneer Angara", "food_type": "VEG", "price": 300},
                {"name": "Kaju Masala", "food_type": "VEG", "price": 280},
                {"name": "Kaju Curry", "food_type": "VEG", "price": 260},
                {"name": "Kaju Paneer Masala", "food_type": "VEG", "price": 320},
                {"name": "Mushroom Masala", "food_type": "VEG", "price": 220},
                {"name": "Paneer Mushroom Masala", "food_type": "VEG", "price": 270},
                {"name": "Baingan Masala", "food_type": "VEG", "price": 160},
                {"name": "Shahi Paneer", "food_type": "VEG", "price": 240},
                {"name": "Matar Paneer", "food_type": "VEG", "price": 190},
                {"name": "Aloo Matar", "food_type": "VEG", "price": 160},
                {"name": "Aloo Gobhi", "food_type": "VEG", "price": 140},
                {"name": "Dal Fry", "food_type": "VEG", "price": 130},
                {"name": "Dal Tadka", "food_type": "VEG", "price": 150},
                {"name": "Dal Butter Fry", "food_type": "VEG", "price": 180},
                {"name": "Jeera Dal", "food_type": "VEG", "price": 120},
                {"name": "Lasuni Methi", "food_type": "VEG", "price": 140},
            ]
        },
        {
            "category": "Mutton Main Course",
            "order": 2,
            "items": [
                {"name": "Mutton Shahi Special", "food_type": "NON_VEG", "price": 330, "plate_price": 330, "half_price": 580, "full_price": 1120},
                {"name": "Mutton Handi (Red/Black)", "food_type": "NON_VEG", "price": 580, "half_price": 580, "full_price": 1050},
                {"name": "Mutton Kadhai", "food_type": "NON_VEG", "price": 340},
                {"name": "Mutton Tawa", "food_type": "NON_VEG", "price": 600},
                {"name": "Mutton Chatpata", "food_type": "NON_VEG", "price": 320, "plate_price": 320, "half_price": 600, "full_price": 1100},
                {"name": "Mutton Kolhapuri", "food_type": "NON_VEG", "price": 300, "plate_price": 300, "half_price": 560, "full_price": 1080},
                {"name": "Mutton Maharaja", "food_type": "NON_VEG", "price": 280, "plate_price": 280, "half_price": 550, "full_price": 1050},
                {"name": "Mutton Lahsuni", "food_type": "NON_VEG", "price": 280, "plate_price": 280, "half_price": 550, "full_price": 1050},
                {"name": "Mutton Angara", "food_type": "NON_VEG", "price": 600, "half_price": 600, "full_price": 1100},
                {"name": "Mutton Masala", "food_type": "NON_VEG", "price": 300},
                {"name": "Mutton Rogan Josh", "food_type": "NON_VEG", "price": 260, "plate_price": 260, "half_price": 520, "full_price": 1000},
                {"name": "Mutton Hyderabadi", "food_type": "NON_VEG", "price": 300, "plate_price": 300, "half_price": 580, "full_price": 1080},
                {"name": "Mutton Changezi", "food_type": "NON_VEG", "price": 320, "plate_price": 320, "half_price": 600, "full_price": 1150},
                {"name": "Mutton Bhuna", "food_type": "NON_VEG", "price": 380},
                {"name": "Mutton Tadka", "food_type": "NON_VEG", "price": 540},
                {"name": "Mutton Lapeta", "food_type": "NON_VEG", "price": 560, "half_price": 560, "full_price": 1060},
                {"name": "Mutton Do Pyaza", "food_type": "NON_VEG", "price": 360},
                {"name": "Mutton Malwani Handi", "food_type": "NON_VEG", "price": 600, "half_price": 600, "full_price": 1050},
                {"name": "Mutton Dum Matka", "food_type": "NON_VEG", "price": 650},
            ]
        },
        {
            "category": "Chicken Main Course",
            "order": 3,
            "items": [
                {"name": "Chicken Shahi Special", "food_type": "NON_VEG", "price": 310, "plate_price": 310, "half_price": 480, "full_price": 850},
                {"name": "Butter Chicken", "food_type": "NON_VEG", "price": 260},
                {"name": "Murg Musallam", "food_type": "NON_VEG", "price": 450, "half_price": 450, "full_price": 800},
                {"name": "Chicken Chatpata", "food_type": "NON_VEG", "price": 250, "plate_price": 250, "half_price": 460, "full_price": 750},
                {"name": "Chicken Maharaja", "food_type": "NON_VEG", "price": 260, "plate_price": 260, "half_price": 440, "full_price": 730},
                {"name": "Chicken Lahsuni", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Changezi", "food_type": "NON_VEG", "price": 280, "plate_price": 280, "half_price": 480, "full_price": 780},
                {"name": "Chicken Kolhapuri", "food_type": "NON_VEG", "price": 250},
                {"name": "Chicken Lapeta", "food_type": "NON_VEG", "price": 450, "half_price": 450, "full_price": 800},
                {"name": "Chicken Angara", "food_type": "NON_VEG", "price": 430, "half_price": 430, "full_price": 820},
                {"name": "Chicken Masala", "food_type": "NON_VEG", "price": 220, "plate_price": 220, "half_price": 400, "full_price": 730},
                {"name": "Chicken Do Pyaza", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Dahiwala", "food_type": "NON_VEG", "price": 240},
                {"name": "Chicken Rogan Josh", "food_type": "NON_VEG", "price": 200, "plate_price": 200, "half_price": 380, "full_price": 650},
                {"name": "Chicken Malwani Handi", "food_type": "NON_VEG", "price": 450, "half_price": 450, "full_price": 800},
                {"name": "Chicken Kadhai", "food_type": "NON_VEG", "price": 250},
                {"name": "Chicken Tawa", "food_type": "NON_VEG", "price": 480},
                {"name": "Chicken Hyderabadi", "food_type": "NON_VEG", "price": 290, "plate_price": 290, "half_price": 400, "full_price": 700},
                {"name": "Chicken Dum Matka", "food_type": "NON_VEG", "price": 450},
                {"name": "Chicken Handi (Red/Black)", "food_type": "NON_VEG", "price": 380, "half_price": 380, "full_price": 680},
                {"name": "Chicken Tikka Masala", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Reshmi Kebab Masala", "food_type": "NON_VEG", "price": 260},
            ]
        },
        {
            "category": "Fish & Prawns",
            "order": 4,
            "items": [
                {"name": "Fish Koliwada", "food_type": "NON_VEG", "price": 350},
                {"name": "Fish Chilli", "food_type": "NON_VEG", "price": 300},
                {"name": "Fish Fry", "food_type": "NON_VEG", "price": 300},
                {"name": "Fish Finger", "food_type": "NON_VEG", "price": 320},
                {"name": "Prawns Chilli", "food_type": "NON_VEG", "price": 460},
                {"name": "Prawns Schezwan Fry", "food_type": "NON_VEG", "price": 480},
                {"name": "Prawns Butter & Garlic", "food_type": "NON_VEG", "price": 450},
                {"name": "Prawns Fry", "food_type": "NON_VEG", "price": 480},
                {"name": "Prawns Koliwada", "food_type": "NON_VEG", "price": 480},
                {"name": "Fish Masala", "food_type": "NON_VEG", "price": 380},
                {"name": "Fish Tawa Masala", "food_type": "NON_VEG", "price": 450},
                {"name": "Fish Curry", "food_type": "NON_VEG", "price": 420},
                {"name": "Fish Angara", "food_type": "NON_VEG", "price": 480},
                {"name": "Prawns Masala", "food_type": "NON_VEG", "price": 450},
                {"name": "Prawns Tawa Masala", "food_type": "NON_VEG", "price": 480},
                {"name": "Prawns Butter Masala", "food_type": "NON_VEG", "price": 440},
            ]
        },
        {
            "category": "Egg Specialties",
            "order": 5,
            "items": [
                {"name": "Egg Masala", "food_type": "EGG", "price": 180},
                {"name": "Egg Curry", "food_type": "EGG", "price": 160},
                {"name": "Egg Tad Fod Masala", "food_type": "EGG", "price": 220},
                {"name": "Egg Bhurji", "food_type": "EGG", "price": 100},
                {"name": "Egg Omelette", "food_type": "EGG", "price": 80},
                {"name": "Egg Fry", "food_type": "EGG", "price": 80},
                {"name": "Boiled Egg", "food_type": "EGG", "price": 60},
            ]
        },
        {
            "category": "Biryani & Rice",
            "order": 6,
            "items": [
                {"name": "Chicken Biryani", "food_type": "NON_VEG", "price": 150, "half_price": 150, "full_price": 260},
                {"name": "Chicken Pulao", "food_type": "NON_VEG", "price": 260},
                {"name": "Egg Biryani", "food_type": "EGG", "price": 200},
                {"name": "Veg Biryani", "food_type": "VEG", "price": 170},
                {"name": "Veg Pulao", "food_type": "VEG", "price": 210},
                {"name": "Dal Khichdi", "food_type": "VEG", "price": 150},
                {"name": "Jeera Rice", "food_type": "VEG", "price": 90, "half_price": 90, "full_price": 140},
                {"name": "Steam Rice", "food_type": "VEG", "price": 120},
                {"name": "Paneer Pulao", "food_type": "VEG", "price": 260},
            ]
        },
        {
            "category": "Tandoor & Starters",
            "order": 7,
            "items": [
                {"name": "Chicken Shahi Tikka", "food_type": "NON_VEG", "price": 320},
                {"name": "Chicken Tandoori", "food_type": "NON_VEG", "price": 250, "half_price": 250, "full_price": 450},
                {"name": "Chicken Lemon Tandoori", "food_type": "NON_VEG", "price": 260, "half_price": 260, "full_price": 480},
                {"name": "Tangdi Kebab", "food_type": "NON_VEG", "price": 150, "half_price": 150, "full_price": 280},
                {"name": "Chicken Leg Bharza", "food_type": "NON_VEG", "price": 130, "half_price": 130, "full_price": 250},
                {"name": "Chicken Malai Kebab", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Banjara Kebab", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Matka Kebab", "food_type": "NON_VEG", "price": 320},
                {"name": "Chicken Pahadi Kebab", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Reshmi Kebab", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Seekh Kebab", "food_type": "NON_VEG", "price": 250},
                {"name": "Mini Platter", "food_type": "NON_VEG", "price": 600},
                {"name": "Special Platter", "food_type": "NON_VEG", "price": 800},
                {"name": "Mix Platter", "food_type": "NON_VEG", "price": 1400},
                {"name": "Fish Tikka", "food_type": "NON_VEG", "price": 300},
                {"name": "Prawns Tikka", "food_type": "NON_VEG", "price": 450},
                {"name": "Paneer Tikka Dry", "food_type": "VEG", "price": 260},
                {"name": "Paneer Pahadi", "food_type": "VEG", "price": 250},
                {"name": "Paneer Banjara", "food_type": "VEG", "price": 250},
                {"name": "Mushroom Tikka", "food_type": "VEG", "price": 240},
                {"name": "Veg Hara Bhara Kebab", "food_type": "VEG", "price": 300},
            ]
        },
        {
            "category": "Roti & Breads",
            "order": 8,
            "items": [
                {"name": "Tandoori Roti", "food_type": "VEG", "price": 10},
                {"name": "Butter Roti", "food_type": "VEG", "price": 15},
                {"name": "Wheat Roti", "food_type": "VEG", "price": 20},
                {"name": "Wheat Butter Roti", "food_type": "VEG", "price": 25},
                {"name": "Chapati", "food_type": "VEG", "price": 15},
                {"name": "Butter Chapati", "food_type": "VEG", "price": 20},
                {"name": "Bhakri (Jowar / Bajra)", "food_type": "VEG", "price": 40},
                {"name": "Butter Naan", "food_type": "VEG", "price": 40},
                {"name": "Garlic Naan", "food_type": "VEG", "price": 60},
                {"name": "Laccha Paratha", "food_type": "VEG", "price": 50},
                {"name": "Kulcha", "food_type": "VEG", "price": 60},
                {"name": "Cheese Garlic Naan", "food_type": "VEG", "price": 90},
                {"name": "Aloo Paratha", "food_type": "VEG", "price": 100},
            ]
        },
        {
            "category": "Chinese Starters & Rice",
            "order": 9,
            "items": [
                {"name": "Soyabean Kentucky", "food_type": "VEG", "price": 160, "half_price": 160, "full_price": 300},
                {"name": "Gobhi Kentucky", "food_type": "VEG", "price": 150, "half_price": 150, "full_price": 290},
                {"name": "Paneer Kentucky", "food_type": "VEG", "price": 180, "half_price": 180, "full_price": 320},
                {"name": "Paneer Chilli", "food_type": "VEG", "price": 240},
                {"name": "Paneer 65", "food_type": "VEG", "price": 260},
                {"name": "Paneer Manchurian", "food_type": "VEG", "price": 250},
                {"name": "Veg Manchurian", "food_type": "VEG", "price": 200},
                {"name": "Veg Crispy", "food_type": "VEG", "price": 220},
                {"name": "Soyabean Chilli", "food_type": "VEG", "price": 180},
                {"name": "Veg 65", "food_type": "VEG", "price": 200},
                {"name": "Mushroom Chilli", "food_type": "VEG", "price": 210},
                {"name": "Chicken Kentucky", "food_type": "NON_VEG", "price": 220, "half_price": 220, "full_price": 430},
                {"name": "Chicken KFC", "food_type": "NON_VEG", "price": 240, "half_price": 240, "full_price": 460},
                {"name": "Chicken Crispy", "food_type": "NON_VEG", "price": 250},
                {"name": "Chicken Chilli", "food_type": "NON_VEG", "price": 230},
                {"name": "Chicken Manchurian", "food_type": "NON_VEG", "price": 220},
                {"name": "Chicken Schezwan Dry", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Creamy Lasoon", "food_type": "NON_VEG", "price": 300},
                {"name": "Chicken Garlic", "food_type": "NON_VEG", "price": 240},
                {"name": "Chicken Sizzler", "food_type": "NON_VEG", "price": 480},
                {"name": "Chicken Chop Dry", "food_type": "NON_VEG", "price": 400},
                {"name": "Chicken 65", "food_type": "NON_VEG", "price": 260},
                {"name": "Mutton Chop Dry", "food_type": "NON_VEG", "price": 540},
                {"name": "Chicken Fried Rice", "food_type": "NON_VEG", "price": 240},
                {"name": "Chicken Schezwan Rice", "food_type": "NON_VEG", "price": 260},
                {"name": "Chicken Singapuri Fried Rice", "food_type": "NON_VEG", "price": 280},
                {"name": "Chicken Hong Kong Fried Rice", "food_type": "NON_VEG", "price": 300},
                {"name": "Chicken Triple Fried Rice", "food_type": "NON_VEG", "price": 340},
                {"name": "Chicken Khabsa Rice", "food_type": "NON_VEG", "price": 450, "half_price": 450, "full_price": 850},
                {"name": "Chicken Mandi Rice", "food_type": "NON_VEG", "price": 480, "half_price": 480, "full_price": 940},
                {"name": "Chicken Hakka Noodles", "food_type": "NON_VEG", "price": 220},
                {"name": "Chicken Schezwan Noodles", "food_type": "NON_VEG", "price": 260},
                {"name": "Chicken Singapuri Noodles", "food_type": "NON_VEG", "price": 280},
            ]
        },
        {
            "category": "Papad, Salad & Sweets",
            "order": 10,
            "items": [
                {"name": "Fry Papad", "food_type": "VEG", "price": 20},
                {"name": "Roasted Papad", "food_type": "VEG", "price": 20},
                {"name": "Masala Papad", "food_type": "VEG", "price": 35},
                {"name": "Green Salad", "food_type": "VEG", "price": 60},
                {"name": "Raita", "food_type": "VEG", "price": 50},
                {"name": "Boondi Raita", "food_type": "VEG", "price": 80},
                {"name": "Veg Raita", "food_type": "VEG", "price": 50},
                {"name": "Tomato Salad", "food_type": "VEG", "price": 30},
                {"name": "Chicken Manchow Soup", "food_type": "NON_VEG", "price": 100},
                {"name": "Chicken Hot & Sour Soup", "food_type": "NON_VEG", "price": 90},
                {"name": "Chicken Sweet Corn Soup", "food_type": "NON_VEG", "price": 140},
                {"name": "Chicken Clear Soup", "food_type": "NON_VEG", "price": 120},
                {"name": "Chicken Mukkad Soup", "food_type": "NON_VEG", "price": 120},
                {"name": "Mutton Mukkad Soup", "food_type": "NON_VEG", "price": 150},
                {"name": "Veg Manchow Soup", "food_type": "VEG", "price": 90},
                {"name": "Veg Hot & Sour Soup", "food_type": "VEG", "price": 80},
                {"name": "Veg Sweet Corn Soup", "food_type": "VEG", "price": 100},
                {"name": "Veg Clear Soup", "food_type": "VEG", "price": 100},
                {"name": "Veg Tomato Soup", "food_type": "VEG", "price": 80},
                {"name": "Gulab Jamun", "food_type": "VEG", "price": 50},
                {"name": "Matka Rabri", "food_type": "VEG", "price": 120},
                {"name": "Rabri with Fresh Ice Cream", "food_type": "VEG", "price": 100},
                {"name": "Mineral Water", "food_type": "VEG", "price": 20},
                {"name": "Cold Drinks", "food_type": "VEG", "price": 25},
            ]
        }
    ]

    total_created = 0
    for cat_data in menu_structure:
        category = Category.objects.create(
            name=cat_data["category"],
            display_order=cat_data["order"]
        )
        for item_data in cat_data["items"]:
            MenuItem.objects.create(
                category=category,
                name=item_data["name"],
                food_type=item_data.get("food_type", "VEG"),
                price=item_data["price"],
                plate_price=item_data.get("plate_price"),
                half_price=item_data.get("half_price"),
                full_price=item_data.get("full_price"),
                is_available=True
            )
            total_created += 1

    print(f"✅ Success! Created {len(menu_structure)} Categories & {total_created} Menu Items.")

if __name__ == '__main__':
    seed_database()