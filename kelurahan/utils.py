from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys

def compress_image(image, max_width=1200, quality=85):
    img = Image.open(image)

    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')

    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)

    output = BytesIO()
    img.save(output, format='JPEG', quality=quality, optimize=True)
    output.seek(0)

    return InMemoryUploadedFile(
        output, 'ImageField',
        f"{image.name.split('.')[0]}.jpg",
        'image/jpeg',
        len(output.getbuffer()), None
    )
