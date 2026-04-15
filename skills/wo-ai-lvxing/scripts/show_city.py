#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
城市景点图片下载 + 展示脚本
用法：python show_city.py --city 上海
输出：打印可在 VS Code Chat 中直接粘贴的 Markdown（使用本地 file:/// 路径）
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    print("缺少依赖，请运行：pip install Pillow requests")
    sys.exit(1)

# ─────────────────────────────────────────────
# 与 generate_travel_diary.py 保持同步的景点数据
# ─────────────────────────────────────────────
ATTRACTION_DATA = {
    "上海": {
        "外滩": {
            "name_en": "The Bund, Shanghai",
            "description": "外滩是上海最具代表性的历史地标，沿黄浦江西岸绵延约1.6公里，两侧矗立着52栋风格各异的万国建筑群。对岸的陆家嘴摩天楼群与这片旧日繁华遥遥相望，构成了魔都最震撼的天际线。",
            "tips": "建议傍晚至夜间游览，华灯璀璨。可乘坐黄浦江游船从水面欣赏双岸夜景。",
            "best_time": "傍晚至夜间",
            "ticket": "免费开放",
            "wikimedia_file": "Bund_at_night_Shanghai.jpg",
            "image_filename": "waitan.jpg"
        },
        "东方明珠广播电视塔": {
            "name_en": "Oriental Pearl Tower",
            "description": "高耸入云的东方明珠塔是上海浦东的精神图腾，高468米，设计灵感源自唐代诗人白居易的名句《大珠小珠落玉盘》。共有15个观光层，站在玻璃地板观景台俯瞰整个上海，脚下是滚滚黄浦江，远望是无边的都市画卷。",
            "tips": "购买联票同时参观塔内《上海城市历史发展陈列馆》，了解上海百年演变历史。",
            "best_time": "下午3点后（可先拍日景再等夜景）",
            "ticket": "约人民币180元（含全程观光）",
            "wikimedia_file": "Oriental_Pearl_Tower_2012.jpg",
            "image_filename": "oriental_pearl.jpg"
        },
        "豫园": {
            "name_en": "Yu Garden",
            "description": "豫园是上海保存最完好的江南古典园林，始建于1559年明代，由官员潘允端为孝敬父亲而打造，《豫》字取《豫悦老亲》之意。园内湖光山石、亭台楼阁曲折相连，龙墙蜿蜒起伏，四百余年古银杏苍劲挺拔。",
            "tips": "游园后别错过隔壁豫园商城的城隍庙小吃，南翔小笼包是必试经典。",
            "best_time": "工作日上午开门时（避开周末高峰）",
            "ticket": "约人民币40元",
            "wikimedia_file": "Yuyuan_Garden.jpg",
            "image_filename": "yuyuan.jpg"
        }
    },
    "商丘": {
        "商丘古城": {
            "name_en": "Historic City of Shangqiu",
            "description": "商丘古城，又称归德府城，始建于明正德六年（1511年），是中国保存最完整的明清古城之一。古城呈龟背形，城墙高大巍峨，外有护城河环绕。此地叠压着商、周、汉、宋、明五个朝代的古城遗址，被誉为「城摞城」的千年奇观。",
            "tips": "可登上城墙步道漫步，傍晚灯光亮起时最为壮观。",
            "best_time": "春秋两季；傍晚城墙灯光最美",
            "ticket": "景区免费，部分建筑有门票",
            "wikimedia_file": "20220726_Gongchen_Gate,_Historic_City_of_Shangqiu.jpg",
            "image_filename": "shangqiu_old_city.jpg"
        },
        "阏伯台（火神台）": {
            "name_en": "Ebo Tai (Fire God Platform)",
            "description": "阏伯台，又名火神台，是中国现存最早的天文台遗址，距今已有四千余年历史。相传帝喾之子阏伯被封于商，守护人间火种，后世尊其为火神。高台呈圆锥形，高35米，拾级而上望尽豫东平原。每逢农历正月初七祭祀大典，万人赶庙会，是商丘最重要的民间节俗。",
            "tips": "农历正月初七是火神庙会，人气最旺；清晨登台看日出别有意境。",
            "best_time": "农历正月初七庙会期间；清晨看日出",
            "ticket": "约人民币30元",
            "wikimedia_file": "WV_Shangqiu_Banner.jpg",
            "image_filename": "ebo_tai.jpg"
        },
        "芒砀山汉梁王陵": {
            "name_en": "Liang State Tombs at Mount Mangdang",
            "description": "芒砀山是豫东平原唯一山地，因刘邦在此斩白蛇起义而名垂青史。山中密布西汉梁国王室陵墓群，梁孝王陵山体开凿深达百余米，号称「天下石室第一陵」。陵中壁画《四神云气图》被誉为「敦煌前之敦煌」，是国宝级文物。",
            "tips": "王陵内部全年恒温，夏天游览凉爽；建议穿舒适步行鞋，陵内通道较低。",
            "best_time": "春季（3-5月）或秋季（9-11月）",
            "ticket": "约人民币120元（含景区交通）",
            "wikimedia_file": "Liang_State_Tombs,_Mangdang_Mountain_1.jpg",
            "image_filename": "mangdang_mountain.jpg"
        }
    },
    "北京": {
        "故宫（紫禁城）": {
            "name_en": "The Forbidden City (Palace Museum)",
            "description": "故宫是中国明清两朝的皇家宫殿，建于1406年，历时24位皇帝居于此处达505年。它占地72公頃，现存建筑980座，是世界上规模最大、保存最完整的古代木结构建筑群。天干中心轴线纵贯全宫，金璦郁璦层叠起伏，是中国封建皇瑟制度的最高展现。",
            "tips": "建议提前在官方App预约门票，现场不售票。建议上午开门时即到避开人流高峰。",
            "best_time": "春秋两季；工作日上午开门时人流较少",
            "ticket": "淡季人民幱60元，旺季人民幱80元",
            "wikimedia_file": "The_Forbidden_City_-_View_from_Coal_Hill.jpg",
            "image_filename": "forbidden_city.jpg"
        },
        "颐和园": {
            "name_en": "Summer Palace (Yiheyuan)",
            "description": "颐和园是中国保存最完整的皇家园林，1998年列入联合国教科文组织世界文化遗产。园内以万寿山和昆明湖为核心，佛香阁岅立山中、七百二十八米长廸延展湖临，清漯水中映帥1000余年前的皇家气象，近代历史与自然山水入画一般合谐共存。",
            "tips": "今可乘坐游船游昆明湖，景夜游巴为汉。建议从东宫门走进，沿长廸漫步至石軸。",
            "best_time": "春季（三億月桃花盛开）或秋季（10月红叶最美）",
            "ticket": "入园票人民幱30元，聪联票人民幱60元（含内景点）",
            "wikimedia_file": "Kina_Summerpalace_117.jpg",
            "image_filename": "summer_palace.jpg"
        },
        "天坛": {
            "name_en": "Temple of Heaven (Tiantan)",
            "description": "天坛是明清两朝帝王祒天、祈谷的神圣場所，建于1420年，与北京故宫同年建成。其中祈年殿是滚天最完美的名片建筑之一，三层蓝色琦琊屋呈圆形，不使一款铉钉纯用梗汰材万榙方杂尉袍。圆丘坛天心石站在上发出的声音层层反射回脸硪奇无比。",
            "tips": "公儸公园早晨常出现各种民间技艺表演，早起进园欣赏。建议游览顺序：局外圆丘坛→皇穹宇→祈年殿。",
            "best_time": "春天(天气晴朗)或秋天(蓝天栅叶映衬祈年殿)最美",
            "ticket": "入园票人民幱15元，聪联票人民幱34元（含内部建筑）",
            "wikimedia_file": "TempleofHeaven-HallofPrayer.jpg",
            "image_filename": "temple_of_heaven.jpg"
        }
    },
    "南京": {
        "中山陵": {
            "name_en": "Sun Yat-sen Mausoleum",
            "description": "中山陵是中国革命先行者孙中山先生的陵墓，建于1926—1929年，依钟山南坡而建。392级石阶象征着艰辛的革命历程，登至祭堂可俯瞰南京城全貌。气势雄伟、庄严肃穆，是中国近代史上最重要的纪念建筑之一，也是南京必游地标。",
            "tips": "建议徒步攀登392级台阶感受革命精神；清晨或傍晚游人较少，光线最美。可与明孝陵合并游览。",
            "best_time": "春季（梅花盛开3-4月）或秋季（红叶10-11月）",
            "ticket": "免费开放",
            "wikimedia_file": "Sun_yatse_mausoleum.jpg",
            "image_filename": "zhongshaling.jpg"
        },
        "明孝陵": {
            "name_en": "Ming Xiaoling Mausoleum",
            "description": "明孝陵是明朝开国皇帝朱元璋及皇后马氏的合葬陵墓，建于1381年，是中国现存最大的明代皇陵。陵前神道两侧排列着12对巨型石兽与6对石人，气势恢宏。2003年列入联合国教科文组织世界遗产名录，是南京最重要的历史遗迹之一。",
            "tips": "从下马坊入口进，沿神道走至宝城；与中山陵相邻，适合合并游览，全程步行约需2—3小时。",
            "best_time": "春季赏梅（2-3月），秋季红叶（10-11月）最佳",
            "ticket": "约人民币70元",
            "wikimedia_file": "Ming_Xiaoling_Mausoleum_Spirit_Way.jpg",
            "image_filename": "ming_xiaoling.jpg"
        },
        "夫子庙秦淮风光带": {
            "name_en": "Confucius Temple & Qinhuai River Scenic Area",
            "description": "夫子庙，古称金陵文庙，始建于1034年北宋，是供奉和祭祀孔子的庙宇。庙前的秦淮河是六朝以来的风流繁华之地，河畔画舫穿梭，两岸酒肆林立。夜晚华灯璀璨倒映水中，是南京最具烟火气的历史街区，灯火辉煌令人流连忘返。",
            "tips": "傍晚乘坐秦淮画舫游览夜景，别错过桂花鸭、状元豆等本地小吃；元宵节灯会时期最为壮观。",
            "best_time": "傍晚至夜间（灯光最美）；元宵节灯会尤为壮观",
            "ticket": "景区免费，游船约人民币100元",
            "wikimedia_file": "Fuzimiao_nanjing.JPG",
            "image_filename": "fuzimiao.jpg"
        }
    },
    "洛阳": {
        "龙门石窟": {
            "name_en": "Longmen Grottoes",
            "description": "龙门石窟是中国三大石刻艺术宝库之一，2000年列入联合国教科文组织世界文化遗产。两山崖壁上密布着2300余个石龛、10万余尊佛像，最高的卢舍那大佛高达17.14米，面容慈悲安详，被誉为'东方蒙娜丽莎'。伊河两岸青山如黛，石窟与山水相映，历经1500年的时光沉淀，至今仍震撼人心。",
            "tips": "建议游览西山石窟为主，重点参观奉先寺卢舍那大佛；夜游龙门灯光秀极为壮观，白天游览适合拍照。",
            "best_time": "春季（4月牡丹盛开）或秋季（10月红叶金黄）",
            "ticket": "约人民币90元",
            "wikimedia_file": "Longmen Grottoes, Luoyang, Henan.jpg",
            "image_filename": "longmen_grottoes.jpg"
        },
        "白马寺": {
            "name_en": "White Horse Temple",
            "description": "白马寺始建于东汉永平十一年（公元68年），是中国第一座官方修建的佛教寺院，素有'中国第一古刹'之称。相传汉明帝遣使西域求法，两位印度高僧以白马驮载佛经来华，皇帝特建此寺以纪念。寺内现存建筑多为元明时期遗构，古朴庄严，近2000年香火不断。",
            "tips": "寺内有来自印度、缅甸、泰国的佛殿，风格迥异；清晨梵钟响起时氛围最为庄严肃穆。",
            "best_time": "清晨（晨钟暮鼓最具禅意）",
            "ticket": "约人民币50元",
            "wikimedia_file": "White Horse Temple 2.jpg",
            "image_filename": "white_horse_temple.jpg"
        },
        "关林": {
            "name_en": "Guanlin Temple",
            "description": "关林是埋葬三国名将关羽首级之处，也是中国唯一以'林'命名的武将冢，始建于汉代，明万历年间扩建为现今规模。殿宇宏伟、古柏参天，石狮石碑成排列队，气势肃穆。关羽被历代帝王封为'武圣'，关林是全球华人祭祀关公的重要圣地，香火旺盛。",
            "tips": "门前立有清代石碑72通，碑林极具历史价值；正月十三关公诞辰庙会人气极旺，是感受民俗的好时机。",
            "best_time": "全年皆宜；正月十三庙会热闹非凡",
            "ticket": "约人民币40元",
            "wikimedia_file": "Guanlin Temple, Luoyang - September 2011 (6154312540).jpg",
            "image_filename": "guanlin.jpg"
        }
    }
}


