#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
旅行日记生成器
功能：下载景点图片、创建文件夹结构、生成 PDF 旅行日记
用法：python generate_travel_diary.py --city 上海 --attractions 外滩 东方明珠塔 豫园
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path
from datetime import datetime
from io import BytesIO

try:
    from fpdf import FPDF
    from PIL import Image
except ImportError:
    print("缺少依赖，请运行：pip install fpdf2 Pillow requests")
    sys.exit(1)


# ─────────────────────────────────────────────
# 景点图片数据库（Wikimedia Commons 公开图片）
# ─────────────────────────────────────────────
ATTRACTION_DATA = {
    "上海": {
        "外滩": {
            "name_en": "The Bund, Shanghai",
            "description": "外滩是上海最具代表性的历史地标，沿黄浦江西岸绵延约1.6公里，两侧矗立着52栋风格各异的万国建筑群。对岸的陆家嘴摩天楼群与这片旧日繁华遥遥相望，构成了魔都最震撼的天际线。",
            "tips": "建议傍晚至夜间游览，日落后建筑灯光全亮，华灯璀璨。也可乘坐黄浦江游船从水面欣赏双岸夜景。",
            "best_time": "傍晚至夜间",
            "ticket": "免费开放",
            "image_url": "",
            "wikimedia_file": "Bund_at_night_Shanghai.jpg",
            "image_filename": "waitan.jpg"
        },
        "东方明珠广播电视塔": {
            "name_en": "Oriental Pearl Tower",
            "description": "高耸入云的东方明珠塔是上海浦东的精神图腾，高468米，设计灵感源自唐代诗人白居易的名句『大珠小珠落玉盘』。共有15个观光层，站在玻璃地板观景台俯瞰整个上海，脚下是滚滚黄浦江，远望是无边的都市画卷。",
            "tips": "购买联票同时参观塔内的『上海城市历史发展陈列馆』，了解上海百年演变历史。",
            "best_time": "下午3点后（可先拍日景再等夜景）",
            "ticket": "约人民币180元（含全程观光）",
            "image_url": "",
            "wikimedia_file": "Oriental_Pearl_Tower_2012.jpg",
            "image_filename": "oriental_pearl.jpg"
        },
        "豫园": {
            "name_en": "Yu Garden",
            "description": "豫园是上海保存最完好的江南古典园林，始建于1559年明代，由官员潘允端为孝敬父亲而打造，『豫』字取『豫悦老亲』之意。园内湖光山石、亭台楼阁曲折相连，龙墙蜿蜒起伏，四百余年古银杏苍劲挺拔。",
            "tips": "游园后别错过隔壁豫园商城的城隍庙小吃，南翔小笼包是必试经典。",
            "best_time": "工作日上午开门时（避开周末高峰）",
            "ticket": "约人民币40元",
            "image_url": "",
            "wikimedia_file": "Yuyuan_Garden.jpg",
            "image_filename": "yuyuan.jpg"
        }
    },
    "商丘": {
        "商丘古城": {
            "name_en": "Historic City of Shangqiu",
            "description": "商丘古城，又称归德府城，始建于明正德六年（1511年），是中国保存最完整的明清古城之一。古城呈龟背形，城墙高大巍峨，外有护城河环绕。城内街道棋盘式分布，是一座活着的历史博物馆。1986年被列为全国历史文化名城，此地叠压着商、周、汉、宋、明五个朝代的古城遗址，被誉为城摞城的千年奇观。",
            "tips": "可登上城墙步道漫步，从东南西北四个方向感受古城全貌，傍晚灯光亮起时最为壮观。",
            "best_time": "春秋两季；傍晚城墙灯光最美",
            "ticket": "景区免费，部分建筑有门票",
            "image_url": "",
            "wikimedia_file": "20220726_Gongchen_Gate,_Historic_City_of_Shangqiu.jpg",
            "image_filename": "shangqiu_old_city.jpg"
        },
        "阏伯台（火神台）": {
            "name_en": "Ebo Tai (Fire God Platform)",
            "description": "阏伯台，又名火神台，是中国现存最早的天文台遗址，距今已有四千余年历史。相传帝喾之子阏伯被封于商，在此主管祭祀，守护人间火种，后世尊其为火神。高台呈圆锥形，高35米，拾级而上望尽豫东平原。每逢农历正月初七祭祀大典，万人赶庙会，是商丘最重要的民间节俗。",
            "tips": "农历正月初七是火神庙会，人气最旺；平日清晨登台看日出别有一番意境。",
            "best_time": "农历正月初七庙会期间；清晨看日出",
            "ticket": "约人民币30元",
            "image_url": "",
            "wikimedia_file": "WV_Shangqiu_Banner.jpg",
            "image_filename": "ebo_tai.jpg"
        },
        "芒砀山汉梁王陵": {
            "name_en": "Liang State Tombs at Mount Mangdang",
            "description": "芒砀山是豫东平原唯一山地，因刘邦在此斩白蛇起义而名垂青史。山中密布西汉梁国王室陵墓群，梁孝王陵山体开凿深达百余米，号称天下石室第一陵。陵中壁画四神云气图色彩绚烂，被誉为敦煌前之敦煌，是国宝级文物。登顶可远眺豫皖鲁三省交界的辽阔平原。",
            "tips": "王陵内部全年恒温，夏天游览凉爽舒适；建议穿舒适步行鞋，陵内通道较低。",
            "best_time": "春季（3-5月）或秋季（9-11月）",
            "ticket": "约人民币120元（含景区交通）",
            "image_url": "",
            "wikimedia_file": "Liang_State_Tombs,_Mangdang_Mountain_1.jpg",
            "image_filename": "mangdang_mountain.jpg"
        }
    },
    "北京": {
        "故宫（紫禁城）": {
            "name_en": "The Forbidden City (Palace Museum)",
            "description": "故宫是中国明清两朝的皇家宫殿，建于1406年，历时24位皇帝居于此处达505年。它占地72公頃，现存建筑980座，是世界上规模最大、保存最完整的古代木结构建筑群。天干中心轴线纵贯全宫，金璦郁璦层叠起伏，是中国封建皇瑟制度的最高展现。",
            "tips": "建议提前在微信小程序预约门票，现场不售票。建议上午开门时即到避开人流高峰。",
            "best_time": "春秋两季；工作日上午开门时人流较少",
            "ticket": "淡季人民幱60元，旺季人民幱80元",
            "image_url": "",
            "wikimedia_file": "The_Forbidden_City_-_View_from_Coal_Hill.jpg",
            "image_filename": "forbidden_city.jpg"
        },
        "颐和园": {
            "name_en": "Summer Palace (Yiheyuan)",
            "description": "颐和园是中国保存最完整的皇家园林，1998年列入联合国教科文组织世界文化遗产。园内以万寿山和昆明湖为核心，佛香阁岅立山中、七百二十八米长廸延展湖临，游昆明湖、登万寿山，近代历史与自然山水入画一般合谐共存。",
            "tips": "建议乘游船游昆明湖。建议从东宫门走进，沿长廸漫步至石軸石般。",
            "best_time": "春季（三五月桃花盛开）或秋季（10月红叶最美）",
            "ticket": "入园票人民幱30元，聪联票人民幱60元（含内景点）",
            "image_url": "",
            "wikimedia_file": "Kina_Summerpalace_117.jpg",
            "image_filename": "summer_palace.jpg"
        },
        "天坛": {
            "name_en": "Temple of Heaven (Tiantan)",
            "description": "天坛是明清两朝帝王祒天、祈谷的神圣場所，建于1420年，与北京故宫同年建成。其中祈年殿是北京最完美的名片建筑之一，三层蓝色琦琊屋呈圆形，不使一款铉钉纯用梗汰材万榙方杂尉袍。圆丘坛中心天心石上发出的声音层层反射回脸，和山回同样神奇。",
            "tips": "公儸公园早晨有各种民间技艺表演，早起进园欣赏。建议游览顺序：圆丘坛→皇穹宇→祈年殿。",
            "best_time": "春天（天气晴朗）或秋天（蓝天栅叶映衬祈年殿）最美",
            "ticket": "入园票人民幱15元，聪联票人民幱34元（含内部建筑）",
            "image_url": "",
            "wikimedia_file": "TempleofHeaven-HallofPrayer.jpg",
            "image_filename": "temple_of_heaven.jpg"
        }
    }
}


