from Link.ModuleConn import ModuleConn
from Link.Pin import Pin
from ModuleClass.basicModule import BasicModule
from UserLib.LibManager import LibManager
from Verilogs.VerilogGenerator import generate_verilog

def test_xor_gate():
    # 初始化 xor_gate 模块
    xor_mod = BasicModule("xor_gate")

    # 添加端口
    xor_mod.add_pin(Pin("a", "input", type_="wire"))
    xor_mod.add_pin(Pin("b", "input", type_="wire"))
    xor_mod.add_pin(Pin("y", "output", type_="wire"))

    # 添加中间信号线（作为无方向 Pin）
    xor_mod.add_pin(Pin("or_out", direction=None, type_="wire"))
    xor_mod.add_pin(Pin("and_out", direction=None, type_="wire"))

    # 加载子模块
    lib = LibManager("UserLib/lib")
    lib.load_all_modules()

    or_gate = lib.get("or_gate")
    and_gate = lib.get("and_gate")

    # 拼贴子模块（三元组：实例名、模块对象、连接结构）
    xor_mod.submodules.append((
        "u_or",
        or_gate,
        ModuleConn("u_or", "or_gate", {
            "a": "a",
            "b": "b",
            "y": "or_out"
        })
    ))

    xor_mod.submodules.append((
        "u_and",
        and_gate,
        ModuleConn("u_and", "and_gate", {
            "a": "a",
            "b": "b",
            "y": "and_out"
        })
    ))

    # 添加最终输出逻辑
    xor_mod.add_logic("assign y = or_out & ~and_out;")

    # 导出 Verilog 文件
    generate_verilog(xor_mod)

if __name__ == "__main__":
    test_xor_gate()