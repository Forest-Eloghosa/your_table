from django.core.management.base import BaseCommand
from reviews.models import Review
from users.models import Profile
from menu.models import MenuItem


BAD_MARKER = "/image/upload/"


def needs_cleaning(path: str) -> bool:
    if not path:
        return False
    return path.startswith("http://") or path.startswith("https://") or path.count(BAD_MARKER) > 1


def clean_path(path: str) -> str:
    if not path:
        return path
    if path.count(BAD_MARKER) > 1:
        idx = path.rfind(BAD_MARKER)
        trimmed = path[idx + len(BAD_MARKER):]
        return trimmed.lstrip("/")
    if path.startswith("http://") or path.startswith("https://"):
        if BAD_MARKER in path:
            idx = path.rfind(BAD_MARKER)
            trimmed = path[idx + len(BAD_MARKER):]
            return trimmed.lstrip("/")
        return path
    return path


def process_queryset(qs, field_name: str, label: str) -> int:
    updated = 0
    for obj in qs:
        path = getattr(obj, field_name)
        current = path.name if hasattr(path, "name") else str(path)
        if not current:
            continue
        if needs_cleaning(current):
            new_name = clean_path(current)
            if new_name != current:
                path.name = new_name
                obj.save(update_fields=[field_name])
                updated += 1
    return updated


class Command(BaseCommand):
    help = "Fix media file paths that contain duplicated Cloudinary prefixes"

    def handle(self, *args, **options):
        total = 0
        total += process_queryset(Profile.objects.all(), "image", "profiles")
        total += process_queryset(Review.objects.all(), "image", "reviews")
        total += process_queryset(MenuItem.objects.all(), "image", "menu")
        self.stdout.write(self.style.SUCCESS(f"Updated {total} media paths"))
