from UserLib.LibManager import LibManager


def generate_verilog(module, path="Verilogs/UserVerilog"):
    import os
    os.makedirs(path, exist_ok=True)

    lines = []

    # 模块头：标准格式，逐行列出 input/output/inout
    lines.append(f"module {module.name} (")
    port_pins = [pin for pin in module.pins if pin.direction in ("input", "output", "inout")]
    for i, pin in enumerate(port_pins):
        comma = "," if i < len(port_pins) - 1 else ""
        lines.append(f"    {pin.declaration()}{comma}")
    lines.append(");")
    lines.append("")

    # 中间信号声明：非 input/output/inout 的 Pin 视为内部 wire
    internal_wires = [pin for pin in module.pins if pin.direction not in ("input", "output", "inout")]
    for wire in internal_wires:
        lines.append(f"    {wire.declaration()}")
    if internal_wires:
        lines.append("")

    for inst_name, submod, conn in module.submodules:
        # submod 是 BasicModule 对象，conn 是 ModuleConn 对象
        port_map = [f".{port}({signal})" for port, signal in conn.port_map.items()]
        lines.append(f"    {submod.name} {inst_name}({', '.join(port_map)});")

    # 逻辑语句
    for stmt in module.logic:
        lines.append(f"    {stmt}")
    if module.logic:
        lines.append("")

    lines.append("endmodule")

    # 写入文件
    file_path = os.path.join(path, f"{module.name}.v")
    with open(file_path, "w") as f:
        f.write("\n".join(lines))

    print(f"[✓] Verilog 文件已生成: {file_path}")
