import base64
import json
import random
from io import BytesIO
from pathlib import Path

import requests as requests
from PIL import Image
import os


class AssetStorage:
    assets = {}

    def __init__(self):
        traits = sorted(os.listdir('sources'))
        for trait in traits:
            self.assets.update({
                trait: [Path(f'sources/{trait}/{item}') for item in os.listdir(Path(f'sources/{trait}'))]
            })

    @property
    def random(self):
        random_arr = []
        for i in self.assets.keys():
            random_arr.append(random.choice(self.assets[i]))
        return random_arr


class NFTImage:

    def __init__(self):
        self.assets = AssetStorage()

    def generate(self):
        arr = self.assets.random
        first = arr.pop(0)
        return self._generate_rec(arr, Image.open(first))

    def _generate_rec(self, arr, image: Image):
        if len(arr) > 0:
            new_image = Image.alpha_composite(image, Image.open(arr[0]))
            arr.pop(0)
            return self._generate_rec(arr, new_image)
        else:
            return image

    def generate_with_ai(self):
        image = self.generate()
        img_base64 = self._image_to_base64(image)
        payload = {"init_images": [img_base64], "prompt": "anime girl"}
        print(json.dumps(payload))
        r = requests.request("POST", 'http://127.0.0.1:7860/sdapi/v1/img2img', data=json.dumps(payload))
        return r.json()

    @staticmethod
    def _image_to_base64(image):
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue())
        return img_str


im = NFTImage()
print(im.generate_with_ai())
