# -*- coding: utf-8 -*-
# Created by richie at 2018/11/22

import json
from pypinyin import lazy_pinyin, Style
import time
import markdown

category_map = {
    u"动作": 8,
    u"喜剧": 9,
    u"爱情": 10,
    u"科幻": 11,
    u"剧情": 12,
    u"恐怖": 13,
    u"战争": 14,
    u"": 8,
}


def get_one_json(file_name, start_id):
    with open(file_name, "r") as f:
        one_page_movie_content_str = f.read()
    one_page_movie_content = json.loads(one_page_movie_content_str, encoding="utf-8")
    lines = []
    for movie in one_page_movie_content:
        try:
            start_id += 1
            if '/' in movie.get('teanslation_title', movie.get("real_title", "无名")):
                name = movie.get('teanslation_title', movie.get("real_title", "无名")).split("/")[0]
            else:
                name = movie.get('teanslation_title', movie.get("real_title"))
            letter = lazy_pinyin(name, style=Style.FIRST_LETTER)[0].upper()
            if len(letter) > 1:
                letter = letter[0]
            s_language = movie.get('language', "")
            if "/" in s_language:
                language = s_language.split("/")[0]
            elif "," in s_language:
                language = s_language.split(",")[0]
            else:
                language = "普通话"

            s_area = movie.get('place', "")

            if "/" in s_area:
                area = s_area.split("/")[0]
            elif " " in s_area:
                area = s_area.split(" ")[0]
            else:
                area = s_area
            if len(language)  > 10:
                print(language)
            # print(start_id,language, area)

            content = "{0}![]({1})".format(movie.get('introduction', ""), movie['content_url'])
            filed = (start_id,
                     15,
                     # category_map.get(movie.get('category', "").split("/")[0], 8),
                     name,
                     movie['real_title'],
                     '',
                     "#FF0000",
                     ",".join(movie.get('actors', [])[:2]),
                     ",".join(movie.get('director', [])),
                     markdown.markdown(content),
                     'error',
                     area,
                     language,
                     int(movie.get("time", 0)),
                     '0',
                     int(time.time()),
                     0,
                     0,
                     0,
                     0,
                     0,
                     5,
                     1,
                     0,
                     0,
                     movie["download_url"],
                     movie["download_url"],
                     'admin',
                     '',
                     letter,
                     10.0,
                     1,
                     0,)
        except Exception:
            continue
        # filed = json.dumps(str(filed), ensure_ascii=False, indent=4, encoding='utf-8')
        # print filed
        lines.append("""INSERT INTO `gx_video` VALUES """ + str(filed))

    return lines, start_id


if __name__ == "__main__":
    f = open("huayu_tv.sql", "a")
    start_id = 4680
    for i in range(1, 22):
        file_name = "dytt_tv_hytv_data/tv_hy_{}.json".format(i)
        print(file_name)
        lines, start_id = get_one_json(file_name, start_id)
        for item in lines:
            f.write(item + ';\n')
    f.close()
