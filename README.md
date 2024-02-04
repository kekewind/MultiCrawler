> **免责声明：**

>本仓库的所有内容仅供学习和参考之用，禁止用于商业用途。任何人或组织不得将本仓库的内容用于非法用途或侵犯他人合法权益。本仓库所涉及的爬虫技术仅用于学习和研究，不得用于对其他平台进行大规模爬虫或其他非法行为。对于因使用本仓库内容而引起的任何法律责任，本仓库不承担任何责任。使用本仓库的内容即表示您同意本免责声明的所有条款和条件。

# 仓库描述

**小红书爬虫**，**抖音爬虫**， **快手爬虫**， **B站爬虫**...。  
目前能根据id下载B站用户所有视频、爬取抖音/快手用户视频信息。

原理：利用Selenium模拟浏览器操作，需要手动登录。

## 使用方法(请自行安装依赖项)

### 进入根目录
   ```shell   
   # 进入项目根目录
   cd MultiCrawler
   
   ```
   
### 运行爬虫程序

   ```shell
   
   python get_user_video_list.py
   python bilibili_video_download.py
   # 浏览器弹出后在40秒内完成登录    
   ```


### 数据保存
- 支持保存到关系型数据库（sqlite3）

## 打赏

如果觉得项目不错的话可以打赏哦。您的支持就是我最大的动力！

无法运行可联系作者，帮忙修改:MuskG2023

## star
- 如果该项目对你有帮助，star一下 ❤️❤️❤️
