from django.db import models
from django.conf import settings

from hospital.file_utils import get_file_path


# Create your models here.
class Hospital(models.Model):
  """Hospital model"""
  
  name = models.CharField(max_length=255, null=False)
  image = models.ImageField(null=True, upload_to=get_file_path)
  user = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE
  )

  _model_name = 'hospital'

  def __str__(self) -> str:
    return self.name