import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

import cloudinary.uploader
from myapp.models import IDCard

fixed = 0
failed = 0

for card in IDCard.objects.all():
    if not card.image:
        continue
    
    # Skip if already on Cloudinary
    if 'cloudinary.com' in str(card.image):
        print(f"SKIP (already cloudinary): {card.name}")
        continue
    
    # Try to re-upload from local file
    local_path = card.image.path if hasattr(card.image, 'path') else None
    
    if local_path and os.path.exists(local_path):
        try:
            result = cloudinary.uploader.upload(local_path, folder='idcard_images')
            card.image = result['public_id']
            card.save()
            print(f"FIXED: {card.name}")
            fixed += 1
        except Exception as e:
            print(f"FAILED: {card.name} - {e}")
            failed += 1
    else:
        print(f"FILE MISSING on disk: {card.name} - {card.image}")
        failed += 1

print(f"\nDone! Fixed: {fixed}, Failed: {failed}")