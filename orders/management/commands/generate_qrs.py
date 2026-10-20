import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Generates print-ready QR codes for restaurant tables'

    def add_arguments(self, parser):
        parser.add_argument('--tables', type=int, default=10, help='Total number of tables')
        parser.add_argument('--domain', type=str, default='http://127.0.0.1:8000', help='Base URL for QR codes')

    def handle(self, *args, **options):
        total_tables = options['tables']
        base_url = options['domain']

        output_dir = os.path.join(settings.MEDIA_ROOT, 'qr_codes')
        os.makedirs(output_dir, exist_ok=True)

        self.stdout.write(f"Generating QR codes for {total_tables} tables...")

        for table_num in range(1, total_tables + 1):
            target_url = f"{base_url}/?table={table_num}"

            # Generate QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4,
            )
            qr.add_data(target_url)
            qr.make(fit=True)

            qr_img = qr.make_image(fill_color="#8B0000", back_color="white").convert('RGB')

            # Canvas setup for table card styling
            card_width, card_height = 400, 480
            card = Image.new('RGB', (card_width, card_height), 'white')
            draw = ImageDraw.Draw(card)

            # Resize QR code and paste into canvas
            qr_resized = qr_img.resize((300, 300))
            card.paste(qr_resized, (50, 80))

            # Draw Header & Table Label
            draw.text((200, 35), "SHAHI SWAD", fill="#8B0000", anchor="mm")
            draw.text((200, 410), f"TABLE {table_num}", fill="#111111", anchor="mm")
            draw.text((200, 440), "Scan QR to Order", fill="#666666", anchor="mm")

            # Save image
            file_path = os.path.join(output_dir, f"table_{table_num}.png")
            card.save(file_path)

        self.stdout.write(self.style.SUCCESS(f"Successfully generated {total_tables} QR codes in 'media/qr_codes/'!"))