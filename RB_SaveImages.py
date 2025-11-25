import os
import torch
from PIL import Image
from PIL import ImageOps
import numpy as np
import json
from datetime import datetime
import random

#Robot's SaveImage Node. support .jpg and .png
#images: iamge array.
#directory path for save image.include datetime strings format
#metadata:metadata for save any strings like prompt

class RB_SaveImages:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "directory": ("STRING", {"default": "./output"}),
                "filename": ("STRING", {"default": "img_{index}.jpg"}),
                "quality": ("INT", {"default": 80}),
                "dpi": ("INT", {"default": 300}),
            },
            "optional": {
                "metadata": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "save_images"
    OUTPUT_NODE = True
    CATEGORY = "RobotNodes"

    def save_images(self, images, directory, filename, quality, dpi, metadata=""):
        saved_paths = []
        # get current datetime
        now = datetime.now()
        full_folder_path = now.strftime(directory)

        # Ensure base directory exists
        os.makedirs(full_folder_path, exist_ok=True)

        for i, image in enumerate(images):
            # Convert the image tensor to a PIL Image
            img = Image.fromarray((image.cpu().numpy() * 255).astype(np.uint8))

            # Create the full folder path based on the folder structure
            os.makedirs(full_folder_path, exist_ok=True)

            # Create the file name and ensure it doesn't overwrite existing files
            index = 0
            while True:
                # 将索引格式化为5位数字符串（不足5位时前面补0）
                formatted_index = f"{index:05d}"
                full_file_name = filename.format(index=formatted_index)  # 使用补零后的序号
                full_file_path = os.path.join(full_folder_path, full_file_name)
                if not os.path.exists(full_file_path):
                    break
                index += 1
           
            if not isinstance(metadata, str):
                metadata = str(metadata)
            
            # Set the DPI info
            img.info['dpi'] = (dpi, dpi)
            
            img.save(full_file_path, quality=quality, dpi=(dpi, dpi), comment=metadata)
            print(f"Image saved with quality: {quality}, DPI: {dpi}, comment: {metadata}")
            del image

            saved_paths.append(full_file_path)

        return (", ".join(saved_paths),)


#robot's node from get image from diretory
#directory: Path from image files
#image_load_cap: one time get how many images, 0 will get all files,
#start_index: file will sort by name, first file index, -1 will get random file,
#load_always: reget file always
class RB_LoadImagesFromDir:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "directory": ("STRING", {"default": ""}),
            },
            "optional": {
                "image_load_cap": ("INT", {"default": 0, "min": 0, "step": 1}),
                "start_index": ("INT", {"default": 0, "min": -1, "step": 1}),
                "load_always": ("BOOLEAN", {"default": False, "label_on": "enabled", "label_off": "disabled"}),
            }
        }

    RETURN_TYPES = ("IMAGE", "MASK", "STRING")
    RETURN_NAMES = ("IMAGE", "MASK", "FILE PATH")
    OUTPUT_IS_LIST = (True, True, True)

    FUNCTION = "load_images"
    CATEGORY = "RobotNodes"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if 'load_always' in kwargs and kwargs['load_always']:
            return float("NaN")
        else:
            return hash(frozenset(kwargs))

    def load_images(self, directory: str, image_load_cap: int = 0, start_index: int = 0, load_always=False):
        print("******" + directory)
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"Directory '{directory}' cannot be found.")
        dir_files = os.listdir(directory)
        if len(dir_files) == 0:
            raise FileNotFoundError(f"No files in directory '{directory}'.")

        # Filter files by extension
        valid_extensions = ['.jpg', '.jpeg', '.png', '.webp']
        dir_files = [f for f in dir_files if any(f.lower().endswith(ext) for ext in valid_extensions)]

        dir_files = sorted(dir_files)
        dir_files = [os.path.join(directory, x) for x in dir_files]

        # start at start_index
        if start_index < 0 :
            dir_files = [random.choice(dir_files)]
        else:
            dir_files = dir_files[start_index:]

        images = []
        masks = []
        file_paths = []

        limit_images = False
        if image_load_cap > 0:
            limit_images = True
        image_count = 0

        for image_path in dir_files:
            if os.path.isdir(image_path) and os.path.ex:
                continue
            if limit_images and image_count >= image_load_cap:
                break
            i = Image.open(image_path)
            i = ImageOps.exif_transpose(i)
            image = i.convert("RGB")
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]

            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

            images.append(image)
            masks.append(mask)
            file_paths.append(str(image_path))
            image_count += 1

        return (images, masks, file_paths)



