import re
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

name = 0
t = 30


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



