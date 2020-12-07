from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def create_test_user(email="user@user.com", password="User123#"):
    return get_user_model().objects.create_user(
        email, password
    )


class PublicRecipeAPITest(TestCase):
    """Test the public access to the Recipe api"""

    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_required(self):
        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeAPITest(TestCase):
    """Test the private access to the Recipe api"""

    def setUp(self):
        self.user = create_test_user()
        self.client = APIClient()

        self.client.force_authenticate(user=self.user)

    def test_list_recipe(self):
        """Test listing recipe for authenticated user"""

        models.Recipe.objects.create(user=self.user,
                                     title='recipe-1',
                                     time_minutes=5,
                                     price=2.0)

        res = self.client.get(RECIPE_URL)

        recipes = models.Recipe.objects.all().order_by('-title')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_list_recipe_for_the_current_user(self):
        """Test that returned recipes list is only for the current user"""

        user1 = create_test_user(email='user1@user.com', password='User123#')

        models.Recipe.objects.create(user=user1,
                                     title='recipe-1',
                                     time_minutes=4,
                                     price=2.5)
        recipe = models.Recipe.objects.create(user=self.user,
                                              title='recipe',
                                              time_minutes=5,
                                              price=5.0)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['title'], recipe.title)
