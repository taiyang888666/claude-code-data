#!/usr/bin/env python3
"""
公众号图片号生成器 V4 - 小红书明亮风
品牌：沉萦 / 青澜传媒
设计风格：莫兰迪纯色底 + 大字主视觉 + 关键句高亮色块 + 干净留白
"""

import re
import os
import math
import random
import requests
import time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ============ 配置 ============
APPID = "wx1b34b874a2ccbf1d"
APPSECRET = "c24b898d7fe9cf727c0796decc72c6d0"

OUTPUT_DIR = Path("/mnt/d/Claude Code Data/公众号图片")
OUTPUT_DIR.mkdir(exist_ok=True)

FONT_BOLD = "/mnt/c/Windows/Fonts/msyhbd.ttc"
FONT_REGULAR = "/mnt/c/Windows/Fonts/msyh.ttc"
FONT_LIGHT = "/mnt/c/Windows/Fonts/msyhl.ttc"
FONT_SIMHEI = "/mnt/c/Windows/Fonts/simhei.ttf"
FONT_KAITI = "/mnt/c/Windows/Fonts/simkai.ttf"

IMG_WIDTH = 1080
IMG_HEIGHT = 1440

# ============ 配色系统（6套莫兰迪色轮换） ============
COLOR_THEMES = [
    {
        "name": "奶油暖棕",
        "bg": (255, 248, 240),
        "accent": (198, 120, 62),
        "highlight_bg": (255, 237, 217),
        "text_dark": (45, 40, 35),
        "text_mid": (120, 100, 80),
        "text_light": (180, 165, 145),
        "tag_bg": (198, 120, 62),
        "tag_text": (255, 255, 255),
    },
    {
        "name": "静谧灰蓝",
        "bg": (235, 240, 248),
        "accent": (55, 90, 145),
        "highlight_bg": (210, 225, 248),
        "text_dark": (35, 40, 55),
        "text_mid": (80, 95, 130),
        "text_light": (145, 160, 190),
        "tag_bg": (55, 90, 145),
        "tag_text": (255, 255, 255),
    },
    {
        "name": "薄荷清新",
        "bg": (238, 248, 240),
        "accent": (50, 135, 80),
        "highlight_bg": (212, 240, 220),
        "text_dark": (35, 50, 40),
        "text_mid": (75, 115, 85),
        "text_light": (145, 185, 155),
        "tag_bg": (50, 135, 80),
        "tag_text": (255, 255, 255),
    },
    {
        "name": "暖粉治愈",
        "bg": (255, 242, 242),
        "accent": (210, 72, 55),
        "highlight_bg": (255, 218, 215),
        "text_dark": (55, 35, 35),
        "text_mid": (150, 85, 80),
        "text_light": (200, 155, 150),
        "tag_bg": (210, 72, 55),
        "tag_text": (255, 255, 255),
    },
    {
        "name": "鹅黄温暖",
        "bg": (255, 250, 235),
        "accent": (210, 150, 20),
        "highlight_bg": (255, 240, 200),
        "text_dark": (50, 45, 30),
        "text_mid": (140, 120, 60),
        "text_light": (190, 175, 130),
        "tag_bg": (210, 150, 20),
        "tag_text": (255, 255, 255),
    },
    {
        "name": "淡紫舒缓",
        "bg": (245, 238, 250),
        "accent": (120, 60, 160),
        "highlight_bg": (230, 215, 245),
        "text_dark": (50, 35, 60),
        "text_mid": (110, 80, 140),
        "text_light": (175, 155, 195),
        "tag_bg": (120, 60, 160),
        "tag_text": (255, 255, 255),
    },
]


def get_theme(topic_num):
    """根据条目号轮换配色"""
    return COLOR_THEMES[(topic_num - 1) % len(COLOR_THEMES)]


# ============ 绘图工具 ============
def create_solid_bg(width, height, color):
    """创建纯色背景"""
    return Image.new("RGBA", (width, height), color + (255,))


def draw_rounded_rect(draw, xy, fill, radius=20):
    """绘制圆角矩形"""
    x0, y0, x1, y1 = xy
    # 四个角的圆
    draw.ellipse([x0, y0, x0 + 2 * radius, y0 + 2 * radius], fill=fill)
    draw.ellipse([x1 - 2 * radius, y0, x1, y0 + 2 * radius], fill=fill)
    draw.ellipse([x0, y1 - 2 * radius, x0 + 2 * radius, y1], fill=fill)
    draw.ellipse([x1 - 2 * radius, y1 - 2 * radius, x1, y1], fill=fill)
    # 填充矩形
    draw.rectangle([x0 + radius, y0, x1 - radius, y1], fill=fill)
    draw.rectangle([x0, y0 + radius, x1, y1 - radius], fill=fill)