def create_folder_structure(base_dir: Path, city: str, attractions: list) -> dict:
    """创建旅行目的地文件夹结构，返回各路径"""
    city_dir = base_dir / "旅行日记" / city
    images_dir = city_dir / "景点图片"
    diary_dir = city_dir / "旅行日记"

    for d in [city_dir, images_dir, diary_dir]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"  ✓ 已创建文件夹：{d}")

    for attraction in attractions:
        attr_dir = images_dir / attraction
        attr_dir.mkdir(exist_ok=True)
        print(f"  ✓ 已创建景点文件夹：{attr_dir}")

    return {
        "city_dir": city_dir,
        "images_dir": images_dir,
        "diary_dir": diary_dir
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
                # 优先用缩略图URL，不行则用原图URL
                return info[0].get("thumburl") or info[0].get("url", "")
        return ""
    except Exception as e:
        print(f"  ! API 查询失败：{e}")
        return ""


def download_image(url: str, save_path: Path, filename_hint: str = "") -> bool:
    """下载图片到指定路径，支持自动通过 Wikimedia API 修正 URL"""
    if save_path.exists():
        print(f"  ✓ 图片已存在，跳过下载：{save_path.name}")
        return True
    # 如果提供了文件名，先尝试通过 API 获取直链
    actual_url = url
    if filename_hint:
        api_url = get_wikimedia_direct_url(filename_hint)
        if api_url:
            actual_url = api_url
            print(f"  → API 直链：{actual_url[:80]}...")
    try:
        headers = {
            "User-Agent": "TravelDiaryBot/1.0 (educational project)"
        }
        resp = requests.get(actual_url, headers=headers, timeout=30, stream=True)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        # 验证图片有效性
        img = Image.open(save_path)
        img.verify()
        print(f"  ✓ 下载成功：{save_path.name} ({save_path.stat().st_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"  ✗ 下载失败（{actual_url[:60]}...）：{e}")
        if save_path.exists():
            save_path.unlink()
        return False


def resize_image_for_pdf(image_path: Path, max_width: int = 700, max_height: int = 400) -> Path:
    """将图片调整尺寸以适合PDF页面，返回处理后的临时路径"""
    try:
        img = Image.open(image_path)
        img = img.convert("RGB")  # 确保RGB模式（PDF不支持RGBA）
        w, h = img.size
        ratio = min(max_width / w, max_height / h)
        if ratio < 1:
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.LANCZOS)
        out_path = image_path.parent / f"_resized_{image_path.name}"
        img.save(out_path, "JPEG", quality=85)
        return out_path
    except Exception as e:
        print(f"  ✗ 图片处理失败：{e}")
        return image_path


class TravelDiaryPDF(FPDF):
    """自定义PDF类，支持中文"""

    def __init__(self, city: str):
        super().__init__()
        self.city = city
        # 添加中文字体（使用内置的 Helvetica 处理英文，中文需要特殊字体）
        self._setup_fonts()

    def _setup_fonts(self):
        """尝试加载系统中文字体（正体 + 粗体变体）"""
        font_candidates = [
            (
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/msyhbd.ttc",
                "MicrosoftYaHei"
            ),
            (
                "C:/Windows/Fonts/simhei.ttf",
                "C:/Windows/Fonts/simhei.ttf",
                "SimHei"
            ),
            (
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/simsun.ttc",
                "SimSun"
            ),
        ]
        self.cn_font = None
        self.cn_font_bold = None
        for regular_path, bold_path, font_name in font_candidates:
            if os.path.exists(regular_path):
                try:
                    self.add_font(font_name, fname=regular_path)
                    self.cn_font = font_name
                    if os.path.exists(bold_path) and bold_path != regular_path:
                        bold_name = font_name + "Bold"
                        self.add_font(bold_name, fname=bold_path)
                        self.cn_font_bold = bold_name
                    else:
                        self.cn_font_bold = font_name  # 没有专门粗体则用同一字体
                    print(f"  ✓ 已加载中文字体：{font_name}")
                    break
                except Exception as e:
                    print(f"  ! 字体加载失败 {font_name}：{e}")
                    self.cn_font = None
                    continue
        if not self.cn_font:
            print("  ! 未找到中文字体，PDF中文字符可能无法正常显示")
            self.cn_font = "Helvetica"
            self.cn_font_bold = "Helvetica"

    def set_cn_font(self, size: int = 12, style: str = ""):
        """设置中文字体，粗体使用独立字体文件"""
        if "B" in style.upper() and self.cn_font_bold:
            self.set_font(self.cn_font_bold, size=size)
        else:
            self.set_font(self.cn_font, size=size)

    def header(self):
        if self.page_no() > 1:
            self.set_cn_font(9)
            self.set_text_color(150, 150, 150)
            self.cell(0, 8, f"{self.city} · 旅行日记", align="C")
            self.ln(4)
            self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_cn_font(9)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"第 {self.page_no()} 页  ·  由「我爱旅行」生成", align="C")
        self.set_text_color(0, 0, 0)


