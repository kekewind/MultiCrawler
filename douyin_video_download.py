from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time

# 假设 execute_database.py 文件中的 store_video_info_to_db 已正确定义
from execute_database import store_video_info_to_db


def scrape_videos_and_store_info(url):
    options = Options()
    options.add_argument('--disable-gpu')
    options.add_argument("window-size=1024,768")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver_path = 'D:\\Program Files\\chromedriver-win64\\chromedriver.exe'
    service = Service(driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    videos_info = []

    try:
        driver.get(url)
        time.sleep(40)  # 为页面加载提供足够的时间

        # 滚动页面以加载所有视频
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # 等待新视频加载
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        videos = soup.find('ul', {'class': 'e6wsjNLL bGEvyQfj'})
        for video in videos:
            title = video.find('a').text if video.find('a') else 'No title'
            href = video.find('a')['href'] if video.find('a') else 'No link'
            user_like = video.find('span', {'class': 'YzDRRUWc author-card-user-video-like'}).find(
                'span').text if video.find('span', {'class': 'YzDRRUWc author-card-user-video-like'}) else '0'
            if soup is None:
                continue
            videos_info.append({
                'title': title,
                'user_like': user_like,
                'href': href
            })

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    return videos_info


if __name__ == "__main__":

    table_name = 'videos'
    database = 'video_info.db'
    url = 'https://www.douyin.com/user/MS4wLjABAAAANEutOI9HI-8T7I_CdiC8Vr2wlt_bIURLSPqNu8L45Wgqg5THH9ZZlGEAuYXCDWx8'
    videos_info = scrape_videos_and_store_info(url)
    store_video_info_to_db(videos_info, database, 'douyin')
