"""
ADQ朋友圈广告素材生成器
生成4张800x800正方形广告卡片
"""

from PIL import Image, ImageDraw, ImageFont
import os

OUTPUT_DIR = "/mnt/d/Claude Code Data/ADQ广告素材"
os.makedirs(OUTPUT_DIR, exist_ok=True)

W, H = 800, 800

# 尝试加载字体
def get_font(size, bold=False):
    paths = [
        "/mnt/c/Windows/Fonts/msyhbd.ttc" if bold else "/mnt/c/Windows/Fonts/msyh.ttc",
        "/mnt/c/Windows/Fonts/simhei.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc" if bold else "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except:
                continue
    return ImageFont.load_default()

def draw_rounded_rect(draw, xy, radius, fill):
    x0, y0, x1, y1 = xy
    # 确保radius不超过宽高一半
    max_r = min((x1-x0)//2, (y1-y0)//2)
    radius = min(radius, max_r)
    if radius <= 0:
        draw.rectangle([x0, y0, x1, y1], fill=fill)
        return
    draw.rectangle([x0+radius, y0, x1-radius, y1], fill=fill)
    draw.rectangle([x0, y0+radius, x1, y1-radius], fill=fill)
    draw.pieslice([x0, y0, x0+2*radius, y0+2*radius], 180, 270, fill=fill)
    draw.pieslice([x1-2*radius, y0, x1, y0+2*radius], 270, 360, fill=fill)
    draw.pieslice([x0, y1-2*radius, x0+2*radius, y1], 90, 180, fill=fill)
    draw.pieslice([x1-2*radius, y1-2*radius, x1, y1], 0, 90, fill=fill)

def text_width(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0]

def text_height(draw, text, font):
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[3] - bbox[1]

def draw_text_centered_in(draw, text, y, font, fill, x_left=0, x_right=W):
    """在指定的x范围内水平居中绘制文字"""
    tw = text_width(draw, text, font)
    x = x_left + (x_right - x_left - tw) // 2
    draw.text((x, y), text, font=font, fill=fill)

def draw_text_centered(draw, text, y, font, fill):
    """在全宽范围内水平居中"""
    draw_text_centered_in(draw, text, y, font, fill, 0, W)


def create_card_1():
    """焦虑数据型 - 升学率对比"""
    img = Image.new('RGB', (W, H), '#1a1a2e')
    draw = ImageDraw.Draw(img)

    f_tag = get_font(24, bold=True)
    f_big = get_font(48, bold=True)
    f_num = get_font(64, bold=True)
    f_mid = get_font(28, bold=True)
    f_sm = get_font(22)
    f_xs = get_font(18)
    f_vs = get_font(28, bold=True)
    f_cta = get_font(24, bold=True)
    f_bar = get_font(20, bold=True)

    # 顶部警告条
    draw.rectangle([0, 0, W, 60], fill='#e74c3c')
    draw_text_centered(draw, "你的孩子正在面对什么？", 16, f_tag, '#ffffff')

    # 副标题
    draw_text_centered(draw, "内地高考 vs 香港身份", 80, f_mid, '#aaaaaa')

    # === 左边卡片 - 内地 ===
    LX0, LX1 = 40, 380
    y = 140
    draw_rounded_rect(draw, [LX0, y, LX1, y+260], 16, '#2d1f1f')
    # 标题栏
    draw.rectangle([LX0, y, LX1, y+45], fill='#c0392b')
    draw_text_centered_in(draw, "内地高考", y+8, f_mid, '#ffffff', LX0, LX1)
    # 大数字
    draw_text_centered_in(draw, "1000万", y+65, f_num, '#e74c3c', LX0, LX1)
    # 说明
    draw_text_centered_in(draw, "考生竞争", y+145, f_mid, '#999999', LX0, LX1)
    draw_text_centered_in(draw, "仅1-2%上985", y+195, f_sm, '#e74c3c', LX0, LX1)

    # === 右边卡片 - 香港身份 ===
    RX0, RX1 = 420, 760
    draw_rounded_rect(draw, [RX0, y, RX1, y+260], 16, '#1f2d1f')
    draw.rectangle([RX0, y, RX1, y+45], fill='#27ae60')
    draw_text_centered_in(draw, "香港身份", y+8, f_mid, '#ffffff', RX0, RX1)
    draw_text_centered_in(draw, "400分", y+65, f_num, '#2ecc71', RX0, RX1)
    draw_text_centered_in(draw, "直上985/211", y+145, f_mid, '#999999', RX0, RX1)
    draw_text_centered_in(draw, "录取率40%", y+195, f_sm, '#2ecc71', RX0, RX1)

    # 中间VS
    draw_text_centered_in(draw, "VS", y+110, f_vs, '#f39c12', LX1, RX0)

    # 港八大数据条
    y2 = 430
    bar_end = 40 + int(720*0.4)
    draw_rounded_rect(draw, [40, y2, 760, y2+80], 12, '#16213e')
    draw_rounded_rect(draw, [40, y2, bar_end, y2+80], 12, '#27ae60')

    draw.text((60, y2+10), "港籍生录取率", font=f_bar, fill='#ffffff')
    draw.text((60, y2+42), "40%", font=f_mid, fill='#ffffff')
    draw.text((bar_end+30, y2+10), "非港籍生录取率", font=f_bar, fill='#aaaaaa')
    draw.text((bar_end+30, y2+42), "6%", font=f_mid, fill='#e74c3c')

    # 底部文案
    y3 = 540
    draw_text_centered(draw, "同一所港八大，身份不同", y3, f_mid, '#ffffff')
    draw_text_centered(draw, "录取率差 7 倍", y3+42, f_big, '#f1c40f')

    # CTA按钮
    cta_y = 660
    draw_rounded_rect(draw, [180, cta_y, 620, cta_y+55], 28, '#e74c3c')
    draw_text_centered_in(draw, "免费评估孩子升学路径 →", cta_y+13, f_cta, '#ffffff', 180, 620)

    # 底部信息
    draw_text_centered(draw, "不成功全额退 | 宸好未来", 740, f_xs, '#666666')

    img.save(os.path.join(OUTPUT_DIR, "01_数据冲击型.png"), quality=95)
    print("✓ 01_数据冲击型.png")

def create_card_2():
    """老板共鸣型"""
    img = Image.new('RGB', (W, H), '#f8f4e8')
    draw = ImageDraw.Draw(img)

    f_big = get_font(42, bold=True)
    f_mid = get_font(28, bold=True)
    f_body = get_font(24)
    f_sm = get_font(20)
    f_xs = get_font(16)
    f_num = get_font(52, bold=True)
    f_cta = get_font(24, bold=True)
    f_tag = get_font(22, bold=True)

    # 顶部标签
    tag_text = "企业老板专属"
    tag_w = text_width(draw, tag_text, f_tag) + 40
    draw_rounded_rect(draw, [30, 25, 30+tag_w, 65], 20, '#c6783e')
    draw.text((50, 30), tag_text, font=f_tag, fill='#ffffff')

    # 主标题
    y = 85
    draw.text((50, y), "做生意你是专家", font=f_big, fill='#2c2c2c')
    draw.text((50, y+55), "但孩子升学，你使不上力", font=f_big, fill='#2c2c2c')

    # 分割线
    draw.line([50, y+120, 750, y+120], fill='#d4c5a0', width=2)

    # 痛点列表
    y2 = 230
    points = [
        ("中考50%分流进职高，你拼命赚的钱", "可能换不来一个好高中"),
        ("高考1000万人挤独木桥", "你陪不了读，也请不动最好的老师"),
        ("但你可以给孩子一个香港身份——", ""),
    ]
    icons = ["●", "●", "★"]
    colors_icon = ['#e74c3c', '#e74c3c', '#f39c12']
    for i, (line1, line2) in enumerate(points):
        draw.text((50, y2+2), icons[i], font=f_sm, fill=colors_icon[i])
        draw.text((80, y2), line1, font=f_body, fill='#333333')
        if line2:
            draw.text((80, y2+32), line2, font=f_sm, fill='#888888')
        y2 += 72

    # 核心卖点框
    y3 = 460
    draw_rounded_rect(draw, [40, y3, 760, y3+130], 16, '#2c5f2d')

    draw.text((70, y3+18), "400分上985", font=f_num, fill='#f1c40f')
    draw.text((470, y3+20), "学费省80%", font=f_mid, fill='#ffffff')
    draw.text((470, y3+55), "有公司就能申请", font=f_mid, fill='#ffffff')
    draw.text((470, y3+90), "不看学历 不限行业", font=f_sm, fill='#aed581')

    # CTA
    cta_y = 630
    draw_rounded_rect(draw, [180, cta_y, 620, cta_y+55], 28, '#c6783e')
    draw_text_centered_in(draw, "测一测你能不能办 →", cta_y+13, f_cta, '#ffffff', 180, 620)

    # 底部
    draw_rounded_rect(draw, [140, 710, 660, 750], 20, '#f0e6d0')
    draw_text_centered_in(draw, "包办成功 · 不成功全额退款 · 零风险", 718, f_sm, '#8b7355', 140, 660)

    img.save(os.path.join(OUTPUT_DIR, "02_老板共鸣型.png"), quality=95)
    print("✓ 02_老板共鸣型.png")

def create_card_3():
    """紧迫感型 - 年龄倒计时"""
    img = Image.new('RGB', (W, H), '#0d1b2a')
    draw = ImageDraw.Draw(img)

    f_big = get_font(40, bold=True)
    f_mid = get_font(26, bold=True)
    f_sm = get_font(19)
    f_xs = get_font(16)
    f_cta = get_font(24, bold=True)
    f_tag = get_font(22, bold=True)

    # 顶部
    draw.rectangle([0, 0, W, 55], fill='#f39c12')
    draw_text_centered(draw, "香港身份办理 · 年龄窗口期", 14, f_tag, '#1a1a1a')

    # 主标题
    draw_text_centered(draw, "你家孩子今年几岁？", 75, f_big, '#ffffff')

    # === 左侧卡片 - 10岁前 ===
    LX0, LX1 = 40, 380
    y = 145
    draw_rounded_rect(draw, [LX0, y, LX1, y+265], 16, '#1b3a2a')
    draw.rectangle([LX0, y, LX1, y+48], fill='#27ae60')
    draw_text_centered_in(draw, "10岁前办好", y+10, f_mid, '#ffffff', LX0, LX1)

    items_left = [
        "港澳台联考 400分上985",
        "校长推荐 免试清北复交",
        "港八大40%录取率",
        "副学士兜底 100%有本科",
        "内地+香港 双通道"
    ]
    ly = y + 62
    for item in items_left:
        draw.text((60, ly), "✓ " + item, font=f_sm, fill='#a8d5ba')
        ly += 37

    # === 右侧卡片 - 10岁后 ===
    RX0, RX1 = 420, 760
    draw_rounded_rect(draw, [RX0, y, RX1, y+265], 16, '#2a1b1b')
    draw.rectangle([RX0, y, RX1, y+48], fill='#c0392b')
    draw_text_centered_in(draw, "10岁后才办", y+10, f_mid, '#ffffff', RX0, RX1)

    items_right = [
        "联考优势大幅缩减",
        "需走香港DSE或国际课程",
        "适应期更长 竞争更大",
        "路径选择少一半",
        "时间成本翻倍"
    ]
    ry = y + 62
    for item in items_right:
        draw.text((440, ry), "✗ " + item, font=f_sm, fill='#e8a0a0')
        ry += 37

    # 中间箭头
    draw_text_centered_in(draw, "→", y+130, f_big, '#f39c12', LX1, RX0)

    # 核心信息条
    y2 = 440
    draw_rounded_rect(draw, [40, y2, 760, y2+85], 12, '#1b2838')
    draw_text_centered(draw, "每晚一年，孩子的选择就少一条路", y2+12, f_mid, '#f39c12')
    draw_text_centered(draw, "2025年审批窗口期 · 有公司的老板最快3个月获批", y2+50, f_sm, '#888888')

    # 大字强调
    draw_text_centered(draw, "别让时间替你做决定", 555, f_big, '#ffffff')

    # CTA
    cta_y = 630
    draw_rounded_rect(draw, [170, cta_y, 630, cta_y+55], 28, '#f39c12')
    draw_text_centered_in(draw, "立即评估最佳办理时间 →", cta_y+13, f_cta, '#1a1a1a', 170, 630)

    # 底部
    draw_text_centered(draw, "不成功全额退 | 专注子女升学的香港身份专家", 720, f_xs, '#555555')

    img.save(os.path.join(OUTPUT_DIR, "03_紧迫感型.png"), quality=95)
    print("✓ 03_紧迫感型.png")

def create_card_4():
    """省钱型 - 学费对比"""
    img = Image.new('RGB', (W, H), '#ffffff')
    draw = ImageDraw.Draw(img)

    f_huge = get_font(60, bold=True)
    f_big = get_font(38, bold=True)
    f_mid = get_font(26, bold=True)
    f_body = get_font(22)
    f_sm = get_font(20)
    f_xs = get_font(18)
    f_cta = get_font(24, bold=True)
    f_tag = get_font(26, bold=True)

    # 顶部渐变条
    for i in range(80):
        r = int(39 + (231-39) * i / 80)
        g = int(174 + (76-174) * i / 80)
        b = int(96 + (60-96) * i / 80)
        draw.line([0, i, W, i], fill=(r, g, b))

    draw_text_centered(draw, "一个身份，4年省64万学费", 24, f_tag, '#ffffff')

    # === 左侧卡片 - 非港籍 ===
    LX0, LX1 = 40, 380
    y = 110
    draw_rounded_rect(draw, [LX0, y, LX1, y+180], 16, '#fff0f0')
    draw.rectangle([LX0, y, LX1, y+45], fill='#e74c3c')
    draw_text_centered_in(draw, "非港籍生", y+8, f_mid, '#ffffff', LX0, LX1)
    draw_text_centered_in(draw, "20万", y+60, f_huge, '#c0392b', LX0, LX1)
    draw_text_centered_in(draw, "/年", y+135, f_mid, '#999999', LX0, LX1)

    # === 右侧卡片 - 港籍 ===
    RX0, RX1 = 420, 760
    draw_rounded_rect(draw, [RX0, y, RX1, y+180], 16, '#f0fff0')
    draw.rectangle([RX0, y, RX1, y+45], fill='#27ae60')
    draw_text_centered_in(draw, "港籍生", y+8, f_mid, '#ffffff', RX0, RX1)
    draw_text_centered_in(draw, "4万", y+60, f_huge, '#27ae60', RX0, RX1)
    draw_text_centered_in(draw, "/年", y+135, f_mid, '#999999', RX0, RX1)

    # 省钱强调条
    y2 = 310
    draw_rounded_rect(draw, [200, y2, 600, y2+60], 30, '#f39c12')
    draw_text_centered_in(draw, "4年省 64万", y2+10, f_big, '#ffffff', 200, 600)

    # 更多优势列表
    y3 = 400
    draw_rounded_rect(draw, [40, y3, 760, y3+210], 16, '#f8f9fa')

    advantages = [
        ("录取率40%", "港八大本地生 vs 外地生6%"),
        ("400分上985", "港澳台联考，降维打击"),
        ("副学士兜底", "成绩不理想也有本科读"),
        ("不成功全退", "零风险，全额退款承诺"),
    ]
    icons = ["▸", "▸", "▸", "▸"]
    ay = y3 + 18
    for i, (title, desc) in enumerate(advantages):
        draw.text((60, ay+2), icons[i], font=f_sm, fill='#27ae60')
        draw.text((85, ay), title, font=f_mid, fill='#2c2c2c')
        tw = text_width(draw, title, f_mid)
        draw.text((95 + tw, ay+4), desc, font=f_sm, fill='#888888')
        ay += 47

    # CTA
    cta_y = 640
    draw_rounded_rect(draw, [140, cta_y, 660, cta_y+55], 28, '#27ae60')
    draw_text_centered_in(draw, "免费评估 · 你的孩子能省多少 →", cta_y+13, f_cta, '#ffffff', 140, 660)

    # 底部
    draw_text_centered(draw, "宸好未来 | 专注子女升学教育的香港身份服务专家", 720, f_xs, '#aaaaaa')

    img.save(os.path.join(OUTPUT_DIR, "04_省钱学费型.png"), quality=95)
    print("✓ 04_省钱学费型.png")


if __name__ == "__main__":
    print("生成ADQ朋友圈广告素材...")
    create_card_1()
    create_card_2()
    create_card_3()
    create_card_4()
    print(f"\n完毕！保存在: {OUTPUT_DIR}")
