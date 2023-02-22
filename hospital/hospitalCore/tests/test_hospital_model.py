import pytest
from django.contrib.auth import get_user_model
from hospitalCore.models import Hospital


def create_user(email='user@example.com', password='123456'):
  """Create and return user"""
  return get_user_model().objects.create_user(email=email, password=password)



@pytest.mark.django_db
class TestHospitalModel():
  """Test hospital"""
  def test_create_hospital(self):
    user = create_user()
    name = 'Hospital1'
    hospital = Hospital.objects.create(user=user, name=name)
    assert hospital.name == name

  def test_get_created_hospital(self):
    user = create_user()
    name = 'Hospital1'
    Hospital.objects.create(user=user, name=name)
    hospital_exists = Hospital.objects.filter(name=name, user=user).exists()
    assert hospital_exists == True
