from django.views.generic import ListView, DetailView
from .models import MenuCategory, MenuItem


class MenuListView(ListView):
    """
    Display all menu categories and their associated items.
    Each menu item includes parsed allergy information.
    """
    template_name = 'menu/menu_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return MenuCategory.objects.prefetch_related('items').all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

            # Parse allergens for each menu item
        for cat in ctx.get('categories', []):
            for item in getattr(cat, 'items', []).all():
                raw = (getattr(item, 'allergens', '') or '').strip()
                if not raw or raw.lower() == 'none':
                    item.allergens_list = []
                else:
                    item.allergens_list = [p.strip() for p in raw.split(',') if p.strip()]

        return ctx


class MenuItemDetailView(DetailView):
    """
    Display details for a single menu item, including allergy information.
    """
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

