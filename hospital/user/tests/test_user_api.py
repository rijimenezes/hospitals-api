import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')


def create_user(**params):
  """Create and return user"""
  return get_user_model().objects.create_user(**params)


@pytest.mark.django_db
class TestPublicUserApi():
  """Test the public features of the user API."""
  def setup_method(self) -> None:
    self.client = APIClient()
    self.user_payload = {
      'email': 'test@example.com',
      'password': 'pasword221',
      'name': 'Test user'
    }

  def test_create_user_success(self):
    "Test create user"
    payload = self.user_payload
    res = self.client.post(CREATE_USER_URL, payload)

    assert res.status_code == status.HTTP_201_CREATED
    user = get_user_model().objects.get(email=payload['email'])
    assert user.check_password(payload['password']) == True
    assert 'password' not in res.data

  def test_user_with_email_exists_error(self):
    """Test error returned if user with email esists."""
    payload = self.user_payload
    create_user(**payload)
    res = self.client.post(CREATE_USER_URL, payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST

  def test_password_too_short_error(self):
    """Test password is too short."""
    payload = self.user_payload
    payload['password'] = '123'
    res = self.client.post(CREATE_USER_URL, payload)
    assert res.status_code == status.HTTP_400_BAD_REQUEST
    user_exists = get_user_model().objects.filter(
      email=payload['email']
    ).exists()
    assert user_exists == False

  def test_create_user_token(self):
    """Test generates token for valid createntials"""
    user_details = self.user_payload
    create_user(**user_details)
    payload = {
      'email': user_details['email'],
      'password': user_details['password']
    }
    res = self.client.post(TOKEN_URL, payload)

    assert 'token' in res.data
    assert res.status_code == status.HTTP_200_OK

  
  def test_create_token_bad_credentials(self):
      """Test returns error if credentials are invalid."""
      create_user(email='test@example.com', password='superpass')

      payload = {'email': 'test@example.com', 'password': 'badpass'}
      res = self.client.post(TOKEN_URL, payload)

      assert 'token' not in res.data
      assert res.status_code == status.HTTP_400_BAD_REQUEST

  def test_create_token_blank_password(self):
      """Test returns an error if payload contains blank password."""
      payload = {'email': 'test@example.com', 'password': ''}
      res = self.client.post(TOKEN_URL, payload)

      assert 'token' not in res.data
      assert res.status_code == status.HTTP_400_BAD_REQUEST

  def test_retrieve_user_unauthorized(self):
      """Test authentication is required for users."""
      res = self.client.get(ME_URL)

      assert res.status_code == status.HTTP_401_UNAUTHORIZED

