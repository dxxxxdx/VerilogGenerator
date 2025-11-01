import tkinter as tk

def next_uuid():
    if not hasattr(next_uuid, "counter"):
        next_uuid.counter = 1001
    val = next_uuid.counter
    next_uuid.counter += 1
    return val

class ModuleItem:
    def __init__(self, canvas, name, x, y, grid_w=2, grid_h=1, pins=None):
        self.canvas = canvas
        self.name = name
        self.grid_w = grid_w
        self.grid_h = grid_h
        self.width = grid_w * canvas.cell_size
        self.height = grid_h * canvas.cell_size
        self.x = x
        self.y = y
        self.uuid = next_uuid()
        self.rect = canvas.create_rectangle(x, y, x+self.width, y+self.height, fill="#e0e0ff", outline="blue", width=2)
        self.text = canvas.create_text(x+self.width//2, y+self.height//2, text=name)
        # pin_defs: { name: {"type": "input"/"output", "pos": (x,y)} }
        self.pin_defs = {}
        self.pins = {}  # maps name -> canvas item id
        self.selected = False
        # 默认引脚配置（落在方格顶点）
        if pins is None:
            pins = [
                {"name": "left", "type": "input", "pos": (x, y+self.height//2)},
                {"name": "right", "type": "output", "pos": (x+self.width, y+self.height//2)}
            ]
        # normalize pins and create visuals
        self.set_pins(pins)

    def set_pins(self, pins):
        # 接受 pins: [{"name": str, "type": str, "pos": (x,y)}]
        # 更新 pin_defs（使用吸附后的绝对坐标），并在画布上创建对应的 oval
        # 清除旧引脚画布元素（若存在）
        for pin_id in list(self.pins.values()):
            try:
                self.canvas.delete(pin_id)
            except Exception:
                pass
        self.pins.clear()
        self.pin_defs.clear()
        for pin in pins:
            px, py = self.canvas.snap_to_grid(*pin["pos"])
            ptype = pin.get("type", "input")
            pname = pin.get("name", f"pin{len(self.pin_defs)+1}")
            self.pin_defs[pname] = {"type": ptype, "pos": (px, py)}
            color = "red" if ptype == "input" else "green"
            pin_id = self.canvas.create_oval(px-6, py-6, px+6, py+6, fill=color, outline="")
            self.pins[pname] = pin_id

    def configure(self, name=None, grid_w=None, grid_h=None, pins=None):
        if name:
            self.name = name
            self.canvas.itemconfig(self.text, text=name)
        if grid_w and grid_h:
            self.grid_w = grid_w
            self.grid_h = grid_h
            self.width = grid_w * self.canvas.cell_size
            self.height = grid_h * self.canvas.cell_size
            self.canvas.coords(self.rect, self.x, self.y, self.x+self.width, self.y+self.height)
            self.canvas.coords(self.text, self.x+self.width//2, self.y+self.height//2)
        if pins:
            # pins positions expected absolute; snap them
            for pin in pins:
                pin["pos"] = self.canvas.snap_to_grid(*pin["pos"])
            self.set_pins(pins)

    def contains(self, px, py):
        return self.x <= px <= self.x+self.width and self.y <= py <= self.y+self.height

    def move(self, dx, dy):
        # 移动图形并同步更新 pin_defs 的绝对坐标
        self.x += dx
        self.y += dy
        self.canvas.move(self.rect, dx, dy)
        self.canvas.move(self.text, dx, dy)
        for pin_id in self.pins.values():
            self.canvas.move(pin_id, dx, dy)
        # 更新 pin_defs 位置
        for pname, info in self.pin_defs.items():
            px, py = info["pos"]
            self.pin_defs[pname]["pos"] = (px + dx, py + dy)

    def get_pin_pos(self, pin_name):
        info = self.pin_defs.get(pin_name)
        if info:
            return self.canvas.snap_to_grid(*info["pos"])
        # fallback: center
        return self.canvas.snap_to_grid(self.x + self.width//2, self.y + self.height//2)

class LineItem:
    def __init__(self, canvas, nodes):
        self.canvas = canvas
        # 只注册唯一节点并吸附到网格顶点
        unique_nodes = []
        for node in nodes:
            snapped = canvas.snap_to_grid(*node)
            if snapped not in unique_nodes:
                unique_nodes.append(snapped)
        self.nodes = unique_nodes  # list of (x,y)
        self.uuid = next_uuid()
        self.line_id = None
        print(f"[✓] 创建线段 uuid={self.uuid}, 节点={self.nodes}")
        self.draw()

    def draw(self):
        # 使用当前 nodes 绘制折线，确保坐标为整数，且至少两个点
        coords = []
        for x, y in self.nodes:
            coords.extend([int(x), int(y)])
        if len(coords) < 4:
            print(f"[!] LineItem.draw: 节点数不足，无法绘制线 uuid={self.uuid}, coords={coords}")
            return
        # 如果之前的 line_id 已被删除（refresh/delete("all")）则强制重新创建
        if self.line_id:
            try:
                # 若 line_id 对应的 item 已被删除，coords 会抛异常或无效；尝试使用 coords 检测
                self.canvas.coords(self.line_id, *coords)
                print(f"[✓] 更新线 uuid={self.uuid}, coords={coords}, line_id={self.line_id}")
                return
            except Exception:
                self.line_id = None
        # 创建新线
        self.line_id = self.canvas.create_line(*coords, fill="black", width=3, tags="line")
        print(f"[✓] 新建线 uuid={self.uuid}, coords={coords}, line_id={self.line_id}")

    def contains_point(self, x, y):
        # 判断点是否在任意线段附近（矩形判定）
        for i in range(len(self.nodes)-1):
            x0, y0 = self.nodes[i]
            x1, y1 = self.nodes[i+1]
            min_x, max_x = min(x0, x1)-5, max(x0, x1)+5
            min_y, max_y = min(y0, y1)-5, max(y0, y1)+5
            if min_x <= x <= max_x and min_y <= y <= max_y:
                return True
        return False

    def add_node(self, x, y):
        snapped = self.canvas.snap_to_grid(x, y)
        if snapped not in self.nodes:
            self.nodes.append(snapped)
            self.draw()
            print(f"[✓] 线 uuid={self.uuid} 增加节点 {snapped}")
        else:
            print(f"[!] 节点 {snapped} 已存在于线 uuid={self.uuid}，不重复添加")

    def export(self):
        return {
            "uuid": self.uuid,
            "nodes": self.nodes
        }

class GridCanvas(tk.Canvas):
    def __init__(self, master, grid_width=20, grid_height=15, cell_size=40, export_callback=None):
        self.grid_width = grid_width
        self.grid_height = grid_height
        self.cell_size = cell_size
        canvas_width = grid_width * cell_size
        canvas_height = grid_height * cell_size
        super().__init__(master, bg="white", width=canvas_width, height=canvas_height)
        self.grid_matrix = [[None for _ in range(grid_width)] for _ in range(grid_height)]
        self.draw_grid()
        self.modules = []
        self.lines = []  # LineItem 实例列表
        self.dragging_module = None
        self.drag_offset = (0, 0)
        self.line_start = None
        self.temp_line = None
        self.export_callback = export_callback
        self.mode = "normal"
        self.place_component = None
        self.selected_line = None
        self._temp_nodes = []
        self._first_node_marker = None  # 首节点可视化标记
        self.bind("<Button-1>", self.on_click)
        self.bind("<Double-1>", self.on_double_click)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<Button-3>", self.on_right_click)

    def draw_grid(self):
        for i in range(self.grid_width + 1):
            for j in range(self.grid_height + 1):
                x = i * self.cell_size
                y = j * self.cell_size
                size = 4
                self.create_line(x - size, y, x + size, y, fill="#aaa")
                self.create_line(x, y - size, x, y + size, fill="#aaa")
        x0 = 4
        y0 = 4
        x1 = self.grid_width * self.cell_size
        y1 = self.grid_height * self.cell_size
        self.create_rectangle(x0, y0, x1, y1, outline="black", width=2)

    def snap_to_grid(self, x, y):
        gx = round(x / self.cell_size) * self.cell_size
        gy = round(y / self.cell_size) * self.cell_size
        return gx, gy

    def set_mode(self, mode, component=None):
        self.mode = mode
        self.place_component = component
        self.selected_line = None
        self._temp_nodes = []
        # 清除临时视觉元素
        if self.temp_line:
            try:
                self.delete(self.temp_line)
            except Exception:
                pass
            self.temp_line = None
        if self._first_node_marker:
            try:
                self.delete(self._first_node_marker)
            except Exception:
                pass
            self._first_node_marker = None
        print(f"[✓] 画布模式切换为: {mode}, 元件: {component}")

    def add_module(self, name, x, y, grid_w=2, grid_h=1, pins=None):
        x, y = self.snap_to_grid(x, y)
        # 支持从 toolbox 传递 dict 参数
        if isinstance(name, dict):
            info = name
            name = info.get("name", "Module")
            grid_w = info.get("grid_w", 2)
            grid_h = info.get("grid_h", 1)
            pins = info.get("pins", None)
        # 若未指定引脚，则生成默认引脚（左右中点）
        if pins is None:
            pins = [
                {"name": "left", "type": "input", "pos": (x, y + (grid_h * self.cell_size)//2)},
                {"name": "right", "type": "output", "pos": (x + grid_w * self.cell_size, y + (grid_h * self.cell_size)//2)}
            ]
        else:
            for pin in pins:
                pin["pos"] = self.snap_to_grid(*pin["pos"])
        mod = ModuleItem(self, name, x, y, grid_w, grid_h, pins=pins)
        self.modules.append(mod)
        return mod

    def clear(self):
        self.delete("all")
        self.draw_grid()
        self.modules.clear()
        self.lines.clear()
        self._temp_nodes = []
        self._first_node_marker = None

    def export_connections(self):
        data = self.get_modules_and_connections()
        if self.export_callback:
            self.export_callback(data)
        return data

    def on_click(self, event):
        if self.mode == "place" and self.place_component:
            x, y = self.snap_to_grid(event.x, event.y)
            self.add_module(self.place_component, x, y)
            self.set_mode("normal")
            return
        elif self.mode == "delete":
            # 删除模块（以及相关连线）
            for mod in reversed(self.modules):
                if mod.contains(event.x, event.y):
                    # 删除与该模块相关的线（若线的任意节点等于模块任意引脚位置）
                    mod_pin_positions = set([self.snap_to_grid(*info["pos"]) for info in mod.pin_defs.values()])
                    self.modules.remove(mod)
                    # 删除模块图形
                    try:
                        self.delete(mod.rect)
                        self.delete(mod.text)
                        for pin_id in mod.pins.values():
                            self.delete(pin_id)
                    except Exception:
                        pass
                    # 过滤相关线
                    remaining = []
                    for l in self.lines:
                        if any(node in mod_pin_positions for node in l.nodes):
                            # 删除线的画布元素
                            try:
                                if l.line_id:
                                    self.delete(l.line_id)
                            except Exception:
                                pass
                            print(f"[✓] 删除与模块 {mod.name} 相关的线 uuid={l.uuid}")
                        else:
                            remaining.append(l)
                    self.lines = remaining
                    self.redraw_lines()
                    return
            # 删除线（点击靠近线段）
            for idx, line in enumerate(list(self.lines)):
                if line.contains_point(event.x, event.y):
                    try:
                        if line.line_id:
                            self.delete(line.line_id)
                    except Exception:
                        pass
                    print(f"[✓] 删除线 uuid={line.uuid}")
                    self.lines.pop(idx)
                    self.redraw_lines()
                    return
            return
        elif self.mode == "connect":
            x, y = self.snap_to_grid(event.x, event.y)
            # 添加临时选点（可见）
            self._temp_nodes.append((x, y))
            if len(self._temp_nodes) == 1:
                if self._first_node_marker:
                    try:
                        self.delete(self._first_node_marker)
                    except Exception:
                        pass
                self._first_node_marker = self.create_oval(x-8, y-8, x+8, y+8, fill="orange", outline="orange", width=2, tags="first_node_marker")
            # 更新临时折线显示
            if len(self._temp_nodes) > 1:
                if self.temp_line:
                    try:
                        self.delete(self.temp_line)
                    except Exception:
                        pass
                coords = []
                for node in self._temp_nodes:
                    coords.extend(node)
                self.temp_line = self.create_line(*coords, fill="orange", dash=(4,2), width=2, tags="temp_line")
            return
        else:
            # normal 模式：拖动模块或通过引脚开始连接临时线（旧行为）
            for mod in reversed(self.modules):
                if mod.contains(event.x, event.y):
                    self.dragging_module = mod
                    self.drag_offset = (event.x - mod.x, event.y - mod.y)
                    return
            for mod in self.modules:
                for pin_name, pin_id in mod.pins.items():
                    coords = self.coords(pin_id)
                    if coords and coords[0] <= event.x <= coords[2] and coords[1] <= event.y <= coords[3]:
                        self.line_start = (mod, pin_name)
                        px, py = mod.get_pin_pos(pin_name)
                        if self.temp_line:
                            try:
                                self.delete(self.temp_line)
                            except Exception:
                                pass
                        self.temp_line = self.create_line(px, py, px, py, fill="orange", dash=(4,2), width=2, tags="temp_line")
                        return

    def on_double_click(self, event):
        if self.mode == "connect" and len(self._temp_nodes) >= 2:
            new_nodes = [self.snap_to_grid(*node) for node in self._temp_nodes]
            found = False
            # 若与已有线有交集，则扩充该线（避免创建重复线）
            for line in self.lines:
                if set(new_nodes).intersection(set(line.nodes)):
                    print(f"[!] 发现已有线与新节点有交集，扩充线 uuid={line.uuid}")
                    for node in new_nodes:
                        line.add_node(*node)
                    found = True
                    break
            if not found:
                line = LineItem(self, self._temp_nodes)
                self.lines.append(line)
            # 清理临时显示
            self.redraw_lines()
            self._temp_nodes = []
            if self.temp_line:
                try:
                    self.delete(self.temp_line)
                except Exception:
                    pass
                self.temp_line = None
            if self._first_node_marker:
                try:
                    self.delete(self._first_node_marker)
                except Exception:
                    pass
                self._first_node_marker = None

    def on_drag(self, event):
        if self.dragging_module:
            x, y = self.snap_to_grid(event.x, event.y)
            dx = x - self.dragging_module.x
            dy = y - self.dragging_module.y
            self.dragging_module.move(dx, dy)
            self.redraw_lines()
        elif self.line_start and self.temp_line:
            mod, pin_name = self.line_start
            x0, y0 = mod.get_pin_pos(pin_name)
            x1, y1 = self.snap_to_grid(event.x, event.y)
            try:
                self.coords(self.temp_line, x0, y0, x1, y1)
            except Exception:
                pass

    def on_release(self, event):
        if self.dragging_module:
            self.dragging_module = None
        elif self.temp_line:
            try:
                self.delete(self.temp_line)
            except Exception:
                pass
            self.temp_line = None

    def redraw_lines(self):
        # 删除所有现有带 tag "line" 的线条项（重新由 LineItem.draw 创建）
        for item in list(self.find_withtag("line")):
            try:
                self.delete(item)
            except Exception:
                pass
        # 强制每条 LineItem 重新创建 line_id，避免使用过期 id
        for line in self.lines:
            line.line_id = None
            line.draw()

    def on_right_click(self, event):
        if self.mode == "normal":
            x, y = self.snap_to_grid(event.x, event.y)
            self.add_module(f"Module{len(self.modules)+1}", x, y)

    def get_modules_and_connections(self):
        result = {
            "modules": [
                {
                    "uuid": m.uuid,
                    "name": m.name,
                    "x": m.x,
                    "y": m.y,
                    "grid_w": m.grid_w,
                    "grid_h": m.grid_h,
                    "pins": [
                        {"name": pin_name,
                         "type": info["type"],
                         "pos": self.snap_to_grid(*info["pos"])}
                        for pin_name, info in m.pin_defs.items()
                    ]
                }
                for m in self.modules
            ],
            "connections": [line.export() for line in self.lines]
        }
        return result

    def refresh(self):
        """刷新并重绘整个画布，包括网格、模块、引脚和线。"""
        # 删除所有，当重建模块和引脚时不要依赖旧 item id
        self.delete("all")
        self.draw_grid()
        # 重绘所有模块：重新创建 rect/text 并据 pin_defs 重建引脚
        for mod in self.modules:
            mod.rect = self.create_rectangle(mod.x, mod.y, mod.x+mod.width, mod.y+mod.height, fill="#e0e0ff", outline="blue", width=2)
            mod.text = self.create_text(mod.x+mod.width//2, mod.y+mod.height//2, text=mod.name)
            # 以 mod.pin_defs 为准重建引脚
            pins = []
            for pname, info in mod.pin_defs.items():
                pins.append({"name": pname, "type": info["type"], "pos": info["pos"]})
            mod.set_pins(pins)
        # 重绘所有线
        self.redraw_lines()


if __name__ == "__main__":
    def print_data(data):
        print("[✓] 当前模块与连线：", data)
    root = tk.Tk()
    root.geometry("1200x1000")
    app = GridCanvas(root, export_callback=print_data)
    app.pack()
    root.mainloop()