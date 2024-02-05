import json
from typing import Optional
from bs4 import BeautifulSoup

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from execute_database import update_downloaded_status, save_video_info, process_all_records


def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def download_file(url, filename, proxies, Refer):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Referer': Refer,  # 修改为视频实际页面的URL
    }
    print(f"Downloading-----{Refer}")
    try:
        with requests_retry_session().get(url, headers=headers, stream=True, proxies=proxies, timeout=60) as r:
            r.raise_for_status()  # 确保请求成功
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # 过滤掉保活新的块
                        f.write(chunk)
            print("Downloading finished.")
            return 1
    except requests.exceptions.RequestException as e:
        print(f"Error during downloading: {e}")
        return 0


# 注意: 请确保引入了requests_retry_session的定义或者使用requests.get代替。


def extract_video_info(html_content):
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'lxml')

    # 初始化一个字典来存储提取的信息
    video_info = {}

    # 提取视频标题
    video_title = soup.title.string if soup.title else "标题未找到"
    video_info['title'] = video_title

    # 查找包含播放量的<span>标签，注意这里的类名可能需要根据实际的HTML结构进行调整
    play_count_span = soup.find('span', class_='view')
    play_count = play_count_span.text.strip() if play_count_span else "播放量未找到"
    video_info['play_count'] = play_count

    # 查找包含创建时间的<span>标签，同样需要根据实际HTML结构调整
    create_time_span = soup.find('span', class_='pubdate')
    create_time = create_time_span.text.strip() if create_time_span else "创建时间未找到"
    video_info['create_time'] = create_time

    return video_info


def extract_playinfo(html_content: str) -> Optional[dict]:
    """
    Extracts the __playinfo__ data from the given HTML content as a string using BeautifulSoup.

    Parameters:
    html_content (str): The HTML content as a string.

    Returns:
    Optional[dict]: A dictionary containing the __playinfo__ data if found, otherwise None.
    """
    # 使用BeautifulSoup解析HTML内容
    soup = BeautifulSoup(html_content, 'lxml')

    # 查找包含__playinfo__数据的<script>标签
    script_tag = soup.find('script', text=lambda t: t and 'window.__playinfo__' in t)

    if script_tag:
        # 从<script>标签的文本中提取JSON字符串
        json_str_start = script_tag.string.find('{')
        json_str_end = script_tag.string.rfind('}') + 1
        json_str = script_tag.string[json_str_start:json_str_end]

        try:
            # 解析JSON字符串为Python字典
            playinfo_data = json.loads(json_str)
            return playinfo_data
        except json.JSONDecodeError:
            print('JSON decode error occurred while parsing __playinfo__ data.')
            return None
    else:
        print('No __playinfo__ object found in the HTML content.')
        return None


def sanitize_filename(filename):
    invalid_chars = ['*', ':', '<', '>', '?', '/', '\\', '|']

    # Remove each invalid character by replacing it with an empty string
    for char in invalid_chars:
        filename = filename.replace(char, '')

    return filename


if __name__ == '__main__':
    database = 'video_info.db'
    print('*' * 30 + 'B站视频下载小助手' + '*' * 30)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'
    }
    proxies = {
        'http': 'socks5://127.0.0.1:10808',
        'https': 'socks5://127.0.0.1:10808',
    }

    href_list = process_all_records(database)

    for start in href_list:
        start = start.strip()
        html = requests.get(start, headers=headers, proxies=proxies)
        playinfo = extract_playinfo(html.content.decode('utf-8'))
        if playinfo is None:
            continue
        info = extract_video_info(html.content.decode('utf-8'))
        save_video_info(info, database)
        if 'data' in playinfo:
            data = playinfo['data']
        else:
            print("No 'data' key found in data, skipping video and audio URL extraction.")
            continue
        if 'dash' in data:
            # 如果存在，继续提取video_url和audio_url
            video_url = data['dash']['video'][0]['baseUrl']  # 选择第一个视频流作为下载链接
            audio_url = data['dash']['audio'][0]['baseUrl']  # 选择第一个音频流作为下载链接
            title = sanitize_filename(info['title'])
            # download_file(video_url, f'malin/{title}.mp4', proxies, start)
            # 下载音频
            isDown = download_file(audio_url, f'lx/{title}.mp3', proxies, start)
            print(f"{title}下载完成")
            update_downloaded_status(video_url, database, isDown)
        else:
            # 如果不存在，可以根据需要处理这种情况，比如打印警告信息或者跳过下载等
            print("No 'dash' key found in data, skipping video and audio URL extraction.")
            continue
