from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from django.db import transaction
from menu.models import MenuItem
import os
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Migrate local MEDIA files referenced by MenuItem.image into the active DEFAULT_FILE_STORAGE (e.g. Cloudinary).\n\nUsage: python manage.py migrate_media_to_storage [--dry-run] [--force]'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Show what would be done but do not upload')
        parser.add_argument('--force', action='store_true', help='Force re-upload even if URL looks remote')
        parser.add_argument('--yes', action='store_true', help='Assume yes for interactive prompts')
        parser.add_argument('--all-files', action='store_true', help='Upload all files under MEDIA_ROOT/menu_images regardless of DB links')
        parser.add_argument('--limit', type=int, help='Limit number of items to process (for testing)')

    def handle(self, *args, **options):
        dry_run = options.get('dry_run')
        force = options.get('force')
        limit = options.get('limit')

        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            self.stderr.write('ERROR: MEDIA_ROOT is not configured in settings. Aborting.')
            return

        qs = MenuItem.objects.all()
        total = qs.count()
        self.stdout.write(f'Found {total} MenuItem(s) to inspect.')

        # Build the list of items we will attempt to process. This allows a dry-run
        # to show exact candidates and enables an interactive confirmation step.
        candidates = []
        processed = 0
        for item in qs:
            if limit and processed >= limit:
                break
            img_name = getattr(item, 'image', None)
            # item.image may be a FieldFile; check its name
            try:
                name = getattr(img_name, 'name', '')
            except Exception:
                name = ''

            # skip empty
            if not name:
                continue

            # heuristics: skip if URL already looks remote (http or cloudinary)
            try:
                url = getattr(img_name, 'url', '')
            except Exception:
                url = ''

            looks_remote = False
            if isinstance(url, str) and url.startswith(('http://', 'https://')) and 'res.cloudinary.com' in url:
                looks_remote = True

            if looks_remote and not force:
                # remote-looking entries are skipped unless --force is used
                continue

            local_path = os.path.join(media_root, name)
            if not os.path.exists(local_path):
                # don't add missing files to candidates; report later
                continue
            # item is a candidate for processing
            local_path = os.path.join(media_root, name)
            if os.path.exists(local_path):
                candidates.append((item, name, url, local_path))

        # Apply limit to candidates if provided
        if limit:
            candidates = candidates[:limit]

        # If requested, include all files under MEDIA_ROOT/menu_images
        all_files = options.get('all_files')
        if all_files:
            menu_images_dir = os.path.join(media_root, 'menu_images')
            if os.path.isdir(menu_images_dir):
                for fname in sorted(os.listdir(menu_images_dir)):
                    rel = os.path.join('menu_images', fname).replace('\\', '/')
                    abs_path = os.path.join(menu_images_dir, fname)
                    # avoid duplicate candidates
                    if any(rel == c[1] for c in candidates):
                        continue
                    # Only include files
                    if os.path.isfile(abs_path):
                        candidates.append((None, rel, '', abs_path))

        self.stdout.write(f'Candidates to process: {len(candidates)}')

        # If not a dry-run, ask for confirmation unless --yes provided
        assume_yes = options.get('yes')
        if not dry_run and not assume_yes:
            self.stdout.write('About to upload the candidate files to the active storage backend.')
            self.stdout.write('Type "yes" to proceed, or anything else to abort: ')
            try:
                answer = input().strip().lower()
            except Exception:
                answer = ''
            if answer != 'yes':
                self.stdout.write('Aborted by user. No files were uploaded.')
                return

        processed = 0
        errors = 0

        # Now perform (or simulate) uploads
        for item, name, url, local_path in candidates:
            label = f'item {item.pk}' if item is not None else name
            self.stdout.write(f'Processing {label}: {name} (remote_url={url})')
            if dry_run:
                processed += 1
                continue

            try:
                with open(local_path, 'rb') as f:
                    django_file = File(f)
                    new_name = os.path.basename(name)
                    with transaction.atomic():
                        if item is not None:
                            # Save to the model field so DB is updated
                            item.image.save(new_name, django_file, save=True)
                            uploaded_url = getattr(item.image, 'url', None)
                        else:
                            # Upload directly to default storage and report URL
                            # Avoid overwriting existing storage entry unless force
                            if not force and default_storage.exists(name):
                                uploaded_url = default_storage.url(name)
                            else:
                                default_storage.save(name, django_file)
                                uploaded_url = default_storage.url(name)
                self.stdout.write(f'UPLOADED: {"item " + str(item.pk) if item is not None else name} -> {uploaded_url}')
                processed += 1
            except Exception as e:
                # If item is None, item may be referenced in error message; guard against that
                try:
                    item_pk = item.pk if item is not None else 'N/A'
                except Exception:
                    item_pk = 'N/A'
                self.stderr.write(f'ERROR uploading item {item_pk}: {e}')
                errors += 1

        self.stdout.write(f'Done. Processed: {processed}. Errors: {errors}.')
