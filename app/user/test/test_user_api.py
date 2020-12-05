from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test publicuser  api test"""

    def setUp(self):
        self.client = APIClient()

    def test_create_valid_user_successful(self):
        """Test creating user with valid payload is successful"""

        payload = {
            'email': 'user@user.com',
            'password': 'User123#',
            'name': 'user'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_create_user_already_exists_fails(self):
        """Test creating user that already exists fails"""
        payload = {
            'email': 'user@user.com',
            'password': 'User123#',
            'name': 'user'
        }
        create_user(**payload)

        payload1 = {
            'email': 'user@user.com',
            'password': 'Test123#',
            'name': 'test'
        }

        res = self.client.post(CREATE_USER_URL, payload1)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_fails(self):
        """Test creating user with password less than 5 (too short) fails"""
        payload = {
            'email': 'user@user.com',
            'password': 'user',
            'name': 'user'
        }

        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for a user"""
        payload = {
            'email': 'user@user.com',
            'password': 'User123#'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)
        self.assertIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_invalid_incredentials(self):
        """Token is not created if invalid credentials are provided"""
        payload = {
            'email': 'user@user.com',
            'password': 'User123#'
        }
        create_user(**payload)
        payload = {
            'email': 'user@user.com',
            'password': 'user'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_no_user(self):
        """Test create token if user does not exist"""
        payload = {
            'email': 'user@user.com',
            'password': 'user'
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_with_missing_field(self):
        """Test create token with missing fields"""
        payload = {
            'email': 'user@user.com',
            'password': ''
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertNotIn('token', res.data)
        self.assertTrue(res.status_code, status.HTTP_400_BAD_REQUEST)
