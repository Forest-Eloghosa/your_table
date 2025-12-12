from django.contrib import admin
from .models import MenuCategory, MenuItem, Restaurant


@admin.register(MenuCategory)
class MenuCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name",)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "price", "is_active", "allergens")
    list_filter = ("category", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "description", "allergens")
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category', 'description', 'price', 'image', 'allergens', 'is_active')
        }),
    )


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "phone", "website")
    search_fields = ("name", "address")
