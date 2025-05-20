import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pyperclip  # 用于从剪贴板获取源代码

def setup_selenium():
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    # 注意：这里不能使用无头模式，因为需要模拟右键操作
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def extract_youtube_links(driver, channel_url):
    try:
        driver.get(channel_url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ytd-grid-video-renderer"))
        )
        
        # 滚动加载所有视频
        last_height = driver.execute_script("return document.documentElement.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            time.sleep(2)
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

def get_page_source_with_selenium(driver, url):
    try:
        driver.get(url)
        # 等待页面基本加载
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # 模拟右键点击并选择"查看页面源代码"
        actions = ActionChains(driver)
        actions.key_down(Keys.CONTROL).send_keys('u').key_up(Keys.CONTROL).perform()
        
        # 切换到新标签页（源代码页）
        driver.switch_to.window(driver.window_handles[-1])
        
        # 等待源代码页面加载
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "pre"))
        )
        
        # 获取完整的源代码
        full_source = driver.find_element(By.TAG_NAME, "pre").text
        return full_source
        
    except Exception as e:
        print(f"获取页面源代码出错: {e}")
        return None
    finally:
        # 关闭源代码标签页，回到原页面
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])

def extract_download_addresses_from_source(full_source):
    if not full_source:
        return None
    
    # 查找所有"下载地址"出现的位置
    download_markers = [m.start() for m in re.finditer('下载地址', full_source)]
    download_segments = []
    
    for marker_pos in download_markers:
        # 提取标记位置后300个字符
        segment = full_source[marker_pos:marker_pos+300]
        download_segments.append(segment)
    
    return download_segments

if __name__ == "__main__":
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
        
        # 第二步：获取完整页面源代码
        print("\n正在获取完整页面源代码...")
        full_source = get_page_source_with_selenium(driver, latest_video['url'])
        
        if full_source:
            # 保存源代码到文件供检查
            with open("full_page_source.txt", "w", encoding="utf-8") as f:
                f.write(full_source)
            print("完整页面源代码已保存到 full_page_source.txt")
            
            # 第三步：从源代码中提取下载地址
            print("\n正在搜索下载地址...")
            download_segments = extract_download_addresses_from_source(full_source)
            
            if download_segments:
                print(f"\n找到 {len(download_segments)} 个匹配片段:")
                for i, segment in enumerate(download_segments, 1):
                    print(f"\n片段 {i}:")
                    print(segment)
                    
                    # 尝试提取URL
                    url_match = re.search(r'(https?://[^\s<>"]+)', segment)
                    if url_match:
                        print(f"提取到的URL: {url_match.group(1)}")
            else:
                print("\n没有找到任何包含'下载地址'的片段")
        else:
            print("\n无法获取完整页面源代码")
            
    finally:
        driver.quit()
