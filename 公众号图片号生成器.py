#!/usr/bin/env python3
"""
公众号图片号生成器 V3 - 国风大改版
品牌：沉萦 / 青澜传媒
设计风格：新中式国风 - 渐变+水墨+圆形装饰+竖排标题
"""

import re
import os
import math
import random
import requests
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

# ============ 配置 ============
APPID = "wx1b34b874a2ccbf1d"
APPSECRET = "c24b898d7fe9cf727c0796decc72c6d0"

OUTPUT_DIR = Path("/mnt/d/Claude Code Data/公众号图片")
OUTPUT_DIR.mkdir(exist_ok=True)

FONT_BOLD = "/mnt/c/Windows/Fonts/msyhbd.ttc"
FONT_REGULAR = "/mnt/c/Windows/Fonts/msyh.ttc"
FONT_KAITI = "/mnt/c/Windows/Fonts/simkai.ttf"
FONT_LIGHT = "/mnt/c/Windows/Fonts/msyhl.ttc"
FONT_SIMHEI = "/mnt/c/Windows/Fonts/simhei.ttf"
FONT_FANGSONG = "/mnt/c/Windows/Fonts/simfang.ttf"

IMG_WIDTH = 1080
IMG_HEIGHT = 1440


# ============ 渐变和纹理工具 ============
def create_gradient(width, height, color_top, color_bottom):
    """创建竖向渐变背景"""
    img = Image.new("RGBA", (width, height))
    for y in range(height):
        ratio = y / height
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * ratio)
        for x in range(width):
            img.putpixel((x, y), (r, g, b, 255))
    return img


def create_radial_gradient(width, height, cx, cy, radius, color_center, color_edge):
    """创建径向渐变"""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
            ratio = min(1.0, dist / radius)
            r = int(color_center[0] + (color_edge[0] - color_center[0]) * ratio)
            g = int(color_center[1] + (color_edge[1] - color_center[1]) * ratio)
            b = int(color_center[2] + (color_edge[2] - color_center[2]) * ratio)
            a = int(color_center[3] + (color_edge[3] - color_center[3]) * ratio)
            overlay.putpixel((x, y), (r, g, b, a))
    return overlay


def add_noise_texture(img, intensity=8):
    """添加纸质噪点纹理"""
    random.seed(77)
    pixels = img.load()
    w, h = img.size
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            noise = random.randint(-intensity, intensity)
            r, g, b, a = pixels[x, y]
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise)), a)
    return img


