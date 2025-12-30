from decimal import Decimal

from django.test import TestCase

from menu.models import MenuCategory, MenuItem, Restaurant


class MenuModelTests(TestCase):
    def setUp(self):
        self.category = MenuCategory.objects.create(
            name="Starters", description="Small plates to share", slug="starters"
        )

    def test_category_str_returns_name(self):
        self.assertEqual(str(self.category), "Starters")

    def test_menu_item_str_and_url(self):
        item = MenuItem.objects.create(
            category=self.category,
            name="Grilled Salmon",
            slug="grilled-salmon",
            description="Chargrilled fillet",
            price=Decimal("18.50"),
            allergens="fish",
            is_active=True,
        )

        self.assertEqual(str(item), "Grilled Salmon")
        self.assertEqual(item.get_absolute_url(), "/menu/grilled-salmon/")
        self.assertTrue(item.is_active)

    def test_restaurant_str_returns_name(self):
        restaurant = Restaurant.objects.create(
            name="Test Kitchen",
            slug="test-kitchen",
            description="",
            address="123 Main St",
            phone="555-1234",
            website="https://example.com",
        )

        self.assertEqual(str(restaurant), "Test Kitchen")