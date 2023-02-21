import pytest

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from user.serializers import UserSerializer

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME_URL = reverse('user:me')
ALL_USERS_URL = reverse('user:all')


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

  def test_retrieve_all_users(self):
    """Test return all users"""
    user1 = self.user_payload
    user2 = {
      'email': 'user2@example.com',
      'password': 'paswrods',
      'name': 'user2'
    }
    create_user(**user1)
    create_user(**user2)
    res = self.client.get(ALL_USERS_URL)
    users = get_user_model().objects.all()
    serializer = UserSerializer(users, many=True)
    assert res.status_code == status.HTTP_200_OK
    
    assert serializer.data == res.data


@pytest.mark.django_db
class TestPrivateUserApi():
    """Test API requests that require authentication."""
    def setup_method(self):
        self.user = create_user(
            email='test@example.com',
            password='superpass123',
            name='Test user',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retriving profile for logged in user."""
        res = self.client.get(ME_URL)

        assert res.status_code == status.HTTP_200_OK
        assert res.data == {
            'email': self.user.email,
            'name': self.user.name,
        }

    def test_post_me_not_allowed(self):
        """Test POST ist not allowed for the endpoint."""
        res = self.client.post(ME_URL, {})

        assert res.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_update_user_profile(self):
        """Test updating the user profile for the authenticated user."""
        payload = {
            'name': 'new name',
            'password': 'newsuperpass123',
        }
        res = self.client.patch(ME_URL, payload)

        self.user.refresh_from_db()
        print(self.user)        
        assert self.user.check_password(payload['password']) == True
        assert res.status_code == status.HTTP_200_OK