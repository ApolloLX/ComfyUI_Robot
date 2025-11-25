from .RB_SaveImages import RB_SaveImages
from .RB_SaveImages import RB_LoadImagesFromDir
from .RB_Test import Example
from .RB_Test import RB_ShowImage
from .RB_Code import RB_Code
from .RB_DeleteFile import RB_DeleteFile
from .RB_DeleteFile import RB_GetFilename

print(f"ComfyUI-Robot Created by RobotDeng on 2025-11-1! ")

NODE_CLASS_MAPPINGS = {
    "RB_SaveImages": RB_SaveImages,
    "RB_LoadImagesFromDir": RB_LoadImagesFromDir,
    "RB_Test": Example,
    "RB_ShowImage": RB_ShowImage,
    "RB_Code": RB_Code,
    "RB_DeleteFile": RB_DeleteFile,
    "RB_GetFilename": RB_GetFilename,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RB_LoadImagesFromDir": "RB LoadImagesFromDir",
    "RB_SaveImages": "RB SaveImages",
    "RB_Test": "RB Test",
    "RB_ShowImage":"RB ShowImage",
    "RB_Code":"RB Code",
    "RB_DeleteFile":"RB_DeleteFile",
    "RB_GetFilename": "RB_GetFilename",
}

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']
