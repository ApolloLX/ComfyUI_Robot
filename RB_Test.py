

class RB_ShowImage:
    def __init__(self):
        self.output_dir = folder_paths.get_output_directory()
        self.type = "output"
        self.prefix_append = ""
        self.compress_level = 4

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "images": ("IMAGE", {"tooltip": "The images to save."}),
                "filename_prefix": ("STRING", {"default": "ComfyUI", "tooltip": "The prefix for the file to save. This may include formatting information such as %date:yyyy-MM-dd% or %Empty Latent Image.width% to include values from nodes."})
            },
            "hidden": {
                "prompt": "PROMPT", "extra_pnginfo": "EXTRA_PNGINFO"
            },
        }

    RETURN_TYPES = ()
    FUNCTION = "save_images"

    OUTPUT_NODE = True

    CATEGORY = "RobotNodes"
    DESCRIPTION = "Just test by Robot."

    def save_images(self, images, filename_prefix="ComfyUI", prompt=None, extra_pnginfo=None):
        filename_prefix += self.prefix_append
        full_output_folder, filename, counter, subfolder, filename_prefix = folder_paths.get_save_image_path(filename_prefix, self.output_dir, images[0].shape[1], images[0].shape[0])
        results = list()
        for (batch_number, image) in enumerate(images):
            i = 255. * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            metadata = None
            if not args.disable_metadata:
                metadata = PngInfo()
                if prompt is not None:
                    metadata.add_text("prompt", json.dumps(prompt))
                if extra_pnginfo is not None:
                    for x in extra_pnginfo:
                        metadata.add_text(x, json.dumps(extra_pnginfo[x]))

            filename_with_batch_num = filename.replace("%batch_num%", str(batch_number))
            file = f"{filename_with_batch_num}_{counter:05}_.png"
            img.save(os.path.join(full_output_folder, file), pnginfo=metadata, compress_level=self.compress_level)
            results.append({
                "filename": file,
                "subfolder": subfolder,
                "type": self.type
            })
            counter += 1

        return { "ui": { "images": results } }
    
    
