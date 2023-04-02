import base64
import json
import random
from io import BytesIO
from pathlib import Path
import uuid
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
        payload = StyleConfig.octane_anime_girls(img_base64)
        r = requests.request("POST", 'http://192.168.1.3:7855/sdapi/v1/img2img',
                             data=json.dumps(payload))
        base64_generated_image = r.json()['images'][0]
        base64_upscaled_image = self.upscale_image(base64_generated_image).json()['image']
        self._base64_to_image(base64_upscaled_image)

    @staticmethod
    def _image_to_base64(image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_bytes = base64.b64encode(buffered.getvalue())
        return img_bytes.decode('utf-8')

    @staticmethod
    def _base64_to_image(b64):
        img = Image.open(BytesIO(base64.b64decode(b64)))
        img.save(f'results/{uuid.uuid4()}.png')

    @staticmethod
    def upscale_image(image):
        payload = {}
        payload['image'] = image
        payload['upscaler_1'] = 'R-ESRGAN 4x+ Anime6B'
        payload['upscaling_resize'] = 4
        r = requests.request("POST", 'http://192.168.1.3:7855/sdapi/v1/extra-single-image',
                             data=json.dumps(payload))
        return r


class StyleConfig:

    @staticmethod
    def octane_anime_girls(image):
        """
        USE DELIBERATEv2
        :param image:
        :return:
        """
        payload = {}
        payload['init_images'] = [image]
        payload['prompt'] = "anime girl, concept art, professional, ((soft colors)), highly detailed photorealistic, hq, 4k, tranding on artstation, shot on leica, raytracing, octane render, 80mm"
        payload['denoising_strength'] = 0.75
        payload['steps'] = 40
        payload['width'] = 768
        payload['sampler_name'] = "DPM2 Karras"
        payload['height'] = 768
        payload['negative_prompt'] = 'blur, unfocus, cropped, ugly'
        return payload

    @staticmethod
    def soft_anime_girls(image):
        """
        USE DOSMIX WITH EMA ANIME2f
        :param image:
        :return:
        """
        payload = {}
        payload['init_images'] = [image]
        payload['prompt'] = "sharp focus, best quality, masterpiece anime girl portrait concept art, professional, ((soft colors)), highly detailed photorealistic, hq, 4k, shot on leica, 80mm"
        payload['denoising_strength'] = 0.75
        payload['steps'] = 30
        payload['width'] = 768
        payload['height'] = 768
        payload['negative_prompt'] = '(realistic:0.7), (low quality, worst quality:1.4), blur, unfocus, cropped, ugly, blurry, weird'
        return payload



im = NFTImage()

for i in range(0, 100):
    im.generate_with_ai()

# Stable Diffusion API не может раскодировать base64 изображение и харкается
# {'detail': 'Invalid encoded image'}
