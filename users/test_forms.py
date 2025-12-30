from io import BytesIO

from PIL import Image
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from users.forms import ProfilePictureForm


class ProfileTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username="profiled", password="pass1234")

    def test_profile_created_when_user_is_created(self):
        self.user.refresh_from_db()
        self.assertTrue(hasattr(self.user, "profile"))
        self.assertEqual(str(self.user.profile), f"Profile({self.user.username})")

    def test_profile_picture_form_accepts_image(self):
        # Create a minimal valid image
        img = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        img.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        image = SimpleUploadedFile("avatar.jpg", img_bytes.getvalue(), content_type="image/jpeg")
        form = ProfilePictureForm(data={}, files={"image": image}, instance=self.user.profile)

        self.assertTrue(form.is_valid(), msg=form.errors)
        profile = form.save()
        self.assertTrue(profile.image.name)