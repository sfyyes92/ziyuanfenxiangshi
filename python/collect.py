import re
from datetime import datetime
from urllib.parse import urljoin
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_selenium_driver():
    """配置Selenium WebDriver"""
    print("[调试] 正在配置Selenium WebDriver...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # 需要下载对应版本的ChromeDriver并指定路径
    service = Service(executable_path='/path/to/chromedriver')  # 请替换为实际路径
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def find_dated_videos(driver, channel_url):
    """
    使用Selenium查找指定YouTube频道中所有以日期开头的视频
    """
    print(f"[调试] 开始处理频道: {channel_url}")
    
    try:
        # 访问频道页面
        print("[调试] 正在访问频道页面...")
        driver.get(channel_url)
        
        # 等待页面加载完成
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a#video-title-link"))
        )
        
        # 获取完整页面内容
        page_content = driver.page_source
        content_length = len(page_content)
        print(f"[调试] 页面内容长度: {content_length} 字符")
        
        # 检查是否包含关键内容
        if 'window.ytcfg.set(' in page_content:
            print("[调试] 成功获取到包含window.ytcfg.set的完整内容")
        else:
            print("[警告] 页面内容可能不完整")
        
        # 保存内容到文件
        with open('youtube_channel_content.txt', 'w', encoding='utf-8') as f:
            f.write(page_content)
        print("[信息] 已将完整页面内容保存到 youtube_channel_content.txt")
        
        # 查找日期格式的视频
        print("[调试] 正在搜索日期格式的视频...")
        videos = []
        video_elements = driver.find_elements(By.CSS_SELECTOR, "a#video-title-link")
        
        date_pattern = re.compile(r'^\d{4}年\d{1,2}月\d{1,2}日')
        
        for idx, element in enumerate(video_elements, 1):
            title = element.get_attribute('title')
            if not title:
                continue
                
            if date_pattern.match(title):
                video_url = element.get_attribute('href')
                date_str = date_pattern.match(title).group()
                
                try:
                    date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
                    videos.append({
                        'date_str': date_str,
                        'date_obj': date_obj,
                        'url': video_url
                    })
                    print(f"[调试] 找到视频 #{idx}: 日期={date_str}, URL={video_url}")
                except ValueError as e:
                    print(f"[警告] 日期解析失败: {date_str}, 错误: {e}")
                    continue
        
        if not videos:
            print("[警告] 没有找到以日期开头的视频")
            return None
        
        # 按日期排序
        videos.sort(key=lambda x: x['date_obj'], reverse=True)
        print(f"[信息] 共找到 {len(videos)} 个日期视频")
        return videos
        
    except Exception as e:
        print(f"[错误] 处理过程中发生异常: {e}")
        return None

def search_paste_links_in_file(filename):
    """在文件中搜索paste.to链接"""
    try:
        print(f"\n[信息] 正在在文件 {filename} 中搜索paste.to链接...")
        with open(filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        paste_pattern = re.compile(r'(https?://paste\.to/[^\s"<]+)')
        matches = paste_pattern.finditer(content)
        
        found_count = 0
        for match in matches:
            found_count += 1
            paste_link = match.group(1)
            start_pos = match.start()
            end_pos = min(start_pos + len(paste_link) + 100, len(content))
            context = content[start_pos:end_pos]
            
            print(f"\n[找到链接 #{found_count}]")
            print(f"完整链接: {paste_link}")
            print("链接及其后100字符内容:")
            print("-" * 50)
            print(context)
            print("-" * 50)
        
        if found_count == 0:
            print("[警告] 未找到任何paste.to链接")
        else:
            print(f"\n[信息] 共找到 {found_count} 个paste.to链接")
        
        return found_count
        
    except Exception as e:
        print(f"[错误] 搜索链接失败: {e}")
        return 0

if __name__ == "__main__":
    driver = None
    try:
        # 初始化Selenium
        driver = setup_selenium_driver()
        
        # 查找最新日期的视频
        channel_url = "https://www.youtube.com/@ZYFXS"
        dated_videos = find_dated_videos(driver, channel_url)
        
        if dated_videos:
            latest_video = dated_videos[0]
            print("\n[信息] 最新视频信息:")
            print(f"发布日期: {latest_video['date_str']}")
            print(f"视频链接: {latest_video['url']}")
            
            # 获取视频页面内容
            print("\n[信息] 正在获取最新视频页面内容...")
            driver.get(latest_video['url'])
            
            # 等待页面加载
            time.sleep(5)  # 确保动态内容加载完成
            
            # 获取完整页面内容
            video_content = driver.page_source
            with open('youtube_video_content.txt', 'w', encoding='utf-8') as f:
                f.write(video_content)
            print("[信息] 已将视频页面内容保存到 youtube_video_content.txt")
            print(f"[信息] 内容长度: {len(video_content)} 字符")
            
            # 验证是否包含关键内容
            if 'window.ytcfg.set(' in video_content:
                print("[调试] 成功获取到包含window.ytcfg.set的完整视频内容")
            else:
                print("[警告] 视频页面内容可能不完整")
            
            # 搜索paste.to链接
            search_paste_links_in_file('youtube_video_content.txt')
            
    except Exception as e:
        print(f"[错误] 主程序异常: {e}")
    finally:
        if driver:
            driver.quit()
            print("[信息] 已关闭浏览器")
