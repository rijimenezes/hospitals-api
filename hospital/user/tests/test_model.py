import pytest
from django.contrib.auth import get_user_model


def create_user(email='user@example.com', password='123456'):
  """Create and return user"""
  return get_user_model().objects.create_user(email=email, password=password)



@pytest.mark.django_db
class TestUserModel():
  """USER MODEL TESTS"""
  def test_create_user_with_email(self):
    email = 'test@example.com'
    password = 'mystringpassword'
    user = create_user(email=email, password=password)
    assert user.email == email
    assert user.check_password(password) == True

  def test_new_user_without_email_raises_error(self):
    """Test that creating a user without an email raises a ValueError"""
    with pytest.raises(ValueError):
      get_user_model().objects.create_user('', 'passwrod')

  def test_create_superuser(self):
    """Test create a new superuser"""
    user = get_user_model().objects.create_superuser(
      'test@example.com',
      'test2244'
    )
    assert user.is_superuser == True