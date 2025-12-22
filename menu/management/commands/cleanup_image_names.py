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
            
            # If it starts with 'https:/' or 'http:/', extract the storage key
            # Example: 'https:/res.cloudinary.com/dz2h47mhg/image/upload/menu_images/foo_xyz' 
            #          -> 'menu_images/foo_xyz'
            if 'https:/' in new_name or 'http:/' in new_name:
                match = re.search(r'(menu_images/[^/\s]+)', new_name)
                if match:
                    new_name = match.group(1)
            
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
