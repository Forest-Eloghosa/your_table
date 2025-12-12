from django.views.generic import ListView, DetailView
from .models import MenuCategory, MenuItem


class MenuListView(ListView):
    template_name = 'menu/menu_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        # Prefetch items so we can annotate them in get_context_data
        return MenuCategory.objects.prefetch_related('items').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        # For each item attach a parsed `allergens_list` attribute so templates
        # don't rely on a custom templatetag. This avoids template tag import
        # issues in some environments and keeps parsing centralized.
        for cat in ctx.get('categories', []):
            for item in getattr(cat, 'items', []).all():
                raw = (getattr(item, 'allergens', '') or '').strip()
                if not raw or raw.lower() == 'none':
                    item.allergens_list = []
                else:
                    item.allergens_list = [p.strip() for p in raw.split(',') if p.strip()]

        return ctx


class MenuItemDetailView(DetailView):
    model = MenuItem
    template_name = 'menu/menu_item_detail.html'
    context_object_name = "item"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        allergens = (self.object.allergens or '').strip()

        if allergens.lower() in ('none', ''):
            ctx['allergy_note'] = None
        else:
            ctx['allergy_note'] = allergens

        return ctx

