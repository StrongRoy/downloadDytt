# -*- coding: utf-8 -*-
# Created by richie at 2018/11/23


import requests
from lxml import html as hl
import json
import re

BASE_DIMAIN = "http://www.ygdy8.net"  # 定义基础域名
HEADERS = {
    "Referer": "http://www.ygdy8.net/html/tv/oumeitv/list_9_1.html",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"
}


# 获取电影列表页的链接
# 最新电影       base_url = "http://www.dytt8.net/html/gndy/dyzz/list_23_{}.html"
# 国内电影       base_url = "http://www.ygdy8.net/html/gndy/china/list_4_{}.html"
# 欧美电视剧
# base_url = "http://www.ygdy8.net/html/tv/oumeitv/list_9_{}.html"
def movie_list_page():
    # base_url = "http://www.ygdy8.net/html/gndy/china/list_4_{}.html"
    # base_url = "https://www.dytt8.net/html/zongyi2013/list_99_2.html"
    base_url = "http://www.ygdy8.net/html/dongman/list_16_{}.html"
    for x in range(1, 153):
        yield x, base_url.format(x)


# 传入电影列表页地址，返回这一页中每一部电影的详情页面链接
def get_detail_url(url):
    response = requests.get(url, headers=HEADERS)
    text = response.text
    html = hl.etree.HTML(text)
    # /*[@id="header"]/div/div[3]/div[3]/div[2]/div[2]/div[2]/ul/table[1]/tbody/tr[2]/td[2]/b/a
    detail_urls = html.xpath("//table[@class='tbspan']//a[@href!='/html/gndy/jddy/index.html']/@href")
    detail_urls = map(lambda x: BASE_DIMAIN + x, detail_urls)

    return detail_urls


# 通过电影的详情页面链接，获取电影的全部数据
def get_movie_content(url):
    print(url)
    movie = {}
    detail_response = requests.get(url, headers=HEADERS)
    detail_response.encoding = 'gb2312'
    detail_text = detail_response.content.decode(encoding="gb2312", errors="ignore")
    # detail_text = detail_response.text
    detail_html = hl.etree.HTML(detail_text)

    # // *[ @ id = "Zoom"]
    if len(detail_html.xpath("//*[@id='Zoom']")) > 0:
        zoom = detail_html.xpath("//*[@id='Zoom']")[0]
    else:
        return movie  # 说明没有爬取成功，直接跳过返回一个空字典

    # text_list = zoom.xpath(".//p/text()|.//p/span/text()")        # 版本1.0，没有考虑到有的页面中会多出span标签
    # text_list = zoom.xpath(".//p/span/text()|.//p/text()")        # 版本2.0，没有考虑到有的页面中会缺少标签
    text_list = zoom.xpath(".//text()")  # 版本3.0，直接获取页面中的文本，进行过滤
    text = [item for item in text_list if len(item) > 60]
    if text:
        text = text[0]
    else:
        text= u"没有抓取到"
    if len(zoom.xpath(".//td/a/@href")) > 0:
        download_url = zoom.xpath(".//td/a/@href")
    elif len(zoom.xpath(".//td//a/@href")) > 0:
        download_url = zoom.xpath(".//td//a/@href")[-1]
    else:
        download_url = u"爬取失败，手动修改！"
    download_url = "\n".join(download_url)

    # // *[ @ id = "Zoom"] / span / p[1] / img
    if len(zoom.xpath(".//p[1]/img/@src")) > 0:
        content_url = zoom.xpath(".//p[1]/img/@src")[0]
    elif len(zoom.xpath(".//p[1]/img/@src")) > 0:
        content_url = zoom.xpath(".//p[1]/img/@src")[-1]
    else:
        content_url = u""
    movie["download_url"] = download_url
    movie["content_url"] = content_url
    movie['introduction'] = text
    if text:
        res = re.match("《([^》]+)》", text, re.M | re.I)
    if res:
        name = res.group(1)
    else:
        name = "动漫"
    movie["name"] = name
    movie["time"] = 2013

    return movie


if __name__ == '__main__':
    page_urls = movie_list_page()
    for (index, page_url) in page_urls:
        file_name = "dytt_dongman_data/data_" + str(index) + ".json"  # 设置存放每一页电影信息的json文件的名称
        one_page_movie_content = []  # 每一页中所有电影的信息
        movie_detail_urls = get_detail_url(page_url)
        for movie_detail_url in movie_detail_urls:
            movie_content = get_movie_content(movie_detail_url)
            if movie_content:
                one_page_movie_content.append(movie_content)

        #     # 将爬取的每一页的电影数据，分别写入到一个json文件中

        one_page_movie_content_str = json.dumps(one_page_movie_content, ensure_ascii=False, indent=4)

        f = open(file_name, "w")
        f.write(one_page_movie_content_str)
        f.close()

        print("第" + str(index) + "页综艺爬取完成，写入到" + file_name + "文件中")
