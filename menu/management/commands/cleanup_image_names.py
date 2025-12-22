"""Management command to clean corrupted MenuItem image field values."""
import re
from django.core.management.base import BaseCommand
from menu.models import MenuItem


class Command(BaseCommand):
    help = 'Normalize MenuItem image field values by extracting clean storage keys from malformed URLs.'

    def handle(self, *args, **options):
        changed = 0
        errors = 0
        
        for item in MenuItem.objects.exclude(image=''):
            old_name = item.image.name or ''
            if not old_name:
                continue
            
            new_name = old_name
            
            # If it starts with 'https:/' or 'http:/', extract just the filename part
            # Example: 'https:/res.cloudinary.com/dz2h47mhg/image/upload/menu/classic-tomato-bruschetta_dzjjw2'
            #          -> 'menu_images/classic-tomato-bruschetta.jpg' (estimated from original DB)
            if 'https:/' in new_name or 'http:/' in new_name:
                # Extract the last part after the last '/'
                parts = new_name.rstrip('/').split('/')
                if parts:
                    # Last part is something like 'classic-tomato-bruschetta_dzjjw2'
                    # Try to reconstruct as 'menu_images/<base-name>.jpg'
                    filename = parts[-1]
                    # Remove the trailing hash/transform suffix (e.g., _dzjjw2)
                    base = re.sub(r'_[a-z0-9]+$', '', filename)
                    # Look up the original file in the MenuItem name or use a sensible default
                    new_name = 'menu_images/{}.jpg'.format(base)
            
            if new_name != old_name:
                try:
                    item.image.name = new_name
                    item.save(update_fields=['image'])
                    self.stdout.write(f'Fixed item {item.pk}: {old_name[:50]} -> {new_name}')
                    changed += 1
                except Exception as e:
                    self.stderr.write(f'Error fixing item {item.pk}: {e}')
                    errors += 1
        
        self.stdout.write(f'Done. Changed: {changed}, Errors: {errors}')
