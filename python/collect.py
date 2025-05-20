import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_youtube_links(driver, channel_url):
    try:
        driver.get(channel_url)
        # 等待页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-grid-video-renderer"))
        )
        # 滚动页面确保加载所有内容
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)  # 等待加载
            new_height = driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        html_content = driver.page_source
    except Exception as e:
        print(f"访问频道页面出错: {e}")
        return None

    date_pattern = re.compile(r'(\d{4})年(\d{1,2})月(\d{1,2})日')
    video_links = []
    
    for date_match in date_pattern.finditer(html_content):
        year, month, day = map(int, date_match.groups())
        date_str = date_match.group()
        date_obj = datetime(year, month, day)
        date_end_pos = date_match.end()
        
        watch_pos = html_content.find('/watch?v=', date_end_pos)
        if watch_pos == -1:
            continue
        
        quote_pos = html_content.find('"', watch_pos)
        if quote_pos == -1:
            continue
        
        watch_part = html_content[watch_pos:quote_pos]
        full_url = f'https://www.youtube.com{watch_part}'
        
        video_links.append({
            'date_str': date_str,
            'date_obj': date_obj,
            'url': full_url
        })
    
    return video_links

def find_latest_video(video_links):
    if not video_links:
        return None
    return sorted(video_links, key=lambda x: x['date_obj'], reverse=True)[0]

def extract_download_addresses(driver, video_url):
    try:
        driver.get(video_url)
        # 等待视频描述加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div#description"))
        )
        # 滚动到描述部分
        description = driver.find_element(By.CSS_SELECTOR, "div#description")
        driver.execute_script("arguments[0].scrollIntoView();", description)
        # 点击"更多"按钮展开完整描述
        try:
            more_button = driver.find_element(By.CSS_SELECTOR, "tp-yt-paper-button#more")
            more_button.click()
            time.sleep(1)
        except:
            pass
        
        html_content = driver.page_source
    except Exception as e:
        print(f"访问视频页面出错: {e}")
        return None

    # 查找所有"下载地址"出现的位置
    download_markers = [m.start() for m in re.finditer('下载地址', html_content)]
    download_segments = []
    
    for marker_pos in download_markers:
        # 提取标记位置后300个字符（扩大范围以确保包含完整地址）
        segment = html_content[marker_pos:marker_pos+300]
        download_segments.append(segment)
    
    return download_segments, html_content

if __name__ == "__main__":
    # 初始化Selenium
    print("初始化浏览器...")
    driver = setup_selenium()
    
    try:
        channel_url = "https://www.youtube.com/@ZYFXS"
        print(f"正在处理频道: {channel_url}")
        
        # 第一步：获取频道中最新的视频
        videos = extract_youtube_links(driver, channel_url)
        
        if not videos:
            print("没有找到任何日期视频")
            exit()
            
        latest_video = find_latest_video(videos)
        print(f"\n找到最新视频: {latest_video['date_str']}")
        print(f"视频链接: {latest_video['url']}")
        
        # 第二步：从视频页面提取所有包含"下载地址"的片段
        print("\n正在从视频页面提取所有包含'下载地址'的片段...")
        download_segments, full_html = extract_download_addresses(driver, latest_video['url'])
        
        # 将完整HTML保存到文件以供检查
        with open("youtube_page.html", "w", encoding="utf-8") as f:
            f.write(full_html)
        print("\n完整页面内容已保存到 youtube_page.html")
        
        if download_segments:
            print(f"\n找到 {len(download_segments)} 个匹配片段:")
            for i, segment in enumerate(download_segments, 1):
                print(f"\n片段 {i}:")
                print(segment)
                
                # 尝试从片段中提取URL
                url_match = re.search(r'(https?://[^\s<>"]+)', segment)
                if url_match:
                    print(f"提取到的URL: {url_match.group(1)}")
        else:
            print("\n没有找到任何包含'下载地址'的片段")
            
    finally:
        # 关闭浏览器
        driver.quit()
