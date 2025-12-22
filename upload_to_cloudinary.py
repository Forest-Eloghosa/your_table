#!/usr/bin/env python
"""
Direct upload script to push local media files to Cloudinary with correct public_ids.
"""
import os
import sys
import django

# Set up Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yourtable.settings')
django.setup()

import cloudinary
import cloudinary.uploader
from django.conf import settings
from menu.models import MenuItem

def upload_menu_images():
    """Upload menu images directly to Cloudinary with correct public_ids."""
    media_root = settings.MEDIA_ROOT
    menu_images_dir = os.path.join(media_root, 'menu_images')
    
    if not os.path.isdir(menu_images_dir):
        print(f"ERROR: {menu_images_dir} not found")
        return
    
    # Get list of MenuItem image names
    menu_items = MenuItem.objects.exclude(image='')
    item_images = {os.path.basename(item.image.name): item for item in menu_items}
    
    files = sorted([f for f in os.listdir(menu_images_dir) if f.lower().endswith('.jpg')])
    print(f"Found {len(files)} .jpg files in {menu_images_dir}")
    
    uploaded = 0
    errors = 0
    
    for fname in files:
        local_path = os.path.join(menu_images_dir, fname)
        # Public ID should be menu_images/filename (no extension needed for Cloudinary)
        public_id = f"menu_images/{os.path.splitext(fname)[0]}"
        
        try:
            result = cloudinary.uploader.upload(
                local_path,
                public_id=public_id,
                overwrite=True,
                resource_type="image"
            )
            print(f"✓ Uploaded {fname} -> {result['secure_url']}")
            
            # If this file is linked to a MenuItem, update the DB field
            if fname in item_images:
                item = item_images[fname]
                # Update the image field to store clean path
                item.image.name = f"menu_images/{fname}"
                item.save(update_fields=['image'])
                print(f"  → Updated MenuItem {item.pk} DB field")
            
            uploaded += 1
        except Exception as e:
            print(f"✗ ERROR uploading {fname}: {e}")
            errors += 1
    
    print(f"\nDone. Uploaded: {uploaded}, Errors: {errors}")

if __name__ == '__main__':
    upload_menu_images()
