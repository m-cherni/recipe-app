from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core import models
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def create_test_user_object(email="user@user.com", password="User123#"):
    "Create and return a user object"
    return get_user_model().objects.create_user(
        email, password
    )


def create_test_tag_object(user, name='tag-1'):
    """Create and return a tag object"""
    return models.Tag.objects.create(user=user, name=name)


def create_test_ingredient_object(user, name='ingredient-1'):
    """Create and return an ingredient object"""
    return models.Ingredient.objects.create(user=user, name=name)


def detail_url(recipe_id):
    """Return url for recipe details"""
    return reverse('recipe:recipe-detail', args=[recipe_id])


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
        self.user = create_test_user_object()
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

        user1 = create_test_user_object(
            email='user1@user.com', password='User123#')

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

    def test_view_recipe_detail(self):
        """Test viewing recipe detail"""
        recipe = models.Recipe.objects.create(user=self.user,
                                              title='recipe',
                                              time_minutes=5,
                                              price=5.0)
        recipe.tags.add(create_test_tag_object(user=self.user))
        recipe.ingredients.add(create_test_ingredient_object(user=self.user))

        url = detail_url(recipe.id)

        res = self.client.get(url)

        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(res.data, serializer.data)

    def test_create_basic_recipe(self):
        """Test creating recipe"""
        payload = {
            'title': 'title-1',
            'time_minutes': 30,
            'price': 5.0
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating a recipe with tags"""
        tag1 = create_test_tag_object(user=self.user, name='tag-1')
        tag2 = create_test_tag_object(user=self.user, name='tag-2')

        payload = {
            'title': 'recipe-1',
            'tags': [tag1.id, tag2.id],
            'time_minutes': 15,
            'price': 10.0
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredient(self):
        """Test create recipe with ingredients"""
        ing1 = models.Ingredient.objects.create(user=self.user, name='ing-1')
        ing2 = models.Ingredient.objects.create(user=self.user, name='ing-2')

        payload = {
            'title': 'recipe-1',
            'ingredients': [ing1.id, ing2.id],
            'time_minutes': 15,
            'price': 20.0
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = models.Recipe.objects.get(id=res.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ing1, ingredients)
        self.assertIn(ing2, ingredients)
