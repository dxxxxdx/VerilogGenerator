import os
import tkinter as tk
from tkinter import ttk, filedialog

from GUI.module_window import Window
from ModuleClass.BasicModule import BasicModule
from UserLib.LibManager import LibManager
import sys
sys.path.append("C:\\Users\\zys\\PycharmProjects\\VerilogGen")


class Enter(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("模块浏览器")
        self.geometry("600x200")

        self.lib_path = "C:\\Users\\zys\\PycharmProjects\\VerilogGen\\UserLib\\lib"
        self.L = LibManager(self.lib_path)
        self.tar_module = None

        all_module = self.L.load_all_modules()
        i = 0
        if all_module:
            for module in all_module:
                if isinstance(module, BasicModule):
                    btn = tk.Button(self, text=module.name, command=lambda m=module: Window(m))
                    btn.pack(side=tk.LEFT, padx=5, pady=5)
                    i += 1
                if i >= 5:
                    break

        def browse_file():
            file_path = filedialog.askopenfilename(
                title="选择一个文件",
                filetypes=[("pkl文件", "*.pkl")]
            )
            if file_path:
                self.L.load_module(file_path)
                module_name = os.path.splitext(os.path.basename(file_path))[0]
                self.tar_module = self.L.get(module_name)
                if self.tar_module:
                    Window(self.tar_module)

        browse_btn = tk.Button(self, text="浏览文件", command=browse_file)
        browse_btn.pack(pady=10)


if __name__ == "__main__":
    app = Enter()
    app.mainloop()



