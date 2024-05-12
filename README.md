# poi86.com

## 使用说明

1. 环境准备

### 依赖

- python=3.9.19
- requests
- beautifulsoup4
- ddddocr
- selenium
- webdriver-manager

#### 环境

1. 创建和激活环境

```bash
pyenv install 3.9.19
pyenv local 3.9.19
python -m venv "$(basename "$(pwd)")_env"
source "$(basename "$(pwd)")_env/bin/activate"
```

2. 退出和删除环境

```bash
source deactivate
rm -rf "$(basename "$(pwd)")_env"
```

#### 安装依赖

1. 安装依赖 `requests`、 `beautifulsoup4`、`selenium`、`webdriver-manager`

```bash
pip install requests beautifulsoup4 selenium webdriver-manager

pip freeze > requirements.txt
pip install -r requirements.txt
```

2. 安装 [ddddocr](https://github.com/sml2h3/ddddocr),`python <= 3.9`

```bash
pip install ddddocr
```

##### 使用`ddddocr`

```python
import ddddocr

ocr = ddddocr.DdddOcr(show_ad=False,det=False,ocr=True)

with open("Captcha.jpeg", 'rb') as f:
image = f.read()

res = ocr.classification(image)
print(res)
```

2. 运行 fetch_geojson_urls.py 文件，该文件会爬取各省市区的地理数据下载链接，并保存到 province_city_district_urls.json 文件中。

## 注意事项

- 请确保您的爬取行为符合网站的使用条款，并且不违反任何法律法规。
- 注意处理异常情况，并且尊重网站的服务器负载。
- 在使用爬虫下载大量数据时，可能需要考虑限速和重试机制，以防止对网站服务器造成过大负载。

## 许可证

本项目采用 MIT 许可证。
