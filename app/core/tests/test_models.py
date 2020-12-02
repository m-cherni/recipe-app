from django.test import TestCase
from django.contrib.auth import get_user_model


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
