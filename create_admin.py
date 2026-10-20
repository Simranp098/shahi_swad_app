import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()
username = 'admin'
email = 'Hotel.shahi.swad@gmail.com'
password = 'Admin@ShahiSwad2026'  # You can change this password later from Django admin

if not User.objects.filter(username=username).exists():
    print(f"Creating live superuser: {username}...")
    User.objects.create_superuser(username=username, email=email, password=password)
    print("✅ Live Superuser created successfully!")
else:
    print(f"User {username} already exists.")