def draw_ink_wash(img, cx, cy, radius, color, opacity=40):
    """绘制水墨晕染效果（大面积模糊圆）"""
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    for i in range(8):
        r = radius - i * (radius // 10)
        a = max(5, opacity - i * (opacity // 10))
        ox = random.randint(-20, 20)
        oy = random.randint(-20, 20)
        draw.ellipse([(cx - r + ox, cy - r + oy), (cx + r + ox, cy + r + oy)],
                     fill=color[:3] + (a,))
    overlay = overlay.filter(ImageFilter.GaussianBlur(radius=30))
    img = Image.alpha_composite(img, overlay)
    return img


def draw_circle_frame(draw, cx, cy, radius, color, width=2):
    """绘制圆形装饰边框"""
    draw.ellipse([(cx - radius, cy - radius), (cx + radius, cy + radius)],
                 outline=color, width=width)


def draw_double_circle(draw, cx, cy, r1, r2, color):
    """绘制双圆装饰"""
    draw.ellipse([(cx - r1, cy - r1), (cx + r1, cy + r1)],
                 outline=color, width=2)
    draw.ellipse([(cx - r2, cy - r2), (cx + r2, cy + r2)],
                 outline=color, width=1)


def draw_arch_decoration(draw, cx, cy, radius, color, segments=12):
    """绘制拱形花纹装饰"""
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        x1 = cx + int((radius - 10) * math.cos(angle))
        y1 = cy + int((radius - 10) * math.sin(angle))
        x2 = cx + int((radius + 10) * math.cos(angle))
        y2 = cy + int((radius + 10) * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)


def draw_corner_ornament(draw, x, y, size, direction, color):
    """绘制角落装饰纹样（方向：1=左上,2=右上,3=左下,4=右下）"""
    dx = 1 if direction in [1, 3] else -1
    dy = 1 if direction in [1, 2] else -1
    # L形主线
    draw.line([(x, y), (x + size * dx, y)], fill=color, width=3)
    draw.line([(x, y), (x, y + size * dy)], fill=color, width=3)
    # 内L
    s2 = size // 3
    draw.line([(x + s2 * dx, y + s2 * dy), (x + size * dx, y + s2 * dy)],
              fill=color, width=1)
    draw.line([(x + s2 * dx, y + s2 * dy), (x + s2 * dx, y + size * dy)],
              fill=color, width=1)
    # 小点装饰
    draw.ellipse([(x + s2 * dx - 3, y + s2 * dy - 3),
                  (x + s2 * dx + 3, y + s2 * dy + 3)], fill=color)


def draw_vertical_text(draw, x, y, text, font, fill, spacing=10):
    """绘制竖排文字"""
    for i, char in enumerate(text):
        draw.text((x, y + i * (font.size + spacing)), char,
                  font=font, fill=fill, anchor="mm")


def draw_horizontal_line_with_diamond(draw, y, x1, x2, color):
    """绘制中间带菱形的横线"""
    cx = (x1 + x2) // 2
    draw.line([(x1, y), (cx - 12, y)], fill=color, width=1)
    draw.line([(cx + 12, y), (x2, y)], fill=color, width=1)
    draw.polygon([(cx, y - 6), (cx + 6, y), (cx, y + 6), (cx - 6, y)], fill=color)


def draw_smoke_trail(draw, cx, cy, length, seed=0):
    """绘制水墨烟缕"""
    random.seed(seed)
    for trail in range(5):
        x = cx + random.randint(-40, 40)
        y = cy
        points = [(x, y)]
        for step in range(length):
            y -= random.randint(8, 20)
            x += random.randint(-10, 10)
            points.append((x, y))
        if len(points) > 2:
            for j in range(len(points) - 1):
                alpha = max(0, int(50 * (1 - j / len(points))))
                w = max(1, 4 - j // (length // 4 + 1))
                draw.line([points[j], points[j + 1]],
                         fill=(140, 125, 100, alpha), width=w)


def text_wrap_cjk(text, font, max_width, draw):
    """中文文本自动换行"""
    lines = []
    for paragraph in text.split('\n'):
        if not paragraph.strip():
            lines.append('')
            continue
        current_line = ''
        for char in paragraph:
            test_line = current_line + char
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] > max_width:
                if current_line:
                    lines.append(current_line)
                current_line = char
            else:
                current_line = test_line
        if current_line:
            lines.append(current_line)
    return lines


# ============ 文案解析 ============
def parse_topics(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    topics = []
    pattern = r'### 第(\d+)条 \| 封面关键词：【(.+?)】\s*\n\s*```\s*\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    for num, keyword, text in matches:
        topics.append({"num": int(num), "keyword": keyword, "text": text.strip()})
    return topics


# ============ 封面页 ============
def gen_cover(topic):
    """封面 - 渐变背景+圆形装饰+大字关键词"""
    # 渐变背景：上方淡米 → 下方暖杏
    img = create_gradient(IMG_WIDTH, IMG_HEIGHT,
                          (248, 242, 230),   # 顶部淡米
                          (235, 218, 195))   # 底部暖杏
    add_noise_texture(img, 5)

    # 水墨晕染装饰
    random.seed(topic["num"])
    img = draw_ink_wash(img, 200, 300, 200, (180, 200, 190, 40), 30)
    img = draw_ink_wash(img, 880, 1100, 250, (200, 180, 160, 35), 25)
    img = draw_ink_wash(img, IMG_WIDTH // 2, IMG_HEIGHT // 2, 350,
                        (210, 195, 175, 20), 20)

    draw = ImageDraw.Draw(img, "RGBA")

    # 四角装饰
    corner_color = (165, 120, 75)
    draw_corner_ornament(draw, 50, 50, 50, 1, corner_color)
    draw_corner_ornament(draw, IMG_WIDTH - 50, 50, 50, 2, corner_color)
    draw_corner_ornament(draw, 50, IMG_HEIGHT - 50, 50, 3, corner_color)
    draw_corner_ornament(draw, IMG_WIDTH - 50, IMG_HEIGHT - 50, 50, 4, corner_color)

    # 中央圆形装饰框
    cx, cy = IMG_WIDTH // 2, IMG_HEIGHT // 2 - 40
    draw_double_circle(draw, cx, cy, 280, 290, (165, 120, 75, 100))
    draw_arch_decoration(draw, cx, cy, 270, (165, 120, 75, 60), 24)

    # 顶部品牌
    font_brand = ImageFont.truetype(FONT_KAITI, 36)
    draw.text((cx, 180), "· 沉 萦 · 线 香 ·",
              font=font_brand, fill=(165, 130, 80), anchor="mm")
    draw_horizontal_line_with_diamond(draw, 225, 320, IMG_WIDTH - 320,
                                     (185, 155, 110))

    # 中央大字关键词 - 朱砂红（加大）
    keyword = topic["keyword"]
    if len(keyword) <= 2:
        font_kw = ImageFont.truetype(FONT_SIMHEI, 220)
        draw.text((cx, cy), keyword, font=font_kw,
                  fill=(175, 55, 40), anchor="mm")
    else:
        font_kw = ImageFont.truetype(FONT_SIMHEI, 160)
        draw.text((cx, cy), keyword, font=font_kw,
                  fill=(175, 55, 40), anchor="mm")

    # 关键词下方横线+装饰
    line_y = cy + 130
    draw_horizontal_line_with_diamond(draw, line_y, cx - 180, cx + 180,
                                     (165, 120, 75))

    # 副标题（加大）
    first_line = topic["text"].split('\n')[0].strip()
    if len(first_line) > 16:
        first_line = first_line[:16] + "…"
    font_sub = ImageFont.truetype(FONT_KAITI, 40)
    draw.text((cx, line_y + 55), first_line,
              font=font_sub, fill=(100, 85, 65), anchor="mm")

    # 左侧竖排小字 "Vol.XXX"
    font_vol = ImageFont.truetype(FONT_KAITI, 20)
    vol_text = f"Vol.{topic['num']:03d}"
    draw_vertical_text(draw, 90, 450, vol_text, font_vol, (160, 140, 110), 8)

    # 底部烟缕
    draw_smoke_trail(draw, cx, IMG_HEIGHT - 150, 30, topic["num"])

    # 底部提示
    font_tip = ImageFont.truetype(FONT_KAITI, 26)
    draw.text((cx, IMG_HEIGHT - 120), "← 左滑阅读 →",
              font=font_tip, fill=(170, 150, 125), anchor="mm")

    return img


# ============ 内容页 ============
def gen_content_pages(topic):
    """内容页 - 左侧竖排标题+右侧正文"""
    text = topic["text"]
    lines_all = [l for l in text.split('\n') if l.strip()]
    product_line = lines_all[-1] if lines_all else ""
    content_text = '\n'.join(lines_all[:-1])

    pages = []
    font_content = ImageFont.truetype(FONT_KAITI, 48)

    temp_img = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)
    max_text_width = IMG_WIDTH - 280
    wrapped = text_wrap_cjk(content_text, font_content, max_text_width, temp_draw)

    line_height = 82
    max_lines_per_page = 10

    page_lines = []
    current_page = []
    for line in wrapped:
        if len(current_page) >= max_lines_per_page:
            page_lines.append(current_page)
            current_page = []
        current_page.append(line)
    if current_page:
        page_lines.append(current_page)

    total_pages = len(page_lines) + 3

    for page_idx, lines in enumerate(page_lines):
        # 渐变背景：淡象牙 → 淡杏
        img = create_gradient(IMG_WIDTH, IMG_HEIGHT,
                              (250, 245, 235),
                              (242, 232, 218))
        add_noise_texture(img, 4)

        # 轻微水墨晕染
        random.seed(topic["num"] * 10 + page_idx)
        img = draw_ink_wash(img, 150, 200, 150, (190, 210, 200, 25), 20)
        img = draw_ink_wash(img, 900, 1200, 180, (200, 185, 170, 20), 15)

        draw = ImageDraw.Draw(img, "RGBA")

        # 四角装饰
        cc = (190, 160, 125)
        draw_corner_ornament(draw, 45, 45, 40, 1, cc)
        draw_corner_ornament(draw, IMG_WIDTH - 45, 45, 40, 2, cc)
        draw_corner_ornament(draw, 45, IMG_HEIGHT - 45, 40, 3, cc)
        draw_corner_ornament(draw, IMG_WIDTH - 45, IMG_HEIGHT - 45, 40, 4, cc)

        # 顶部标识 - 关键词+线
        font_kw_small = ImageFont.truetype(FONT_SIMHEI, 34)
        draw.text((IMG_WIDTH // 2, 80), f"· {topic['keyword']} ·",
                  font=font_kw_small, fill=(175, 55, 40), anchor="mm")
        draw_horizontal_line_with_diamond(draw, 110, 200, IMG_WIDTH - 200,
                                         (200, 175, 145))

        # 左侧装饰竖线 - 天青色渐变
        for y in range(160, IMG_HEIGHT - 200):
            ratio = (y - 160) / (IMG_HEIGHT - 360)
            alpha = int(80 * (1 - abs(ratio - 0.5) * 2))
            draw.point((95, y), fill=(100, 155, 155, max(0, alpha)))
            draw.point((96, y), fill=(100, 155, 155, max(0, alpha)))

        # 左侧竖排关键词装饰
        font_side = ImageFont.truetype(FONT_KAITI, 22)
        draw_vertical_text(draw, 60, 250, topic["keyword"],
                          font_side, (175, 55, 40, 80), 15)

        # 正文区域
        y_start = 170
        for i, line in enumerate(lines):
            if line == '':
                y_start += line_height // 2
                continue
            y_pos = y_start + i * line_height
            draw.text((140, y_pos), line,
                      font=font_content, fill=(55, 45, 35))

        # 底部装饰
        draw_horizontal_line_with_diamond(draw, IMG_HEIGHT - 170,
                                         150, IMG_WIDTH - 150,
                                         (200, 175, 145))

        # 页码
        font_num = ImageFont.truetype(FONT_KAITI, 22)
        draw.text((IMG_WIDTH // 2, IMG_HEIGHT - 120),
                  f"— {page_idx + 2} / {total_pages} —",
                  font=font_num, fill=(170, 150, 125), anchor="mm")

        # 右下角品牌
        font_brand_s = ImageFont.truetype(FONT_KAITI, 18)
        draw.text((IMG_WIDTH - 80, IMG_HEIGHT - 80), "沉萦",
                  font=font_brand_s, fill=(185, 150, 85), anchor="mm")

        pages.append(img)

    return pages, product_line, total_pages


# ============ 产品推荐页 ============
def gen_product_page(topic, product_line, total_pages):
    """产品页 - 圆形装饰+品牌展示"""
    img = create_gradient(IMG_WIDTH, IMG_HEIGHT,
                          (245, 238, 225),
                          (238, 225, 205))
    add_noise_texture(img, 5)

    random.seed(topic["num"] + 100)
    img = draw_ink_wash(img, IMG_WIDTH // 2, 400, 300,
                        (180, 195, 185, 30), 25)
    img = draw_ink_wash(img, IMG_WIDTH // 2, 1000, 280,
                        (195, 175, 155, 25), 20)

    draw = ImageDraw.Draw(img, "RGBA")

    # 四角
    cc = (170, 135, 95)
    draw_corner_ornament(draw, 45, 45, 45, 1, cc)
    draw_corner_ornament(draw, IMG_WIDTH - 45, 45, 45, 2, cc)
    draw_corner_ornament(draw, 45, IMG_HEIGHT - 45, 45, 3, cc)
    draw_corner_ornament(draw, IMG_WIDTH - 45, IMG_HEIGHT - 45, 45, 4, cc)

    # 顶部
    font_tag = ImageFont.truetype(FONT_KAITI, 36)
    draw.text((IMG_WIDTH // 2, 180), "· 今 日 推 荐 ·",
              font=font_tag, fill=(100, 155, 155), anchor="mm")
    draw_horizontal_line_with_diamond(draw, 220, 280, IMG_WIDTH - 280,
                                     (170, 145, 115))

    # 中央大圆装饰框
    cx, cy = IMG_WIDTH // 2, 550
    draw_double_circle(draw, cx, cy, 200, 215, (170, 135, 95, 120))
    draw_arch_decoration(draw, cx, cy, 190, (170, 135, 95, 50), 20)

    # 圆内产品文字
    font_product = ImageFont.truetype(FONT_KAITI, 44)
    # 自动换行产品文字
    temp_draw = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    prod_lines = text_wrap_cjk(product_line, font_product, 320, temp_draw)
    for i, pl in enumerate(prod_lines):
        draw.text((cx, cy - 20 + i * 50), pl,
                  font=font_product, fill=(175, 55, 40), anchor="mm")

    # 烟缕装饰
    draw_smoke_trail(draw, cx, 800, 25, topic["num"] + 50)

    # 品牌展示区
    draw_horizontal_line_with_diamond(draw, 900, 300, IMG_WIDTH - 300,
                                     (185, 150, 85))

    font_brand = ImageFont.truetype(FONT_SIMHEI, 84)
    draw.text((cx, 990), "沉 萦",
              font=font_brand, fill=(185, 150, 85), anchor="mm")

    font_desc = ImageFont.truetype(FONT_KAITI, 28)
    descs = ["天然香料 · 古法制香", "一支香的时间，给自己20分钟"]
    for i, d in enumerate(descs):
        draw.text((cx, 1080 + i * 48), d,
                  font=font_desc, fill=(120, 105, 85), anchor="mm")

    draw_horizontal_line_with_diamond(draw, 1200, 350, IMG_WIDTH - 350,
                                     (185, 150, 85))

    # 页码
    font_num = ImageFont.truetype(FONT_KAITI, 22)
    draw.text((cx, IMG_HEIGHT - 120),
              f"— {total_pages - 1} / {total_pages} —",
              font=font_num, fill=(170, 150, 125), anchor="mm")

    return img


# ============ 尾页 ============
def gen_tail_page(topic, total_pages):
    """尾页 - 关注引导"""
    img = create_gradient(IMG_WIDTH, IMG_HEIGHT,
                          (242, 235, 220),
                          (230, 215, 195))
    add_noise_texture(img, 5)

    random.seed(topic["num"] + 200)
    img = draw_ink_wash(img, IMG_WIDTH // 2, IMG_HEIGHT // 2, 400,
                        (200, 190, 175, 20), 18)
    img = draw_ink_wash(img, 250, 350, 200, (185, 200, 195, 25), 20)
    img = draw_ink_wash(img, 830, 1050, 220, (200, 180, 165, 22), 18)

    draw = ImageDraw.Draw(img, "RGBA")

    # 四角 - 朱砂色
    cc = (175, 55, 40)
    draw_corner_ornament(draw, 50, 50, 50, 1, cc)
    draw_corner_ornament(draw, IMG_WIDTH - 50, 50, 50, 2, cc)
    draw_corner_ornament(draw, 50, IMG_HEIGHT - 50, 50, 3, cc)
    draw_corner_ornament(draw, IMG_WIDTH - 50, IMG_HEIGHT - 50, 50, 4, cc)

    cx, cy = IMG_WIDTH // 2, IMG_HEIGHT // 2 - 50

    # 大圆装饰
    draw_double_circle(draw, cx, cy, 300, 315, (175, 55, 40, 80))
    draw_arch_decoration(draw, cx, cy, 285, (175, 55, 40, 40), 28)

    # 品牌大字
    font_brand = ImageFont.truetype(FONT_SIMHEI, 100)
    draw.text((cx, cy - 80), "沉 萦",
              font=font_brand, fill=(185, 150, 85), anchor="mm")

    # slogan
    font_slogan = ImageFont.truetype(FONT_KAITI, 32)
    draw.text((cx, cy + 20), "点一支香",
              font=font_slogan, fill=(100, 85, 65), anchor="mm")
    draw.text((cx, cy + 65), "给自己一段安静的时光",
              font=font_slogan, fill=(100, 85, 65), anchor="mm")

    # 分割
    draw_horizontal_line_with_diamond(draw, cy + 120, cx - 150, cx + 150, cc)

    # 关注引导
    font_follow = ImageFont.truetype(FONT_KAITI, 32)
    draw.text((cx, cy + 180), "关注公众号「青澜传媒」",
              font=font_follow, fill=(55, 45, 35), anchor="mm")
    draw.text((cx, cy + 225), "每晚一支香，伴你入眠",
              font=font_follow, fill=(55, 45, 35), anchor="mm")

    # 底部烟缕
    draw_smoke_trail(draw, cx, IMG_HEIGHT - 130, 25, topic["num"] + 300)

    # 互动引导
    font_tip = ImageFont.truetype(FONT_KAITI, 24)
    draw.text((cx, IMG_HEIGHT - 90), "点赞 · 收藏 · 分享",
              font=font_tip, fill=(170, 150, 125), anchor="mm")

    # 页码
    font_num = ImageFont.truetype(FONT_KAITI, 22)
    draw.text((cx, IMG_HEIGHT - 130),
              f"— {total_pages} / {total_pages} —",
              font=font_num, fill=(170, 150, 125), anchor="mm")

    return img


# ============ 生成流程 ============
def generate_carousel(topic):
    topic_dir = OUTPUT_DIR / f"第{topic['num']:03d}条_{topic['keyword']}"
    topic_dir.mkdir(exist_ok=True)
    images = []

    content_pages, product_line, total_pages = gen_content_pages(topic)

    # 封面
    cover = gen_cover(topic)
    p = topic_dir / "01_封面.png"
    cover.convert("RGB").save(str(p), quality=95)
    images.append(p)

    # 内容
    for i, page in enumerate(content_pages):
        p = topic_dir / f"{i + 2:02d}_内容.png"
        page.convert("RGB").save(str(p), quality=95)
        images.append(p)

    # 产品
    prod = gen_product_page(topic, product_line, total_pages)
    idx = len(images) + 1
    p = topic_dir / f"{idx:02d}_产品.png"
    prod.convert("RGB").save(str(p), quality=95)
    images.append(p)

    # 尾页
    tail = gen_tail_page(topic, total_pages)
    idx = len(images) + 1
    p = topic_dir / f"{idx:02d}_尾页.png"
    tail.convert("RGB").save(str(p), quality=95)
    images.append(p)

    print(f"  ✓ 第{topic['num']}条【{topic['keyword']}】共{len(images)}张")
    return images


# ============ 微信API ============
def get_access_token():
    url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
    return requests.get(url).json()["access_token"]

def upload_image(access_token, image_path):
    url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
    with open(image_path, "rb") as f:
        resp = requests.post(url, files={"media": (os.path.basename(image_path), f, "image/png")}).json()
    return resp["media_id"], resp.get("url", "")

def create_draft(access_token, title, html, thumb_id):
    url = f"https://api.weixin.qq.com/cgi-bin/draft/add?access_token={access_token}"
    data = {"articles": [{"title": title, "author": "沉萦", "content": html,
                          "thumb_media_id": thumb_id, "need_open_comment": 1}]}
    return requests.post(url, json=data).json()["media_id"]

def publish_draft(access_token, media_id):
    url = f"https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token={access_token}"
    return requests.post(url, json={"media_id": media_id}).json()

def build_html(urls):
    return "\n".join(f'<p style="text-align:center;"><img src="{u}" style="width:100%;"/></p>' for u in urls)


# ============ 主流程 ============
def run(topic_nums=None, publish=False):
    topics = parse_topics("/mnt/d/Claude Code Data/全部选题逐字稿文案（100条完整版）.md")
    print(f"共{len(topics)}条选题")
    if topic_nums:
        topics = [t for t in topics if t["num"] in topic_nums]
    print(f"生成{len(topics)}条")

    results = []
    for topic in topics:
        imgs = generate_carousel(topic)
        results.append({"topic": topic, "images": imgs})

    print(f"\n完毕！保存在: {OUTPUT_DIR}")

    if publish:
        token = get_access_token()
        for r in results:
            t, imgs = r["topic"], r["images"]
            print(f"\n上传【{t['keyword']}】...")
            urls, thumb = [], None
            for i, ip in enumerate(imgs):
                mid, u = upload_image(token, ip)
                urls.append(u)
                if i == 0: thumb = mid
                time.sleep(0.5)
            html = build_html(urls)
            title = f"【{t['keyword']}】{t['text'].split(chr(10))[0][:20]}"
            did = create_draft(token, title, html, thumb)
            print(f"  草稿: {did}")
            resp = publish_draft(token, did)
            print(f"  发布: {resp}")
            time.sleep(1)

    return results


if __name__ == "__main__":
    run(topic_nums=[1, 2, 3], publish=False)
