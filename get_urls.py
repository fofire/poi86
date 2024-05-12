import json

def get_urls(file_path, num_provinces_to_fetch=None):
    """
    从JSON文件中读取并返回省、市、县的GeoJSON和Shapefile URL列表。

    :param file_path: JSON文件的路径。
    :param num_provinces_to_fetch: 要处理的省份数量。如果为None，则处理所有省份。
    :return: 包含URLs的列表。
    """
    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    if num_provinces_to_fetch is None or num_provinces_to_fetch > len(data):
        num_provinces_to_fetch = len(data)

    urls = []
    for province in data[:num_provinces_to_fetch]:
        urls.extend([geojson['url'] for geojson in province.get("geojsons", [])])
        urls.extend([shapefile['url'] for shapefile in province.get("shapefiles", [])])

        if province['province'] != "台湾省":
            for city in province.get('cities', []):
                urls.extend([geojson['url'] for geojson in city.get('geojsons', [])])
                urls.extend([shapefile['url'] for shapefile in city.get('shapefiles', [])])

                for district in city.get('districts', []):
                    urls.extend([geojson['url'] for geojson in district.get('geojsons', [])])
                    urls.extend([shapefile['url'] for shapefile in district.get('shapefiles', [])])

    return urls


if __name__ == "__main__":
    json_path = "downloads/province_city_district_urls.json"  
    get_urls(json_path) 