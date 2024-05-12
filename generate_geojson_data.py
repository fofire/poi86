import requests
from bs4 import BeautifulSoup
import json
import os

base_url = "https://www.poi86.com"
download_path = "downloads"
os.makedirs(download_path, exist_ok=True)  # 确保下载路径存在
num_provinces_to_fetch = None  # 设置要获取的省份数量，None表示获取全部省份


def get_info(url, tag_class, inner_tag="a"):
    """
    从指定URL的网页中提取特定类的标签下的链接和文本信息。
    """
    try:
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
    except requests.RequestException as e:
        print(f"请求错误: {e}")
        return []
    try:
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")
        elements = soup.find_all(class_=tag_class)
    except Exception as e:
        print(f"解析HTML错误: {e}")
        return []

    # response = requests.get(url)
    # html_content = response.text
    # soup = BeautifulSoup(html_content, 'html.parser')
    # elements = soup.find_all(class_=tag_class)
    info_list = []
    for element in elements:
        info_link = element.find(inner_tag)
        if info_link:
            info_name = info_link.text.strip()
            info_url = base_url + info_link["href"]
            info_list.append({"name": info_name, "url": info_url})
    return info_list


def generate_special_urls_for_taiwan(base_url, admin_code):
    """
    仅为台湾省生成包含“area”类型的geojson和shapefile链接。
    """
    return {
        "geojsons": [
            {
                "name": "area",
                "url": f"{base_url}/poi/download_area_geojson/{admin_code}.html",
            }
        ],
        "shapefiles": [
            {
                "name": "area",
                "url": f"{base_url}/poi/download_area_shapefile/{admin_code}.html",
            }
        ],
    }


def generate_download_urls(base_url, admin_code, file_type):
    """
    根据文件格式生成不同数据类型的下载URL。
    对于"area"类型的数据，其URL格式与其他数据类型有所不同。
    """
    data_types = [
        "area",
#        "buildings",
#        "landuse",
#        "railways",
#        "roads",
#        "water",
#        "waterways",
    ]
    file_type_path = "geojson" if file_type == "geojson" else "shapefile"

    urls = []
    for data_type in data_types:
        if data_type == "area":
            url = f"{base_url}/poi/download_area_{file_type_path}/{admin_code}.html"
        else:
            url = f"{base_url}/poi/download_area_{data_type}_{file_type_path}/{admin_code}.html"
        urls.append({"name": data_type, "url": url})
    return urls


# soup = BeautifulSoup(requests.get(f"{base_url}/poi/amap/areas.html").text, 'html.parser')
# col_md_2_elements = soup.find_all(class_="col-md-2")
try:
    
    soup = BeautifulSoup(
        # https://www.poi86.com/poi/amap/areas.html
        requests.get(f"{base_url}/poi/amap/areas.html").text, "html.parser"
    )
    
    col_md_2_elements = soup.find_all(class_="col-md-2")
except Exception as e:
    print(f"解析省份页面失败: {e}")
    col_md_2_elements = []

data = []

if num_provinces_to_fetch is None or num_provinces_to_fetch > len(col_md_2_elements):
    num_provinces_to_fetch = len(col_md_2_elements)

for province_index, element in enumerate(
    col_md_2_elements[:num_provinces_to_fetch], start=1
):
    province = element.find("strong").text.strip()
    print(f"正在获取第 {province_index}/{num_provinces_to_fetch} 个省份：{province}")
    if province == "台湾省":  # 特别处理台湾省
        special_urls = generate_special_urls_for_taiwan(
            base_url, province_code)
        data.append(
            {"province": province, "url": province_url, **special_urls})
    else:
        province_url = base_url + element.find("a")["href"]
        province_code = province_url.split("/")[-1].split(".")[0]  # 获取省份行政编号
        province_geojsons = generate_download_urls(
            base_url, province_code, "geojson")
       # province_shapefiles = generate_download_urls(
       #     base_url, province_code, "shapefile"
       # )
        cities = get_info(province_url, "list-group-item")
        for city_index, city in enumerate(cities, start=1):
            print(
                f"  正在获取省份 {province} 下的第 {city_index}/{len(cities)} 个城市：{city['name']}"
            )
            city_url = city["url"]
            city_code = city_url.split("/")[-1].split(".")[0]  # 获取城市行政编号
            city["geojsons"] = generate_download_urls(
                base_url, city_code, "geojson")
 #           city["shapefiles"] = generate_download_urls(
 #               base_url, city_code, "shapefile"
 #           )
            city["districts"] = []
            districts = get_info(city_url, "list-group-item")
            for district in districts:
                district_url = district["url"]
                district_code = district_url.split("/")[-2]  # 获取区县行政编号
                district["geojsons"] = generate_download_urls(
                    base_url, district_code, "geojson"
                )
#                district["shapefiles"] = generate_download_urls(
#                    base_url, district_code, "shapefile"
#                )
                city["districts"].append(district)
        data.append(
            {
                "province": province,
                "url": province_url,
                "geojsons": province_geojsons,
#                "shapefiles": province_shapefiles,
                "cities": cities,
            }
        )


# with open(f"{download_path}/province_city_district_urls.json", "w", encoding="utf-8") as json_file:
#     json.dump(data, json_file, ensure_ascii=False, indent=4)

# print("数据已保存至 province_city_district_urls.json")
try:
    with open(
        f"{download_path}/province_city_district_urls.json", "w", encoding="utf-8"
    ) as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
    print("数据已保存至 province_city_district_urls.json")
except Exception as e:
    print(f"写入文件时出错: {e}")
