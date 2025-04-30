from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

def fetch_video_links(url):
    # 初始化webdriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    
    try:
        # 打开目标页面
        driver.get(url)
        
        # 给页面足够的时间加载动态内容
        time.sleep(5)  # 简单的等待方法，实际应用中考虑更智能的等待方式
        
        # 查找页面上的所有视频链接
        video_elements = driver.find_elements(By.XPATH, '//*[@id="video-title"]')
        
        links = []
        for elem in video_elements:
            href = elem.get_attribute('href')
            if href:
                links.append(href)
                print(f"Found video link: {href}")
                
        return links
    
    finally:
        # 关闭浏览器
        driver.quit()

if __name__ == "__main__":
    youtube_url = "https://www.youtube.com/@ZYFXS"
    video_links = fetch_video_links(youtube_url)
    print("All video links:")
    for link in video_links:
        print(link)
