import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from rest_framework import status
from django.urls import reverse

@pytest.mark.django_db
class TestUsernameView:
    def setup_method(self):
        self.client = APIClient()

    def test_username_view_authenticated(self):
        user = User.objects.create_user(username='testuser', password='testpassword')

        self.client.force_authenticate(user=user)
        url = reverse("username")
        response = self.client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data['username'] == 'testuser'

    def test_username_view_unauthenticated(self):
        url = reverse("username")

        response = self.client.get(url)

        assert response.status_code == status.HTTP_403_FORBIDDEN
