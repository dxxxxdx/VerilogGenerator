import os
import pickle
import sys
sys.path.append("C:\\Users\\zys\\PycharmProjects\\VerilogGen")
from ModuleClass import BasicModule


class LibManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, lib_path: str = ""):
        if hasattr(self, "_initialized"):
            return
        # 修正为绝对路径
        if not lib_path:
            lib_path = "UserLib/lib"
        self.lib_path = os.path.abspath(lib_path)
        self.instances: dict[str, object] = {}
        self._initialized = True

    @classmethod
    def get_instance(cls, lib_path: str = "UserLib/lib"):
        if cls._instance is None:
            cls._instance = cls(lib_path)
        return cls._instance

    def load_all_modules(self):
        # 自动创建库路径，避免 FileNotFoundError
        if not os.path.exists(self.lib_path):
            os.makedirs(self.lib_path, exist_ok=True)
        for filename in os.listdir(self.lib_path):
            if filename.endswith(".pkl"):
                module_name = filename[:-4]
                if module_name in self.instances:
                    continue
                file_path = os.path.join(self.lib_path, filename)
                try:
                    with open(file_path, "rb") as f:
                        instance = pickle.load(f)
                        self.instances[module_name] = instance
                        print(f"[✓] 已加载模块: {module_name}")
                except Exception as e:
                    print(f"[✗] 加载模块 {module_name} 失败: {e}")

    def get(self, name: str):
        if name not in self.instances:
            print(f"[✗] 模块 '{name}' 尚未加载或不存在")
            return None
        else:
            return self.instances[name]

    def load_module(self, file_path: str):
        try:
            with open(file_path, "rb") as f:
                instance = pickle.load(f)
                self.instances[os.path.splitext(os.path.basename(file_path))[0]] = instance
        except Exception as e:
            print(f"[✗] 加载模块文件失败: {file_path}, 错误: {e}")