def draw_dot_decoration(draw, x, y, color, count=3, spacing=18, size=6):
    """绘制小圆点装饰"""
    for i in range(count):
        cx = x + i * spacing
        draw.ellipse([(cx - size, y - size), (cx + size, y + size)], fill=color)


def draw_line_decoration(draw, y, x1, x2, color, width=2):
    """绘制简洁横线"""
    draw.line([(x1, y), (x2, y)], fill=color, width=width)


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


def is_highlight_line(line):
    """判断是否需要高亮的行（包含【】标记的）"""
    return '【' in line and '】' in line


def strip_highlight_marks(line):
    """去掉高亮标记符号"""
    return line.replace('【', '').replace('】', '')


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
    """封面 - 大字关键词 + 彩色标签 + 钩子文案"""
    theme = get_theme(topic["num"])
    img = create_solid_bg(IMG_WIDTH, IMG_HEIGHT, theme["bg"])
    draw = ImageDraw.Draw(img, "RGBA")

    # 顶部品牌标签（小圆角色块）
    font_brand = ImageFont.truetype(FONT_BOLD, 28)
    brand_text = "沉萦 · 线香日记"
    bbox = draw.textbbox((0, 0), brand_text, font=font_brand)
    tw = bbox[2] - bbox[0]
    tag_x = (IMG_WIDTH - tw) // 2 - 24
    draw_rounded_rect(draw, (tag_x, 160, tag_x + tw + 48, 210),
                      fill=theme["tag_bg"], radius=25)
    draw.text((IMG_WIDTH // 2, 185), brand_text,
              font=font_brand, fill=theme["tag_text"], anchor="mm")

    # 装饰小圆点
    draw_dot_decoration(draw, IMG_WIDTH // 2 - 27, 270, theme["accent"] + (80,),
                        count=3, spacing=27, size=5)

    # 中央超大关键词
    keyword = topic["keyword"]
    if len(keyword) <= 2:
        font_kw = ImageFont.truetype(FONT_SIMHEI, 260)
    elif len(keyword) <= 4:
        font_kw = ImageFont.truetype(FONT_SIMHEI, 180)
    else:
        font_kw = ImageFont.truetype(FONT_SIMHEI, 140)

    draw.text((IMG_WIDTH // 2, IMG_HEIGHT // 2 - 80), keyword,
              font=font_kw, fill=theme["text_dark"], anchor="mm")

    # 关键词下方 - 第一句话作为hook
    first_line = topic["text"].split('\n')[0].strip()
    if len(first_line) > 20:
        first_line = first_line[:20] + "…"
    font_hook = ImageFont.truetype(FONT_REGULAR, 38)
    draw.text((IMG_WIDTH // 2, IMG_HEIGHT // 2 + 120), first_line,
              font=font_hook, fill=theme["text_mid"], anchor="mm")

    # 分割线
    draw_line_decoration(draw, IMG_HEIGHT // 2 + 190,
                         IMG_WIDTH // 2 - 150, IMG_WIDTH // 2 + 150,
                         theme["text_light"], 2)

    # 底部引导
    font_tip = ImageFont.truetype(FONT_REGULAR, 28)
    draw.text((IMG_WIDTH // 2, IMG_HEIGHT - 200), "左滑继续阅读",
              font=font_tip, fill=theme["text_light"], anchor="mm")

    # 底部向左箭头装饰
    arrow_y = IMG_HEIGHT - 155
    draw.text((IMG_WIDTH // 2, arrow_y), ">>>",
              font=ImageFont.truetype(FONT_REGULAR, 32),
              fill=theme["accent"] + (120,), anchor="mm")

    return img


# ============ 内容页 ============
def gen_content_pages(topic):
    """内容页 - 大字排版 + 关键句高亮"""
    theme = get_theme(topic["num"])
    text = topic["text"]
    lines_all = [l for l in text.split('\n') if l.strip()]

    # 最后一行是产品推荐
    product_line = lines_all[-1] if lines_all else ""
    content_lines = lines_all[:-1]

    pages = []
    font_content = ImageFont.truetype(FONT_REGULAR, 46)
    font_highlight = ImageFont.truetype(FONT_BOLD, 46)

    temp_img = Image.new("RGBA", (IMG_WIDTH, IMG_HEIGHT))
    temp_draw = ImageDraw.Draw(temp_img)
    max_text_width = IMG_WIDTH - 200  # 左右各留100

    # 对每行做换行处理
    all_wrapped = []
    for line in content_lines:
        is_hl = is_highlight_line(line)
        clean_line = strip_highlight_marks(line) if is_hl else line
        wrapped = text_wrap_cjk(clean_line, font_content, max_text_width, temp_draw)
        for w in wrapped:
            all_wrapped.append({"text": w, "highlight": is_hl})
        all_wrapped.append({"text": "", "highlight": False})  # 段落间空行

    # 分页
    line_height = 80
    max_lines_per_page = 11
    page_groups = []
    current = []
    for item in all_wrapped:
        if len(current) >= max_lines_per_page:
            page_groups.append(current)
            current = []
        current.append(item)
    if current:
        page_groups.append(current)

    total_pages = len(page_groups) + 3  # 封面 + 内容页 + 产品页 + 尾页

    for page_idx, group in enumerate(page_groups):
        img = create_solid_bg(IMG_WIDTH, IMG_HEIGHT, theme["bg"])
        draw = ImageDraw.Draw(img, "RGBA")

        # 顶部 - 关键词标签
        font_tag = ImageFont.truetype(FONT_BOLD, 24)
        tag_text = f"# {topic['keyword']}"
        bbox = draw.textbbox((0, 0), tag_text, font=font_tag)
        tw = bbox[2] - bbox[0]
        draw_rounded_rect(draw, (80, 65, 80 + tw + 36, 107),
                          fill=theme["accent"] + (30,), radius=21)
        draw.text((98, 86), tag_text,
                  font=font_tag, fill=theme["accent"], anchor="lm")

        # 顶部右侧页码
        font_pn = ImageFont.truetype(FONT_LIGHT, 22)
        draw.text((IMG_WIDTH - 80, 86),
                  f"{page_idx + 2}/{total_pages}",
                  font=font_pn, fill=theme["text_light"], anchor="rm")

        # 顶部分割线
        draw_line_decoration(draw, 125, 80, IMG_WIDTH - 80,
                             theme["text_light"] + (60,), 1)

        # 正文
        y_start = 180
        for i, item in enumerate(group):
            if item["text"] == "":
                y_start += line_height // 3
                continue

            y_pos = y_start + i * line_height

            if item["highlight"]:
                # 高亮行 - 加圆角色块背景
                bbox = draw.textbbox((100, y_pos), item["text"], font=font_highlight)
                tw = bbox[2] - bbox[0]
                th = bbox[3] - bbox[1]
                draw_rounded_rect(draw,
                                  (85, y_pos - 8, 85 + tw + 30, y_pos + th + 12),
                                  fill=theme["highlight_bg"], radius=8)
                draw.text((100, y_pos), item["text"],
                          font=font_highlight, fill=theme["accent"])
            else:
                draw.text((100, y_pos), item["text"],
                          font=font_content, fill=theme["text_dark"])

        # 底部装饰线
        draw_line_decoration(draw, IMG_HEIGHT - 120, 80, IMG_WIDTH - 80,
                             theme["text_light"] + (60,), 1)

        # 底部品牌
        font_br = ImageFont.truetype(FONT_LIGHT, 20)
        draw.text((IMG_WIDTH // 2, IMG_HEIGHT - 80), "沉萦 CHENYING",
                  font=font_br, fill=theme["text_light"], anchor="mm")

        pages.append(img)

    return pages, product_line, total_pages


# ============ 产品推荐页 ============
def gen_product_page(topic, product_line, total_pages):
    """产品页 - 自然融入式推荐"""
    theme = get_theme(topic["num"])
    img = create_solid_bg(IMG_WIDTH, IMG_HEIGHT, theme["bg"])
    draw = ImageDraw.Draw(img, "RGBA")

    cx = IMG_WIDTH // 2

    # 顶部装饰圆点
    draw_dot_decoration(draw, cx - 27, 200, theme["accent"] + (80,),
                        count=3, spacing=27, size=5)

    # 产品推荐文字 - 大号居中
    font_prod = ImageFont.truetype(FONT_BOLD, 52)
    wrapped = text_wrap_cjk(product_line, font_prod, IMG_WIDTH - 200,
                            draw)
    y = 360
    for line in wrapped:
        draw.text((cx, y), line,
                  font=font_prod, fill=theme["text_dark"], anchor="mm")
        y += 72

    # 分割线
    draw_line_decoration(draw, y + 40, cx - 120, cx + 120,
                         theme["text_light"], 2)

    # 品牌展示
    font_brand = ImageFont.truetype(FONT_SIMHEI, 72)
    draw.text((cx, y + 140), "沉 萦",
              font=font_brand, fill=theme["accent"], anchor="mm")

    font_desc = ImageFont.truetype(FONT_REGULAR, 28)
    descs = ["天然香料 · 古法制香", "一支香的时间 给自己20分钟"]
    for i, d in enumerate(descs):
        draw.text((cx, y + 230 + i * 50), d,
                  font=font_desc, fill=theme["text_mid"], anchor="mm")

    # 底部标签
    font_tag = ImageFont.truetype(FONT_BOLD, 24)
    tags = ["#线香", "#居家好物", "#情绪治愈"]
    tag_total_w = 0
    tag_widths = []
    for t in tags:
        bb = draw.textbbox((0, 0), t, font=font_tag)
        w = bb[2] - bb[0] + 32
        tag_widths.append(w)
        tag_total_w += w
    tag_total_w += 16 * (len(tags) - 1)

    tx = (IMG_WIDTH - tag_total_w) // 2
    tag_y = IMG_HEIGHT - 260
    for i, t in enumerate(tags):
        draw_rounded_rect(draw, (tx, tag_y, tx + tag_widths[i], tag_y + 42),
                          fill=theme["accent"] + (25,), radius=21)
        draw.text((tx + tag_widths[i] // 2, tag_y + 21), t,
                  font=font_tag, fill=theme["accent"], anchor="mm")
        tx += tag_widths[i] + 16

    # 页码
    font_pn = ImageFont.truetype(FONT_LIGHT, 22)
    draw.text((cx, IMG_HEIGHT - 80),
              f"{total_pages - 1}/{total_pages}",
              font=font_pn, fill=theme["text_light"], anchor="mm")

    return img


# ============ 尾页 ============
def gen_tail_page(topic, total_pages):
    """尾页 - 干净CTA + 互动引导"""
    theme = get_theme(topic["num"])
    img = create_solid_bg(IMG_WIDTH, IMG_HEIGHT, theme["bg"])
    draw = ImageDraw.Draw(img, "RGBA")

    cx = IMG_WIDTH // 2
    cy = IMG_HEIGHT // 2 - 60

    # 品牌大字
    font_brand = ImageFont.truetype(FONT_SIMHEI, 100)
    draw.text((cx, cy - 100), "沉 萦",
              font=font_brand, fill=theme["text_dark"], anchor="mm")

    # slogan
    font_slogan = ImageFont.truetype(FONT_REGULAR, 34)
    draw.text((cx, cy), "每晚一支香",
              font=font_slogan, fill=theme["text_mid"], anchor="mm")
    draw.text((cx, cy + 50), "给自己一段安静的时光",
              font=font_slogan, fill=theme["text_mid"], anchor="mm")

    # 分割线
    draw_line_decoration(draw, cy + 120, cx - 120, cx + 120,
                         theme["accent"], 2)

    # 关注引导 - 用高亮色块
    font_follow = ImageFont.truetype(FONT_BOLD, 36)
    follow_text = "关注  @青澜传媒"
    bb = draw.textbbox((0, 0), follow_text, font=font_follow)
    fw = bb[2] - bb[0]
    draw_rounded_rect(draw,
                      (cx - fw // 2 - 30, cy + 170, cx + fw // 2 + 30, cy + 228),
                      fill=theme["tag_bg"], radius=29)
    draw.text((cx, cy + 199), follow_text,
              font=font_follow, fill=theme["tag_text"], anchor="mm")

    # 互动引导
    font_action = ImageFont.truetype(FONT_REGULAR, 30)
    actions = [
        "觉得有用就 点赞 收藏",
        "身边有需要的人 转发给TA",
        "有故事想说 评论区等你"
    ]
    for i, a in enumerate(actions):
        draw.text((cx, cy + 310 + i * 55), a,
                  font=font_action, fill=theme["text_mid"], anchor="mm")

    # 底部装饰
    draw_dot_decoration(draw, cx - 27, IMG_HEIGHT - 140,
                        theme["accent"] + (80,), count=3, spacing=27, size=5)

    # 页码
    font_pn = ImageFont.truetype(FONT_LIGHT, 22)
    draw.text((cx, IMG_HEIGHT - 80),
              f"{total_pages}/{total_pages}",
              font=font_pn, fill=theme["text_light"], anchor="mm")

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

    print(f"  ✓ 第{topic['num']}条【{topic['keyword']}】共{len(images)}张 (配色:{get_theme(topic['num'])['name']})")
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
    topics = parse_topics("/mnt/d/Claude Code Data/全部选题逐字稿文案_v2.md")
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
    run(topic_nums=[4], publish=False)
