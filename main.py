import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import sys
from io import StringIO

name = 0
t = 30

# HTML:https:\/\/c1.7bbffvip.com\/video\/yongbaoqingchun\/HD\/index.m3u8
# 实际:https://c1.7bbffvip.com/video/yongbaoqingchun/HD/index.m3u8

def try_m3u8(m3u8_url):
    headers = {
        'Referer': "https://www.xckyy.com/",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }

    m3u8_response = requests.get(m3u8_url, headers=headers, timeout=10)

    if m3u8_response.ok:
        print("m3u8访问成功!")
        m3u8_content = m3u8_response.text
        ts_regex = r"\b(00.*?\.ts)\b"
        ts_matches = re.findall(ts_regex, m3u8_content, re.DOTALL)
        return m3u8_url, ts_matches
    else:
        print("m3u8访问失败,错误码", m3u8_response, f"  对应m3u8网址:{m3u8_url}\n正在调整对应网址")
        return False


def get_m3u8(url='https://www.xckyy.com/xcp/57159-1-1.html'):
    global name

    m3u8_regex = r'(url\":\"(.*?\\\/video\\\/[\w.]+\\\/.*?)")'
    regexp = re.compile(m3u8_regex, re.DOTALL)
    script = 0

    headers = {
        'Referer': "https://www.xckyy.com/",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }
    respond = requests.get(url, headers=headers, timeout=30)
    respond.encoding = respond.apparent_encoding
    soup = BeautifulSoup(respond.text, 'html.parser')

    name = soup.find("div", attrs={"class": "video_title fl"}).find("h2").text
    print(f"开始下载{name}")

    play_source = soup.find("ul", attrs={"class": "content_playlist clearfix sort-list"}).find("a").text

    scripts = soup.find_all("script", attrs={"type": "text/javascript"})
    for script in scripts:
        if regexp.search(str(script)):
            script = regexp.search(str(script))
            break

    name_ = script[2].replace("\\", "")
    m3u8_url = name_

    if try_m3u8(m3u8_url):
        return try_m3u8(m3u8_url)
    else:
        r = re.match(r".*?/video/([\w./]+)/index.m3u8", m3u8_url)
        part = r[1]
        if '/' in part:
            part_update = part.split('/')[0]
            m3u8_url = m3u8_url.replace(f"{part}", f"{part_update}")

        m3u8_url = m3u8_url.replace("/index", f"/{play_source}/index")
        return try_m3u8(m3u8_url)


def download(m3u8_url, ts_matches, t):  # 修改download函数以接受线程数量
    error = 0  # 检测是否超出长度

    headers = {
        'Referer': 'https://www.xckyy.com/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }

    url = str(m3u8_url).rsplit("index.m3u8", 1)[0]

    ts_matches = [url + str(ts).zfill(7) + ".ts" for ts in range(5000)]
    total = len(ts_matches)

    # 创建输出目录
    output_dir = Path('video_segments')
    output_dir.mkdir(exist_ok=True)

    # 下载单个TS文件
    def download_ts(url, index):
        nonlocal error
        if error > 30:
            return False
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            resp.raise_for_status()
            with open(output_dir / f"{index + 1:04d}.ts", 'wb') as f:
                f.write(resp.content)
            print(f"下载进度: {index + 1}/{total}")
        except Exception as e:
            print(f"下载失败 {url}: {str(e)}")
            error += 1

    # 并发下载
    with ThreadPoolExecutor(max_workers= t ) as executor:  # 使用传入的线程数量
        executor.map(download_ts, ts_matches, range(total))


    # 合并文件
    output_file = Path(f"{name}.mp4")
    with open(output_file, 'wb') as merged:
        for i in range(1, total + 1):
            ts_file = output_dir / f"{i:04d}.ts"
            if ts_file.exists():
                with open(ts_file, 'rb') as f:
                    merged.write(f.read())
                ts_file.unlink()

    # 清理临时目录
    try:
        output_dir.rmdir()
        print("临时文件已全部清除!")
    except OSError:
        print("警告: 临时目录未完全清理,请手动清理")

    print(f"视频已成功保存为: {output_file}")


def search(string):
    date = list(dict())
    url = "https://www.xckyy.com/search/-------------.html?wd=" + string
    headers = {
        'Referer': "https://www.xckyy.com/",
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0'
    }
    respond = requests.get(url, headers=headers, timeout=30)
    respond.encoding = respond.apparent_encoding
    soup = BeautifulSoup(respond.text, 'html.parser')
    if respond.ok:
        content = soup.find("div", attrs={"class": "pannel search_box clearfix"})
        lis = content.find_all("li", attrs={"class": "searchlist_item"})
        for li in lis:
            a = li.find("a")
            span = li.find("span", attrs={"class": "info_right"})
            if span.text == "电影":
                name = a.get("title")
                scr = a.get("href")
                url = "https://www.xckyy.com" + str(scr).replace("xcv", "xcp").replace(".html", "-1-1.html")
                date.append({"name": f"{name}", "url": f"{url}"})
        return date  # 列表套字典
    else:
        print("异常" + str(respond.status_code))


def show(date):
    for i in range(len(date)):
        print(f"{i + 1}.{date[i]["name"]}")


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


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloaderApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()