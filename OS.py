# Updated System Code (DarkoOS.py)

import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import os
import sys

# Import config
try:
    from config import user, passw, ram, disk_gb
except ImportError:
    messagebox.showerror("Error", "Config file not found. Please reinstall.")
    sys.exit(1)

class DarkoOS:
    def __init__(self, root):
        self.root = root
        self.root.title("DarkoOS Virtual Machine")
        self.root.geometry("1000x700")
        self.root.configure(bg="#050505")

        self.user = user
        self.password = passw
        self.ram = ram
        self.disk_gb = disk_gb
        self.disk_path = "v_disk"

        os.makedirs(self.disk_path, exist_ok=True)
        self.login_screen()

    # ---------- LOGIN ----------
    def login_screen(self):
        self.login_frame = tk.Frame(self.root, bg="#050505")
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(
            self.login_frame,
            text="DarkoOS",
            font=("Courier", 35, "bold"),
            fg="#00ADB5",
            bg="#050505"
        ).pack(pady=20)

        self.ent_pass = tk.Entry(
            self.login_frame,
            show="*",
            bg="#1A1A1A",
            fg="white",
            bd=0,
            font=("Arial", 14),
            insertbackground="white"
        )
        self.ent_pass.pack(pady=10, ipady=5)

        tk.Button(
            self.login_frame,
            text="UNLOCK",
            bg="#00ADB5",
            fg="black",
            bd=0,
            command=self.check_pass
        ).pack(ipadx=30, ipady=5)

    def check_pass(self):
        if self.ent_pass.get() == self.password:
            self.login_frame.destroy()
            self.boot_desktop()
        else:
            messagebox.showerror("Denied", "Wrong password")

    # ---------- DISK ----------
    def get_disk_usage(self):
        total = 0
        # Add system file size
        system_file = os.path.join(os.path.dirname(__file__), "DarkoOS.py")
        if os.path.exists(system_file):
            total += os.path.getsize(system_file)
        config_file = os.path.join(os.path.dirname(__file__), "config.py")
        if os.path.exists(config_file):
            total += os.path.getsize(config_file)
        for r, d, f in os.walk(self.disk_path):
            for file in f:
                total += os.path.getsize(os.path.join(r, file))
        return round(total / (1024 * 1024), 2)

    def get_disk_stats(self):
        used = self.get_disk_usage()
        total = self.disk_gb * 1024
        free = total - used
        return used, free, total

    # ---------- DESKTOP ----------
    def boot_desktop(self):
        self.top = tk.Frame(self.root, bg="#1A1A1A", height=35)
        self.top.pack(fill="x")

        self.info = tk.Label(
            self.top,
            bg="#1A1A1A",
            fg="#00ADB5",
            font=("Consolas", 10)
        )
        self.info.pack(side="left", padx=10)
        self.update_stats()

        self.desk = tk.Frame(self.root, bg="#050505")
        self.desk.pack(fill="both", expand=True)

        tk.Button(
            self.desk, text="📁 Explorer",
            bg="#1A1A1A", fg="white", bd=0,
            command=self.open_explorer
        ).place(x=30, y=30)

        tk.Button(
            self.desk, text="🖥 Terminal",
            bg="#1A1A1A", fg="white", bd=0,
            command=self.open_terminal
        ).place(x=30, y=80)

        tk.Button(
            self.desk, text="🧮 Calculator",
            bg="#1A1A1A", fg="white", bd=0,
            command=self.open_calculator
        ).place(x=30, y=130)

        # Desktop context menu
        ctx = tk.Menu(self.desk, tearoff=0)
        ctx.add_command(label="New Folder", command=lambda: self.create_io("dir", None, self.disk_path))
        ctx.add_command(label="New Text File", command=lambda: self.create_io("file", None, self.disk_path))

        def popup(e):
            try:
                ctx.tk_popup(e.x_root, e.y_root)
            finally:
                ctx.grab_release()

        self.desk.bind("<Button-3>", popup)

    def update_stats(self):
        used, free, total = self.get_disk_stats()
        self.info.config(
            text=f"USER: {self.user} | RAM: {self.ram} MB | "
                 f"STORAGE: {used} / {total} MB (Free {free} MB)"
        )
        self.root.after(3000, self.update_stats)

    # ---------- EXPLORER ----------
    def open_explorer(self, current_dir=None):
        if current_dir is None:
            current_dir = self.disk_path

        exp = tk.Toplevel(self.root)
        exp.title("Explorer - " + current_dir)
        exp.geometry("750x500")
        exp.configure(bg="#1A1A1A")

        used, free, total = self.get_disk_stats()
        tk.Label(
            exp,
            text=f"Used: {used} MB | Free: {free} MB | Total: {total} MB",
            bg="#1A1A1A",
            fg="#00ADB5",
            font=("Consolas", 10)
        ).pack(fill="x")

        self.ex_list = tk.Listbox(
            exp,
            bg="#0A0A0A",
            fg="white",
            font=("Consolas", 11),
            bd=0
        )
        self.ex_list.pack(fill="both", expand=True, padx=10, pady=10)

        def refresh():
            self.ex_list.delete(0, "end")
            if current_dir != self.disk_path:
                self.ex_list.insert("end", "📁 ..")
            for i in os.listdir(current_dir):
                path = os.path.join(current_dir, i)
                if os.path.isdir(path):
                    icon = "📁 "
                elif i.endswith(".drk"):
                    icon = "⚙ "
                else:
                    icon = "📄 "
                self.ex_list.insert("end", icon + i)

        ctx = tk.Menu(exp, tearoff=0)
        ctx.add_command(label="New Folder", command=lambda: self.create_io("dir", refresh, current_dir))
        ctx.add_command(label="New Text File", command=lambda: self.create_io("file", refresh, current_dir))
        ctx.add_separator()
        ctx.add_command(label="Delete", command=lambda: self.delete_io(refresh, current_dir))
        ctx.add_command(label="Rename", command=lambda: self.rename_io(refresh, current_dir))

        def popup(e):
            ctx.tk_popup(e.x_root, e.y_root)
            ctx.grab_release()

        self.ex_list.bind("<Button-3>", popup)
        self.ex_list.bind("<Double-1>", lambda e: self.open_item(refresh, current_dir))

        refresh()

    def create_io(self, t, cb, current_dir):
        name = simpledialog.askstring("Name", "Enter name:")
        if not name:
            return
        path = os.path.join(current_dir, name)
        if t == "dir":
            os.mkdir(path)
        else:
            with open(path + ".txt", "w", encoding="utf-8") as f:
                f.write("")
        if cb:
            cb()

    def delete_io(self, cb, current_dir):
        sel = self.ex_list.get(tk.ACTIVE)
        if not sel or sel == "📁 ..":
            return
        name = sel[2:]
        path = os.path.join(current_dir, name)
        if messagebox.askyesno("Confirm", f"Delete {name}?"):
            if os.path.isdir(path):
                os.rmdir(path)
            else:
                os.remove(path)
            cb()

    def rename_io(self, cb, current_dir):
        sel = self.ex_list.get(tk.ACTIVE)
        if not sel or sel == "📁 ..":
            return
        old_name = sel[2:]
        old_path = os.path.join(current_dir, old_name)
        new_name = simpledialog.askstring("Rename", "Enter new name:", initialvalue=old_name)
        if not new_name or new_name == old_name:
            return
        new_path = os.path.join(current_dir, new_name)
        os.rename(old_path, new_path)
        cb()

    def open_item(self, cb, current_dir):
        sel = self.ex_list.get(tk.ACTIVE)
        if not sel:
            return
        if sel == "📁 ..":
            parent_dir = os.path.dirname(current_dir)
            cb()
            self.open_explorer(parent_dir)
            return
        name = sel[2:]
        path = os.path.join(current_dir, name)
        if "📁" in sel:
            self.open_explorer(path)
        elif "⚙" in sel:
            prog = name[:-4]
            if prog == "cmd":
                self.open_terminal()
            elif prog == "explorer":
                self.open_explorer()
            elif prog == "calculator":
                self.open_calculator()
            else:
                self.open_file_from_terminal(path)
        else:
            self.open_file_from_terminal(path)

    # ---------- TERMINAL ----------
    def open_terminal(self):
        win = tk.Toplevel(self.root)
        win.title("Terminal")
        win.geometry("650x450")

        out = scrolledtext.ScrolledText(
            win, bg="black", fg="#00FF00",
            font=("Consolas", 10), insertbackground="white"
        )
        out.pack(fill="both", expand=True)

        out.insert("end", "DarkoOS Terminal\nType help\n> ")

        def cmd(event=None):
            line = out.get("end-2l", "end").replace("> ", "").strip()
            args = line.split()

            if not args:
                out.insert("end", "> ")
                return "break"

            c = args[0].lower()

            if c == "help":
                out.insert("end",
                    "help\nprint <text>\ndir\nstart <file>\nclear\n"
                    "mkdir <name>\ntouch <name>\nrm <name>\n"
                    "calc <expression>\n"
                )
            elif c == "print" or c == "echo":
                out.insert("end", " ".join(args[1:]) + "\n")
            elif c == "dir" or c == "ls":
                for f in os.listdir(self.disk_path):
                    out.insert("end", f + "\n")
            elif c == "clear" or c == "cls":
                out.delete("1.0", "end")
                out.insert("end", "> ")
            elif c == "start" and len(args) > 1:
                path = os.path.join(self.disk_path, args[1])
                if os.path.exists(path):
                    if os.path.isdir(path):
                        out.insert("end", "Cannot start directory\n")
                    elif path.endswith(".drk"):
                        prog = os.path.basename(path)[:-4]
                        if prog == "cmd":
                            self.open_terminal()
                        elif prog == "explorer":
                            self.open_explorer()
                        elif prog == "calculator":
                            self.open_calculator()
                        else:
                            self.open_file_from_terminal(path)
                    else:
                        self.open_file_from_terminal(path)
                else:
                    out.insert("end", "File not found\n")
            elif c == "mkdir" and len(args) > 1:
                os.mkdir(os.path.join(self.disk_path, args[1]))
                out.insert("end", "Folder created\n")
            elif c == "touch" and len(args) > 1:
                open(os.path.join(self.disk_path, args[1]), "w").close()
                out.insert("end", "File created\n")
            elif c == "rm" and len(args) > 1:
                path = os.path.join(self.disk_path, args[1])
                if os.path.exists(path):
                    if os.path.isdir(path):
                        os.rmdir(path)
                    else:
                        os.remove(path)
                    out.insert("end", "Deleted\n")
                else:
                    out.insert("end", "Not found\n")
            elif c == "calc" and len(args) > 1:
                expression = " ".join(args[1:])
                try:
                    result = eval(expression)
                    out.insert("end", f"{result}\n")
                except Exception as e:
                    out.insert("end", f"Error: {e}\n")
            else:
                out.insert("end", "Unknown command\n")

            out.insert("end", "> ")
            out.see("end")
            return "break"

        out.bind("<Return>", cmd)

    # ---------- CALCULATOR ----------
    def open_calculator(self):
        calc = tk.Toplevel(self.root)
        calc.title("Calculator")
        calc.geometry("300x400")
        calc.configure(bg="#1A1A1A")

        self.calc_entry = tk.Entry(calc, bg="#0A0A0A", fg="white", font=("Arial", 20), bd=0, justify="right")
        self.calc_entry.pack(fill="x", padx=10, pady=10)

        buttons_frame = tk.Frame(calc, bg="#1A1A1A")
        buttons_frame.pack()

        buttons = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2), ('/', 1, 3),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2), ('*', 2, 3),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2), ('-', 3, 3),
            ('0', 4, 0), ('.', 4, 1), ('=', 4, 2), ('+', 4, 3),
        ]

        for (text, row, col) in buttons:
            tk.Button(buttons_frame, text=text, bg="#00ADB5", fg="black", font=("Arial", 16), bd=0,
                      command=lambda t=text: self.calc_button(t)).grid(row=row, column=col, ipadx=20, ipady=20)

        tk.Button(buttons_frame, text="C", bg="#630000", fg="white", font=("Arial", 16), bd=0,
                  command=self.calc_clear).grid(row=0, column=0, columnspan=4, sticky="we", ipadx=20, ipady=10)

    def calc_button(self, text):
        if text == "=":
            try:
                result = str(eval(self.calc_entry.get()))
                self.calc_entry.delete(0, tk.END)
                self.calc_entry.insert(tk.END, result)
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self.calc_entry.insert(tk.END, text)

    def calc_clear(self):
        self.calc_entry.delete(0, tk.END)

    def open_file_from_terminal(self, path):
        win = tk.Toplevel(self.root)
        win.title(os.path.basename(path))

        area = scrolledtext.ScrolledText(
            win, bg="#0F0F0F", fg="white",
            font=("Consolas", 11)
        )
        area.pack(fill="both", expand=True)

        with open(path, "r", encoding="utf-8") as f:
            area.insert("1.0", f.read())

        tk.Button(
            win, text="SAVE",
            bg="#00ADB5", fg="black",
            command=lambda: self.save_file(path, area.get("1.0", "end-1c"))
        ).pack(fill="x")

    def save_file(self, path, content):
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        messagebox.showinfo("DarkoOS", "Saved")


if __name__ == "__main__":
    root = tk.Tk()
    DarkoOS(root)
    root.mainloop()
