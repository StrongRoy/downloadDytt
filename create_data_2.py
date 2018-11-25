# -*- coding: utf-8 -*-
# Created by richie at 2018/11/22


# sql = "(25, 9, '我的间谍前男友', 'The Ballad of Buster Scruggs ', '', '#FF0000', '米拉·库尼斯 Mila Kunis ', '苏珊娜·福格尔 Susanna Fogel ', '<span style=\"color:#183778;font-family:Verdana, Arial, Helvetica, sans-serif;white-space:normal;background-color:#FFFFFF;\">奥黛丽（米拉·库妮丝 饰）和摩根（凯特·迈克金农 饰）两位好闺蜜，因奥黛丽前男友的间谍身份，意外被卷入一场国际阴谋，她们开始与各位杀手斗智斗勇，在一名可疑但有魅力的英国特工带领下，实施拯救世界的计划，在欧洲大陆上演惊心动魄又啼笑皆非的国际逃亡之旅。</span>', 'video/2018-11-21/5bf5104c5d4fe.jpg', '美国', '英语', 2018, '', 1542787260, 2, 2, 2, 2, 1542787209, 4, 1, 0, 0, 'ftp://ygdy8:ygdy8@yg45.dydytt.net:8355/阳光电影www.ygdy8.com.我的间谍前男友.BD.720p.国英双语双字.mkv', 'ftp://ygdy8:ygdy8@yg45.dydytt.net:8355/阳光电影www.ygdy8.com.我的间谍前男友.BD.720p.国英双语双字.mkv', 'admin', '', 'W', 10.0, 1, 0);"


import requests
from lxml import html as hl
import json
import re

BASE_DIMAIN = "http://www.dytt8.net"  # 定义基础域名
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36"
}


# 获取电影列表页的链接
def movie_list_page():
    base_url = "http://www.dytt8.net/html/gndy/dyzz/list_23_{}.html"
    for x in range(1, 40):
        yield x,base_url.format(x)


# 传入电影列表页地址，返回这一页中每一部电影的详情页面链接
def get_detail_url(url):
    response = requests.get(url, headers=HEADERS)
    text = response.text
    html = hl.etree.HTML(text)
    detail_urls = html.xpath("//table[@class='tbspan']//a[@href!='/html/gndy/jddy/index.html']/@href")
    detail_urls = map(lambda x: BASE_DIMAIN + x, detail_urls)

    return detail_urls


# 通过电影的详情页面链接，获取电影的全部数据
def get_movie_content(url):
    movie = {}
    detail_response = requests.get(url, headers=HEADERS)
    detail_response.encoding = 'gb2312'
    detail_text = detail_response.content.decode(encoding="gb2312", errors="ignore")
    # detail_text = detail_response.text
    detail_html = hl.etree.HTML(detail_text)


    if len(detail_html.xpath("//div[@id='Zoom']")) > 0:
        zoom = detail_html.xpath("//div[@id='Zoom']")[0]
    else:
        return movie  # 说明没有爬取成功，直接跳过返回一个空字典

    # text_list = zoom.xpath(".//p/text()|.//p/span/text()")        # 版本1.0，没有考虑到有的页面中会多出span标签
    # text_list = zoom.xpath(".//p/span/text()|.//p/text()")        # 版本2.0，没有考虑到有的页面中会缺少标签
    text_list = zoom.xpath(".//text()")  # 版本3.0，直接获取页面中的文本，进行过滤

    for (index, text) in enumerate(text_list):
        # print(text)
        # if text.startswith(u'《'):
        #     print text
        if text.startswith(u"◎译　　名"):
            movie["teanslation_title"] = text.replace(u"◎译　　名", "").strip()
        elif text.startswith(u"◎片　　名"):
            movie["real_title"] = text.replace(u"◎片　　名", "").strip()
        elif text.startswith(u"◎年　　代"):
            movie["time"] = text.replace(u"◎年　　代", "").strip()
        elif text.startswith(u"◎产　　地"):
            movie["place"] = text.replace(u"◎产　　地", "").strip()
        elif text.startswith(u"◎类　　别"):
            movie["category"] = text.replace(u"◎类　　别", "").strip()
        elif text.startswith(u"◎语　　言"):
            movie["language"] = text.replace(u"◎语　　言", "").strip()
        elif text.startswith(u"◎上映日期"):
            movie["release_time"] = text.replace(u"◎上映日期", "").strip()
        elif text.startswith(u"◎豆瓣评分"):
            movie["douban_score"] = text.replace(u"◎豆瓣评分", "").strip()
        elif text.startswith(u"◎片　　长"):
            movie["length"] = text.replace(u"◎片　　长", "").strip()
        elif text.startswith(u"◎导　　演"):
            movie["director"] = text.replace(u"◎导　　演", "").strip()
        elif text.startswith(u"◎主　　演"):
            actors = []
            actors.append(text.replace(u"◎主　　演", "").strip())
            for num in range(index + 1, index + 10):
                if (text_list[num].startswith(u"◎简　　介")):
                    break
                else:
                    actors.append(text_list[num].strip())
            movie["actors"] = actors
        elif text.startswith(u"◎简　　介"):
            conttent_index = index + 1
            movie["introduction"] = text_list[conttent_index].strip()

    if len(zoom.xpath(".//td/a/@href")) > 0:
        download_url = zoom.xpath(".//td/a/@href")[0]
    elif len(zoom.xpath(".//td//a/@href")) > 0:
        download_url = zoom.xpath(".//td//a/@href")[-1]
    else:
        download_url = u"爬取失败，手动修改！"

    # // *[ @ id = "Zoom"] / span / table / tbody / tr / td / a
    # // *[ @ id = "Zoom"] / span / p[1] / img[2]

    if len(zoom.xpath(".//p[1]/img[2]/@src")) > 0:
        content_url = zoom.xpath(".//p[1]/img[2]/@src")[0]
    elif len(zoom.xpath(".//p[1]/img[2]/@src")) > 0:
        content_url = zoom.xpath(".//p[1]/img[2]/@src")[-1]
    else:
        content_url = u"爬取失败，手动修改！"

    movie["download_url"] = download_url
    movie["content_url"] = content_url
    return movie


if __name__ == '__main__':
    page_urls = movie_list_page()
    for (index, page_url) in page_urls:
        print(index,page_url)
        file_name = "new_movie_" + str(index) + ".json"  # 设置存放每一页电影信息的json文件的名称
        one_page_movie_content = []  # 每一页中所有电影的信息
        movie_detail_urls = get_detail_url(page_url)

        for movie_detail_url in movie_detail_urls:
            movie_content = get_movie_content(movie_detail_url)
            one_page_movie_content.append(movie_content)

        #     # 将爬取的每一页的电影数据，分别写入到一个json文件中

        one_page_movie_content_str = json.dumps(one_page_movie_content, ensure_ascii=False, indent=4)

        f = open(file_name, "w")
        f.write(one_page_movie_content_str)
        f.close()

        print("第" + str(index) + "页电影爬取完成，写入到" + file_name + "文件中")
