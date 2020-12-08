from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer

INGREDIENT_URL = reverse('recipe:ingredient-list')


class PublicIngredientAPITest(TestCase):
    """Test public api ingredient"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_required(self):
        """Test that authentication is required to access the api"""
        res = self.client.get(INGREDIENT_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_retrieve_ingredients_assigned_to_recipe(self):
        """Test retrieve ingredients assigned to recipe"""

        ingredient1 = Ingredient.objects.create(
            user=self.user, name='ingredient-1')
        ingredient2 = Ingredient.objects.create(
            user=self.user, name='ingredient-2')
        recipe = Recipe.objects.create(
            title='recipe',
            time_minutes=20,
            price=5.0,
            user=self.user
        )

        recipe.ingredients.add(ingredient1)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_ingredients_assigned_unique(self):
        """Test filtering ingredients by assigned returns unique items"""
        ingredient = Ingredient.objects.create(
            user=self.user, name='ingredient-1')
        Ingredient.objects.create(user=self.user, name='ingredient-2')
        recipe1 = Recipe.objects.create(
            title='recipe-1',
            time_minutes=20,
            price=5.0,
            user=self.user
        )
        recipe1.ingredients.add(ingredient)
        recipe2 = Recipe.objects.create(
            title='recipe-2',
            time_minutes=3,
            price=5.0,
            user=self.user
        )
        recipe2.ingredients.add(ingredient)

        res = self.client.get(INGREDIENT_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
