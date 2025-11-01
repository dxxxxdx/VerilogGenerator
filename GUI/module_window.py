import tkinter as tk
import GUI.Canvas as Canvas
from GUI.toolbox import Toolbox
from ModuleClass.BasicModule import BasicModule


class Window(tk.Toplevel):
    def __init__(self, module: BasicModule | None):
        # 确保至少有一个 root 存在（若从独立运行调用）
        if not tk._default_root:
            root = tk.Tk()
            root.withdraw()
        super().__init__()
        self.title("Verilog 拼贴系统")
        self.geometry("1000x700")
        self.module = module

        # 画布（右侧），传递回调
        self.canvas = Canvas.GridCanvas(self, grid_width=30, grid_height=20, cell_size=30, export_callback=self.on_export)
        self.canvas.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 工具栏（左侧）
        self.toolbox = Toolbox(self, self.canvas)
        self.toolbox.pack(side=tk.LEFT, fill=tk.Y)

        # 按钮区
        btn_frame = tk.Frame(self)
        btn_frame.pack(side=tk.BOTTOM, pady=10)
        tk.Button(btn_frame, text="添加模块", command=self.add_module_dialog).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="清空画布", command=self.canvas.clear).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="导出连接关系", command=self.canvas.export_connections).pack(side=tk.LEFT, padx=5)

        # 若传入模块，可以在此做额外初始化（例如加载已放置元件）
        if self.module:
            # 简单示例：将模块名显示在窗口标题
            self.title(f"Verilog 拼贴系统 - {getattr(self.module, 'name', 'unnamed')}")
        else:
            # 不销毁窗口，保留空画布以便调试
            print("[i] 未提供 module，打开空画布供调试")

        # 关闭时确保退出主循环（若作为独立脚本运行）
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def add_module_dialog(self):
        # 简单弹窗输入模块名
        dialog = tk.Toplevel(self)
        dialog.title("添加模块")
        tk.Label(dialog, text="模块名:").pack(side=tk.LEFT)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var).pack(side=tk.LEFT)

        def on_ok():
            name = name_var.get().strip()
            if name:
                self.canvas.add_module(name, 100, 100)
            dialog.destroy()

        tk.Button(dialog, text="确定", command=on_ok).pack(side=tk.LEFT)

    def on_export(self, data):
        # 导出回调，可扩展为保存文件等
        print("[✓] 当前模块与连线：", data)

    def on_close(self):
        # 销毁此窗口；如果没有其它窗口，退出主循环由 root 处理
        try:
            self.destroy()
        except Exception:
            pass


# 仅在直接运行此文件时启动一个可交互的测试窗口
if __name__ == "__main__":
    # 创建主 root，并显示一个子窗口（Window 是 Toplevel）
    root = tk.Tk()
    root.title("VerilogGen - 主窗口 (hidden for demo)")
    root.withdraw()  # 将主窗口隐藏，只展示 Toplevel

    # 构建一个简单的 BasicModule 供调试（不会持久化）
    test_mod = BasicModule("demo_module")
    # 可选：如果 BasicModule 有 pins/logic 接口，可在此添加示例
    try:
        if hasattr(test_mod, "add_pin"):
            # 仅在存在 Pin 类时调用（保持鲁棒）
            from Link.Pin import Pin  # noqa: E402
            test_mod.add_pin(Pin("a", "input"))
            test_mod.add_pin(Pin("b", "input"))
            test_mod.add_pin(Pin("y", "output"))
            if hasattr(test_mod, "add_logic"):
                test_mod.add_logic("assign y = a & b;")
    except Exception:
        pass

    win = Window(test_mod)
    win.focus_force()
    root.mainloop()
