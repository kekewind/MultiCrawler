import time
from execute_database import insert_video_hrefs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def fetch_video_links(user_id):
    driver_path = 'D:\\Program Files\\chromedriver-win64\\chromedriver.exe'
    service = Service(executable_path=driver_path)
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 无头模式，如果不需要浏览器弹出可以取消注释
    driver = webdriver.Chrome(service=service, options=options)

    up_url = f'https://space.bilibili.com/{user_id}'
    driver.get(up_url)
    time.sleep(30)
    # 使用WebDriverWait等待“更多”按钮出现并点击
    try:
        more_button = WebDriverWait(driver, 30).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(text(), '更多')]"))
        )
        more_button.click()
    except Exception as e:
        print("No 'More' button found or error clicking it:", e)

    # 使用WebDriverWait等待最后一页的数字出现
    last_page_element = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((By.XPATH, "//li[contains(@title, '最后一页')]/a"))
    )
    total_pages = int(last_page_element.text)

    video_links = []  # 用于存储视频链接的列表

    for page in range(1, total_pages + 1):
        time.sleep(1)
        WebDriverWait(driver, 30).until(
            EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class,"cover")]'))
        )
        videos = driver.find_elements(By.XPATH, '//a[contains(@class,"cover")]')
        print(f"Fetching videos from page {page}...")

        for video in videos:
            link = video.get_attribute('href')
            if link not in video_links:  # 避免重复添加链接
                video_links.append(link)

        # 如果不是最后一页，则点击“下一页”按钮
        if page < total_pages:
            next_page_button = WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.XPATH, "//li[@class='be-pager-next']/a"))
            )
            next_page_button.click()

    driver.quit()  # 关闭浏览器
    return video_links


if __name__ == "__main__":
    user_id = '517327498'  # 示例用户ID
    video_links = fetch_video_links(user_id)
    print(f"Total videos fetched: {len(video_links)}")
    insert_video_hrefs(video_links, 'video_info_lx.db')
    for link in video_links:
        print(link)
