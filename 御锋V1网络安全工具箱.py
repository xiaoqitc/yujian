import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, simpledialog
import base64
import hashlib
import hmac
import socket
import json
import os
import platform
import sys
import threading
import time
import subprocess
import re
import concurrent.futures
import shutil
import tempfile
import zipfile
import random
import string
import py_compile
import importlib.util
import inspect

# 可选导入，如果缺失不影响基本功�?try
# 可选导入，如果缺失不影响基本功能
try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    print("警告: dns.resolver 模块未安装，DNS查询功能不可用")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("警告: requests 模块未安装，网络请求功能不可用")

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import unpad, pad
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("警告: pycryptodome 模块未安装，AES加密功能不可用")

# 密码管理类
class PasswordManager:
    def __init__(self):
        self.config_file = "login_config.json"
    
    def save_password(self, username, password):
        """保存用户名和密码到本地文件"""
        try:
            config_data = {
                "username": username,
                "password": password,
                "remember": True
            }
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存密码失败: {e}")
            return False
    
    def load_password(self):
        """从本地文件加载用户名和密码"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config_data = json.load(f)
                return config_data.get("username", ""), config_data.get("password", ""), config_data.get("remember", False)
            return "", "", False
        except Exception as e:
            print(f"加载密码失败: {e}")
            return "", "", False
    
    def clear_password(self):
        """清除保存的密码"""
        try:
            if os.path.exists(self.config_file):
                os.remove(self.config_file)
            return True
        except Exception as e:
            print(f"清除密码失败: {e}")
            return False

# 自定义美化滚动条类
class CustomScrollbar(tk.Frame):
    def __init__(self, parent, orient="vertical", **kwargs):
        tk.Frame.__init__(self, parent, **kwargs)
        self.orient = orient
        self.parent = parent
        
        # 创建滚动条样式
        self.style = ttk.Style()
        self.style.configure("Custom.Horizontal.TScrollbar", 
                           background="#4A90E2", 
                           troughcolor="#E8E8E8",
                           width=12,
                           borderwidth=0,
                           relief="flat")
        self.style.configure("Custom.Vertical.TScrollbar", 
                           background="#4A90E2", 
                           troughcolor="#E8E8E8",
                           width=12,
                           borderwidth=0,
                           relief="flat")
        
        # 创建滚动条
        if orient == "vertical":
            self.scrollbar = ttk.Scrollbar(self, orient="vertical", style="Custom.Vertical.TScrollbar")
        else:
            self.scrollbar = ttk.Scrollbar(self, orient="horizontal", style="Custom.Horizontal.TScrollbar")
        
        self.scrollbar.pack(fill="both", expand=True)
    
    def configure(self, **kwargs):
        self.scrollbar.configure(**kwargs)
    
    def set(self, first, last):
        self.scrollbar.set(first, last)
    
    def get(self):
        return self.scrollbar.get()

# 自定义带滚动条的文本框
class ScrolledTextWithCustomScrollbars(tk.Frame):
    def __init__(self, parent, **kwargs):
        tk.Frame.__init__(self, parent)
        
        # 创建文本框
        self.text = tk.Text(self, **kwargs)
        
        # 创建自定义滚动条
        self.v_scrollbar = CustomScrollbar(self, orient="vertical")
        self.h_scrollbar = CustomScrollbar(self, orient="horizontal")
        
        # 配置文本框的滚动
        self.text.configure(yscrollcommand=self.v_scrollbar.set, xscrollcommand=self.h_scrollbar.set)
        self.v_scrollbar.configure(command=self.text.yview)
        self.h_scrollbar.configure(command=self.text.xview)
        
        # 布局
        self.text.grid(row=0, column=0, sticky="nsew")
        self.v_scrollbar.grid(row=0, column=1, sticky="ns")
        self.h_scrollbar.grid(row=1, column=0, sticky="ew")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
    
    def get(self, *args, **kwargs):
        return self.text.get(*args, **kwargs)
    
    def insert(self, *args, **kwargs):
        return self.text.insert(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        return self.text.delete(*args, **kwargs)
    
    def configure(self, **kwargs):
        return self.text.configure(**kwargs)
    
    def config(self, **kwargs):
        return self.text.config(**kwargs)

# 搜索功能类
class SearchDialog:
    def __init__(self, parent, text_widget):
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("搜索")
        self.dialog.geometry("400x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.text_widget = text_widget
        self.search_results = []
        self.current_index = -1
        
        # 创建搜索框架
        search_frame = tk.Frame(self.dialog)
        search_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(search_frame, text="搜索内容:", font=('Microsoft YaHei UI', 10)).pack(side=tk.LEFT)
        self.search_entry = tk.Entry(search_frame, width=30, font=('Microsoft YaHei UI', 10))
        self.search_entry.pack(side=tk.LEFT, padx=5)
        self.search_entry.focus()
        
        # 创建选项框架
        options_frame = tk.Frame(self.dialog)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.case_sensitive = tk.BooleanVar()
        tk.Checkbutton(options_frame, text="区分大小写", variable=self.case_sensitive, 
                      font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT)
        
        self.regex_search = tk.BooleanVar()
        tk.Checkbutton(options_frame, text="正则表达式", variable=self.regex_search, 
                      font=('Microsoft YaHei UI', 9)).pack(side=tk.LEFT, padx=10)
        
        # 创建按钮框架
        button_frame = tk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="查找下一个", command=self.find_next).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="查找上一个", command=self.find_previous).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="全部高亮", command=self.highlight_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="清除高亮", command=self.clear_highlights).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="关闭", command=self.dialog.destroy).pack(side=tk.RIGHT, padx=5)
        
        # 绑定回车键
        self.search_entry.bind('<Return>', lambda e: self.find_next())
        self.search_entry.bind('<KeyRelease>', self.on_search_change)
    
    def on_search_change(self, event=None):
        self.current_index = -1
        self.clear_highlights()
    
    def find_next(self):
        search_text = self.search_entry.get()
        if not search_text:
            return
        
        content = self.text_widget.get("1.0", tk.END)
        if not self.case_sensitive.get():
            search_text = search_text.lower()
            content_lower = content.lower()
        else:
            content_lower = content
        
        if self.regex_search.get():
            try:
                import re
                pattern = re.compile(search_text, 0 if self.case_sensitive.get() else re.IGNORECASE)
                matches = list(pattern.finditer(content))
            except re.error:
                messagebox.showerror("错误", "正则表达式格式错误")
                return
        else:
            matches = []
            start = 0
            while True:
                pos = content_lower.find(search_text, start)
                if pos == -1:
                    break
                matches.append(type('Match', (), {'start': lambda: pos, 'end': lambda: pos + len(search_text)})())
                start = pos + 1
        
        if not matches:
            messagebox.showinfo("搜索结果", "未找到匹配内容")
            return
        
        self.current_index = (self.current_index + 1) % len(matches)
        match = matches[self.current_index]
        
        # 滚动到匹配位置
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_num = content[:line_start].count('\n') + 1
        col_num = match.start() - line_start + 1
        
        self.text_widget.see(f"{line_num}.{col_num}")
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        self.text_widget.tag_add("search_highlight", f"{line_num}.{col_num}", f"{line_num}.{col_num + len(search_text)}")
        self.text_widget.tag_config("search_highlight", background="yellow", foreground="black")
        
        # 更新状态
        self.dialog.title(f"搜索 - {self.current_index + 1}/{len(matches)}")
    
    def find_previous(self):
        search_text = self.search_entry.get()
        if not search_text:
            return
        
        content = self.text_widget.get("1.0", tk.END)
        if not self.case_sensitive.get():
            search_text = search_text.lower()
            content_lower = content.lower()
        else:
            content_lower = content
        
        if self.regex_search.get():
            try:
                import re
                pattern = re.compile(search_text, 0 if self.case_sensitive.get() else re.IGNORECASE)
                matches = list(pattern.finditer(content))
            except re.error:
                messagebox.showerror("错误", "正则表达式格式错误")
                return
        else:
            matches = []
            start = 0
            while True:
                pos = content_lower.find(search_text, start)
                if pos == -1:
                    break
                matches.append(type('Match', (), {'start': lambda: pos, 'end': lambda: pos + len(search_text)})())
                start = pos + 1
        
        if not matches:
            messagebox.showinfo("搜索结果", "未找到匹配内容")
            return
        
        self.current_index = (self.current_index - 1) % len(matches)
        match = matches[self.current_index]
        
        # 滚动到匹配位置
        line_start = content.rfind('\n', 0, match.start()) + 1
        line_num = content[:line_start].count('\n') + 1
        col_num = match.start() - line_start + 1
        
        self.text_widget.see(f"{line_num}.{col_num}")
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        self.text_widget.tag_add("search_highlight", f"{line_num}.{col_num}", f"{line_num}.{col_num + len(search_text)}")
        self.text_widget.tag_config("search_highlight", background="yellow", foreground="black")
        
        # 更新状态
        self.dialog.title(f"搜索 - {self.current_index + 1}/{len(matches)}")
    
    def highlight_all(self):
        search_text = self.search_entry.get()
        if not search_text:
            return
        
        content = self.text_widget.get("1.0", tk.END)
        if not self.case_sensitive.get():
            search_text = search_text.lower()
            content_lower = content.lower()
        else:
            content_lower = content
        
        if self.regex_search.get():
            try:
                import re
                pattern = re.compile(search_text, 0 if self.case_sensitive.get() else re.IGNORECASE)
                matches = list(pattern.finditer(content))
            except re.error:
                messagebox.showerror("错误", "正则表达式格式错误")
                return
        else:
            matches = []
            start = 0
            while True:
                pos = content_lower.find(search_text, start)
                if pos == -1:
                    break
                matches.append(type('Match', (), {'start': lambda: pos, 'end': lambda: pos + len(search_text)})())
                start = pos + 1
        
        if not matches:
            messagebox.showinfo("搜索结果", "未找到匹配内容")
            return
        
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)
        
        for match in matches:
            line_start = content.rfind('\n', 0, match.start()) + 1
            line_num = content[:line_start].count('\n') + 1
            col_num = match.start() - line_start + 1
            
            self.text_widget.tag_add("search_highlight", f"{line_num}.{col_num}", f"{line_num}.{col_num + len(search_text)}")
        
        self.text_widget.tag_config("search_highlight", background="yellow", foreground="black")
        messagebox.showinfo("搜索结果", f"找到 {len(matches)} 个匹配项")
    
    def clear_highlights(self):
        self.text_widget.tag_remove("search_highlight", "1.0", tk.END)

class SecurityToolkitGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("御锋V1网络安全工具箱")
        self.root.geometry("900x600")
        self.root.minsize(800, 500)
        
        # 设置字体以支持中文
        self.font = ('Microsoft YaHei UI', 10)
        
        # 确保中文显示正常
        if platform.system() == "Linux":
            self.font = ('WenQuanYi Micro Hei', 10)
        elif platform.system() == "Darwin":  # macOS
            self.font = ('Heiti TC', 10)
        
        # 初始化密码管理器
        self.password_manager = PasswordManager()
        
        # 初始化变量
        self.fofa_email = tk.StringVar()
        self.fofa_api_key = tk.StringVar()
        self.port_scan_results = []
        self.is_scanning = False
        self.test_request_history = []
        
        # 显示登录面板
        self.show_login()
    
    def show_login(self):
        # 清除现有内容
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建登录框架
        login_frame = tk.Frame(self.root)
        login_frame.pack(expand=True)
        
        # 创建标题
        title_label = tk.Label(login_frame, text="御锋V1网络安全工具箱", font=('Microsoft YaHei UI', 20, 'bold'))
        title_label.pack(pady=40)
        
        # 创建账号输入
        tk.Label(login_frame, text="账号:", font=self.font).pack(pady=5)
        username_entry = tk.Entry(login_frame, font=self.font, width=30)
        username_entry.pack(pady=5)
        
        # 创建密码输入
        tk.Label(login_frame, text="密码:", font=self.font).pack(pady=5)
        password_entry = tk.Entry(login_frame, font=self.font, width=30, show="*")
        password_entry.pack(pady=5)
        
        # 创建记住密码复选框
        remember_var = tk.BooleanVar()
        remember_checkbox = tk.Checkbutton(login_frame, text="记住密码", variable=remember_var, 
                                         font=self.font, fg="#666666")
        remember_checkbox.pack(pady=5)
        
        # 加载保存的密码
        saved_username, saved_password, saved_remember = self.password_manager.load_password()
        if saved_username and saved_password and saved_remember:
            username_entry.insert(0, saved_username)
            password_entry.insert(0, saved_password)
            remember_var.set(True)
        
        # 创建登录按钮
        def check_login():
            username = username_entry.get()
            password = password_entry.get()
            remember = remember_var.get()
            
            if username == "admin" and password == "admin":
                # 如果勾选了记住密码，保存到本地
                if remember:
                    self.password_manager.save_password(username, password)
                else:
                    # 如果没有勾选记住密码，清除保存的密码
                    self.password_manager.clear_password()
                
                messagebox.showinfo("登录成功", "欢迎使用御锋V1网络安全工具箱！")
                self.create_main_frame()
            else:
                messagebox.showerror("登录失败", "账号或密码错误！")
        
        ttk.Button(login_frame, text="登录", command=check_login).pack(pady=20)
        
        # 显示作者信息
        author_frame = tk.Frame(self.root)
        author_frame.pack(side=tk.BOTTOM, pady=20)
        
        tk.Label(author_frame, text="作者: 小白", font=self.font).pack()
        tk.Label(author_frame, text="微信: ccyuwu8888", font=self.font).pack()
        tk.Label(author_frame, text="QQ: 1544185387", font=self.font).pack()
    
    def detect_and_install_dependencies(self):
        # 创建依赖检测对话框
        dependency_window = tk.Toplevel(self.root)
        dependency_window.title("依赖检测与安装")
        dependency_window.geometry("700x500")
        dependency_window.transient(self.root)
        dependency_window.grab_set()
        
        # 创建选择方式框架
        select_frame = tk.Frame(dependency_window)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(select_frame, text="选择分析方式:", font=self.font).pack(side=tk.LEFT, padx=5)
        
        selected_files = []
        selected_directory = ""
        
        def select_files():
            from tkinter import filedialog
            files = filedialog.askopenfilenames(
                title="选择Python脚本",
                filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
            )
            selected_files.clear()
            selected_files.extend(files)
            file_list.delete(0, tk.END)
            for file in selected_files:
                file_list.insert(tk.END, os.path.basename(file))
            status_label.config(text=f"已选择 {len(selected_files)} 个文件")
        
        def select_directory():
            from tkinter import filedialog
            directory = filedialog.askdirectory(title="选择目录")
            if directory:
                selected_directory = directory
                # 扫描目录下的所有Python文件
                py_files = []
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            py_files.append(os.path.join(root, file))
                
                selected_files.clear()
                selected_files.extend(py_files)
                file_list.delete(0, tk.END)
                for file in selected_files:
                    file_list.insert(tk.END, os.path.relpath(file, directory))
                status_label.config(text=f"已扫描目录，发现 {len(selected_files)} 个Python文件")
        
        def auto_scan_current():
            # 自动扫描当前目录
            current_dir = os.getcwd()
            py_files = []
            for root, dirs, files in os.walk(current_dir):
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))
            
            selected_files.clear()
            selected_files.extend(py_files)
            file_list.delete(0, tk.END)
            for file in selected_files:
                file_list.insert(tk.END, os.path.relpath(file, current_dir))
            status_label.config(text=f"已扫描当前目录，发现 {len(selected_files)} 个Python文件")
        
        ttk.Button(select_frame, text="选择文件", command=select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="选择目录", command=select_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="扫描当前目录", command=auto_scan_current).pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        status_label = tk.Label(select_frame, text="请选择要分析的文件或目录", font=self.font, fg="blue")
        status_label.pack(side=tk.RIGHT, padx=5)
        
        # 显示选中的文件列表
        file_list_frame = tk.Frame(dependency_window)
        file_list_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(file_list_frame, text="已选择的文件:", font=self.font).pack(anchor=tk.W)
        file_list = tk.Listbox(file_list_frame, height=4, font=self.font)
        file_list.pack(fill=tk.X)
        
        # 创建进度文本
        progress_text = ScrolledTextWithCustomScrollbars(dependency_window, font=self.font)
        progress_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        def check_dependencies():
            if not selected_files:
                progress_text.insert(tk.END, "请先选择要分析的Python脚本文件。\n")
                return
                
            progress_text.insert(tk.END, f"正在分析 {len(selected_files)} 个Python脚本...\n")
            
            all_dependencies = set()
            
            # 分析每个脚本的依赖
            for script in selected_files:
                progress_text.insert(tk.END, f"\n分析 {os.path.basename(script)} 的依赖...\n")
                try:
                    with open(script, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 使用正则表达式提取import语句
                    import_pattern = re.compile(r'^\s*import\s+([a-zA-Z0-9_.]+)', re.MULTILINE)
                    from_pattern = re.compile(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import', re.MULTILINE)
                    
                    imports = import_pattern.findall(content)
                    from_imports = from_pattern.findall(content)
                    
                    # 提取顶级包名
                    dependencies = set()
                    for imp in imports:
                        package = imp.split('.')[0]
                        dependencies.add(package)
                    
                    for imp in from_imports:
                        package = imp.split('.')[0]
                        dependencies.add(package)
                    
                    # 排除Python标准库
                    stdlib_packages = {'sys', 'os', 'json', 're', 'math', 'random', 'datetime', 'time', 'io', 'string',
                                       'tkinter', 'threading', 'subprocess', 'hmac', 'socket', 'platform',
                                       'base64', 'hashlib', 'dns', 'requests', 'Crypto', 'urllib', 'concurrent',
                                       'shutil', 'tempfile', 'zipfile', 'py_compile', 'importlib', 'queue',
                                       'collections', 'itertools', 'functools', 'contextlib', 'pathlib'}  # 扩展标准库列表
                    dependencies = {d for d in dependencies if d not in stdlib_packages}
                    
                    if dependencies:
                        progress_text.insert(tk.END, f"发现依赖: {', '.join(dependencies)}\n")
                        all_dependencies.update(dependencies)
                    else:
                        progress_text.insert(tk.END, "未发现外部依赖。\n")
                except Exception as e:
                    progress_text.insert(tk.END, f"分析失败: {str(e)}\n")
            
            if not all_dependencies:
                progress_text.insert(tk.END, "\n所有脚本均不需要安装额外依赖。\n")
                progress_text.insert(tk.END, "依赖检测完成。\n")
                return
            
            # 显示发现的依赖
            progress_text.insert(tk.END, f"\n共发现 {len(all_dependencies)} 个需要安装的依赖:\n")
            for dep in sorted(all_dependencies):
                progress_text.insert(tk.END, f"- {dep}\n")
            
            # 创建安装按钮
            install_button = ttk.Button(dependency_window, text="开始安装所有依赖", 
                                       command=lambda: install_deps(all_dependencies))
            install_button.pack(pady=5)
            
            progress_text.insert(tk.END, "\n点击'开始安装所有依赖'按钮安装所需依赖。\n")
        
        def install_deps(dependencies):
            progress_text.insert(tk.END, "\n开始并行安装依赖...\n")
            
            # 使用线程池并行安装依赖，提高速度
            def install_package(dep):
                progress_text.insert(tk.END, f"\n正在安装 {dep}...\n")
                try:
                    # 使用subprocess调用pip安装依赖，添加--no-cache-dir选项加快速度
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--no-cache-dir", dep],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    progress_text.insert(tk.END, result.stdout)
                    progress_text.insert(tk.END, f"\n{dep} 安装成功。\n")
                    return True, dep
                except subprocess.CalledProcessError as e:
                    progress_text.insert(tk.END, f"\n安装失败: {e.stderr}\n")
                    return False, dep
                except Exception as e:
                    progress_text.insert(tk.END, f"\n安装时发生未知错误: {str(e)}\n")
                    return False, dep
            
            # 使用线程池并行安装，默认使用CPU核心数*5的线程数
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(install_package, dependencies))
            
            success_count = sum(1 for success, _ in results if success)
            total_count = len(results)
            
            progress_text.insert(tk.END, f"\n依赖安装完成。成功: {success_count}/{total_count}\n")
            
            if success_count == total_count:
                progress_text.insert(tk.END, "所有依赖安装成功！\n")
            else:
                progress_text.insert(tk.END, "部分依赖安装失败，请检查网络连接或手动安装。\n")
        
        # 创建分析按钮
        ttk.Button(dependency_window, text="开始分析依赖", command=check_dependencies).pack(pady=5)
        progress_text.insert(tk.END, "请选择要分析的Python脚本文件或目录，然后点击'开始分析依赖'按钮。\n")
    
    def create_main_frame(self):
        # 清除现有界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 创建顶部标题
        header_frame = tk.Frame(self.root, bg="#165DFF", height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="御锋V1网络安全工具箱", 
                              font=('Microsoft YaHei UI', 20, 'bold'), 
                              fg="white", bg="#165DFF")
        title_label.pack(pady=20)
        
        # 创建搜索框架
        search_frame = tk.Frame(self.root, bg="#F2F3F5")
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="快速搜索:", font=self.font).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=40, font=self.font)
        search_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def quick_search():
            search_term = self.search_var.get().strip().lower()
            if not search_term:
                return
            # 支持多关键词
            keywords = [k for k in search_term.split() if k]
            # 功能名和关键词映射
            search_functions = [
                (['解码', '解密', 'base64', 'url', 'aes', 'md5', 'sha', 'hmac'], self.show_decoder),
                (['dns', '域名', '解析'], self.show_dns_lookup),
                (['fofa', '资产', '搜索'], self.show_fofa_search),
                (['端口', '扫描', 'port'], self.show_port_scan),
                (['请求', 'http', '测试'], self.show_test_request),
                (['打包', 'exe', 'apk'], self.show_packer),
                (['依赖', '包管理', 'requirements'], self.show_dependency_manager),
                (['目录', '文件夹', 'explorer'], self.show_directory_tools),
                (['sqlmap', 'sql', '注入'], self.show_sqlmap_tool),
                (['系统', '信息', 'system'], self.show_system_info),
                (['网络', 'ping', 'traceroute'], self.show_network_tools),
                (['文件', '哈希', '比较'], self.show_file_tools),
                (['编码', '十六进制', '二进制'], self.show_encoding_tools),
                (['关于', '作者'], self.show_about),
            ]
            for keys, func in search_functions:
                for kw in keywords:
                    for k in keys:
                        if kw in k or k in kw:
                            func()
                            return
            messagebox.showinfo("搜索结果", f"未找到与 '{search_term}' 相关的功能")
        
        search_entry.bind('<Return>', lambda e: quick_search())
        ttk.Button(search_frame, text="搜索", command=quick_search).pack(side=tk.LEFT, padx=5)
        
        # 创建功能按钮区域
        buttons_frame = tk.Frame(self.root, bg="#F2F3F5")
        buttons_frame.pack(fill=tk.X)
        
        button_style = ttk.Style()
        button_style.configure('TButton', font=self.font, padding=10)
        
        # 第一行按钮
        row1_frame = tk.Frame(buttons_frame, bg="#F2F3F5")
        row1_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(row1_frame, text="解码/解密工具", command=self.show_decoder).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="DNS解析工具", command=self.show_dns_lookup).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="FOFA查询工具", command=self.show_fofa_search).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="端口扫描工具", command=self.show_port_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(row1_frame, text="测试请求工具", command=self.show_test_request).pack(side=tk.LEFT, padx=5)
        
        # 第二行按钮
        row2_frame = tk.Frame(buttons_frame, bg="#F2F3F5")
        row2_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(row2_frame, text="打包工具", command=self.show_packer).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2_frame, text="依赖管理", command=self.show_dependency_manager).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2_frame, text="目录工具", command=self.show_directory_tools).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2_frame, text="SQLMap工具", command=self.show_sqlmap_tool).pack(side=tk.LEFT, padx=5)
        ttk.Button(row2_frame, text="依赖检测", command=self.detect_and_install_dependencies).pack(side=tk.LEFT, padx=5)
        
        # 第三行按钮
        row3_frame = tk.Frame(buttons_frame, bg="#F2F3F5")
        row3_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(row3_frame, text="系统信息", command=self.show_system_info).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3_frame, text="网络工具", command=self.show_network_tools).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3_frame, text="文件工具", command=self.show_file_tools).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3_frame, text="编码工具", command=self.show_encoding_tools).pack(side=tk.LEFT, padx=5)
        ttk.Button(row3_frame, text="关于", command=self.show_about).pack(side=tk.RIGHT, padx=5)
        
        # 创建内容区域
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # 默认显示欢迎信息
        self.show_welcome()
    
    def show_welcome(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        welcome_text = """
