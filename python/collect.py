import re
import webbrowser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    """配置Selenium Chrome驱动"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式，不显示浏览器窗口
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # 自动下载并安装ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def get_latest_date_video(channel_url, driver):
    """获取最新日期的视频"""
    try:
        driver.get(channel_url)
        
        # 等待视频元素加载（可能需要根据实际情况调整等待时间和选择器）
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a#video-title-link"))
        )
        
        # 获取所有视频元素
        video_elements = driver.find_elements(By.CSS_SELECTOR, "a#video-title-link")
        
        date_pattern = re.compile(r'^(20\d{2}年[01]?\d月[0-3]?\d日)')
        dated_videos = []
        
        for video in video_elements:
            title = video.get_attribute("title").strip()
            match = date_pattern.match(title)
            if match:
                date_str = match.group(1)
                try:
                    # 将中文日期转换为datetime对象
                    date_obj = datetime.strptime(date_str, '%Y年%m月%d日')
                    video_url = video.get_attribute("href")
                    dated_videos.append((date_obj, title, video_url))
                except ValueError:
                    continue
        
        if not dated_videos:
            print("没有找到以日期开头的视频")
            return None
        
        # 按日期排序，最新的在前
        dated_videos.sort(reverse=True, key=lambda x: x[0])
        
        return dated_videos[0]  # 返回最新日期的视频
        
    except Exception as e:
        print(f"发生错误: {e}")
        return None

def main():
    channel_url = "https://www.youtube.com/@ZYFXS"
    
    print("正在启动浏览器...")
    driver = setup_driver()
    
    try:
        print(f"正在访问频道: {channel_url}")
        latest_video = get_latest_date_video(channel_url, driver)
        
        if latest_video:
            date_obj, title, url = latest_video
            print("\n找到最新日期的视频:")
            print(f"日期: {date_obj.strftime('%Y年%m月%d日')}")
            print(f"标题: {title}")
            print(f"URL: {url}")
            
            # 询问用户是否要打开视频
            choice = input("\n是否要在浏览器中打开此视频？(y/n): ").lower()
            if choice == 'y':
                webbrowser.open(url)
        else:
            print("未能找到符合条件的视频")
            
    finally:
        print("\n关闭浏览器...")
        driver.quit()

if __name__ == "__main__":
    main()
