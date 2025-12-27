# Updated System Code (DarkoOS.py)

import tkinter as tk
from tkinter import messagebox, scrolledtext, simpledialog
import os
import sys
import urllib.request

try:
    from tkhtmlview import HTMLLabel
except ImportError:
    messagebox.showerror("Error", "tkhtmlview not found. Install with 'pip install tkhtmlview'")
    sys.exit(1)

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
        return round(total / (1024 * 1024), 2)  # in MB

    def get_disk_stats(self):
        used = self.get_disk_usage()  # MB
        total = self.disk_gb * 1024  # MB
        free = total - used
        used_gb = used / 1024
        free_gb = free / 1024
        total_gb = total / 1024
        return used_gb, free_gb, total_gb

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

        tk.Button(
            self.top, text="Shutdown",
            bg="#630000", fg="white", bd=0,
            command=self.root.destroy
        ).pack(side="right", padx=10)

        self.desk = tk.Frame(self.root, bg="#050505")
        self.desk.pack(fill="both", expand=True)

        # Default buttons
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

        tk.Button(
            self.desk, text="🌐 Browser",
            bg="#1A1A1A", fg="white", bd=0,
            command=self.open_browser
        ).place(x=30, y=180)

        # Desktop context menu
        self.desk_ctx = tk.Menu(self.desk, tearoff=0)
        self.desk_ctx.add_command(label="New Folder", command=lambda: self.create_io("dir", self.refresh_desktop, self.disk_path))
        self.desk_ctx.add_command(label="New Text File", command=lambda: self.create_io("file", self.refresh_desktop, self.disk_path))
        self.desk_ctx.add_separator()
        self.desk_ctx.add_command(label="Refresh", command=self.refresh_desktop)

        def popup(e):
            try:
                self.desk_ctx.tk_popup(e.x_root, e.y_root)
            finally:
                self.desk_ctx.grab_release()

        self.desk.bind("<Button-3>", popup)

        self.icons = []
        self.refresh_desktop()

    def refresh_desktop(self):
        # Clear existing icons except default buttons
        for icon in self.icons:
            icon.destroy()
        self.icons = []

        x, y = 150, 30  # Start position for custom icons
        for i in os.listdir(self.disk_path):
            path = os.path.join(self.disk_path, i)
            if os.path.isdir(path):
                icon_text = "📁 " + i
                cmd = lambda p=path: self.open_explorer(p)
            elif i.endswith(".drk"):
                icon_text = "⚙ " + i
                prog = i[:-4]
                if prog == "cmd":
                    cmd = self.open_terminal
                elif prog == "explorer":
                    cmd = self.open_explorer
                elif prog == "calculator":
                    cmd = self.open_calculator
                elif prog == "browser":
                    cmd = self.open_browser
                else:
                    cmd = lambda p=path: self.open_file_from_terminal(p)
            else:
                icon_text = "📄 " + i
                cmd = lambda p=path: self.open_file_from_terminal(p)

            btn = tk.Button(
                self.desk, text=icon_text,
                bg="#1A1A1A", fg="white", bd=0,
                command=cmd
            )
            btn.place(x=x, y=y)
            self.icons.append(btn)

            y += 50
            if y > 500:
                y = 30
                x += 150

    def update_stats(self):
        used, free, total = self.get_disk_stats()
        self.info.config(
            text=f"USER: {self.user} | RAM: {self.ram} MB | "
                 f"STORAGE: {used:.2f} / {total:.2f} GB (Free {free:.2f} GB)"
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

        used_gb, free_gb, total_gb = self.get_disk_stats()
        tk.Label(
            exp,
            text=f"Disk (virtual) C: {used_gb:.2f}GB / {total_gb:.2f}GB",
            bg="#1A1A1A",
            fg="#00ADB5",
            font=("Consolas", 10)
        ).pack(fill="x")

        tk.Label(
            exp,
            text=f"Free: {free_gb:.2f}GB",
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
        self.ex_list.bind("<Double-1>", lambda e: self.open_item(refresh, current_dir, exp))

        refresh()

    def create_io(self, t, cb, current_dir):
        name = simpledialog.askstring("Name", "Enter name:")
        if not name:
            return
        path = os.path.join(current_dir, name)
        if t == "dir":
            os.mkdir(path)
        else:
            open(path + ".txt", "w", encoding="utf-8").close()
        if cb:
            cb()
        if current_dir == self.disk_path:
            self.refresh_desktop()

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
        if current_dir == self.disk_path:
            self.refresh_desktop()

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
        if current_dir == self.disk_path:
            self.refresh_desktop()

    def open_item(self, cb, current_dir, exp):
        sel = self.ex_list.get(tk.ACTIVE)
        if not sel:
            return
        if sel == "📁 ..":
            parent_dir = os.path.dirname(current_dir)
            exp.destroy()
            self.open_explorer(parent_dir)
            return
        name = sel[2:]
        path = os.path.join(current_dir, name)
        if "📁" in sel:
            exp.destroy()
            self.open_explorer(path)
        elif "⚙" in sel:
            prog = name[:-4]
            if prog == "cmd":
                self.open_terminal()
            elif prog == "explorer":
                self.open_explorer()
            elif prog == "calculator":
                self.open_calculator()
            elif prog == "browser":
                self.open_browser()
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

        out.insert("end", "DarkoOS Terminal\nType 'help' for commands\n> ")

        self.terminal_history = []
        self.history_index = 0

        def cmd(event=None):
            line = out.get("end-2l linestart", "end").strip()[2:]  # Remove '> '
            if not line:
                out.insert("end", "> ")
                return "break"

            self.terminal_history.append(line)
            self.history_index = len(self.terminal_history)

            args = line.split()
            c = args[0].lower()

            if c == "help":
                out.insert("end", "\nAvailable commands:\n"
                                  "help - show this list\n"
                                  "echo <text> - print text\n"
                                  "dir - list files\n"
                                  "start <program> - start program (cmd, explorer, calculator, browser, file)\n"
                                  "clear - clear screen\n"
                                  "mkdir <name> - create folder\n"
                                  "touch <name> - create file\n"
                                  "rm <name> - delete file/folder\n"
                                  "calc <expression> - calculate\n"
                                  "exit - close terminal\n")
            elif c == "echo" or c == "print":
                out.insert("end", "\n>> " + " ".join(args[1:]) + "\n")
            elif c == "dir" or c == "ls":
                out.insert("end", "\n")
                for f in os.listdir(self.disk_path):
                    out.insert("end", f + "\n")
            elif c == "clear" or c == "cls":
                out.delete("1.0", "end")
                out.insert("end", "> ")
                return "break"
            elif c == "start" and len(args) > 1:
                target = args[1].lower()
                if target == "cmd":
                    self.open_terminal()
                    out.insert("end", "\nStarted new terminal\n")
                elif target == "explorer":
                    self.open_explorer()
                    out.insert("end", "\nStarted explorer\n")
                elif target == "calculator":
                    self.open_calculator()
                    out.insert("end", "\nStarted calculator\n")
                elif target == "browser":
                    self.open_browser()
                    out.insert("end", "\nStarted browser\n")
                else:
                    path = os.path.join(self.disk_path, target)
                    if os.path.exists(path):
                        if os.path.isdir(path):
                            out.insert("end", "\nCannot start directory\n")
                        else:
                            self.open_file_from_terminal(path)
                            out.insert("end", "\nOpened file\n")
                    else:
                        out.insert("end", "\nNot found\n")
            elif c == "mkdir" and len(args) > 1:
                try:
                    os.mkdir(os.path.join(self.disk_path, args[1]))
                    out.insert("end", "\nFolder created\n")
                except Exception as e:
                    out.insert("end", f"\nError: {e}\n")
            elif c == "touch" and len(args) > 1:
                try:
                    open(os.path.join(self.disk_path, args[1]), "w").close()
                    out.insert("end", "\nFile created\n")
                except Exception as e:
                    out.insert("end", f"\nError: {e}\n")
            elif c == "rm" and len(args) > 1:
                path = os.path.join(self.disk_path, args[1])
                if os.path.exists(path):
                    try:
                        if os.path.isdir(path):
                            os.rmdir(path)
                        else:
                            os.remove(path)
                        out.insert("end", "\nDeleted\n")
                    except Exception as e:
                        out.insert("end", f"\nError: {e}\n")
                else:
                    out.insert("end", "\nNot found\n")
            elif c == "calc" and len(args) > 1:
                expression = " ".join(args[1:])
                try:
                    result = eval(expression)
                    out.insert("end", f"\n>> {result}\n")
                except Exception as e:
                    out.insert("end", f"\nError: {e}\n")
            elif c == "exit":
                win.destroy()
                return "break"
            else:
                try:
                    result = eval(line)
                    out.insert("end", f"\n>> {result}\n")
                except Exception as e:
                    out.insert("end", f"\nUnknown command or error: {e}\n")

            out.insert("end", "> ")
            out.see("end")
            return "break"

        def arrow_up(event):
            if self.history_index > 0:
                self.history_index -= 1
                out.delete("end-1l linestart+2c", "end")  # Clear current line after '> '
                out.insert("end", self.terminal_history[self.history_index])
            return "break"

        def arrow_down(event):
            if self.history_index < len(self.terminal_history) - 1:
                self.history_index += 1
                out.delete("end-1l linestart+2c", "end")
                out.insert("end", self.terminal_history[self.history_index])
            elif self.history_index == len(self.terminal_history) - 1:
                self.history_index += 1
                out.delete("end-1l linestart+2c", "end")
            return "break"

        out.bind("<Return>", cmd)
        out.bind("<Up>", arrow_up)
        out.bind("<Down>", arrow_down)

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

    # ---------- BROWSER ----------
    def open_browser(self):
        win = tk.Toplevel(self.root)
        win.title("Browser")
        win.geometry("800x600")

        frame = tk.Frame(win, bg="#1A1A1A")
        frame.pack(fill="x")

        self.url_entry = tk.Entry(frame, bg="#0A0A0A", fg="white", font=("Arial", 14), bd=0, width=50)
        self.url_entry.pack(side="left", padx=10, pady=5, fill="x", expand=True)
        self.url_entry.insert(0, "https://www.google.com")

        tk.Button(frame, text="Go", bg="#00ADB5", fg="black", bd=0,
                  command=self.load_page).pack(side="right", padx=10)

        self.browser_content = tk.Frame(win)
        self.browser_content.pack(fill="both", expand=True)

        self.load_page()  # Load initial page

    def load_page(self):
        url = self.url_entry.get()
        try:
            with urllib.request.urlopen(url) as response:
                content = response.read().decode('utf-8')

            for widget in self.browser_content.winfo_children():
                widget.destroy()

            html_label = HTMLLabel(self.browser_content, html=content)
            html_label.pack(fill="both", expand=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page: {e}")

    def open_file_from_terminal(self, path):
        win = tk.Toplevel(self.root)
        win.title(os.path.basename(path))

        area = scrolledtext.ScrolledText(
            win, bg="#0F0F0F", fg="white",
            font=("Consolas", 11)
        )
        area.pack(fill="both", expand=True)

        try:
            with open(path, "r", encoding="utf-8") as f:
                area.insert("1.0", f.read())
        except Exception as e:
            messagebox.showerror("Error", str(e))

        tk.Button(
            win, text="SAVE",
            bg="#00ADB5", fg="black",
            command=lambda: self.save_file(path, area.get("1.0", "end-1c"))
        ).pack(fill="x")

    def save_file(self, path, content):
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)
            messagebox.showinfo("DarkoOS", "Saved")
        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    DarkoOS(root)
    root.mainloop()
