import os
import uuid


def get_file_path(instance, filename: str):
    """Generate file path for new image."""
    ext = os.path.splitext(filename)[1]
    filename = f'{uuid.uuid4()}{ext}'    
    
    return os.path.join('uploads', instance._model_name, filename)