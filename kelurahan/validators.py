from django.core.exceptions import ValidationError
import os

MAX_IMAGE_SIZE_MB = 5
ALLOWED_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp']

def validate_image_size(image):
    max_size = MAX_IMAGE_SIZE_MB * 1024 * 1024
    if image.size > max_size:
        raise ValidationError(
            f'Ukuran file terlalu besar ({image.size / 1024 / 1024:.1f} MB). '
            f'Maksimal {MAX_IMAGE_SIZE_MB} MB.'
        )

def validate_image_extension(image):
    ext = os.path.splitext(image.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'Format file tidak didukung ({ext}). Gunakan JPEG, PNG, atau WebP.'
        )