欢迎使用御锋V1网络安全工具箱！

这是一个集成了多种网络安全功能的工具集，包括：

1. 解码/解密工具 - 支持Base64、URL、AES和MD5加解密
2. DNS解析工具 - 查询各种DNS记录类型
3. FOFA查询工具 - 通过FOFA搜索引擎进行资产发现
4. 端口扫描工具 - 扫描目标主机开放的端口
5. 测试请求工具 - 发送HTTP请求并查看响应
6. 打包工具 - 将Python脚本打包成EXE或APK
7. 依赖管理 - 自动检测和安装Python脚本依赖
8. 目录工具 - 快速打开目录并使用不同工具
9. SQLMap工具 - 图形化SQL注入检测工具

请点击上方的功能按钮开始使用相应的工具。
"""
        welcome_label = tk.Label(self.content_frame, text=welcome_text, font=self.font, justify=tk.LEFT)
        welcome_label.pack(pady=20)
    
    def show_decoder(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建主滚动框架
        main_canvas = tk.Canvas(self.content_frame, bg="#F5F5F5")
        main_scrollbar = CustomScrollbar(self.content_frame, orient="vertical")
        scrollable_frame = tk.Frame(main_canvas, bg="#F5F5F5")
        
        # 配置滚动
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_scrollbar.configure(command=main_canvas.yview)
        
        # 增强的鼠标滚轮绑定 - 更快的滚动速度
        def _on_mousewheel(event):
            # 增加滚动速度，从原来的1倍增加到3倍
            scroll_amount = int(-3 * (event.delta / 120))
            main_canvas.yview_scroll(scroll_amount, "units")
        
        # 绑定鼠标滚轮事件
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 添加键盘滚动支持
        def _on_key_scroll(event):
            if event.keysym == "Up":
                main_canvas.yview_scroll(-2, "units")
            elif event.keysym == "Down":
                main_canvas.yview_scroll(2, "units")
            elif event.keysym == "Page_Up":
                main_canvas.yview_scroll(-1, "pages")
            elif event.keysym == "Page_Down":
                main_canvas.yview_scroll(1, "pages")
            elif event.keysym == "Home":
                main_canvas.yview_moveto(0)
            elif event.keysym == "End":
                main_canvas.yview_moveto(1)
        
        main_canvas.bind_all("<Key>", _on_key_scroll)
        
        # 添加快速滚动按钮
        def scroll_to_top():
            main_canvas.yview_moveto(0)
        
        def scroll_to_bottom():
            main_canvas.yview_moveto(1)
        
        def scroll_up_fast():
            main_canvas.yview_scroll(-5, "units")
        
        def scroll_down_fast():
            main_canvas.yview_scroll(5, "units")
        
        # 布局主滚动区域
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # 创建快速滚动按钮框架
        quick_scroll_frame = tk.Frame(self.content_frame, bg="#F5F5F5")
        quick_scroll_frame.pack(side="right", fill="y", padx=(5, 0))
        
        ttk.Button(quick_scroll_frame, text="↑↑", command=scroll_to_top, width=3).pack(pady=2)
        ttk.Button(quick_scroll_frame, text="↑", command=scroll_up_fast, width=3).pack(pady=2)
        ttk.Button(quick_scroll_frame, text="↓", command=scroll_down_fast, width=3).pack(pady=2)
        ttk.Button(quick_scroll_frame, text="↓↓", command=scroll_to_bottom, width=3).pack(pady=2)
        
        # 创建解码/解密工具界面
        title_label = tk.Label(scrollable_frame, text="解码/解密工具", font=('Microsoft YaHei UI', 18, 'bold'), 
                              bg="#F5F5F5", fg="#2C3E50")
        title_label.pack(pady=(20, 10))
        
        # 创建选项卡
        tab_control = ttk.Notebook(scrollable_frame)
        
        # Base64选项卡
        base64_tab = ttk.Frame(tab_control)
        tab_control.add(base64_tab, text="Base64")
        
        input_frame = tk.Frame(base64_tab, bg="#F5F5F5")
        input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(input_frame, text="输入:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=5)
        base64_input = ScrolledTextWithCustomScrollbars(base64_tab, width=70, height=5, font=self.font)
        base64_input.pack(padx=10, pady=5)
        
        button_frame = tk.Frame(base64_tab, bg="#F5F5F5")
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="解码", command=lambda: self.base64_decode(base64_input, base64_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="编码", command=lambda: self.base64_encode(base64_input, base64_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="搜索", command=lambda: SearchDialog(self.root, base64_input.text)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(base64_tab, text="输出:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        base64_output = ScrolledTextWithCustomScrollbars(base64_tab, width=70, height=10, font=self.font)
        base64_output.pack(padx=10, pady=5)
        
        # URL选项卡
        url_tab = ttk.Frame(tab_control)
        tab_control.add(url_tab, text="URL")
        
        tk.Label(url_tab, text="输入:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        url_input = ScrolledTextWithCustomScrollbars(url_tab, width=70, height=5, font=self.font)
        url_input.pack(padx=10, pady=5)
        
        url_frame = tk.Frame(url_tab, bg="#F5F5F5")
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(url_frame, text="解码", command=lambda: self.url_decode(url_input, url_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(url_frame, text="编码", command=lambda: self.url_encode(url_input, url_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(url_frame, text="搜索", command=lambda: SearchDialog(self.root, url_input.text)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(url_tab, text="输出:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        url_output = ScrolledTextWithCustomScrollbars(url_tab, width=70, height=10, font=self.font)
        url_output.pack(padx=10, pady=5)
        
        # AES选项卡
        aes_tab = ttk.Frame(tab_control)
        tab_control.add(aes_tab, text="AES")
        
        # 创建AES输入框架
        aes_input_frame = tk.Frame(aes_tab, bg="#F5F5F5")
        aes_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(aes_input_frame, text="数据:", font=self.font, bg="#F5F5F5").grid(row=0, column=0, sticky=tk.W, pady=5)
        aes_data = ScrolledTextWithCustomScrollbars(aes_input_frame, width=50, height=5, font=self.font)
        aes_data.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(aes_input_frame, text="密钥:", font=self.font, bg="#F5F5F5").grid(row=1, column=0, sticky=tk.W, pady=5)
        aes_key = tk.Entry(aes_input_frame, width=50, font=self.font, relief="solid", bd=1, bg="white")
        aes_key.grid(row=1, column=1, padx=5, pady=5)
        
        # 添加密钥长度提示
        key_hint_label = tk.Label(aes_input_frame, text="💡 密钥长度: 16字节(AES-128) | 24字节(AES-192) | 32字节(AES-256)", 
                                 font=('Microsoft YaHei UI', 9), fg="#666666", bg="#F5F5F5")
        key_hint_label.grid(row=1, column=2, sticky=tk.W, padx=5, pady=5)
        
        tk.Label(aes_input_frame, text="IV:", font=self.font, bg="#F5F5F5").grid(row=2, column=0, sticky=tk.W, pady=5)
        aes_iv = tk.Entry(aes_input_frame, width=50, font=self.font, relief="solid", bd=1, bg="white")
        aes_iv.grid(row=2, column=1, padx=5, pady=5)
        
        # 创建AES模式选择
        aes_mode_frame = tk.Frame(aes_tab, bg="#F5F5F5")
        aes_mode_frame.pack(fill=tk.X, padx=10, pady=5)
        
        aes_mode = tk.StringVar(value="ECB")
        tk.Label(aes_mode_frame, text="模式:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(aes_mode_frame, text="ECB", variable=aes_mode, value="ECB").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(aes_mode_frame, text="CBC", variable=aes_mode, value="CBC").pack(side=tk.LEFT, padx=5)
        
        # 创建AES按钮框架
        aes_button_frame = tk.Frame(aes_tab, bg="#F5F5F5")
        aes_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(aes_button_frame, text="解密", 
                  command=lambda: self.aes_decrypt(aes_data, aes_key, aes_iv, aes_mode, aes_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(aes_button_frame, text="加密", 
                  command=lambda: self.aes_encrypt(aes_data, aes_key, aes_iv, aes_mode, aes_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(aes_button_frame, text="搜索", 
                  command=lambda: SearchDialog(self.root, aes_data.text)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(aes_tab, text="结果:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        aes_output = ScrolledTextWithCustomScrollbars(aes_tab, width=70, height=8, font=self.font)
        aes_output.pack(padx=10, pady=5)
        
        # MD5选项卡
        md5_tab = ttk.Frame(tab_control)
        tab_control.add(md5_tab, text="MD5")
        
        tk.Label(md5_tab, text="输入:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        md5_input = ScrolledTextWithCustomScrollbars(md5_tab, width=70, height=5, font=self.font)
        md5_input.pack(padx=10, pady=5)
        
        md5_frame = tk.Frame(md5_tab, bg="#F5F5F5")
        md5_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(md5_frame, text="计算MD5", command=lambda: self.calculate_md5(md5_input, md5_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(md5_frame, text="搜索", command=lambda: SearchDialog(self.root, md5_input.text)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(md5_tab, text="MD5值:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        md5_output = ScrolledTextWithCustomScrollbars(md5_tab, width=70, height=5, font=self.font)
        md5_output.pack(padx=10, pady=5)
        
        # SHA选项卡
        sha_tab = ttk.Frame(tab_control)
        tab_control.add(sha_tab, text="SHA")
        
        tk.Label(sha_tab, text="输入:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        sha_input = ScrolledTextWithCustomScrollbars(sha_tab, width=70, height=5, font=self.font)
        sha_input.pack(padx=10, pady=5)
        
        sha_frame = tk.Frame(sha_tab, bg="#F5F5F5")
        sha_frame.pack(fill=tk.X, padx=10, pady=5)
        
        sha_type = tk.StringVar(value="sha256")
        ttk.Radiobutton(sha_frame, text="SHA1", variable=sha_type, value="sha1").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sha_frame, text="SHA256", variable=sha_type, value="sha256").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(sha_frame, text="SHA512", variable=sha_type, value="sha512").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(sha_frame, text="计算SHA", command=lambda: self.calculate_sha(sha_input, sha_type, sha_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(sha_frame, text="搜索", command=lambda: SearchDialog(self.root, sha_input.text)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(sha_tab, text="SHA值:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        sha_output = ScrolledTextWithCustomScrollbars(sha_tab, width=70, height=5, font=self.font)
        sha_output.pack(padx=10, pady=5)
        
        # HMAC选项卡
        hmac_tab = ttk.Frame(tab_control)
        tab_control.add(hmac_tab, text="HMAC")
        
        hmac_input_frame = tk.Frame(hmac_tab, bg="#F5F5F5")
        hmac_input_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(hmac_input_frame, text="数据:", font=self.font, bg="#F5F5F5").grid(row=0, column=0, sticky=tk.W, pady=5)
        hmac_data = ScrolledTextWithCustomScrollbars(hmac_input_frame, width=50, height=3, font=self.font)
        hmac_data.grid(row=0, column=1, padx=5, pady=5)
        
        tk.Label(hmac_input_frame, text="密钥:", font=self.font, bg="#F5F5F5").grid(row=1, column=0, sticky=tk.W, pady=5)
        hmac_key = tk.Entry(hmac_input_frame, width=50, font=self.font, relief="solid", bd=1, bg="white")
        hmac_key.grid(row=1, column=1, padx=5, pady=5)
        
        hmac_button_frame = tk.Frame(hmac_tab, bg="#F5F5F5")
        hmac_button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        hmac_algorithm = tk.StringVar(value="sha256")
        ttk.Radiobutton(hmac_button_frame, text="MD5", variable=hmac_algorithm, value="md5").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(hmac_button_frame, text="SHA256", variable=hmac_algorithm, value="sha256").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(hmac_button_frame, text="SHA512", variable=hmac_algorithm, value="sha512").pack(side=tk.LEFT, padx=5)
        
        ttk.Button(hmac_button_frame, text="计算HMAC", 
                  command=lambda: self.calculate_hmac(hmac_data, hmac_key, hmac_algorithm, hmac_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(hmac_button_frame, text="搜索", 
                  command=lambda: SearchDialog(self.root, hmac_data.text)).pack(side=tk.LEFT, padx=5)
        
        tk.Label(hmac_tab, text="HMAC值:", font=self.font, bg="#F5F5F5").pack(anchor=tk.W, padx=10, pady=5)
        hmac_output = ScrolledTextWithCustomScrollbars(hmac_tab, width=70, height=5, font=self.font)
        hmac_output.pack(padx=10, pady=5)
        
        # 显示选项卡
        tab_control.pack(expand=1, fill=tk.BOTH, padx=20, pady=10)
    
    def show_dns_lookup(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建DNS解析工具界面
        title_label = tk.Label(self.content_frame, text="DNS解析工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建输入框架
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(input_frame, text="域名:", font=self.font).pack(side=tk.LEFT, padx=5)
        domain_entry = tk.Entry(input_frame, width=50, font=self.font)
        domain_entry.pack(side=tk.LEFT, padx=5)
        domain_entry.insert(0, "example.com")
        
        # 创建记录类型选择
        record_type_frame = tk.Frame(self.content_frame)
        record_type_frame.pack(fill=tk.X, padx=10, pady=5)
        
        record_type = tk.StringVar(value="A")
        tk.Label(record_type_frame, text="记录类型:", font=self.font).pack(side=tk.LEFT, padx=5)
        
        record_types = ["A", "MX", "NS", "TXT", "CNAME", "AAAA", "SRV"]
        for rt in record_types:
            ttk.Radiobutton(record_type_frame, text=rt, variable=record_type, value=rt).pack(side=tk.LEFT, padx=5)
        
        # 创建查询按钮
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(button_frame, text="查询", 
                  command=lambda: self.dns_query(domain_entry, record_type, dns_output)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="搜索", 
                  command=lambda: SearchDialog(self.root, dns_output.text)).pack(side=tk.LEFT, padx=5)
        
        # 创建结果显示区域
        tk.Label(self.content_frame, text="查询结果:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        dns_output = ScrolledTextWithCustomScrollbars(self.content_frame, width=80, height=15, font=self.font)
        dns_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
    
    def show_fofa_search(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建FOFA查询工具界面
        title_label = tk.Label(self.content_frame, text="FOFA查询工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 检查是否已设置FOFA API密钥
        if not self.fofa_email.get() or not self.fofa_api_key.get():
            if not self.setup_fofa_api():
                self.show_welcome()
                return
        
        # 创建查询语法输入
        tk.Label(self.content_frame, text="查询语法:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        query_entry = scrolledtext.ScrolledText(self.content_frame, width=70, height=3, font=self.font)
        query_entry.pack(padx=10, pady=5)
        query_entry.insert(tk.END, 'app="Apache-Shiro"')
        
        # 创建结果数量选择
        result_frame = tk.Frame(self.content_frame)
        result_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(result_frame, text="显示结果数量:", font=self.font).pack(side=tk.LEFT, padx=5)
        result_count = tk.StringVar(value="10")
        ttk.Combobox(result_frame, textvariable=result_count, values=["10", "20", "50", "100"], width=5).pack(side=tk.LEFT, padx=5)
        
        # 创建查询按钮
        ttk.Button(self.content_frame, text="查询", 
                  command=lambda: self.fofa_query(query_entry, result_count, fofa_output)).pack(pady=10)
        
        # 创建结果显示区域
        tk.Label(self.content_frame, text="查询结果:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        
        # 创建表格
        columns = ("序号", "主机", "标题", "IP", "端口", "国家", "城市")
        fofa_output = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            fofa_output.heading(col, text=col)
            width = 100 if col != "标题" else 200
            fofa_output.column(col, width=width, anchor=tk.CENTER)
        
        fofa_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=fofa_output.yview)
        fofa_output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_port_scan(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建端口扫描工具界面
        title_label = tk.Label(self.content_frame, text="端口扫描工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建输入框架
        input_frame = tk.Frame(self.content_frame)
        input_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(input_frame, text="目标主机:", font=self.font).pack(side=tk.LEFT, padx=5)
        host_entry = tk.Entry(input_frame, width=30, font=self.font)
        host_entry.pack(side=tk.LEFT, padx=5)
        host_entry.insert(0, "example.com")
        
        tk.Label(input_frame, text="端口范围:", font=self.font).pack(side=tk.LEFT, padx=5)
        port_range_entry = tk.Entry(input_frame, width=20, font=self.font)
        port_range_entry.pack(side=tk.LEFT, padx=5)
        port_range_entry.insert(0, "1-100")
        
        # 创建扫描选项
        options_frame = tk.Frame(self.content_frame)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        scan_type = tk.StringVar(value="tcp")
        tk.Label(options_frame, text="扫描类型:", font=self.font).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(options_frame, text="TCP", variable=scan_type, value="tcp").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(options_frame, text="UDP", variable=scan_type, value="udp").pack(side=tk.LEFT, padx=5)
        
        # 创建线程数选择
        tk.Label(options_frame, text="线程数:", font=self.font).pack(side=tk.LEFT, padx=5)
        thread_count = tk.StringVar(value="50")
        ttk.Combobox(options_frame, textvariable=thread_count, values=["10", "50", "100", "200"], width=5).pack(side=tk.LEFT, padx=5)
        
        # 创建扫描按钮
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.scan_button = ttk.Button(button_frame, text="开始扫描", 
                  command=lambda: self.start_port_scan(host_entry, port_range_entry, scan_type, thread_count, port_output))
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="停止扫描", 
                  command=self.stop_port_scan).pack(side=tk.LEFT, padx=5)
        
        # 创建结果显示区域
        tk.Label(self.content_frame, text="扫描结果:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        
        # 创建进度条
        progress_frame = tk.Frame(self.content_frame)
        progress_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, maximum=100)
        progress_bar.pack(fill=tk.X)
        
        # 创建结果表格
        columns = ("端口", "状态", "服务", "描述")
        port_output = ttk.Treeview(self.content_frame, columns=columns, show="headings", height=10)
        
        for col in columns:
            port_output.heading(col, text=col)
            width = 100 if col != "描述" else 300
            port_output.column(col, width=width, anchor=tk.CENTER)
        
        port_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=port_output.yview)
        port_output.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def show_test_request(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建测试请求工具界面
        title_label = tk.Label(self.content_frame, text="测试请求工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建URL输入
        url_frame = tk.Frame(self.content_frame)
        url_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(url_frame, text="URL:", font=self.font).pack(side=tk.LEFT, padx=5)
        url_entry = tk.Entry(url_frame, width=60, font=self.font)
        url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        url_entry.insert(0, "https://www.example.com")
        
        # 创建请求方法选择
        method_frame = tk.Frame(self.content_frame)
        method_frame.pack(fill=tk.X, padx=10, pady=5)
        
        method = tk.StringVar(value="GET")
        tk.Label(method_frame, text="请求方法:", font=self.font).pack(side=tk.LEFT, padx=5)
        
        methods = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"]
        for m in methods:
            ttk.Radiobutton(method_frame, text=m, variable=method, value=m).pack(side=tk.LEFT, padx=5)
        
        # 创建请求头
        headers_frame = tk.LabelFrame(self.content_frame, text="请求头", font=self.font)
        headers_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        headers_text = ScrolledTextWithCustomScrollbars(headers_frame, width=70, height=5, font=self.font)
        headers_text.pack(padx=10, pady=5)
        headers_text.insert(tk.END, "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\nAccept: */*")
        
        # 创建请求体
        body_frame = tk.LabelFrame(self.content_frame, text="请求体", font=self.font)
        body_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        body_text = ScrolledTextWithCustomScrollbars(body_frame, width=70, height=5, font=self.font)
        body_text.pack(padx=10, pady=5)
        
        # 创建按钮
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="发送请求", 
                  command=lambda: self.send_test_request(url_entry, method, headers_text, body_text, response_text, status_label)).pack(side=tk.LEFT, padx=5)
        
        # 创建历史记录下拉菜单
        tk.Label(button_frame, text="历史记录:", font=self.font).pack(side=tk.LEFT, padx=5)
        
        history_combo = ttk.Combobox(button_frame, values=["无历史记录"], width=20, state="readonly")
        history_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="重发", 
                  command=lambda: self.resend_test_request(history_combo, url_entry, method, headers_text, body_text, response_text, status_label)).pack(side=tk.LEFT, padx=5)
        
        # 创建状态标签
        status_frame = tk.Frame(self.content_frame)
        status_frame.pack(fill=tk.X, padx=10, pady=5)
        
        status_label = tk.Label(status_frame, text="状态: 就绪", font=self.font, fg="green")
        status_label.pack(anchor=tk.W)
        
        # 创建响应区域
        response_frame = tk.LabelFrame(self.content_frame, text="响应", font=self.font)
        response_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        response_text = ScrolledTextWithCustomScrollbars(response_frame, width=70, height=10, font=self.font)
        response_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 添加搜索按钮
        search_button = ttk.Button(response_frame, text="搜索响应", 
                                 command=lambda: SearchDialog(self.root, response_text.text))
        search_button.pack(pady=5)
    
    def show_packer(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建打包工具界面
        title_label = tk.Label(self.content_frame, text="打包工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建打包类型选择
        package_type = tk.StringVar(value="exe")
        
        type_frame = tk.Frame(self.content_frame)
        type_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(type_frame, text="打包类型:", font=self.font).pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="EXE (Windows)", variable=package_type, value="exe").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(type_frame, text="APK (Android)", variable=package_type, value="apk").pack(side=tk.LEFT, padx=5)
        
        # 创建文件选择框架
        file_frame = tk.Frame(self.content_frame)
        file_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(file_frame, text="源文件:", font=self.font).pack(side=tk.LEFT, padx=5)
        source_file_var = tk.StringVar()
        source_entry = tk.Entry(file_frame, textvariable=source_file_var, width=50, font=self.font)
        source_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def select_source_file():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="选择Python源文件",
                filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
            )
            if file_path:
                source_file_var.set(file_path)
        
        ttk.Button(file_frame, text="浏览", command=select_source_file).pack(side=tk.LEFT, padx=5)
        
        # 创建输出路径框架
        output_frame = tk.Frame(self.content_frame)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(output_frame, text="输出路径:", font=self.font).pack(side=tk.LEFT, padx=5)
        output_path_var = tk.StringVar()
        output_entry = tk.Entry(output_frame, textvariable=output_path_var, width=50, font=self.font)
        output_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def select_output_path():
            from tkinter import filedialog
            if package_type.get() == "exe":
                path = filedialog.asksaveasfilename(
                    title="选择输出路径",
                    defaultextension=".exe",
                    filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
                )
            else:
                path = filedialog.asksaveasfilename(
                    title="选择输出路径",
                    defaultextension=".apk",
                    filetypes=[("APK文件", "*.apk"), ("所有文件", "*.*")]
                )
            if path:
                output_path_var.set(path)
        
        ttk.Button(output_frame, text="浏览", command=select_output_path).pack(side=tk.LEFT, padx=5)
        
        # 创建打包选项框架
        options_frame = tk.LabelFrame(self.content_frame, text="打包选项", font=self.font)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # 图标选择
        icon_frame = tk.Frame(options_frame)
        icon_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(icon_frame, text="图标文件:", font=self.font).pack(side=tk.LEFT, padx=5)
        icon_var = tk.StringVar()
        icon_entry = tk.Entry(icon_frame, textvariable=icon_var, width=40, font=self.font)
        icon_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def select_icon():
            from tkinter import filedialog
            icon_path = filedialog.askopenfilename(
                title="选择图标文件",
                filetypes=[("图标文件", "*.ico"), ("所有文件", "*.*")]
            )
            if icon_path:
                icon_var.set(icon_path)
        
        ttk.Button(icon_frame, text="浏览", command=select_icon).pack(side=tk.LEFT, padx=5)
        
        # 其他选项
        other_frame = tk.Frame(options_frame)
        other_frame.pack(fill=tk.X, padx=10, pady=5)
        
        hide_console = tk.BooleanVar(value=True)
        ttk.Checkbutton(other_frame, text="隐藏控制台窗口", variable=hide_console).pack(side=tk.LEFT, padx=5)
        
        one_file = tk.BooleanVar(value=True)
        ttk.Checkbutton(other_frame, text="打包为单文件", variable=one_file).pack(side=tk.LEFT, padx=5)
        
        # 创建打包按钮
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def start_pack():
            source_file = source_file_var.get().strip()
            output_path = output_path_var.get().strip()
            
            if not source_file or not output_path:
                messagebox.showerror("错误", "请选择源文件和输出路径")
                return
            
            if not os.path.exists(source_file):
                messagebox.showerror("错误", "源文件不存在")
                return
            
            # 开始打包
            try:
                if package_type.get() == "exe":
                    self.pack_to_exe(source_file, output_path, icon_var.get(), hide_console.get(), one_file.get())
                else:
                    self.pack_to_apk(source_file, output_path)
            except Exception as e:
                messagebox.showerror("打包失败", str(e))
        
        ttk.Button(button_frame, text="开始打包", command=start_pack).pack(side=tk.LEFT, padx=5)
        
        # 创建日志显示区域
        log_frame = tk.LabelFrame(self.content_frame, text="打包日志", font=self.font)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        log_text = ScrolledTextWithCustomScrollbars(log_frame, width=70, height=10, font=self.font)
        log_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 保存日志文本引用
        self.pack_log_text = log_text

    def show_about(self):
        self.show_welcome()
        messagebox.showinfo("关于", "御锋V1网络安全工具箱\n作者: 小白\n微信: ccyuwu8888\nQQ: 1544185387\n\n本工具完全免费开源\n账号密码请查看GitHub或联系作者")

    def base64_decode(self, input_widget, output_widget):
        try:
            data = input_widget.get("1.0", tk.END).strip()
            result = base64.b64decode(data.encode()).decode(errors='ignore')
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, result)
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"解码失败: {e}")

    def base64_encode(self, input_widget, output_widget):
        try:
            data = input_widget.get("1.0", tk.END).strip()
            result = base64.b64encode(data.encode()).decode()
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, result)
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"编码失败: {e}")

    def url_decode(self, input_widget, output_widget):
        try:
            from urllib.parse import unquote
            data = input_widget.get("1.0", tk.END).strip()
            result = unquote(data)
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, result)
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"解码失败: {e}")

    def url_encode(self, input_widget, output_widget):
        try:
            from urllib.parse import quote
            data = input_widget.get("1.0", tk.END).strip()
            result = quote(data)
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, result)
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"编码失败: {e}")

    def aes_encrypt(self, data_widget, key_widget, iv_widget, mode_var, output_widget):
        if not CRYPTO_AVAILABLE:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, "AES加密功能不可用，请安装pycryptodome模块")
            return
        try:
            data = pad(data_widget.get("1.0", tk.END).strip().encode(), AES.block_size)
            key = key_widget.get().encode()
            
            # 密钥长度检查和自动处理
            key_length = len(key)
            if key_length not in [16, 24, 32]:
                if key_length < 16:
                    # 密钥太短，用0填充到16字节
                    key = key + b'\x00' * (16 - key_length)
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度不足({key_length}字节)，已自动填充到16字节\n\n")
                elif key_length < 24:
                    # 密钥长度在16-24之间，截取到16字节
                    key = key[:16]
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度({key_length}字节)不符合AES标准，已截取为16字节\n\n")
                elif key_length < 32:
                    # 密钥长度在24-32之间，截取到24字节
                    key = key[:24]
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度({key_length}字节)不符合AES标准，已截取为24字节\n\n")
                else:
                    # 密钥太长，截取到32字节
                    key = key[:32]
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度({key_length}字节)超过AES标准，已截取为32字节\n\n")
            
            mode = mode_var.get()
            if mode == "ECB":
                cipher = AES.new(key, AES.MODE_ECB)
                result = base64.b64encode(cipher.encrypt(data)).decode()
            else:
                iv = iv_widget.get().encode()
                cipher = AES.new(key, AES.MODE_CBC, iv)
                result = base64.b64encode(cipher.encrypt(data)).decode()
            
            # 显示加密结果
            if output_widget.get("1.0", tk.END).strip().startswith("⚠️"):
                # 如果已有警告信息，追加结果
                output_widget.insert(tk.END, f"✅ 加密成功！\n\n🔐 加密结果:\n{result}")
            else:
                output_widget.delete("1.0", tk.END)
                output_widget.insert(tk.END, f"✅ 加密成功！\n\n🔐 加密结果:\n{result}")
                
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"❌ 加密失败: {e}\n\n💡 密钥长度要求:\n• AES-128: 16字节\n• AES-192: 24字节\n• AES-256: 32字节")

    def aes_decrypt(self, data_widget, key_widget, iv_widget, mode_var, output_widget):
        if not CRYPTO_AVAILABLE:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, "AES解密功能不可用，请安装pycryptodome模块")
            return
        try:
            data = base64.b64decode(data_widget.get("1.0", tk.END).strip())
            key = key_widget.get().encode()
            
            # 密钥长度检查和自动处理
            key_length = len(key)
            if key_length not in [16, 24, 32]:
                if key_length < 16:
                    # 密钥太短，用0填充到16字节
                    key = key + b'\x00' * (16 - key_length)
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度不足({key_length}字节)，已自动填充到16字节\n\n")
                elif key_length < 24:
                    # 密钥长度在16-24之间，截取到16字节
                    key = key[:16]
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度({key_length}字节)不符合AES标准，已截取为16字节\n\n")
                elif key_length < 32:
                    # 密钥长度在24-32之间，截取到24字节
                    key = key[:24]
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度({key_length}字节)不符合AES标准，已截取为24字节\n\n")
                else:
                    # 密钥太长，截取到32字节
                    key = key[:32]
                    output_widget.delete("1.0", tk.END)
                    output_widget.insert(tk.END, f"⚠️ 密钥长度({key_length}字节)超过AES标准，已截取为32字节\n\n")
            
            mode = mode_var.get()
            if mode == "ECB":
                cipher = AES.new(key, AES.MODE_ECB)
                result = unpad(cipher.decrypt(data), AES.block_size).decode(errors='ignore')
            else:
                iv = iv_widget.get().encode()
                cipher = AES.new(key, AES.MODE_CBC, iv)
                result = unpad(cipher.decrypt(data), AES.block_size).decode(errors='ignore')
            
            # 显示解密结果
            if output_widget.get("1.0", tk.END).strip().startswith("⚠️"):
                # 如果已有警告信息，追加结果
                output_widget.insert(tk.END, f"✅ 解密成功！\n\n🔓 解密结果:\n{result}")
            else:
                output_widget.delete("1.0", tk.END)
                output_widget.insert(tk.END, f"✅ 解密成功！\n\n🔓 解密结果:\n{result}")
                
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"❌ 解密失败: {e}\n\n💡 密钥长度要求:\n• AES-128: 16字节\n• AES-192: 24字节\n• AES-256: 32字节")

    def calculate_md5(self, input_widget, output_widget):
        try:
            data = input_widget.get("1.0", tk.END).strip().encode()
            result = hashlib.md5(data).hexdigest()
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, result)
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"计算失败: {e}")

    def calculate_sha(self, input_widget, sha_type, output_widget):
        try:
            data = input_widget.get("1.0", tk.END).strip().encode()
            if sha_type.get() == "sha1":
                result = hashlib.sha1(data).hexdigest()
            elif sha_type.get() == "sha256":
                result = hashlib.sha256(data).hexdigest()
            elif sha_type.get() == "sha512":
                result = hashlib.sha512(data).hexdigest()
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, result)
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"计算失败: {e}")

    def calculate_hmac(self, data_widget, key_widget, algorithm, output_widget):
        try:
            data = data_widget.get("1.0", tk.END).strip().encode()
            key = key_widget.get().encode()
            if algorithm.get() == "md5":
                result = hmac.new(key, data, hashlib.md5).hexdigest()
            elif algorithm.get() == "sha256":
                result = hmac.new(key, data, hashlib.sha256).hexdigest()
            elif algorithm.get() == "sha512":
                result = hmac.new(key, data, hashlib.sha512).hexdigest()
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, result)
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"计算失败: {e}")

    def dns_query(self, domain_entry, record_type_var, output_widget):
        if not DNS_AVAILABLE:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, "DNS查询功能不可用，请安装dnspython模块")
            return
        try:
            domain = domain_entry.get().strip()
            record_type = record_type_var.get()
            resolver = dns.resolver.Resolver()
            answers = resolver.resolve(domain, record_type)
            output_widget.delete("1.0", tk.END)
            for rdata in answers:
                output_widget.insert(tk.END, str(rdata) + "\n")
        except Exception as e:
            output_widget.delete("1.0", tk.END)
            output_widget.insert(tk.END, f"查询失败: {e}")

    def setup_fofa_api(self):
        email = simpledialog.askstring("FOFA邮箱", "请输入FOFA邮箱:")
        key = simpledialog.askstring("FOFA API Key", "请输入FOFA API Key:")
        if email and key:
            self.fofa_email.set(email)
            self.fofa_api_key.set(key)
            return True
        return False

    def fofa_query(self, query_entry, result_count_var, output_table):
        if not REQUESTS_AVAILABLE:
            messagebox.showerror("功能不可用", "网络请求功能不可用，请安装requests模块")
            return
        try:
            email = self.fofa_email.get()
            key = self.fofa_api_key.get()
            query = query_entry.get("1.0", tk.END).strip()
            size = int(result_count_var.get())
            url = f"https://fofa.info/api/v1/search/all?email={email}&key={key}&qbase64={base64.b64encode(query.encode()).decode()}&size={size}&fields=host,title,ip,port,country,city"
            resp = requests.get(url)
            data = resp.json()
            output_table.delete(*output_table.get_children())
            if data.get("results"):
                for idx, row in enumerate(data["results"], 1):
                    output_table.insert("", tk.END, values=(idx, *row))
            else:
                messagebox.showerror("查询失败", data.get("errmsg", "未知错误"))
        except Exception as e:
            messagebox.showerror("查询失败", str(e))

    def start_port_scan(self, host_entry, port_range_entry, scan_type_var, thread_count_var, output_table):
        # 这里只做简单演示，实际可用线程池并发
        import queue
        host = host_entry.get().strip()
        port_range = port_range_entry.get().strip()
        scan_type = scan_type_var.get()
        thread_count = int(thread_count_var.get())
        try:
            start, end = map(int, port_range.split('-'))
        except:
            messagebox.showerror("端口范围错误", "请输入正确的端口范围，如1-100")
            return
        self.is_scanning = True
        self.port_scan_results.clear()
        output_table.delete(*output_table.get_children())
        q = queue.Queue()
        for port in range(start, end+1):
            q.put(port)
        def scan():
            while not q.empty() and self.is_scanning:
                port = q.get()
                try:
                    if scan_type == "tcp":
                        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        s.settimeout(0.5)
                        result = s.connect_ex((host, port))
                        s.close()
                        if result == 0:
                            output_table.insert("", tk.END, values=(port, "开放", "", ""))
                    # UDP略
                except:
                    pass
        threads = []
        for _ in range(thread_count):
            t = threading.Thread(target=scan)
            t.start()
            threads.append(t)
        def wait_threads():
            for t in threads:
                t.join()
            self.is_scanning = False
        threading.Thread(target=wait_threads, daemon=True).start()

    def stop_port_scan(self):
        self.is_scanning = False

    def send_test_request(self, url_entry, method_var, headers_text, body_text, response_text, status_label):
        if not REQUESTS_AVAILABLE:
            response_text.delete("1.0", tk.END)
            response_text.insert(tk.END, "网络请求功能不可用，请安装requests模块")
            status_label.config(text="状态: 功能不可用", fg="red")
            return
        url = url_entry.get().strip()
        method = method_var.get()
        headers = {}
        for line in headers_text.get("1.0", tk.END).strip().splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                headers[k.strip()] = v.strip()
        data = body_text.get("1.0", tk.END).strip()
        
        # 更新状态为正在请求
        status_label.config(text="状态: 正在请求...", fg="blue")
        response_text.delete("1.0", tk.END)
        response_text.insert(tk.END, "正在发送请求...\n")
        
        try:
            resp = requests.request(method, url, headers=headers, data=data, timeout=30)
            
            # 清空响应区域并显示完整响应信息
            response_text.delete("1.0", tk.END)
            
            # 显示请求信息
            response_text.insert(tk.END, "=== 请求信息 ===\n")
            response_text.insert(tk.END, f"URL: {url}\n")
            response_text.insert(tk.END, f"方法: {method}\n")
            response_text.insert(tk.END, f"请求头: {headers}\n")
            if data:
                response_text.insert(tk.END, f"请求体: {data}\n")
            response_text.insert(tk.END, "\n")
            
            # 显示响应状态
            response_text.insert(tk.END, "=== 响应状态 ===\n")
            response_text.insert(tk.END, f"状态码: {resp.status_code}\n")
            response_text.insert(tk.END, f"状态描述: {resp.reason}\n")
            response_text.insert(tk.END, f"响应时间: {resp.elapsed.total_seconds():.2f}秒\n")
            response_text.insert(tk.END, "\n")
            
            # 显示响应头
            response_text.insert(tk.END, "=== 响应头 ===\n")
            for key, value in resp.headers.items():
                response_text.insert(tk.END, f"{key}: {value}\n")
            response_text.insert(tk.END, "\n")
            
            # 显示响应体
            response_text.insert(tk.END, "=== 响应体 ===\n")
            try:
                # 尝试格式化JSON
                if 'application/json' in resp.headers.get('content-type', ''):
                    import json
                    formatted_json = json.dumps(resp.json(), indent=2, ensure_ascii=False)
                    response_text.insert(tk.END, formatted_json)
                else:
                    response_text.insert(tk.END, resp.text)
            except:
                response_text.insert(tk.END, resp.text)
            
            # 更新状态
            if resp.status_code < 400:
                status_label.config(text=f"状态: {resp.status_code} - {resp.reason}", fg="green")
            else:
                status_label.config(text=f"状态: {resp.status_code} - {resp.reason}", fg="orange")
            
            # 保存到历史记录
            self.test_request_history.append((url, method, headers, data))
            
        except requests.exceptions.Timeout:
            response_text.delete("1.0", tk.END)
            response_text.insert(tk.END, "请求超时（30秒）")
            status_label.config(text="状态: 超时", fg="red")
        except requests.exceptions.ConnectionError:
            response_text.delete("1.0", tk.END)
            response_text.insert(tk.END, "连接错误，请检查网络连接和URL")
            status_label.config(text="状态: 连接错误", fg="red")
        except Exception as e:
            response_text.delete("1.0", tk.END)
            response_text.insert(tk.END, f"请求失败: {e}")
            status_label.config(text="状态: 失败", fg="red")

    def resend_test_request(self, history_combo, url_entry, method_var, headers_text, body_text, response_text, status_label):
        idx = history_combo.current()
        if idx < 0 or idx >= len(self.test_request_history):
            return
        url, method, headers, data = self.test_request_history[idx]
        url_entry.delete(0, tk.END)
        url_entry.insert(0, url)
        method_var.set(method)
        headers_text.delete("1.0", tk.END)
        for k, v in headers.items():
            headers_text.insert(tk.END, f"{k}: {v}\n")
        body_text.delete("1.0", tk.END)
        body_text.insert(tk.END, data)
        self.send_test_request(url_entry, method_var, headers_text, body_text, response_text, status_label)

    def pack_to_exe(self, source_file, output_path, icon_path, hide_console, one_file):
        """打包为EXE文件"""
        self.pack_log_text.insert(tk.END, "开始打包为EXE文件...\n")
        
        # 检查是否安装了pyinstaller
        try:
            import PyInstaller
        except ImportError:
            self.pack_log_text.insert(tk.END, "正在安装PyInstaller...\n")
            subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        
        # 构建pyinstaller命令
        cmd = [sys.executable, "-m", "PyInstaller"]
        
        if hide_console:
            cmd.append("--windowed")
        
        if one_file:
            cmd.append("--onefile")
        
        if icon_path and os.path.exists(icon_path):
            cmd.extend(["--icon", icon_path])
        
        cmd.extend(["--distpath", os.path.dirname(output_path)])
        cmd.extend(["--name", os.path.splitext(os.path.basename(output_path))[0]])
        cmd.append(source_file)
        
        self.pack_log_text.insert(tk.END, f"执行命令: {' '.join(cmd)}\n")
        
        # 执行打包
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            self.pack_log_text.insert(tk.END, "打包成功！\n")
            self.pack_log_text.insert(tk.END, result.stdout)
        else:
            self.pack_log_text.insert(tk.END, "打包失败！\n")
            self.pack_log_text.insert(tk.END, result.stderr)
            raise Exception("打包失败")

    def pack_to_apk(self, source_file, output_path):
        """打包为APK文件"""
        self.pack_log_text.insert(tk.END, "开始打包为APK文件...\n")
        self.pack_log_text.insert(tk.END, "APK打包功能需要安装buildozer，请参考以下步骤：\n")
        self.pack_log_text.insert(tk.END, "1. 安装buildozer: pip install buildozer\n")
        self.pack_log_text.insert(tk.END, "2. 初始化buildozer.spec文件\n")
        self.pack_log_text.insert(tk.END, "3. 配置buildozer.spec文件\n")
        self.pack_log_text.insert(tk.END, "4. 运行buildozer android debug\n")
        self.pack_log_text.insert(tk.END, "注意：APK打包需要Linux环境或WSL\n")

    def show_dependency_manager(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建依赖管理工具界面
        title_label = tk.Label(self.content_frame, text="依赖管理工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建选择方式框架
        select_frame = tk.Frame(self.content_frame)
        select_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(select_frame, text="选择分析方式:", font=self.font).pack(side=tk.LEFT, padx=5)
        
        selected_files = []
        selected_directory = ""
        
        def select_files():
            from tkinter import filedialog
            files = filedialog.askopenfilenames(
                title="选择Python脚本",
                filetypes=[("Python文件", "*.py"), ("所有文件", "*.*")]
            )
            selected_files.clear()
            selected_files.extend(files)
            file_list.delete(0, tk.END)
            for file in selected_files:
                file_list.insert(tk.END, os.path.basename(file))
            status_label.config(text=f"已选择 {len(selected_files)} 个文件")
        
        def select_directory():
            from tkinter import filedialog
            directory = filedialog.askdirectory(title="选择目录")
            if directory:
                selected_directory = directory
                # 扫描目录下的所有Python文件
                py_files = []
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        if file.endswith('.py'):
                            py_files.append(os.path.join(root, file))
                
                selected_files.clear()
                selected_files.extend(py_files)
                file_list.delete(0, tk.END)
                for file in selected_files:
                    file_list.insert(tk.END, os.path.relpath(file, directory))
                status_label.config(text=f"已扫描目录，发现 {len(selected_files)} 个Python文件")
        
        def auto_scan_current():
            # 自动扫描当前目录
            current_dir = os.getcwd()
            py_files = []
            for root, dirs, files in os.walk(current_dir):
                for file in files:
                    if file.endswith('.py'):
                        py_files.append(os.path.join(root, file))
            
            selected_files.clear()
            selected_files.extend(py_files)
            file_list.delete(0, tk.END)
            for file in selected_files:
                file_list.insert(tk.END, os.path.relpath(file, current_dir))
            status_label.config(text=f"已扫描当前目录，发现 {len(selected_files)} 个Python文件")
        
        ttk.Button(select_frame, text="选择文件", command=select_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="选择目录", command=select_directory).pack(side=tk.LEFT, padx=5)
        ttk.Button(select_frame, text="扫描当前目录", command=auto_scan_current).pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        status_label = tk.Label(select_frame, text="请选择要分析的文件或目录", font=self.font, fg="blue")
        status_label.pack(side=tk.RIGHT, padx=5)
        
        # 显示选中的文件列表
        file_list_frame = tk.Frame(self.content_frame)
        file_list_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(file_list_frame, text="已选择的文件:", font=self.font).pack(anchor=tk.W)
        file_list = tk.Listbox(file_list_frame, height=4, font=self.font)
        file_list.pack(fill=tk.X)
        
        # 创建按钮框架
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def check_dependencies():
            if not selected_files:
                messagebox.showwarning("警告", "请先选择要分析的Python脚本文件。")
                return
                
            progress_text.delete("1.0", tk.END)
            progress_text.insert(tk.END, f"正在分析 {len(selected_files)} 个Python脚本...\n")
            
            all_dependencies = set()
            
            # 分析每个脚本的依赖
            for script in selected_files:
                progress_text.insert(tk.END, f"\n分析 {os.path.basename(script)} 的依赖...\n")
                try:
                    with open(script, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 使用正则表达式提取import语句
                    import_pattern = re.compile(r'^\s*import\s+([a-zA-Z0-9_.]+)', re.MULTILINE)
                    from_pattern = re.compile(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import', re.MULTILINE)
                    
                    imports = import_pattern.findall(content)
                    from_imports = from_pattern.findall(content)
                    
                    # 提取顶级包名
                    dependencies = set()
                    for imp in imports:
                        package = imp.split('.')[0]
                        dependencies.add(package)
                    
                    for imp in from_imports:
                        package = imp.split('.')[0]
                        dependencies.add(package)
                    
                    # 排除Python标准库
                    stdlib_packages = {'sys', 'os', 'json', 're', 'math', 'random', 'datetime', 'time', 'io', 'string',
                                       'tkinter', 'threading', 'subprocess', 'hmac', 'socket', 'platform',
                                       'base64', 'hashlib', 'dns', 'requests', 'Crypto', 'urllib', 'concurrent',
                                       'shutil', 'tempfile', 'zipfile', 'py_compile', 'importlib', 'queue',
                                       'collections', 'itertools', 'functools', 'contextlib', 'pathlib'}
                    dependencies = {d for d in dependencies if d not in stdlib_packages}
                    
                    if dependencies:
                        progress_text.insert(tk.END, f"发现依赖: {', '.join(dependencies)}\n")
                        all_dependencies.update(dependencies)
                    else:
                        progress_text.insert(tk.END, "未发现外部依赖。\n")
                except Exception as e:
                    progress_text.insert(tk.END, f"分析失败: {str(e)}\n")
            
            if not all_dependencies:
                progress_text.insert(tk.END, "\n所有脚本均不需要安装额外依赖。\n")
                progress_text.insert(tk.END, "依赖检测完成。\n")
                return
            
            # 显示发现的依赖
            progress_text.insert(tk.END, f"\n共发现 {len(all_dependencies)} 个需要安装的依赖:\n")
            for dep in sorted(all_dependencies):
                progress_text.insert(tk.END, f"- {dep}\n")
            
            # 启用安装按钮
            install_button.config(state="normal")
            progress_text.insert(tk.END, "\n点击'开始安装所有依赖'按钮安装所需依赖。\n")
        
        def install_deps():
            progress_text.insert(tk.END, "\n开始并行安装依赖...\n")
            
            # 获取所有依赖
            all_deps = set()
            for script in selected_files:
                try:
                    with open(script, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    import_pattern = re.compile(r'^\s*import\s+([a-zA-Z0-9_.]+)', re.MULTILINE)
                    from_pattern = re.compile(r'^\s*from\s+([a-zA-Z0-9_.]+)\s+import', re.MULTILINE)
                    
                    imports = import_pattern.findall(content)
                    from_imports = from_pattern.findall(content)
                    
                    dependencies = set()
                    for imp in imports:
                        package = imp.split('.')[0]
                        dependencies.add(package)
                    
                    for imp in from_imports:
                        package = imp.split('.')[0]
                        dependencies.add(package)
                    
                    stdlib_packages = {'sys', 'os', 'json', 're', 'math', 'random', 'datetime', 'time', 'io', 'string',
                                       'tkinter', 'threading', 'subprocess', 'hmac', 'socket', 'platform',
                                       'base64', 'hashlib', 'dns', 'requests', 'Crypto', 'urllib', 'concurrent',
                                       'shutil', 'tempfile', 'zipfile', 'py_compile', 'importlib', 'queue',
                                       'collections', 'itertools', 'functools', 'contextlib', 'pathlib'}
                    dependencies = {d for d in dependencies if d not in stdlib_packages}
                    all_deps.update(dependencies)
                except:
                    pass
            
            if not all_deps:
                progress_text.insert(tk.END, "没有发现需要安装的依赖。\n")
                return
            
            # 使用线程池并行安装依赖，提高速度
            def install_package(dep):
                progress_text.insert(tk.END, f"\n正在安装 {dep}...\n")
                try:
                    # 使用subprocess调用pip安装依赖，添加--no-cache-dir选项加快速度
                    result = subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--no-cache-dir", dep],
                        capture_output=True,
                        text=True,
                        check=True
                    )
                    progress_text.insert(tk.END, result.stdout)
                    progress_text.insert(tk.END, f"\n{dep} 安装成功。\n")
                    return True, dep
                except subprocess.CalledProcessError as e:
                    progress_text.insert(tk.END, f"\n安装失败: {e.stderr}\n")
                    return False, dep
                except Exception as e:
                    progress_text.insert(tk.END, f"\n安装时发生未知错误: {str(e)}\n")
                    return False, dep
            
            # 使用线程池并行安装，默认使用CPU核心数*5的线程数
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = list(executor.map(install_package, all_deps))
            
            success_count = sum(1 for success, _ in results if success)
            total_count = len(results)
            
            progress_text.insert(tk.END, f"\n依赖安装完成。成功: {success_count}/{total_count}\n")
            
            if success_count == total_count:
                progress_text.insert(tk.END, "所有依赖安装成功！\n")
            else:
                progress_text.insert(tk.END, "部分依赖安装失败，请检查网络连接或手动安装。\n")
        
        ttk.Button(button_frame, text="开始分析依赖", command=check_dependencies).pack(side=tk.LEFT, padx=5)
        install_button = ttk.Button(button_frame, text="开始安装所有依赖", command=install_deps, state="disabled")
        install_button.pack(side=tk.LEFT, padx=5)
        
        # 创建进度文本
        progress_frame = tk.LabelFrame(self.content_frame, text="分析日志", font=self.font)
        progress_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        progress_text = ScrolledTextWithCustomScrollbars(progress_frame, font=self.font)
        progress_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        progress_text.insert(tk.END, "请选择要分析的Python脚本文件或目录，然后点击'开始分析依赖'按钮。\n")

    def show_directory_tools(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建目录工具界面
        title_label = tk.Label(self.content_frame, text="目录工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建目录选择框架
        dir_frame = tk.Frame(self.content_frame)
        dir_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(dir_frame, text="目标目录:", font=self.font).pack(side=tk.LEFT, padx=5)
        dir_var = tk.StringVar()
        dir_entry = tk.Entry(dir_frame, textvariable=dir_var, width=50, font=self.font)
        dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def select_directory():
            from tkinter import filedialog
            directory = filedialog.askdirectory(title="选择目录")
            if directory:
                dir_var.set(directory)
        
        ttk.Button(dir_frame, text="浏览", command=select_directory).pack(side=tk.LEFT, padx=5)
        
        # 创建工具类型选择
        tool_frame = tk.Frame(self.content_frame)
        tool_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(tool_frame, text="工具类型:", font=self.font).pack(side=tk.LEFT, padx=5)
        
        tool_type = tk.StringVar(value="file_explorer")
        ttk.Radiobutton(tool_frame, text="文件管理器", variable=tool_type, value="file_explorer").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tool_frame, text="命令行", variable=tool_type, value="cmd").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tool_frame, text="PowerShell", variable=tool_type, value="powershell").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tool_frame, text="VS Code", variable=tool_type, value="vscode").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(tool_frame, text="记事本", variable=tool_type, value="notepad").pack(side=tk.LEFT, padx=5)
        
        # 创建按钮框架
        button_frame = tk.Frame(self.content_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def open_directory():
            directory = dir_var.get().strip()
            if not directory:
                messagebox.showerror("错误", "请选择目录")
                return
            
            if not os.path.exists(directory):
                messagebox.showerror("错误", "目录不存在")
                return
            
            tool = tool_type.get()
            try:
                if tool == "file_explorer":
                    if platform.system() == "Windows":
                        os.startfile(directory)
                    elif platform.system() == "Darwin":  # macOS
                        subprocess.run(["open", directory])
                    else:  # Linux
                        subprocess.run(["xdg-open", directory])
                elif tool == "cmd":
                    if platform.system() == "Windows":
                        subprocess.Popen(["cmd", "/k", "cd", "/d", directory])
                    else:
                        subprocess.Popen(["gnome-terminal", "--working-directory", directory])
                elif tool == "powershell":
                    if platform.system() == "Windows":
                        subprocess.Popen(["powershell", "-NoExit", "-Command", f"cd '{directory}'"])
                    else:
                        messagebox.showinfo("提示", "PowerShell仅在Windows系统上可用")
                elif tool == "vscode":
                    subprocess.Popen(["code", directory])
                elif tool == "notepad":
                    if platform.system() == "Windows":
                        subprocess.Popen(["notepad", directory])
                    else:
                        subprocess.Popen(["gedit", directory])
                
                messagebox.showinfo("成功", f"已使用 {tool} 打开目录: {directory}")
            except Exception as e:
                messagebox.showerror("错误", f"打开目录失败: {e}")
        
        ttk.Button(button_frame, text="打开目录", command=open_directory).pack(side=tk.LEFT, padx=5)
        
        # 创建快速访问框架
        quick_frame = tk.LabelFrame(self.content_frame, text="快速访问", font=self.font)
        quick_frame.pack(fill=tk.X, padx=10, pady=10)
        
        def open_current_dir():
            dir_var.set(os.getcwd())
            open_directory()
        
        def open_desktop():
            desktop = os.path.join(os.path.expanduser("~"), "Desktop")
            dir_var.set(desktop)
            open_directory()
        
        def open_documents():
            documents = os.path.join(os.path.expanduser("~"), "Documents")
            dir_var.set(documents)
            open_directory()
        
        def open_downloads():
            downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            dir_var.set(downloads)
            open_directory()
        
        ttk.Button(quick_frame, text="当前目录", command=open_current_dir).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(quick_frame, text="桌面", command=open_desktop).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(quick_frame, text="文档", command=open_documents).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(quick_frame, text="下载", command=open_downloads).pack(side=tk.LEFT, padx=5, pady=5)
        
        # 创建最近访问列表
        recent_frame = tk.LabelFrame(self.content_frame, text="最近访问", font=self.font)
        recent_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        recent_list = tk.Listbox(recent_frame, font=self.font)
        recent_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 添加一些示例路径
        recent_paths = [
            os.getcwd(),
            os.path.join(os.path.expanduser("~"), "Desktop"),
            os.path.join(os.path.expanduser("~"), "Documents"),
            os.path.join(os.path.expanduser("~"), "Downloads")
        ]
        
        for path in recent_paths:
            if os.path.exists(path):
                recent_list.insert(tk.END, path)
        
        def on_recent_select(event):
            selection = recent_list.curselection()
            if selection:
                selected_path = recent_list.get(selection[0])
                dir_var.set(selected_path)
        
        recent_list.bind('<<ListboxSelect>>', on_recent_select)

    def show_sqlmap_tool(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 获取当前脚本的绝对路径，确保sqlmap路径健壮
        base_dir = os.path.dirname(os.path.abspath(__file__))
        sqlmap_path = os.path.join(base_dir, "CN_Sqlmap-main", "sqlmap.py")
        if not os.path.exists(sqlmap_path):
            # 创建错误提示
            error_frame = tk.Frame(self.content_frame)
            error_frame.pack(expand=True)
            tk.Label(error_frame, text="SQLMap未找到", font=self.font, fg="red").pack(pady=20)
            tk.Label(error_frame, text="请确保CN_Sqlmap-main目录存在且包含sqlmap.py文件", font=self.font).pack()
            def download_sqlmap():
                messagebox.showinfo("提示", "请手动下载SQLMap并解压到CN_Sqlmap-main目录")
            ttk.Button(error_frame, text="下载SQLMap", command=download_sqlmap).pack(pady=10)
            return
        
        # 创建主滚动框架
        main_canvas = tk.Canvas(self.content_frame, bg="#F5F5F5")
        main_scrollbar = CustomScrollbar(self.content_frame, orient="vertical")
        scrollable_frame = tk.Frame(main_canvas, bg="#F5F5F5")
        
        # 配置滚动
        scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        main_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=main_scrollbar.set)
        main_scrollbar.configure(command=main_canvas.yview)
        
        # 鼠标滚轮绑定
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # 布局主滚动区域
        main_canvas.pack(side="left", fill="both", expand=True)
        main_scrollbar.pack(side="right", fill="y")
        
        # 创建标题
        title_label = tk.Label(scrollable_frame, text="SQLMap工具", font=('Microsoft YaHei UI', 18, 'bold'), 
                              bg="#F5F5F5", fg="#2C3E50")
        title_label.pack(pady=(20, 10))
        
        # 创建输入方式选择框架
        input_method_frame = tk.LabelFrame(scrollable_frame, text="输入方式", font=self.font, 
                                         bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        input_method_frame.pack(fill=tk.X, padx=20, pady=10)
        
        input_method = tk.StringVar(value="url")
        ttk.Radiobutton(input_method_frame, text="URL参数", variable=input_method, value="url").pack(side=tk.LEFT, padx=15, pady=10)
        ttk.Radiobutton(input_method_frame, text="请求包文件", variable=input_method, value="request").pack(side=tk.LEFT, padx=15, pady=10)
        
        # 创建URL输入框架
        url_frame = tk.LabelFrame(scrollable_frame, text="URL配置", font=self.font, 
                                bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        url_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(url_frame, text="目标URL:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=10, pady=10)
        url_var = tk.StringVar()
        url_entry = tk.Entry(url_frame, textvariable=url_var, width=60, font=self.font, 
                           relief="solid", bd=1, bg="white")
        url_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        url_entry.insert(0, "http://example.com/vulnerable.php?id=1")
        
        # 创建参数输入框架
        param_frame = tk.LabelFrame(scrollable_frame, text="参数配置", font=self.font, 
                                  bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        param_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(param_frame, text="参数:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=10, pady=10)
        param_var = tk.StringVar()
        param_entry = tk.Entry(param_frame, textvariable=param_var, width=60, font=self.font, 
                             relief="solid", bd=1, bg="white")
        param_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        param_entry.insert(0, "id")
        
        # 创建请求包文件选择框架
        request_file_frame = tk.LabelFrame(scrollable_frame, text="请求包文件", font=self.font, 
                                         bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        request_file_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(request_file_frame, text="请求包文件:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=10, pady=10)
        request_file_var = tk.StringVar()
        request_file_entry = tk.Entry(request_file_frame, textvariable=request_file_var, width=50, font=self.font, 
                                    relief="solid", bd=1, bg="white")
        request_file_entry.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.X, expand=True)
        
        def select_request_file():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(
                title="选择请求包文件",
                filetypes=[
                    ("HTTP请求文件", "*.txt"),
                    ("所有文件", "*.*")
                ]
            )
            if file_path:
                request_file_var.set(file_path)
                # 自动解析请求包中的参数
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # 简单的参数提取逻辑
                    if '?' in content and '=' in content:
                        # 提取URL中的参数
                        url_match = re.search(r'GET\s+([^\s]+)', content)
                        if url_match:
                            url = url_match.group(1)
                            url_var.set(url)
                            # 提取参数名
                            param_match = re.search(r'[?&](\w+)=', url)
                            if param_match:
                                param_var.set(param_match.group(1))
                except Exception as e:
                    print(f"解析请求包失败: {e}")
        
        ttk.Button(request_file_frame, text="浏览", command=select_request_file, 
                  style='Accent.TButton').pack(side=tk.LEFT, padx=10, pady=10)
        
        # 创建请求包预览框架
        request_preview_frame = tk.LabelFrame(scrollable_frame, text="请求包预览", font=self.font, 
                                            bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        request_preview_frame.pack(fill=tk.X, padx=20, pady=10)
        
        request_preview_text = ScrolledTextWithCustomScrollbars(request_preview_frame, width=80, height=8, font=self.font)
        request_preview_text.pack(padx=10, pady=10, fill=tk.X)
        
        def preview_request_file():
            file_path = request_file_var.get().strip()
            if not file_path or not os.path.exists(file_path):
                request_preview_text.delete("1.0", tk.END)
                request_preview_text.insert(tk.END, "请选择有效的请求包文件")
                return
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                request_preview_text.delete("1.0", tk.END)
                request_preview_text.insert(tk.END, content)
            except Exception as e:
                request_preview_text.delete("1.0", tk.END)
                request_preview_text.insert(tk.END, f"读取文件失败: {e}")
        
        ttk.Button(request_preview_frame, text="预览请求包", command=preview_request_file, 
                  style='Accent.TButton').pack(pady=10)
        
        # 创建数据库类型选择
        db_frame = tk.LabelFrame(scrollable_frame, text="数据库类型", font=self.font, 
                               bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        db_frame.pack(fill=tk.X, padx=20, pady=10)
        
        db_type = tk.StringVar(value="mysql")
        db_types = ["mysql", "mssql", "oracle", "postgresql", "sqlite", "access", "firebird", "sybase"]
        for i, db in enumerate(db_types):
            ttk.Radiobutton(db_frame, text=db.upper(), variable=db_type, value=db).pack(side=tk.LEFT, padx=10, pady=10)
        
        # 创建注入技术选择
        tech_frame = tk.LabelFrame(scrollable_frame, text="注入技术", font=self.font, 
                                 bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        tech_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tech_type = tk.StringVar(value="B")
        tech_options = [
            ("布尔盲注", "B"),
            ("时间盲注", "T"),
            ("联合查询", "U"),
            ("错误注入", "E"),
            ("堆叠注入", "S")
        ]
        for text, value in tech_options:
            ttk.Radiobutton(tech_frame, text=text, variable=tech_type, value=value).pack(side=tk.LEFT, padx=10, pady=10)
        
        # 创建选项框架
        options_frame = tk.LabelFrame(scrollable_frame, text="高级选项", font=self.font, 
                                    bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        options_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # 第一行选项
        opt1_frame = tk.Frame(options_frame, bg="#F5F5F5")
        opt1_frame.pack(fill=tk.X, padx=10, pady=10)
        
        level_var = tk.StringVar(value="1")
        tk.Label(opt1_frame, text="检测等级:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=10)
        level_combo = ttk.Combobox(opt1_frame, textvariable=level_var, values=["1", "2", "3", "4", "5"], width=8)
        level_combo.pack(side=tk.LEFT, padx=5)
        
        risk_var = tk.StringVar(value="1")
        tk.Label(opt1_frame, text="风险等级:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=10)
        risk_combo = ttk.Combobox(opt1_frame, textvariable=risk_var, values=["1", "2", "3"], width=8)
        risk_combo.pack(side=tk.LEFT, padx=5)
        
        threads_var = tk.StringVar(value="10")
        tk.Label(opt1_frame, text="线程数:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=10)
        threads_combo = ttk.Combobox(opt1_frame, textvariable=threads_var, values=["1", "5", "10", "20", "50"], width=8)
        threads_combo.pack(side=tk.LEFT, padx=5)
        
        # 第二行选项
        opt2_frame = tk.Frame(options_frame, bg="#F5F5F5")
        opt2_frame.pack(fill=tk.X, padx=10, pady=10)
        
        dump_data = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt2_frame, text="获取数据", variable=dump_data).pack(side=tk.LEFT, padx=10)
        
        dump_tables = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt2_frame, text="获取表名", variable=dump_tables).pack(side=tk.LEFT, padx=10)
        
        dump_columns = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt2_frame, text="获取列名", variable=dump_columns).pack(side=tk.LEFT, padx=10)
        
        current_db = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt2_frame, text="当前数据库", variable=current_db).pack(side=tk.LEFT, padx=10)
        
        all_dbs = tk.BooleanVar(value=False)
        ttk.Checkbutton(opt2_frame, text="所有数据库", variable=all_dbs).pack(side=tk.LEFT, padx=10)
        
        # 第三行选项
        opt3_frame = tk.Frame(options_frame, bg="#F5F5F5")
        opt3_frame.pack(fill=tk.X, padx=10, pady=10)
        
        batch_mode = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt3_frame, text="批处理模式", variable=batch_mode).pack(side=tk.LEFT, padx=10)
        
        random_agent = tk.BooleanVar(value=True)
        ttk.Checkbutton(opt3_frame, text="随机User-Agent", variable=random_agent).pack(side=tk.LEFT, padx=10)
        
        proxy_var = tk.StringVar()
        tk.Label(opt3_frame, text="代理:", font=self.font, bg="#F5F5F5").pack(side=tk.LEFT, padx=10)
        proxy_entry = tk.Entry(opt3_frame, textvariable=proxy_var, width=25, font=self.font, 
                             relief="solid", bd=1, bg="white")
        proxy_entry.pack(side=tk.LEFT, padx=5)
        proxy_entry.insert(0, "http://127.0.0.1:8080")
        
        # 创建命令预览
        preview_frame = tk.LabelFrame(scrollable_frame, text="生成的命令", font=self.font, 
                                    bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        preview_frame.pack(fill=tk.X, padx=20, pady=10)
        
        preview_text = ScrolledTextWithCustomScrollbars(preview_frame, width=80, height=6, font=self.font)
        preview_text.pack(padx=10, pady=10, fill=tk.X)
        
        def update_preview():
            method = input_method.get()
            url = url_var.get().strip()
            param = param_var.get().strip()
            request_file = request_file_var.get().strip()
            db = db_type.get()
            tech = tech_type.get()
            level = level_var.get()
            risk = risk_var.get()
            threads = threads_var.get()
            
            # 构建SQLMap命令
            if method == "url":
                if not url or not param:
                    preview_text.delete("1.0", tk.END)
                    preview_text.insert(tk.END, "请填写目标URL和参数")
                    return
                cmd_parts = [sys.executable, sqlmap_path, "-u", url, "-p", param]
            else:  # request file
                if not request_file or not os.path.exists(request_file):
                    preview_text.delete("1.0", tk.END)
                    preview_text.insert(tk.END, "请选择有效的请求包文件")
                    return
                cmd_parts = [sys.executable, sqlmap_path, "-r", request_file]
            
            # 添加数据库类型
            if db != "mysql":
                cmd_parts.extend(["--dbms", db])
            
            # 添加注入技术
            if tech != "B":
                cmd_parts.extend(["--technique", tech])
            
            # 添加检测等级和风险等级
            cmd_parts.extend(["--level", level, "--risk", risk])
            
            # 添加线程数
            cmd_parts.extend(["--threads", threads])
            
            # 添加选项
            if dump_data.get():
                cmd_parts.append("--dump")
            if dump_tables.get():
                cmd_parts.append("--tables")
            if dump_columns.get():
                cmd_parts.append("--columns")
            if current_db.get():
                cmd_parts.append("--current-db")
            if all_dbs.get():
                cmd_parts.append("--dbs")
            if batch_mode.get():
                cmd_parts.append("--batch")
            if random_agent.get():
                cmd_parts.append("--random-agent")
            if proxy_var.get().strip():
                cmd_parts.extend(["--proxy", proxy_var.get().strip()])
            
            # 显示命令
            preview_text.delete("1.0", tk.END)
            preview_text.insert(tk.END, " ".join(cmd_parts))
        
        # 绑定更新事件
        input_method.trace("w", lambda *args: update_preview())
        url_var.trace("w", lambda *args: update_preview())
        param_var.trace("w", lambda *args: update_preview())
        request_file_var.trace("w", lambda *args: update_preview())
        db_type.trace("w", lambda *args: update_preview())
        tech_type.trace("w", lambda *args: update_preview())
        level_var.trace("w", lambda *args: update_preview())
        risk_var.trace("w", lambda *args: update_preview())
        threads_var.trace("w", lambda *args: update_preview())
        proxy_var.trace("w", lambda *args: update_preview())
        
        # 创建按钮框架
        button_frame = tk.Frame(scrollable_frame, bg="#F5F5F5")
        button_frame.pack(fill=tk.X, padx=20, pady=20)
        
        def run_sqlmap():
            method = input_method.get()
            if method == "url":
                url = url_var.get().strip()
                param = param_var.get().strip()
                if not url or not param:
                    messagebox.showerror("错误", "请填写目标URL和参数")
                    return
            else:
                request_file = request_file_var.get().strip()
                if not request_file or not os.path.exists(request_file):
                    messagebox.showerror("错误", "请选择有效的请求包文件")
                    return
            
            # 获取生成的命令
            cmd = preview_text.get("1.0", tk.END).strip()
            if not cmd or cmd in ["请填写目标URL和参数", "请选择有效的请求包文件"]:
                messagebox.showerror("错误", "请先生成有效的命令")
                return
            
            # 确认执行
            result = messagebox.askyesno("确认", f"确定要执行以下命令吗？\n\n{cmd}")
            if not result:
                return
            
            try:
                # 执行SQLMap命令
                subprocess.Popen(cmd.split(), cwd=os.path.dirname(sqlmap_path))
                messagebox.showinfo("成功", "SQLMap已启动，请查看命令行窗口")
            except Exception as e:
                messagebox.showerror("错误", f"执行失败: {e}")
        
        def copy_command():
            cmd = preview_text.get("1.0", tk.END).strip()
            if cmd and cmd not in ["请填写目标URL和参数", "请选择有效的请求包文件"]:
                self.root.clipboard_clear()
                self.root.clipboard_append(cmd)
                messagebox.showinfo("成功", "命令已复制到剪贴板")
        
        def save_command():
            cmd = preview_text.get("1.0", tk.END).strip()
            if cmd and cmd not in ["请填写目标URL和参数", "请选择有效的请求包文件"]:
                from tkinter import filedialog
                file_path = filedialog.asksaveasfilename(
                    title="保存命令",
                    defaultextension=".bat",
                    filetypes=[("批处理文件", "*.bat"), ("文本文件", "*.txt"), ("所有文件", "*.*")]
                )
                if file_path:
                    try:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(cmd)
                        messagebox.showinfo("成功", f"命令已保存到: {file_path}")
                    except Exception as e:
                        messagebox.showerror("错误", f"保存失败: {e}")
        
        # 创建按钮样式
        button_style = ttk.Style()
        button_style.configure('Action.TButton', font=('Microsoft YaHei UI', 10, 'bold'))
        
        ttk.Button(button_frame, text="生成命令", command=update_preview, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="复制命令", command=copy_command, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="保存命令", command=save_command, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="执行SQLMap", command=run_sqlmap, 
                  style='Action.TButton').pack(side=tk.LEFT, padx=10)
        
        # 创建预设模板框架
        template_frame = tk.LabelFrame(scrollable_frame, text="预设模板", font=self.font, 
                                     bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        template_frame.pack(fill=tk.X, padx=20, pady=10)
        
        def load_template(template_name):
            templates = {
                "基础检测": {
                    "method": "url",
                    "url": "http://example.com/vulnerable.php?id=1",
                    "param": "id",
                    "db": "mysql",
                    "tech": "B",
                    "level": "1",
                    "risk": "1",
                    "threads": "10"
                },
                "完整扫描": {
                    "method": "url",
                    "url": "http://example.com/vulnerable.php?id=1",
                    "param": "id",
                    "db": "mysql",
                    "tech": "B",
                    "level": "5",
                    "risk": "3",
                    "threads": "20"
                },
                "数据获取": {
                    "method": "url",
                    "url": "http://example.com/vulnerable.php?id=1",
                    "param": "id",
                    "db": "mysql",
                    "tech": "U",
                    "level": "3",
                    "risk": "2",
                    "threads": "10"
                },
                "请求包检测": {
                    "method": "request",
                    "url": "",
                    "param": "",
                    "db": "mysql",
                    "tech": "B",
                    "level": "2",
                    "risk": "2",
                    "threads": "10"
                }
            }
            
            if template_name in templates:
                template = templates[template_name]
                input_method.set(template["method"])
                url_var.set(template["url"])
                param_var.set(template["param"])
                db_type.set(template["db"])
                tech_type.set(template["tech"])
                level_var.set(template["level"])
                risk_var.set(template["risk"])
                threads_var.set(template["threads"])
                update_preview()
        
        template_buttons = [
            ("基础检测", "基础检测"),
            ("完整扫描", "完整扫描"),
            ("数据获取", "数据获取"),
            ("请求包检测", "请求包检测")
        ]
        
        for text, template_name in template_buttons:
            ttk.Button(template_frame, text=text, 
                      command=lambda tn=template_name: load_template(tn)).pack(side=tk.LEFT, padx=10, pady=10)
        
        # 创建请求包示例框架
        example_frame = tk.LabelFrame(scrollable_frame, text="请求包示例", font=self.font, 
                                    bg="#F5F5F5", fg="#34495E", relief="groove", bd=2)
        example_frame.pack(fill=tk.X, padx=20, pady=10)
        
        example_text = """GET /vulnerable.php?id=1&name=test HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Connection: close

