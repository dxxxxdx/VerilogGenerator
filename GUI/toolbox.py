import tkinter as tk
from GUI.Canvas import GridCanvas
from UserLib.LibManager import LibManager


class Toolbox(tk.Frame):
    def __init__(self, master, canvas: GridCanvas):
        super().__init__(master, bd=2, relief=tk.GROOVE, width=200)
        self.component_list = None
        self.canvas = canvas  # 画布引用，用于回调操作
        self.selected_component = tk.StringVar()
        self.lib_manager = LibManager.get_instance("UserLib/lib")
        self.lib_manager.load_all_modules()
        self.module_names = list(self.lib_manager.instances.keys())
        self.build_ui()
        self.register_callbacks()

    def build_ui(self):
        tk.Label(self, text="元件库", font=("Arial", 14)).pack(pady=5)

        self.component_list = tk.Listbox(self, height=10)
        # 用 LibManager 的模块名填充元件库
        for item in self.module_names:
            self.component_list.insert(tk.END, item)
        self.component_list.pack(pady=5)

        self.place_button = tk.Button(self, text="放置元件")
        self.place_button.pack(pady=10)

        tk.Label(self, text="工具", font=("Arial", 14)).pack(pady=5)
        self.connect_button = tk.Button(self, text="连接模式")
        self.connect_button.pack(pady=2)

        self.delete_button = tk.Button(self, text="删除模式")
        self.delete_button.pack(pady=2)

    def register_callbacks(self):
        self.place_button.config(command=self.place_selected_component)
        self.connect_button.config(command=self.activate_connect_mode)
        self.delete_button.config(command=self.activate_delete_mode)

    def place_selected_component(self):
        try:
            selected = self.component_list.get(tk.ACTIVE)
        except tk.TclError:
            selected = None
        if not selected:
            print("[✗] 请先从元件库选择一个元件")
            return
        # 获取模块对象
        module = self.lib_manager.get(selected)
        if not module:
            print(f"[✗] 未找到模块: {selected}")
            return
        # 自动设置模块大小和引脚
        pin_count = len(getattr(module, "pins", []))
        grid_w = max(pin_count, 2)
        grid_h = 1
        pins = []
        # 按引脚顺序分布在模块左右两侧
        for idx, pin in enumerate(module.pins):
            # 左侧 input，右侧 output
            if getattr(pin, "direction", "input") == "input":
                px = self.canvas.snap_to_grid(0, 0)[0]
                py = self.canvas.snap_to_grid(0, idx * self.canvas.cell_size)[1]
            else:
                px = self.canvas.snap_to_grid(grid_w * self.canvas.cell_size, 0)[0]
                py = self.canvas.snap_to_grid(0, idx * self.canvas.cell_size)[1]
            pins.append({
                "name": getattr(pin, "name", f"pin{idx+1}"),
                "type": getattr(pin, "direction", "input"),
                "pos": (px, py)
            })
        # 告诉 canvas 进入放置模式，并传递模块名、大小、引脚信息
        self.canvas.set_mode("place", {
            "name": selected,
            "grid_w": grid_w,
            "grid_h": grid_h,
            "pins": pins
        })
        print(f"[✓] 选择放置元件: {selected}，宽度={grid_w}，引脚数={pin_count}")

    def activate_connect_mode(self):
        self.canvas.set_mode("connect", None)
        print("[✓] 进入连接模式")

    def activate_delete_mode(self):
        self.canvas.set_mode("delete", None)
        print("[✓] 进入删除模式")