class RB_LoadImage:
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True})},
                }

    CATEGORY = "image"

    RETURN_TYPES = ("IMAGE", "MASK")
    FUNCTION = "load_image"
    def load_image(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        
        img = node_helpers.pillow(Image.open, image_path)
        
        output_images = []
        output_masks = []
        w, h = None, None

        excluded_formats = ['MPO']
        
        for i in ImageSequence.Iterator(img):
            i = node_helpers.pillow(ImageOps.exif_transpose, i)

            if i.mode == 'I':
                i = i.point(lambda i: i * (1 / 255))
            image = i.convert("RGB")

            if len(output_images) == 0:
                w = image.size[0]
                h = image.size[1]
            
            if image.size[0] != w or image.size[1] != h:
                continue
            
            image = np.array(image).astype(np.float32) / 255.0
            image = torch.from_numpy(image)[None,]
            if 'A' in i.getbands():
                mask = np.array(i.getchannel('A')).astype(np.float32) / 255.0
                mask = 1. - torch.from_numpy(mask)
            else:
                mask = torch.zeros((64,64), dtype=torch.float32, device="cpu")
            output_images.append(image)
            output_masks.append(mask.unsqueeze(0))

        if len(output_images) > 1 and img.format not in excluded_formats:
            output_image = torch.cat(output_images, dim=0)
            output_mask = torch.cat(output_masks, dim=0)
        else:
            output_image = output_images[0]
            output_mask = output_masks[0]

        return (output_image, output_mask)

    @classmethod
    def IS_CHANGED(s, image):
        image_path = folder_paths.get_annotated_filepath(image)
        m = hashlib.sha256()
        with open(image_path, 'rb') as f:
            m.update(f.read())
        return m.digest().hex()

    @classmethod
    def VALIDATE_INPUTS(s, image):
        if not folder_paths.exists_annotated_filepath(image):
            return "Invalid image file: {}".format(image)

        return True    


class Example:

    """
    一个示例节点
    类方法
    INPUT_TYPES (dict):
    用于告知主程序节点的输入参数。
    IS_CHANGED:
    可选方法，用于控制节点何时重新执行,通常情况下处于注释状态。
    属性
    RETURN_TYPES (tuple):
    输出元组中每个元素的类型。
    RETURN_NAMES (tuple):
    可选：输出元组中每个输出的名称。
    FUNCTION (str):
    入口方法的名称。例如，如果 FUNCTION = "execute"，则会运行 Example().execute()
    OUTPUT_NODE ([bool]):
    如果该节点是从图形输出结果/图像的输出节点，例如 SaveImage 节点。
    后端将迭代这些输出节点，并尝试在其父图形正确连接时执行所有它们的父节点。
    如果不存在，则假定为 False。
    CATEGORY (str):
    节点在用户界面中显示的类别。
    execute(s) -> tuple || None:
    入口方法。此方法的名称必须与属性 FUNCTION 的值相同。
    例如，如果 FUNCTION = "execute"，则此方法的名称必须是 execute，如果 FUNCTION = "foo"，则其名称必须是 foo。
    """

    #初始化方法，在类实例化时调用，可以做一些初始化操作，但很多自定义节点由于都有各自的模块文件夹，所以通常是在模块文件夹里的__init__.py文件中进行初始化操作
    def __init__(self):
        pass
    
    @classmethod
    def INPUT_TYPES(s):

        """
            返回一个包含所有输入字段配置的字典。
            某些类型（字符串）："MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT"。
            输入类型 "INT", "STRING" 或 "FLOAT" 是节点字段的特殊值。
            类型可以是用于选择的列表。

            返回：`dict`（字典）：
            - 键 input_fields_group (`string`): 可以是`required`、`optional`、`hidden`中的任意一种。但至少得有一个`required`属性，该属性表示必填项，而optional表示可选项，hidden表示隐藏项。
            - 值 input_fields (`dict`): 包含输入字段配置：
                * 键 field_name (`string`): 入口方法参数的名称
                * 值 field_config (`tuple`):这里的tuple是指元组
                    + 第一个值是指示字段类型的字符串或用于选择的列表。
                    + 第二个值是 "INT", "STRING" 或 "FLOAT" 类型的配置。
        """
        return {
            "required": {
                # "image": ("IMAGE",),#冒号后第一个被引号引起来的，代表的数据类型，通常有以下几种："MODEL", "VAE", "CLIP", "CONDITIONING", "LATENT", "IMAGE", "INT", "STRING", "FLOAT"
                "image": ("IMAGE",{"forceInput": True}),
                "FilePath": ("STRING", {
                    "multiline": False, #值为True时，表示输入框可以输入多行文本，False表示只能输入一行文本。
                    "default": "D:\\"
                }),
            },
         }
        #required属性中至少得有一项，比如，这里的"int_field": ("INT", {}) 这一项，否则无法正常运行。
        #optional属性是可选的，可以没有。
    
    #返回值类型，必须与入口函数的返回值保持类似的形式。
    RETURN_TYPES = ("STRING",)

    #解开下面这行注释，将能自定义输出口的名字，引号内的就是输出口的名字，可中文。
    RETURN_NAMES = ("FileName",)
    
    
    #入口函数，这里的"test"必须与下面的def test()函数名保持一致，即便要改名，也得两个都改成一样的。
    FUNCTION = "SaveJPG"
    
    #设置该变量的值为True，表示该节点可以不用连接到任何组件，直接运行。为False时，则会弹出警告。
    # OUTPUT_NODE = True

    #分类名，这里的Example将会直接出现在界面的右键的一级菜单中
    CATEGORY = "RobotNodes"


    #该自定义节点的执行入口，如果你需要写什么函数或功能，在这里写。另外，def 后面的函数名（这里是test）可以自定义，但必须与上面的FUNCTION =""的双引号中的内容保持一致(被双引号括起来的是字符串，一个编程的基础概念）。
    #形式参数可以从上面的INPUT_TYPES函数的返回值中获取，例如： int_field, float_field, print_to_screen,string_field,text=None。
    #注意：即便是选填项，也要在变量名后加一个"=None"，否则会报错。
    def SaveJPG(self,Image,FilePath ):
        print(strFile)
        return (strFile,)
    #以上自定义方法写法和一般的python方法写法一致，但对返回值有要求，return (image,) 中的image必须与RETURN_TYPES中的内容保持一致，否则无法正常运行。
    #另外，返回值由于是元组，所以括号不能省略，并且在元组中只有一个元素的时候，需要加一个逗号，例如return (image,)。

    
    

    """
    当前节点会在任意输入发生变化时重新执行，但该方法可以用来强制节点在输入不变时再次执行。
    你可以使该节点返回一个数字或字符串。该值会与节点上次执行时返回的值进行比较，如果不同，则节点会再次执行。
    在核心仓库中，这个IS_CHANGED方法用于 LoadImage 节点，他们返回图像哈希值作为字符串。如果图像哈希值在执行间发生变化，LoadImage 节点会再次执行。
    """

    #一旦你放开IS_CHANGED方法的注释，就可以让你的节点在输入不变时依旧能够执行。
    """
    以下是我个人理解（执行情况进过实际验证）：
    不使用该方法的情况下，如果节点输入的数据不变，不会再次执行。
    要想使用该方法，得保证它返回一个发生变化的值。也就是说，我们要想方设法返回一个值，并保证它每次都不一样。可以使用返回一个时间戳，或者返回一个随机数，或者NaN，来达成想要的效果。
    ★需要注意的是，该方法隐藏了内部的异常，即便抛出异常，似乎也被另外的代码进行了捕获，所以在控制台看不到任何报错，反而还能在输入值不变的情况下，稳定触发。
    但这存在一个BUG，当你想要用开关控制它时，不管是开或者关，都没法影响到它的执行。
    形式参数里不要乱用未定义的变量，会直接触发异常，导致输入不变依旧执行但无法控制开关。
    """
    # @classmethod
    # def IS_CHANGED(s, string_field, int_field,float_field, print_to_screen,text=None):
    #     print("验证是否执行")
    #     return float("NaN")
    ##该方法的返回值只要和上一次执行的返回值不相等，就可以保证该节点在输入不变时依旧能够执行。float("NaN") 恰好具备这个特点。

# 设置web目录，位于该目录中的任何.js文件都将被前端加载为前端扩展。使用的方法是，在当前文件所在目录下，建立一个somejs文件夹（可以自己改名，但要与下方代码保持一致），然后在该文件夹里面添加js代码。
# 注意：如果采用了独立的__init__.py文件（也就是该自定义节点有专属的文件夹的情况下），需要在__init__.py文件中添加WEB_DIRECTORY变量，否则会识别不到该前端代码文件。
# WEB_DIRECTORY = "./somejs"

# NOTE: names should be globally unique
#节点类映射，引号中的Example表示节点在界面中使用英文搜索可找到的名称
#右侧的Example则对应代码中的类名，也就是在这个python文件的最开始部分那个class 后面的类名（类名都是以大写字母开头的），如果写错，载入阶段就会直接报错。
#NODE_CLASS_MAPPINGS = {
#    "RobotNode01": Example
#}

# 节点名称映射，在界面中显示的节点名称，需要跟上面的节点类映射中的键名（就是那个引号中的内容）对应。
#NODE_DISPLAY_NAME_MAPPINGS = {
#    "RobotNode01": "Robot_Test"
#}