"""
        
        example_text_widget = ScrolledTextWithCustomScrollbars(example_frame, width=80, height=6, font=self.font)
        example_text_widget.pack(padx=10, pady=10, fill=tk.X)
        example_text_widget.insert(tk.END, example_text)
        
        def save_example():
            from tkinter import filedialog
            file_path = filedialog.asksaveasfilename(
                title="保存请求包示例",
                defaultextension=".txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")]
            )
            if file_path:
                try:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(example_text)
                    messagebox.showinfo("成功", f"示例已保存到: {file_path}")
                except Exception as e:
                    messagebox.showerror("错误", f"保存失败: {e}")
        
        ttk.Button(example_frame, text="保存示例", command=save_example, 
                  style='Action.TButton').pack(pady=10)
        
        # 初始化预览
        update_preview()

    def show_system_info(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建系统信息界面
        title_label = tk.Label(self.content_frame, text="系统信息", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建信息显示区域
        info_frame = tk.LabelFrame(self.content_frame, text="系统详细信息", font=self.font)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # 使用自定义滚动条文本框
        info_text = ScrolledTextWithCustomScrollbars(info_frame, width=80, height=20, font=self.font)
        info_text.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 添加搜索按钮
        search_button = ttk.Button(info_frame, text="搜索", 
                                 command=lambda: SearchDialog(self.root, info_text.text))
        search_button.pack(pady=5)
        
        # 收集系统信息
        system_info = []
        system_info.append("=== 系统信息 ===\n")
        system_info.append(f"操作系统: {platform.system()} {platform.release()}")
        system_info.append(f"系统版本: {platform.version()}")
        system_info.append(f"机器类型: {platform.machine()}")
        system_info.append(f"处理器: {platform.processor()}")
        system_info.append(f"Python版本: {sys.version}")
        system_info.append(f"Python路径: {sys.executable}")
        
        system_info.append("\n=== 网络信息 ===\n")
        try:
            hostname = socket.gethostname()
            system_info.append(f"主机名: {hostname}")
            ip_address = socket.gethostbyname(hostname)
            system_info.append(f"IP地址: {ip_address}")
        except:
            system_info.append("无法获取网络信息")
        
        system_info.append("\n=== 环境信息 ===\n")
        system_info.append(f"当前工作目录: {os.getcwd()}")
        system_info.append(f"用户目录: {os.path.expanduser('~')}")
        system_info.append(f"临时目录: {tempfile.gettempdir()}")
        
        system_info.append("\n=== 模块信息 ===\n")
        system_info.append(f"DNS模块: {'可用' if DNS_AVAILABLE else '不可用'}")
        system_info.append(f"Requests模块: {'可用' if REQUESTS_AVAILABLE else '不可用'}")
        system_info.append(f"Crypto模块: {'可用' if CRYPTO_AVAILABLE else '不可用'}")
        
        # 显示信息
        info_text.insert(tk.END, "\n".join(system_info))
        info_text.text.config(state=tk.DISABLED)

    def show_network_tools(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建网络工具界面
        title_label = tk.Label(self.content_frame, text="网络工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建选项卡
        tab_control = ttk.Notebook(self.content_frame)
        
        # Ping工具选项卡
        ping_tab = ttk.Frame(tab_control)
        tab_control.add(ping_tab, text="Ping工具")
        
        ping_frame = tk.Frame(ping_tab)
        ping_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(ping_frame, text="目标主机:", font=self.font).pack(side=tk.LEFT, padx=5)
        ping_host = tk.Entry(ping_frame, width=30, font=self.font)
        ping_host.pack(side=tk.LEFT, padx=5)
        ping_host.insert(0, "www.baidu.com")
        
        ping_count = tk.StringVar(value="4")
        tk.Label(ping_frame, text="次数:", font=self.font).pack(side=tk.LEFT, padx=5)
        ttk.Combobox(ping_frame, textvariable=ping_count, values=["1", "4", "10"], width=5).pack(side=tk.LEFT, padx=5)
        
        def ping_host_func():
            host = ping_host.get().strip()
            count = ping_count.get()
            if not host:
                messagebox.showerror("错误", "请输入目标主机")
                return
            
            ping_output.delete("1.0", tk.END)
            ping_output.insert(tk.END, f"正在ping {host}...\n")
            
            try:
                if platform.system() == "Windows":
                    cmd = ["ping", "-n", count, host]
                else:
                    cmd = ["ping", "-c", count, host]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                ping_output.insert(tk.END, result.stdout)
                if result.stderr:
                    ping_output.insert(tk.END, f"\n错误: {result.stderr}")
            except subprocess.TimeoutExpired:
                ping_output.insert(tk.END, "Ping超时")
            except Exception as e:
                ping_output.insert(tk.END, f"Ping失败: {e}")
        
        ttk.Button(ping_frame, text="Ping", command=ping_host_func).pack(side=tk.LEFT, padx=5)
        
        ping_output = ScrolledTextWithCustomScrollbars(ping_tab, width=70, height=15, font=self.font)
        ping_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # Traceroute工具选项卡
        trace_tab = ttk.Frame(tab_control)
        tab_control.add(trace_tab, text="路由跟踪")
        
        trace_frame = tk.Frame(trace_tab)
        trace_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(trace_frame, text="目标主机:", font=self.font).pack(side=tk.LEFT, padx=5)
        trace_host = tk.Entry(trace_frame, width=30, font=self.font)
        trace_host.pack(side=tk.LEFT, padx=5)
        trace_host.insert(0, "www.baidu.com")
        
        def trace_host_func():
            host = trace_host.get().strip()
            if not host:
                messagebox.showerror("错误", "请输入目标主机")
                return
            
            trace_output.delete("1.0", tk.END)
            trace_output.insert(tk.END, f"正在跟踪路由到 {host}...\n")
            
            try:
                if platform.system() == "Windows":
                    cmd = ["tracert", host]
                else:
                    cmd = ["traceroute", host]
                
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
                trace_output.insert(tk.END, result.stdout)
                if result.stderr:
                    trace_output.insert(tk.END, f"\n错误: {result.stderr}")
            except subprocess.TimeoutExpired:
                trace_output.insert(tk.END, "路由跟踪超时")
            except Exception as e:
                trace_output.insert(tk.END, f"路由跟踪失败: {e}")
        
        ttk.Button(trace_frame, text="跟踪", command=trace_host_func).pack(side=tk.LEFT, padx=5)
        
        trace_output = ScrolledTextWithCustomScrollbars(trace_tab, width=70, height=15, font=self.font)
        trace_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 显示选项卡
        tab_control.pack(expand=1, fill=tk.BOTH)

    def show_file_tools(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建文件工具界面
        title_label = tk.Label(self.content_frame, text="文件工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建选项卡
        tab_control = ttk.Notebook(self.content_frame)
        
        # 文件哈希计算选项卡
        hash_tab = ttk.Frame(tab_control)
        tab_control.add(hash_tab, text="文件哈希")
        
        hash_frame = tk.Frame(hash_tab)
        hash_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(hash_frame, text="文件路径:", font=self.font).pack(side=tk.LEFT, padx=5)
        hash_file_var = tk.StringVar()
        hash_file_entry = tk.Entry(hash_frame, textvariable=hash_file_var, width=40, font=self.font)
        hash_file_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        def select_hash_file():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(title="选择文件")
            if file_path:
                hash_file_var.set(file_path)
        
        ttk.Button(hash_frame, text="浏览", command=select_hash_file).pack(side=tk.LEFT, padx=5)
        
        def calculate_file_hash():
            file_path = hash_file_var.get().strip()
            if not file_path or not os.path.exists(file_path):
                messagebox.showerror("错误", "请选择有效的文件")
                return
            
            hash_output.delete("1.0", tk.END)
            hash_output.insert(tk.END, f"正在计算文件哈希: {file_path}\n\n")
            
            try:
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                md5_hash = hashlib.md5(data).hexdigest()
                sha1_hash = hashlib.sha1(data).hexdigest()
                sha256_hash = hashlib.sha256(data).hexdigest()
                
                hash_output.insert(tk.END, f"MD5: {md5_hash}\n")
                hash_output.insert(tk.END, f"SHA1: {sha1_hash}\n")
                hash_output.insert(tk.END, f"SHA256: {sha256_hash}\n")
                hash_output.insert(tk.END, f"\n文件大小: {len(data)} 字节")
                
            except Exception as e:
                hash_output.insert(tk.END, f"计算哈希失败: {e}")
        
        ttk.Button(hash_frame, text="计算哈希", command=calculate_file_hash).pack(side=tk.LEFT, padx=5)
        
        hash_output = ScrolledTextWithCustomScrollbars(hash_tab, width=70, height=10, font=self.font)
        hash_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 文件比较选项卡
        compare_tab = ttk.Frame(tab_control)
        tab_control.add(compare_tab, text="文件比较")
        
        compare_frame = tk.Frame(compare_tab)
        compare_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(compare_frame, text="文件1:", font=self.font).grid(row=0, column=0, sticky=tk.W, pady=5)
        file1_var = tk.StringVar()
        file1_entry = tk.Entry(compare_frame, textvariable=file1_var, width=40, font=self.font)
        file1_entry.grid(row=0, column=1, padx=5, pady=5)
        
        def select_file1():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(title="选择第一个文件")
            if file_path:
                file1_var.set(file_path)
        
        ttk.Button(compare_frame, text="浏览", command=select_file1).grid(row=0, column=2, padx=5, pady=5)
        
        tk.Label(compare_frame, text="文件2:", font=self.font).grid(row=1, column=0, sticky=tk.W, pady=5)
        file2_var = tk.StringVar()
        file2_entry = tk.Entry(compare_frame, textvariable=file2_var, width=40, font=self.font)
        file2_entry.grid(row=1, column=1, padx=5, pady=5)
        
        def select_file2():
            from tkinter import filedialog
            file_path = filedialog.askopenfilename(title="选择第二个文件")
            if file_path:
                file2_var.set(file_path)
        
        ttk.Button(compare_frame, text="浏览", command=select_file2).grid(row=1, column=2, padx=5, pady=5)
        
        def compare_files():
            file1 = file1_var.get().strip()
            file2 = file2_var.get().strip()
            
            if not file1 or not file2:
                messagebox.showerror("错误", "请选择两个文件")
                return
            
            if not os.path.exists(file1) or not os.path.exists(file2):
                messagebox.showerror("错误", "文件不存在")
                return
            
            compare_output.delete("1.0", tk.END)
            compare_output.insert(tk.END, f"正在比较文件...\n\n")
            
            try:
                with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                    data1 = f1.read()
                    data2 = f2.read()
                
                if data1 == data2:
                    compare_output.insert(tk.END, "文件内容完全相同\n")
                else:
                    compare_output.insert(tk.END, "文件内容不同\n")
                
                compare_output.insert(tk.END, f"文件1大小: {len(data1)} 字节\n")
                compare_output.insert(tk.END, f"文件2大小: {len(data2)} 字节\n")
                
                # 计算哈希值进行比较
                hash1 = hashlib.md5(data1).hexdigest()
                hash2 = hashlib.md5(data2).hexdigest()
                
                compare_output.insert(tk.END, f"\n文件1 MD5: {hash1}\n")
                compare_output.insert(tk.END, f"文件2 MD5: {hash2}\n")
                
                if hash1 == hash2:
                    compare_output.insert(tk.END, "\nMD5哈希值相同")
                else:
                    compare_output.insert(tk.END, "\nMD5哈希值不同")
                
            except Exception as e:
                compare_output.insert(tk.END, f"比较失败: {e}")
        
        ttk.Button(compare_frame, text="比较文件", command=compare_files).grid(row=2, column=1, pady=10)
        
        compare_output = ScrolledTextWithCustomScrollbars(compare_tab, width=70, height=10, font=self.font)
        compare_output.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)
        
        # 显示选项卡
        tab_control.pack(expand=1, fill=tk.BOTH)

    def show_encoding_tools(self):
        # 清除现有内容
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        # 创建编码工具界面
        title_label = tk.Label(self.content_frame, text="编码工具", font=('Microsoft YaHei UI', 16, 'bold'))
        title_label.pack(pady=10)
        title_label.configure(anchor="w")
        
        # 创建选项卡
        tab_control = ttk.Notebook(self.content_frame)
        
        # 十六进制编码选项卡
        hex_tab = ttk.Frame(tab_control)
        tab_control.add(hex_tab, text="十六进制")
        
        tk.Label(hex_tab, text="输入:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        hex_input = ScrolledTextWithCustomScrollbars(hex_tab, width=70, height=5, font=self.font)
        hex_input.pack(padx=10, pady=5)
        
        hex_frame = tk.Frame(hex_tab)
        hex_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def hex_encode():
            try:
                data = hex_input.get("1.0", tk.END).strip()
                if not data:
                    return
                result = data.encode().hex()
                hex_output.delete("1.0", tk.END)
                hex_output.insert(tk.END, result)
            except Exception as e:
                hex_output.delete("1.0", tk.END)
                hex_output.insert(tk.END, f"编码失败: {e}")
        
        def hex_decode():
            try:
                data = hex_input.get("1.0", tk.END).strip()
                if not data:
                    return
                result = bytes.fromhex(data).decode(errors='ignore')
                hex_output.delete("1.0", tk.END)
                hex_output.insert(tk.END, result)
            except Exception as e:
                hex_output.delete("1.0", tk.END)
                hex_output.insert(tk.END, f"解码失败: {e}")
        
        ttk.Button(hex_frame, text="编码", command=hex_encode).pack(side=tk.LEFT, padx=5)
        ttk.Button(hex_frame, text="解码", command=hex_decode).pack(side=tk.LEFT, padx=5)
        
        tk.Label(hex_tab, text="输出:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        hex_output = ScrolledTextWithCustomScrollbars(hex_tab, width=70, height=10, font=self.font)
        hex_output.pack(padx=10, pady=5)
        
        # 二进制编码选项卡
        bin_tab = ttk.Frame(tab_control)
        tab_control.add(bin_tab, text="二进制")
        
        tk.Label(bin_tab, text="输入:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        bin_input = ScrolledTextWithCustomScrollbars(bin_tab, width=70, height=5, font=self.font)
        bin_input.pack(padx=10, pady=5)
        
        bin_frame = tk.Frame(bin_tab)
        bin_frame.pack(fill=tk.X, padx=10, pady=5)
        
        def bin_encode():
            try:
                data = bin_input.get("1.0", tk.END).strip()
                if not data:
                    return
                result = ' '.join(format(ord(c), '08b') for c in data)
                bin_output.delete("1.0", tk.END)
                bin_output.insert(tk.END, result)
            except Exception as e:
                bin_output.delete("1.0", tk.END)
                bin_output.insert(tk.END, f"编码失败: {e}")
        
        def bin_decode():
            try:
                data = bin_input.get("1.0", tk.END).strip()
                if not data:
                    return
                # 移除空格并每8位分割
                binary_str = data.replace(' ', '')
                result = ''
                for i in range(0, len(binary_str), 8):
                    byte = binary_str[i:i+8]
                    if len(byte) == 8:
                        result += chr(int(byte, 2))
                bin_output.delete("1.0", tk.END)
                bin_output.insert(tk.END, result)
            except Exception as e:
                bin_output.delete("1.0", tk.END)
                bin_output.insert(tk.END, f"解码失败: {e}")
        
        ttk.Button(bin_frame, text="编码", command=bin_encode).pack(side=tk.LEFT, padx=5)
        ttk.Button(bin_frame, text="解码", command=bin_decode).pack(side=tk.LEFT, padx=5)
        
        tk.Label(bin_tab, text="输出:", font=self.font).pack(anchor=tk.W, padx=10, pady=5)
        bin_output = ScrolledTextWithCustomScrollbars(bin_tab, width=70, height=10, font=self.font)
        bin_output.pack(padx=10, pady=5)
        
        # 显示选项卡
        tab_control.pack(expand=1, fill=tk.BOTH)


# 主程序入口
if __name__ == "__main__":
    try:
        # 创建主窗口
        root = tk.Tk()
        
        # 创建应用程序实例
        app = SecurityToolkitGUI(root)
        
        # 启动主循环
        root.mainloop()
    except Exception as e:
        print(f"程序启动失败: {e}")
        import traceback
        traceback.print_exc()