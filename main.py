# main.py
from get_urls import get_urls
from download_file import open_url, init_webdriver

def main():
    download_path = "downloads"
    file_path = download_path + "/province_city_district_urls.json"
    num_provinces_to_fetch = None  # 设置为您想处理的省份数量 None表示处理所有省份
    urls = get_urls(file_path, num_provinces_to_fetch)
    
    # 初始化webdriver
    driver = init_webdriver(download_path)
    
    # 遍历URLs并执行操作
    for page_url in urls:  # 这里[:1]确保只处理第一个URL
        open_url(driver, page_url, download_path)  # 确保传递driver实例
        
    # 所有操作完成后关闭webdriver
    driver.quit()
    
if __name__ == "__main__":
    main()
