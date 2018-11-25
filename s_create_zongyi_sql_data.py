# -*- coding: utf-8 -*-
# Created by richie at 2018/11/22

import json
from pypinyin import lazy_pinyin, Style
import time
import markdown
import os
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
            name = movie.get('name',"无名")
            letter = lazy_pinyin(name, style=Style.FIRST_LETTER)[0].upper()
            language = "普通话"
            area = "中国"

            content = "{0}![]({1})".format(movie.get('introduction', ""), movie['content_url'])
            filed = (start_id,
                     3,
                     name,
                     "",
                     '',
                     "#FF0000",
                     "",
                     "",
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
    filename = "dongman.sql"
    if os.path.exists(filename):
        os.remove(filename)
    f = open(filename, "a")
    start_id = 8675
    for i in range(1, 21):
        file_name = "dytt_dongman_data/data_{}.json".format(i)
        print(file_name)
        lines, start_id = get_one_json(file_name, start_id)
        for item in lines:
            f.write(item + ';\n')
    f.close()
