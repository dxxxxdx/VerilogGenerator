import os
import pickle

from Link import Pin, ModuleConn



class BasicModule:
    """
    表示一个 Verilog 模块。
    支持端口定义（基于 Pin）、逻辑语句、子模块实例化。
    """

    def __init__(self, name: str):
        self.name = name
        self.pins: [Pin] = [] # Pin 对象
        self.logic: list[str] = []     # Verilog 逻辑语句
        self.submodules: list[tuple[str, BasicModule,ModuleConn:ModuleConn]] = []  # (实例名, 子模块对象)

    def add_pin(self, pin: Pin):
        """
        添加一个端口。
        """
        self.pins.append(pin)

    def get_pin(self, name: str) -> Pin:
        """
        根据端口名获取对应的 Pin 对象。
        如果未找到，抛出异常。
        """
        for pin in self.pins:
            if pin.name == name:
                return pin
        raise ValueError(f"[✗] 模块 '{self.name}' 中未找到名为 '{name}' 的端口")


    def add_logic(self, line: str):
        """
        添加一行 Verilog 逻辑语句。
        """
        self.logic.append(line)


    def collect_submodule_names(self) -> set[str]:
        """
        递归收集所有子模块名称（不重复）。
        """
        names = set()
        for _, submod in self.submodules:
            names.add(submod.name)
            names.update(submod.collect_submodule_names())
        return names

    def export(self, path: str = "UserLib/lib"):
        """
        将当前模块对象导出为 .pkl 文件。
        默认保存到 UserLib/lib 目录下。
        """
        os.makedirs(path, exist_ok=True)
        file_path = os.path.join(path, f"{self.name}.pkl")
        with open(file_path, "wb") as f:
            pickle.dump(self, f)
        print(f"[✓] 模块 '{self.name}' 已导出到: {file_path}")