def generate_pdf(city: str, attractions_data: list, output_path: Path, date_str: str):
    """生成旅行日记 PDF"""
    pdf = TravelDiaryPDF(city)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)
    pdf.add_page()

    # ── 封面 ──
    pdf.set_cn_font(32, "B")
    pdf.set_text_color(30, 80, 160)
    pdf.ln(20)
    pdf.cell(0, 20, f"✈  {city}", align="C", ln=True)

    pdf.set_cn_font(18)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 12, "旅 行 日 记", align="C", ln=True)

    pdf.set_cn_font(11)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 8, date_str, align="C", ln=True)
    pdf.ln(5)

    # 封面装饰线
    pdf.set_draw_color(30, 80, 160)
    pdf.set_line_width(0.5)
    pdf.line(30, pdf.get_y(), 180, pdf.get_y())
    pdf.ln(10)

    # ── 序言 ──
    pdf.add_page()
    pdf.set_cn_font(16, "B")
    pdf.set_text_color(30, 80, 160)
    pdf.cell(0, 12, f"序言 · 初遇{city}", ln=True)
    pdf.set_draw_color(30, 80, 160)
    pdf.set_line_width(0.3)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    pdf.set_cn_font(12)
    pdf.set_text_color(50, 50, 50)
    preface = (
        f"有些城市，未曾踏足便已魂牵梦萦。{city}，这座被无数旅人歌颂的城市，"
        f"终于在这个春天，以一种特别的方式向我敞开了她的大门。"
        f"这里有百年外滩的历史沧桑，有浦东新区的现代奇迹，也有"
        f"深藏老弄堂里的市井温情。每一处景致都像是一页未读完的故事，"
        f"值得我们用脚步去丈量，用心去感受。"
    )
    pdf.multi_cell(0, 7, preface)
    pdf.ln(4)
    second_para = (
        f"今天的旅程，让我得以穿越{city}的时空，"
        f"从古典园林的亭台楼阁，到现代都市的摩天玻璃，"
        f"感受这座城市独特的气质——既有东方的含蓄内敛，也有西洋的开阔包容。"
        f"这或许正是{city}令人着迷的原因：她从不试图让你选择，"
        f"而是将所有的美好，一并呈现在你眼前。"
    )
    pdf.multi_cell(0, 7, second_para)
    pdf.ln(8)

    # ── 各景点游记 ──
    for idx, attraction in enumerate(attractions_data, 1):
        pdf.add_page()

        # 景点标题
        pdf.set_cn_font(16, "B")
        pdf.set_text_color(30, 80, 160)
        pdf.cell(0, 12, f"📍 第{idx}站 · {attraction['name']}", ln=True)
        pdf.set_cn_font(10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, attraction.get("name_en", ""), ln=True)
        pdf.set_draw_color(30, 80, 160)
        pdf.set_line_width(0.3)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)

        # 景点图片
        img_path = attraction.get("image_path")
        if img_path and Path(img_path).exists():
            try:
                resized = resize_image_for_pdf(Path(img_path))
                img = Image.open(resized)
                w_px, h_px = img.size
                # 按比例计算 PDF 中的尺寸（mm），最大宽170mm
                max_w_mm = 170
                ratio = max_w_mm / w_px
                w_mm = max_w_mm
                h_mm = h_px * ratio * 0.264583  # pixels to mm (96dpi)
                h_mm = min(h_mm, 100)  # 最高100mm
                pdf.image(str(resized), x=20, y=pdf.get_y(), w=w_mm, h=h_mm)
                pdf.ln(h_mm + 5)
                # 清理临时文件
                if "_resized_" in str(resized):
                    try:
                        resized.unlink()
                    except Exception:
                        pass
            except Exception as e:
                print(f"  ! 插入图片失败：{e}")
                pdf.set_cn_font(10)
                pdf.set_text_color(150, 100, 100)
                pdf.cell(0, 8, f"[图片加载失败：{attraction['name']}]", ln=True)
                pdf.ln(3)
        else:
            pdf.set_cn_font(10)
            pdf.set_text_color(150, 100, 100)
            pdf.cell(0, 8, f"[图片未能下载，可在网上搜索：{attraction.get('name_en', attraction['name'])}]", ln=True)
            pdf.ln(3)

        # 景点简介
        pdf.set_cn_font(12)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 7, attraction.get("description", ""))
        pdf.ln(4)

        # 游记
        diary_text = (
            f"站在{attraction['name']}的那一刻，"
            f"时间仿佛在这里放慢了脚步。{attraction.get('diary_extra', '')}"
            f"这里的每一个细节都让我流连忘返，"
            f"那些光与影的变幻，那些远道而来的游人，"
            f"还有空气中弥漫着的历史气息，"
            f"都让这次游览成为一段难以忘怀的记忆。"
        )
        pdf.set_cn_font(11)
        pdf.set_text_color(70, 70, 70)
        pdf.multi_cell(0, 7, diary_text)
        pdf.ln(4)

        # 旅行贴士
        pdf.set_fill_color(240, 245, 255)
        pdf.set_draw_color(180, 200, 240)
        pdf.set_cn_font(10, "B")
        pdf.set_text_color(30, 80, 160)
        x, y = pdf.get_x(), pdf.get_y()
        tips_text = (
            f"💡 旅行贴士  |  "
            f"最佳时间：{attraction.get('best_time', '全天')}  |  "
            f"门票：{attraction.get('ticket', '免费')}  |  "
            f"{attraction.get('tips', '')}"
        )
        pdf.multi_cell(0, 7, tips_text, border=1, fill=True)
        pdf.ln(6)

    # ── 尾记 ──
    pdf.add_page()
    pdf.set_cn_font(16, "B")
    pdf.set_text_color(30, 80, 160)
    pdf.cell(0, 12, f"尾记 · 再见{city}", ln=True)
    pdf.set_draw_color(30, 80, 160)
    pdf.set_line_width(0.3)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(6)

    pdf.set_cn_font(12)
    pdf.set_text_color(50, 50, 50)
    ending = (
        f"总有一天，我要真正收拾行囊，踏上前往{city}的旅途。"
        f"但在那之前，今天这场虚拟的漫游，"
        f"已经在心里种下了一颗向往的种子。"
        f"旅行的意义或许就在于此——"
        f"它让你在日常的喧嚣中，保留一片属于远方的想象空间。"
    )
    pdf.multi_cell(0, 7, ending)
    pdf.ln(6)
    second_ending = (
        f"感谢{city}，感谢这次虚拟的相遇。"
        f"每一座城市都有她独特的灵魂，"
        f"而{city}的灵魂，是那种古今交织、中西融合的独特魅力。"
        f"带着这份感动，期待与你的真实相逢。"
    )
    pdf.multi_cell(0, 7, second_ending)
    pdf.ln(10)

    # ── 景点贴士汇总表 ──
    pdf.set_cn_font(14, "B")
    pdf.set_text_color(30, 80, 160)
    pdf.cell(0, 10, "📌 旅行小贴士汇总", ln=True)
    pdf.set_draw_color(30, 80, 160)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(4)

    # 表头
    col_widths = [55, 45, 65]
    headers = ["景点", "最佳时间", "注意事项"]
    pdf.set_fill_color(30, 80, 160)
    pdf.set_text_color(255, 255, 255)
    pdf.set_cn_font(10, "B")
    for i, (h, w) in enumerate(zip(headers, col_widths)):
        pdf.cell(w, 8, h, border=1, fill=True)
    pdf.ln()

    # 表内容
    pdf.set_text_color(50, 50, 50)
    pdf.set_cn_font(9)
    for i, attraction in enumerate(attractions_data):
        fill = (i % 2 == 0)
        pdf.set_fill_color(245, 248, 255) if fill else pdf.set_fill_color(255, 255, 255)
        pdf.cell(col_widths[0], 8, attraction["name"], border=1, fill=fill)
        pdf.cell(col_widths[1], 8, attraction.get("best_time", "全天"), border=1, fill=fill)
        tips = attraction.get("tips", "")[:35] + ("..." if len(attraction.get("tips", "")) > 35 else "")
        pdf.cell(col_widths[2], 8, tips, border=1, fill=fill)
        pdf.ln()

    pdf.ln(8)
    pdf.set_cn_font(9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 6, f"✍ 由「我爱旅行」技能自动生成  ·  {date_str}", align="C", ln=True)

    # 保存 PDF
    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    print(f"\n  ✅ PDF 旅行日记已生成：{output_path}")


