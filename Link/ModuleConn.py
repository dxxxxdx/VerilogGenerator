class ModuleConn:
    """
    表示一个子模块的连接关系。
    包含实例名、模块对象、端口映射（结构式连接）。
    """

    def __init__(self, inst_name: str, module_name: str, port_map: dict[str, str]):
        self.inst_name = inst_name
        self.module_name = module_name
        self.port_map = port_map

    def __repr__(self):
        return f"<ModuleConn '{self.inst_name}' ports: {self.port_map}>"

