# 导入所需的模块
from selenium import webdriver
from selenium.webdriver.chrome.service import Service  
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import re
import os
import ddddocr
import time

def check_file_existence(download_path, expected_filename):
    """
    检查在指定下载路径中是否存在预期的文件名。

    :param download_path: 文件下载路径。
    :param expected_filename: 预期的下载文件名。
    :return: 如果文件存在返回True，否则返回False。
    """
    file_path = os.path.join(download_path, expected_filename)
    return os.path.exists(file_path)

# 初始化Webdriver，配置下载路径
def init_webdriver(download_path):
    # 设置Chrome选项
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 以无头模式运行Chrome
    chrome_options.add_argument('--disable-gpu')  # 禁用GPU加速
    chrome_options.add_argument('--no-sandbox')  # 在Linux上运行时需要的选项
    chrome_options.add_argument('--disable-dev-shm-usage')  # 禁用/dev/shm临时目录
    # 配置Chrome下载首选项
    chrome_options.add_experimental_option("prefs", {
        "download.default_directory": download_path,  # 设置下载路径
        "download.prompt_for_download": False,  # 禁用下载时的提示
        "download.directory_upgrade": True,  # 允许下载路径的更改
        "safebrowsing.enabled": True  # 启用安全浏览
    })
    # 使用ChromeDriverManager安装Chrome驱动并创建服务
    service = Service(ChromeDriverManager().install())
    # 返回配置好的Chrome WebDriver实例
    return webdriver.Chrome(service=service, options=chrome_options)

# 根据页面URL和标题构造预期的下载文件名
def construct_expected_filename(page_url, page_title):
    """
    根据URL和页面标题构造预期的下载文件名，区分GeoJSON和Shapefile。

    :param page_url: 页面的URL。
    :param page_title: 页面的标题。
    :return: 预期的下载文件名。
    """
    # 使用正则表达式从URL中提取行政区划代码
    admin_code_match = re.search(r'/(\d+).html', page_url)
    admin_code = admin_code_match.group(1) if admin_code_match else ''

    # 根据URL确定是GeoJSON还是Shapefile
    if "geojson" in page_url.lower():
        file_type = "GeoJSON"
    elif "shapefile" in page_url.lower():
        file_type = "Shapefile"
    else:
        file_type = "Unknown"

    # 替换页面标题中不适合文件名的字符，并去除可能的GeoJSON或Shapefile字样
    page_title_cleaned = re.sub(r'(GeoJSON|Shapefile)', '', page_title, flags=re.I).strip()
    page_title_cleaned = page_title_cleaned.replace("下载-POI数据", "").strip()

    # 构造文件名
    filename = f"{page_title_cleaned}_{admin_code}_{file_type}_(poi86.com).zip"
    return filename
def capture_captcha(driver, captcha_xpath, captcha_path):
    """
    截取验证码图片并保存。

    :param driver: WebDriver实例，用于浏览页面和定位元素。
    :param captcha_xpath: 验证码图片的XPath。
    :param captcha_path: 验证码图片的保存路径。
    :return: None
    """
    captcha_element = driver.find_element(By.XPATH, captcha_xpath)
    captcha_element.screenshot(captcha_path)
    print(f"验证码截图已保存为: {captcha_path}")

def recognize_captcha(captcha_path):
    """
    识别给定路径的验证码图片。

    :param captcha_path: 验证码图片的路径。
    :return: 识别出的验证码文本。
    """
    ocr = ddddocr.DdddOcr(show_ad=False, det=False, ocr=True)
    with open(captcha_path, 'rb') as f:
        image = f.read()
    captcha_text = ocr.classification(image)
    return captcha_text

# 打开页面并获取预期的下载文件名
def open_url(driver,page_url, download_path):
    max_attempts=10
    attempt = 0
    while attempt < max_attempts:
        # 初始化WebDriver
        # driver = init_webdriver(download_path)
        # 打开页面
        driver.get(page_url)
        # 获取页面标题
        page_title = driver.title
        print(f"页面标题： {page_title}")  # 打印page_title)
        # 构造预期的下载文件名
        expected_filename = construct_expected_filename(page_url, page_title)
        print(f"预期的下载文件名: {expected_filename}") 
        # 检查文件是否存在
        file_exists = check_file_existence(download_path, expected_filename)
        print(f"文件{'存在' if file_exists else '不存在'}。")
        
        # 如果文件已存在，则不继续执行后续操作
        if file_exists:
            print("文件已存在，跳过下载。")
            return  # 使用return语句提前退出函数
        
        captcha_xpath = "/html/body/div[2]/div/div[2]/form/div[1]/div/img"
        captcha_input_xpath = "/html/body/div[2]/div/div[2]/form/div[1]/input"
        submit_button_xpath = "/html/body/div[2]/div/div[2]/form/div[2]/button" 
        error_message_xpath = "/html/body/div[1]/div/div/div[2]/div"
        
        captcha_path = os.path.join(download_path, "captcha.png")
        capture_captcha(driver, captcha_xpath, captcha_path)

        captcha_text = recognize_captcha(captcha_path)
        print(f"验证码为: {captcha_text}")

        if re.match(r'^[a-zA-Z0-9]{4}$', captcha_text):
            print(f"验证码识别成功: {captcha_text}")
            # 找到验证码输入框并输入验证码
            captcha_input_element = driver.find_element(By.XPATH, captcha_input_xpath)
            captcha_input_element.send_keys(captcha_text)

            # 找到提交按钮并点击
            submit_button_element = driver.find_element(By.XPATH, submit_button_xpath)
            submit_button_element.click()
            # 等待
            time.sleep(3)
            # 检查是否出现了“验证码错误”的提示
            error_messages = driver.find_elements(By.XPATH, error_message_xpath)
            if error_messages and "验证码错误" in error_messages[0].text:
                print("验证码错误，重试...")
                attempt += 1
                continue
            else:
                print("操作成功或没有错误提示")
                break
        else:
            print("验证码识别格式不符合预期，重试...")
            attempt += 1
            continue
    if attempt == max_attempts:
        print("达到最大尝试次数，停止尝试。")
    
    # 退出WebDriver
    # driver.quit()
    

if __name__ == "__main__":

	download_path = "downloads"  # 设置下载路径
	page_url = "https://www.poi86.com/poi/download_area_geojson/421083.html"  # 设置页面URL
	# 初始化webdriver
	driver = init_webdriver(download_path)
	# 遍历URLs并执行操作
	open_url(driver, page_url, download_path)  # 确保传递driver实例
	# 所有操作完成后关闭webdriver
	driver.quit()
