from UserLib.LibManager import LibManager
import os
from typing import Any


def _ensure_semicolon(s: str) -> str:
    s = s.rstrip()
    return s if s.endswith(";") else s + ";"


def generate_verilog(module: Any, path: str = "Verilogs/UserVerilog") -> str:
    """
    生成模块的 Verilog 文件，返回生成的文件路径。
    对 module 的结构做了容错处理：检测 pins、submodules、conn.port_map 等属性是否存在。
    """
    if module is None:
        raise ValueError("module 不能为空")

    os.makedirs(path, exist_ok=True)

    lines = []

    # 模块头
    mod_name = getattr(module, "name", "unnamed_module")
    lines.append(f"module {mod_name} (")

    port_pins = []
    for pin in getattr(module, "pins", []) or []:
        direction = getattr(pin, "direction", None)
        if direction in ("input", "output", "inout"):
            port_pins.append(pin)

    for i, pin in enumerate(port_pins):
        if hasattr(pin, "declaration"):
            decl = pin.declaration()
        else:
            # 降级：尽量输出有方向和名字的声明
            decl = f"{getattr(pin, 'direction', 'wire')} {getattr(pin, 'name', 'sig')}"
        comma = "," if i < len(port_pins) - 1 else ""
        lines.append(f"    {decl}{comma}")
    lines.append(");")
    lines.append("")

    # 内部信号（不是端口的 pin）
    internal_wires = [pin for pin in getattr(module, "pins", []) or [] if getattr(pin, "direction", None) not in ("input", "output", "inout")]
    for wire in internal_wires:
        if hasattr(wire, "declaration"):
            decl = wire.declaration()
        else:
            decl = f"wire {getattr(wire,'name','w')}"
        lines.append(f"    {_ensure_semicolon(decl)}")
    if internal_wires:
        lines.append("")

    # 子模块实例化（兼容不同长度的元组/列表）
    for item in getattr(module, "submodules", []) or []:
        # 支持 (inst_name, submod, conn) / (inst_name, submod) / 其他可迭代结构
        try:
            if isinstance(item, (tuple, list)) and len(item) >= 2:
                inst_name, submod = item[0], item[1]
                conn = item[2] if len(item) >= 3 else None
            else:
                # 非常规项，尝试索引
                inst_name = getattr(item, "inst_name", None) or getattr(item, 0, None)
                submod = getattr(item, "submodule", None) or getattr(item, 1, None)
                conn = getattr(item, "conn", None) or getattr(item, 2, None)
        except Exception:
            continue

        if not submod:
            continue

        port_map_items = []
        if conn and hasattr(conn, "port_map") and isinstance(getattr(conn, "port_map"), dict):
            # 稳定排序输出，便于 diff
            for port, sig in sorted(conn.port_map.items()):
                port_map_items.append(f".{port}({sig})")

        port_map_text = ", ".join(port_map_items) if port_map_items else ""
        if port_map_text:
            lines.append(f"    {getattr(submod, 'name', 'submod')} {inst_name} ({port_map_text});")
        else:
            lines.append(f"    {getattr(submod, 'name', 'submod')} {inst_name} ();")

    # 逻辑语句
    for stmt in getattr(module, "logic", []) or []:
        lines.append(f"    {stmt}")
    if getattr(module, "logic", []):
        lines.append("")

    lines.append("endmodule")

    file_path = os.path.join(path, f"{mod_name}.v")
    with open(file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines))

    print(f"[✓] Verilog 文件已生成: {file_path}")
    return file_path
