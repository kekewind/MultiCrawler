from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
from execute_database import insert_into_database
from bs4 import BeautifulSoup


def extract_videos_info(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    videos_data = []

    # 查找所有视频的 div
    videos = soup.find_all('div', class_='video-card video-item vertical')

    for video in videos:
        # 从海报图片的 'alt' 属性中提取标题
        title = video.find('div', class_='poster').find('img').get('alt', '无标题')

        # 从 'info-text' span 中提取喜欢数
        likes_text = video.find('span', class_='info-text').text if video.find('span', class_='info-text') else '未找到'
        # 假设格式总是 "[数字]喜欢"，将喜欢数文本转换为整数
        likes = int(''.join(filter(str.isdigit, likes_text)))

        video_info = {
            'title': title,
            'user_like': likes,
        }

        videos_data.append(video_info)

    return videos_data


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
        time.sleep(5)  # 为页面加载提供足够的时间

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

        videos_info = []

        try:
            videos = soup.find_all('div',
                                   class_='video-card video-item vertical')  # Adjusted to find divs with the correct class
            for video in videos:
                # Assuming the title might be in an 'img' tag's 'alt' attribute inside a 'div' with the class 'poster'
                title = video.find('div', class_='poster').find('img').get('alt', 'No title')

                # Find the 'span' containing likes
                user_like_element = video.find('div', class_='video-info no-jump-avatar').find('span',
                                                                                               class_='info-text')
                user_like = user_like_element.text if user_like_element else '0 likes'

                # Assuming the href might not be directly available, but you might need to extract it from some other element
                href = 'No link'  # Update this part based on where the link can be found in your HTML structure

                videos_info.append({
                    'title': title,
                    'user_like': user_like,
                    'href': href
                })

        except Exception as e:
            print(f"An error occurred: {e}")
    finally:
        driver.quit()  # Ensure the driver quits after scraping
    return videos_info


if __name__ == "__main__":
    table_name = 'videos'
    database = 'video_info.db'
    url = 'https://www.kuaishou.com/profile/3xa8g6xcb3h8x2c'

    html_file_path = r'C:\Users\13636\Downloads\AI北极熊（收徒）-快手.html'
    with open(html_file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    # 假设 `html_content` 包含您提供的HTML源代码
    videos_info = extract_videos_info(html_content)
    print(videos_info)
    # 打印视频数据列表
    fields = ['title', 'user_like']
    for video in videos_info:
        values = [video['title'], video['user_like']]
        insert_into_database(database, table_name, fields, values)
    # videos_info = scrape_videos_and_store_info(url)
    # store_video_info_to_db(videos_info, database, 'kuaishou')
