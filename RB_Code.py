from pathlib import Path
from .sup import ROOT, AlwaysEqualProxy

class RB_Code:

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "code_input": ("STRING", {
                    "default": "# 例：把 3 个输入拼成列表后输出\n"
                              "outputs[0] = inputs['In01']\n"
                              "outputs[1] = inputs['In02']\n"
                              "outputs[2] = inputs['In03']",
                    "multiline": True, "dynamicPrompts": False}),
                "file": ("STRING", {"default": "./res/hello.py", "multiline": False}),
                "use_file": ("BOOLEAN", {"default": False}),
                "run_always": ("BOOLEAN", {"default": False}),
                "In01": (AlwaysEqualProxy("*"),),
                "In02": (AlwaysEqualProxy("*"),),
                "In03": (AlwaysEqualProxy("*"),),
            }
        }

    CATEGORY = "RobotNodes"
    FUNCTION = "execute"
    RETURN_TYPES = (AlwaysEqualProxy("*"),) * 3
    RETURN_NAMES = ("out01", "out02", "out03")

    @classmethod
    def IS_CHANGED(cls, code_input, file, use_file, run_always, **kwargs):
        return float("nan") if run_always else "$$" + str(kwargs) + "$$" + cls.get_exec_string(code_input, file, use_file) + "$$"

    def execute(self, code_input, file, use_file, run_always,
                In01=None, In02=None, In03=None, **kwargs):
        # 1. 准备环境
        outputs = [None, None, None]          # 固定 3 个输出口
        inputs = kwargs.copy()
        inputs.update({"In01": In01, "In02": In02, "In03": In03})

        code = self.get_exec_string(code_input, file, use_file)

        # 2. 运行用户代码
        try:
            # 把 outputs 列表直接丢进去，用户就地修改即可
            exec(code, {"inputs": inputs, "outputs": outputs})
        except Exception as e:
            raise RuntimeError(f"Error executing user code: {e}")

        # 3. 返回长度=3 的元组
        return tuple(outputs)      # (out01, out02, out03)

    @staticmethod
    def get_exec_string(code_input, file, use_file):
        if use_file:
            fname = Path(ROOT / file) if (ROOT / file).is_file() else Path(file)
            if fname.is_file():
                return fname.read_text(encoding="utf-8")
        return code_input
