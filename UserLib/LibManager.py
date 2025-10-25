import os
import pickle

class LibManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, lib_path: str = "lib"):
        if hasattr(self, "_initialized"):
            return  # 防止重复初始化
        self.lib_path = lib_path
        self.instances: dict[str, object] = {}  # 模块名 → 单例实例
        self._initialized = True

    def load_all_modules(self):
        for filename in os.listdir(self.lib_path):
            if filename.endswith(".pkl"):
                module_name = filename[:-4]
                if module_name in self.instances:
                    continue
                file_path = os.path.join(self.lib_path, filename)
                with open(file_path, "rb") as f:
                    instance = pickle.load(f)
                    self.instances[module_name] = instance
                    print(f"[✓] 已加载模块: {module_name}")

    def get(self, name: str):
        if name not in self.instances:
            raise ValueError(f"[✗] 模块 '{name}' 尚未加载或不存在")
        return self.instances[name]
