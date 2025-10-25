class Pin:
    """
    表示一个 Verilog 端口（Pin），支持方向、类型、宽度、连接状态。
    """

    def __init__(self, name: str, direction: str, type_: str = 'wire', width: int = 1):
        """
        初始化 Pin。

        参数:
        - name: 端口名（如 'data'）
        - direction: 'input' 或 'output'
        - type_: Verilog 类型（默认 'wire'）
        - width: 位宽（默认 1）
        """
        self.name = name
        self.direction = direction
        self.type_ = type_
        self.width = width

    # Verilog declaration logic
    def declaration(self):
        if self.direction:
            return f"{self.direction} {self.type_} {self.name};"
        else:
            return f"{self.type_} {self.name};"

    def __repr__(self):
        width_note = f" [{self.width}bit]" if self.width > 1 else ""
        return f"<Pin {self.direction} {self.type_}{width_note} >"
