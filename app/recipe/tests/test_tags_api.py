from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag, Recipe
from recipe.serializers import TagSerializer

TAG_URL = reverse('recipe:tag-list')


class PublicTagApiTest(TestCase):
    """Test list tags"""

    def setUp(self):
        self.client = APIClient()

    def test_login_is_required(self):
        """Test that login is required"""
        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTagApiTest(TestCase):
    """Test Tag api fr authenticated user"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            'user@user.com',
            'Test123#'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrive tags for authenticated user"""
        Tag.objects.create(user=self.user, name='tag-1')
        Tag.objects.create(user=self.user, name='tag-2')

        res = self.client.get(TAG_URL)

        tags = Tag.objects.all().order_by('-name')
        serializer = TagSerializer(tags, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_returned_limited_to_user(self):
        """Test that tags returned are limited to the authenticated user"""
        user2 = get_user_model().objects.create_user(
            'user1@user.com',
            'Test123#'
        )

        tag = Tag.objects.create(user=self.user, name='tag-1')
        Tag.objects.create(user=user2, name='tag-2')

        res = self.client.get(TAG_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)

    def test_create_tag_successful(self):
        """Test create tag is successful"""

        payload = {'name': 'tag-1'}

        self.client.post(TAG_URL, payload)

        exists = Tag.objects.filter(
            user=self.user,
            name=payload['name']
        ).exists()

        self.assertTrue(exists)

    def test_create_name_invalid(self):
        """Test create tag with invalid name"""
        payload = {'name': ''}

        res = self.client.post(TAG_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_retrieve_tags_assigned_to_recipe(self):
        """Test retrieve tags assigned to recipe"""

        tag1 = Tag.objects.create(user=self.user, name='tag-1')
        tag2 = Tag.objects.create(user=self.user, name='tag-2')
        recipe = Recipe.objects.create(
            title='recipe',
            time_minutes=20,
            price=5.0,
            user=self.user
        )

        recipe.tags.add(tag1)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_retrieve_tags_assigned_unique(self):
        """Test filtering tags by assigned returns unique items"""
        tag = Tag.objects.create(user=self.user, name='tag-1')
        Tag.objects.create(user=self.user, name='tag-2')
        recipe1 = Recipe.objects.create(
            title='recipe-1',
            time_minutes=20,
            price=5.0,
            user=self.user
        )
        recipe1.tags.add(tag)
        recipe2 = Recipe.objects.create(
            title='recipe-2',
            time_minutes=3,
            price=5.0,
            user=self.user
        )
        recipe2.tags.add(tag)

        res = self.client.get(TAG_URL, {'assigned_only': 1})

        self.assertEqual(len(res.data), 1)