def main():
    parser = argparse.ArgumentParser(description="旅行日记生成器")
    parser.add_argument("--city", default="上海", help="城市名称")
    parser.add_argument("--output-dir", default=".", help="输出基础目录")
    args = parser.parse_args()

    city = args.city
    base_dir = Path(args.output_dir)
    date_str = datetime.now().strftime("%Y年%m月%d日")

    print(f"\n🌏 开始生成「{city}」旅行日记...\n")

    # 获取该城市的景点数据
    city_data = ATTRACTION_DATA.get(city, {})
    if not city_data:
        print(f"  ✗ 未找到城市 {city} 的数据，请检查 ATTRACTION_DATA")
        sys.exit(1)

    attraction_names = list(city_data.keys())

    # 1. 创建文件夹结构
    print("📁 创建文件夹结构...")
    paths = create_folder_structure(base_dir, city, attraction_names)

    # 2. 下载景点图片
    print("\n🖼️  下载景点图片...")
    attractions_list = []
    for name, data in city_data.items():
        img_dir = paths["images_dir"] / name
        img_dir.mkdir(exist_ok=True)
        img_path = img_dir / data["image_filename"]
        success = download_image(
            data.get("image_url", ""),
            img_path,
            filename_hint=data.get("wikimedia_file", "")
        )
        attractions_list.append({
            "name": name,
            "name_en": data["name_en"],
            "description": data["description"],
            "tips": data["tips"],
            "best_time": data["best_time"],
            "ticket": data["ticket"],
            "image_path": str(img_path) if success else None,
            "diary_extra": ""
        })

    # 3. 生成 PDF
    print("\n📄 生成 PDF 旅行日记...")
    pdf_filename = f"{city}_旅行日记_{datetime.now().strftime('%Y%m%d')}.pdf"
    pdf_output = paths["diary_dir"] / pdf_filename
    generate_pdf(city, attractions_list, pdf_output, date_str)

    # 4. 保存景点元数据 JSON
    meta_path = paths["city_dir"] / "attractions_meta.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump({
            "city": city,
            "date": date_str,
            "attractions": [
                {k: v for k, v in a.items() if k != "image_path"}
                for a in attractions_list
            ]
        }, f, ensure_ascii=False, indent=2)
    print(f"  ✓ 元数据已保存：{meta_path}")

    print(f"\n✅ 完成！请查看：{paths['city_dir']}")
    print(f"   PDF 日记：{pdf_output}")


if __name__ == "__main__":
    main()
