from request import *
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
from io import StringIO



class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频下载器")
        self.root.geometry("800x600")

        # 设置全局样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="#000000")  # 黑色字体
        self.style.map("TButton", background=[("active", "#45a049")])

        # 初始化变量
        self.search_results = []
        self.selected_video = None

        # 创建界面
        self.create_widgets()

        # 重定向输出
        sys.stdout = RedirectText(self.log_area)

    def create_widgets(self):
        # 搜索区域
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        search_btn = ttk.Button(search_frame, text="搜索", command=self.start_search)
        search_btn.pack(side=tk.LEFT, padx=5)

        # 线程数量输入框
        thread_frame = ttk.Frame(self.root, padding=10)
        thread_frame.pack(fill=tk.X)

        thread_label = ttk.Label(thread_frame, text="线程数量(决定下载速度,默认30): ")

        thread_label.pack(side=tk.LEFT)

        self.thread_entry = ttk.Entry(thread_frame, width=5)
        self.thread_entry.pack(side=tk.LEFT, padx=5)
        self.thread_entry.insert(0, str(t))  # 默认值

        # 结果列表
        result_frame = ttk.Frame(self.root, padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_list = tk.Listbox(result_frame, height=10, fg="#000000", bg="#FFFFFF")  # 黑色字体，白色背景
        self.result_list.pack(fill=tk.BOTH, expand=True)
        self.result_list.bind("<<ListboxSelect>>", self.on_select)

        # 下载按钮
        self.download_btn = ttk.Button(self.root, text="开始下载", state=tk.DISABLED, command=self.start_download)
        self.download_btn.pack(pady=20)

        # 日志区域
        log_frame = ttk.Frame(self.root, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="normal", fg="#000000",
                                                  bg="#FFFFFF")  # 白色字体，深灰色背景
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def start_search(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        self.result_list.delete(0, tk.END)
        self.result_list.insert(tk.END, "搜索中...")

        thread = threading.Thread(target=self.do_search, args=(query,))
        thread.daemon = True
        thread.start()

    def do_search(self, query):
        try:
            self.search_results = search(query)
            self.root.after(0, self.update_results)
        except Exception as e:
            print(f"搜索失败: {str(e)}")

    def update_results(self):
        self.result_list.delete(0, tk.END)
        if not self.search_results:
            self.result_list.insert(tk.END, "没有找到相关结果")
            return

        for item in self.search_results:
            self.result_list.insert(tk.END, item["name"])

    def on_select(self, event):
        selection = self.result_list.curselection()
        if selection:
            index = selection[0]
            self.selected_video = self.search_results[index]
            self.download_btn.config(state=tk.NORMAL)

    def start_download(self):
        global t
        try:
            t = int(self.thread_entry.get())
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的线程数量")
            return

        if not self.selected_video:
            return

        thread = threading.Thread(target=self.do_download)
        thread.daemon = True
        thread.start()

    def do_download(self):
        try:
            url = self.selected_video["url"]
            print(f"开始处理：{self.selected_video['name']}")
            m3u8_url, ts_matches = get_m3u8(url)
            download(m3u8_url, ts_matches, t)  # 传递线程数量
            print("下载完成！")
        except Exception as e:
            print(f"下载失败: {str(e)}")

    def on_closing(self):
        sys.stdout = sys.__stdout__
        self.root.destroy()
class RedirectText(object):
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, string):
        self.text_widget.insert(tk.END, string)
        self.text_widget.see(tk.END)

    def flush(self):
        pass


class VideoDownloaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("视频下载器")
        self.root.geometry("800x600")

        # 设置全局样式
        self.style = ttk.Style()
        self.style.configure("TButton", padding=6, relief="flat", background="#4CAF50", foreground="#000000")  # 黑色字体
        self.style.map("TButton", background=[("active", "#45a049")])

        # 初始化变量
        self.search_results = []
        self.selected_video = None

        # 创建界面
        self.create_widgets()

        # 重定向输出
        sys.stdout = RedirectText(self.log_area)

    def create_widgets(self):
        # 搜索区域
        search_frame = ttk.Frame(self.root, padding=10)
        search_frame.pack(fill=tk.X)

        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        search_btn = ttk.Button(search_frame, text="搜索", command=self.start_search)
        search_btn.pack(side=tk.LEFT, padx=5)

        # 线程数量输入框
        thread_frame = ttk.Frame(self.root, padding=10)
        thread_frame.pack(fill=tk.X)

        thread_label = ttk.Label(thread_frame, text="线程数量(决定下载速度,默认30): ")

        thread_label.pack(side=tk.LEFT)

        self.thread_entry = ttk.Entry(thread_frame, width=5)
        self.thread_entry.pack(side=tk.LEFT, padx=5)
        self.thread_entry.insert(0, str(t))  # 默认值

        # 结果列表
        result_frame = ttk.Frame(self.root, padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True)

        self.result_list = tk.Listbox(result_frame, height=10, fg="#000000", bg="#FFFFFF")  # 黑色字体，白色背景
        self.result_list.pack(fill=tk.BOTH, expand=True)
        self.result_list.bind("<<ListboxSelect>>", self.on_select)

        # 下载按钮
        self.download_btn = ttk.Button(self.root, text="开始下载", state=tk.DISABLED, command=self.start_download)
        self.download_btn.pack(pady=20)

        # 日志区域
        log_frame = ttk.Frame(self.root, padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_area = scrolledtext.ScrolledText(log_frame, wrap=tk.WORD, state="normal", fg="#000000",
                                                  bg="#FFFFFF")  # 白色字体，深灰色背景
        self.log_area.pack(fill=tk.BOTH, expand=True)

    def start_search(self):
        query = self.search_entry.get()
        if not query:
            messagebox.showwarning("提示", "请输入搜索关键词")
            return

        self.result_list.delete(0, tk.END)
        self.result_list.insert(tk.END, "搜索中...")

        thread = threading.Thread(target=self.do_search, args=(query,))
        thread.daemon = True
        thread.start()

    def do_search(self, query):
        try:
            self.search_results = search(query)
            self.root.after(0, self.update_results)
        except Exception as e:
            print(f"搜索失败: {str(e)}")

    def update_results(self):
        self.result_list.delete(0, tk.END)
        if not self.search_results:
            self.result_list.insert(tk.END, "没有找到相关结果")
            return

        for item in self.search_results:
            self.result_list.insert(tk.END, item["name"])

    def on_select(self, event):
        selection = self.result_list.curselection()
        if selection:
            index = selection[0]
            self.selected_video = self.search_results[index]
            self.download_btn.config(state=tk.NORMAL)

    def start_download(self):
        global t
        try:
            t = int(self.thread_entry.get())
        except ValueError:
            messagebox.showwarning("提示", "请输入有效的线程数量")
            return

        if not self.selected_video:
            return

        thread = threading.Thread(target=self.do_download)
        thread.daemon = True
        thread.start()

    def do_download(self):
        try:
            url = self.selected_video["url"]
            print(f"开始处理：{self.selected_video['name']}")
            m3u8_url, ts_matches = get_m3u8(url)
            download(m3u8_url, ts_matches, t)  # 传递线程数量
            print("下载完成！")
        except Exception as e:
            print(f"下载失败: {str(e)}")

    def on_closing(self):
        sys.stdout = sys.__stdout__
        self.root.destroy()