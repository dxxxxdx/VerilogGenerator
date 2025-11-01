from ModuleClass.BasicModule import BasicModule
from Link.Pin import Pin
import os
import pickle

def create_and_module(export_path: str = "UserLib/lib"):
    m = BasicModule("and_gate")
    m.add_pin(Pin("a", "input"))
    m.add_pin(Pin("b", "input"))
    m.add_pin(Pin("y", "output"))
    m.add_logic("assign y = a & b;")
    m.export(export_path)

    saved = os.path.join(export_path, "and_gate.pkl")
    print(f"[✓] 已保存: {saved}")

    # 验证读取
    with open(saved, "rb") as f:
        loaded = pickle.load(f)
    print("[✓] 读取验证 -> 模块名:", getattr(loaded, "name", None),
          "端口:", [getattr(p, "name", None) for p in getattr(loaded, "pins", [])])
    return saved

def create_basic_gates(export_path: str = "UserLib/lib"):
    gates = [
        {
            "name": "and_gate",
            "pins": [Pin("a", "input"), Pin("b", "input"), Pin("y", "output")],
            "logic": ["assign y = a & b;"]
        },
        {
            "name": "or_gate",
            "pins": [Pin("a", "input"), Pin("b", "input"), Pin("y", "output")],
            "logic": ["assign y = a | b;"]
        },
        {
            "name": "not_gate",
            "pins": [Pin("a", "input"), Pin("y", "output")],
            "logic": ["assign y = ~a;"]
        },
        {
            "name": "xor_gate",
            "pins": [Pin("a", "input"), Pin("b", "input"), Pin("y", "output")],
            "logic": ["assign y = a ^ b;"]
        },
        {
            "name": "nand_gate",
            "pins": [Pin("a", "input"), Pin("b", "input"), Pin("y", "output")],
            "logic": ["assign y = ~(a & b);"]
        },
        {
            "name": "nor_gate",
            "pins": [Pin("a", "input"), Pin("b", "input"), Pin("y", "output")],
            "logic": ["assign y = ~(a | b);"]
        }
    ]
    os.makedirs(export_path, exist_ok=True)
    for gate in gates:
        m = BasicModule(gate["name"])
        for pin in gate["pins"]:
            m.add_pin(pin)
        for line in gate["logic"]:
            m.add_logic(line)
        m.export(export_path)
        print(f"[✓] 已创建并保存: {gate['name']}")

if __name__ == "__main__":

    create_basic_gates()
