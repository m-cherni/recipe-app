from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Tag
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
