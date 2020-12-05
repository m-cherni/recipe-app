from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITest(TestCase):
    """Test public api ingredient"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_required(self):
        """Test that authentication is required to access the api"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateIngredientAPITest(TestCase):
    """Test private access to the api"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@user.com',
            'User123#'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredients_list(self):
        """Test retrieving ingredient for authenticated user"""
        Ingredient.objects.create(name='ing-1', user=self.user)
        Ingredient.objects.create(name='ing-2', user=self.user)

        res = self.client.get(INGREDIENT_URL)

        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_ingredients_list_for_current_user(self):
        """Test retrieving ingredients only for the current user"""
        user2 = get_user_model().objects.create_user(
            'user1@user.com',
            'User123#'
        )

        Ingredient.objects.create(name='ing-1', user=user2)

        ingredient = Ingredient.objects.create(name='ing', user=self.user)

        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient(self):
        """Test create a new ingredient"""
        payload = {
            'name': 'ing-1'
        }

        self.client.post(INGREDIENT_URL, payload)

        exists = Ingredient.objects.filter(user=self.user,
                                           name=payload['name']).exists()
        self.assertTrue(exists)

    def test_create_ingredient_with_invalid_data(self):
        """Test create ingredient with invalid name"""
        payload = {
            'name': ''
        }

        res = self.client.post(INGREDIENT_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