def get_wikimedia_direct_url(filename: str) -> str:
    """通过 Wikimedia Commons API 获取图片直链"""
    try:
        api_url = "https://commons.wikimedia.org/w/api.php"
        params = {
            "action": "query",
            "titles": f"File:{filename}",
            "prop": "imageinfo",
            "iiprop": "url",
            "iiurlwidth": 1000,
            "format": "json"
        }
        headers = {"User-Agent": "TravelDiaryBot/1.0 (educational project)"}
        resp = requests.get(api_url, params=params, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                return info[0].get("thumburl") or info[0].get("url", "")
        return ""
    except Exception:
        return ""


def download_image(wikimedia_file: str, save_path: Path) -> bool:
    """下载图片到本地路径"""
    if save_path.exists() and save_path.stat().st_size > 1000:
        return True
    url = get_wikimedia_direct_url(wikimedia_file)
    if not url:
        return False
    try:
        headers = {"User-Agent": "TravelDiaryBot/1.0"}
        resp = requests.get(url, headers=headers, timeout=30, stream=True)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        img = Image.open(save_path)
        img.verify()
        return True
    except Exception as e:
        if save_path.exists():
            save_path.unlink()
        return False


def main():
    parser = argparse.ArgumentParser(description="城市景点展示工具")
    parser.add_argument("--city", required=True, help="城市名称")
    parser.add_argument("--output-dir", default=".", help="输出基础目录")
    parser.add_argument("--round", type=int, default=1, help="本轮展示（用于避免重复）")
    args = parser.parse_args()

    city = args.city
    base_dir = Path(args.output_dir)
    city_data = ATTRACTION_DATA.get(city)

    if not city_data:
        print(f"ERROR: 未找到城市 {city} 的景点数据")
        sys.exit(1)

    # 下载图片到本地
    images_dir = base_dir / "旅行日记" / city / "景点图片"
    images_dir.mkdir(parents=True, exist_ok=True)

    result = {"city": city, "attractions": []}

    for name, data in city_data.items():
        attr_dir = images_dir / name
        attr_dir.mkdir(exist_ok=True)
        img_path = attr_dir / data["image_filename"]
        success = download_image(data["wikimedia_file"], img_path)
        # 转为绝对路径，适配 file:/// 协议
        abs_path = str(img_path.resolve()).replace("\\", "/")
        result["attractions"].append({
            "name": name,
            "name_en": data["name_en"],
            "description": data["description"],
            "tips": data["tips"],
            "best_time": data["best_time"],
            "ticket": data["ticket"],
            "image_local_path": abs_path if success else "",
            "image_ok": success
        })

    # 输出 JSON 供调用方读取
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
