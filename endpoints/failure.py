from io import BytesIO

from PIL import Image
from flask import send_file

from utils import http
from utils.endpoint import Endpoint


class Failure(Endpoint):
    def generate(self, avatars, text, usernames):
        base = Image.open(self.assets.get('assets/failure/failure.bmp')).convert('RGBA')
        avatar = http.get_image(avatars[0]).resize((215, 215)).convert('RGBA')

        base.paste(avatar, (143, 525), avatar)
        base = base.convert('RGB')

        b = BytesIO()
        base.save(b, format='jpeg')
        b.seek(0)
        return send_file(b, mimetype='image/jpeg')


def setup(cache):
    return Failure(cache)
