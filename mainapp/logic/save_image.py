from io import BytesIO

from PIL import Image
from django.core.files import File

def save_save(image):

    img = Image.open(image)
    rgb_image = img.convert('RGB')
    rgb_image = rgb_image.resize((500, 500))
    filestream = BytesIO()
    rgb_image.save(filestream, 'JPEG')
    image = File(filestream, name=image.name)
    return image
