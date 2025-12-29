from django.db import models
from django.urls import reverse


class MenuCategory(models.Model):
    """
    Represents a category of menu items, e.g. Appetizers, Main Courses, Desserts.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = "Menu Category"
        verbose_name_plural = "Menu Categories"

    def __str__(self):
        return self.name


class MenuItem(models.Model):
    """
    Represents a single item on the menu.
    Fields include name, description, price, image, allergens, and active status.
    """
    category = models.ForeignKey(MenuCategory, related_name='items', on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu/', blank=True, null=True)
    allergens = models.CharField(max_length=255, blank=True, help_text='Optional comma-separated list of allergens, e.g. "nuts, dairy, soy"')
    is_active = models.BooleanField(default=True)

    def get_absolute_url(self):
        return reverse('menu:menu_item_detail', args=[self.slug])

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """
    Minimal Restaurant model so other apps (bookings, specials) can reference it.

    Fields kept small to avoid migration conflicts; extend later as needed.
    """
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    address = models.CharField(max_length=300, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    image = models.ImageField(upload_to='restaurants/', blank=True, null=True)

    class Meta:
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('menu:restaurant_detail', args=[self.slug])
