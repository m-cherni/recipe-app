from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def create_test_user(email='user@user.com',
                     password='User123#'):
    return get_user_model().objects.create_user(
        email,
        password
    )


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test create a new user with email is successful"""
        email = "test@test.com"
        password = "Test123#"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email of new user is normalized"""
        email = "test@teSt.com"
        password = "Test123#"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email.lower())

    def test_new_user_email_valid_email(self):
        """Test email of new user is valid and raise error if not"""
        with self.assertRaises(ValueError):
            email = None
            password = "Test123#"
            get_user_model().objects.create_user(
                email=email,
                password=password
            )

    def test_create_new_superuser(self):
        """Test creating new superuser"""
        user = get_user_model().objects.create_superuser(
            'admin@admin.com',
            'Admin123#'
        )

        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test create a tag"""
        tag = models.Tag.objects.create(
            user=create_test_user(),
            name='test-tag'
        )

        self.assertEqual(str(tag), tag.name)

    def test_ingredient_str(self):
        """Test create ingredient model"""
        ingredient = models.Ingredient.objects.create(
            user=create_test_user(),
            name='test-ingredient'
        )

        self.assertEqual(str(ingredient), ingredient.name)

    def test_recipe_str(self):
        """Test create recipe object"""
        recipe = models.Recipe.objects.create(
            user=create_test_user(),
            title='test-recipe',
            time_minutes=5,
            price=5.0
        )

        self.assertEqual(str(recipe), recipe.title)

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the correct location"""
        uuid = 'test-uuid'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'myimage.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
