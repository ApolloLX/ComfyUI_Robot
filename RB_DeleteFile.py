import os
import folder_paths

class RB_DeleteFile:
    """
    删除指定文件的节点（简化版）
    注意：直接删除文件，无安全检查和确认
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filename": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入完整文件路径"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("status",)
    FUNCTION = "delete_file"
    CATEGORY = "RobotNodes"

    def delete_file(self, filename):
        # 直接使用用户输入的文件路径
        target_path = filename
        
        try:
            if os.path.exists(target_path):
                os.remove(target_path)
                return (f"成功删除：{target_path}",)
                print (f"成功删除：{target_path}",)
            else:
                return (f"文件不存在：{target_path}",)
                print (f"文件不存在：{target_path}",)          
        except Exception as e:
            return (f"删除失败：{str(e)}",)
            print (f"删除失败：{str(e)}",) 

class RB_GetFilename:
    """
    提取文件名节点
    输入包含目录的文件名，返回不含目录的文件名
    """
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "full_path": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "输入完整文件路径"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filename",)
    FUNCTION = "get_filename"
    CATEGORY = "RobotNodes"

    def get_filename(self, full_path):
        # 使用os.path.basename提取文件名
        filename = os.path.basename(full_path)
        return (filename,)
