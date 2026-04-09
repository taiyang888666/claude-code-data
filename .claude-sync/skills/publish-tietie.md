---
description: "生成公众号贴图图片并通过浏览器自动化发布为草稿"
usage: "/publish-tietie <条目号> [--generate] [--upload] [--draft]"
---

# 公众号贴图发布技能

将指定条目生成图片、上传素材库、通过浏览器自动化在微信公众号后台创建贴图草稿。

## 参数说明

- `{{args}}` 包含条目号（如 `2` 或 `1,2,3`）
- `--generate`：仅生成图片
- `--upload`：仅上传到素材库
- `--draft`：仅浏览器自动化创建草稿
- 不加标志则执行完整流程

## 完整流程

### 第一步：生成图片

运行 Python 脚本生成贴图图片：

```bash
cd "/mnt/d/Claude Code Data"
python3 公众号图片号生成器_v4.py
```

脚本会自动：
- 从 `全部选题逐字稿文案_v2.md` 解析文案
- 为每条生成：封面 → 内容页(1-3张) → 产品推荐页 → 尾页
- 输出到 `公众号图片/第XXX条_关键词/` 目录
- 使用6套莫兰迪配色轮换

如需只生成特定条目，修改脚本最后的 `run(topic_nums=[...])` 参数。

### 第二步：上传图片到素材库

通过微信API上传图片（按正确顺序，从01_封面到最后的尾页）：

```python
import requests, os, time

APPID = "wx1b34b874a2ccbf1d"
APPSECRET = "c24b898d7fe9cf727c0796decc72c6d0"

# 获取 access_token
token_url = f"https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={APPID}&secret={APPSECRET}"
access_token = requests.get(token_url).json()["access_token"]

# 上传每张图片
upload_url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={access_token}&type=image"
image_dir = "/mnt/d/Claude Code Data/公众号图片/第XXX条_关键词/"

for filename in sorted(os.listdir(image_dir)):
    if filename.endswith('.png'):
        filepath = os.path.join(image_dir, filename)
        with open(filepath, "rb") as f:
            resp = requests.post(upload_url, files={"media": (filename, f, "image/png")}).json()
        print(f"上传 {filename}: media_id={resp.get('media_id')}")
        time.sleep(0.5)
```

**重要**：图片按文件名排序上传（01_封面, 02_内容, ... 尾页），因为素材库显示按上传时间倒序，后续选择时需要从后往前选。

### 第三步：浏览器自动化创建贴图草稿

#### 3.1 打开贴图编辑器

使用 Chrome MCP 导航到贴图编辑器：

```
URL: https://mp.weixin.qq.com/cgi-bin/appmsg?t=media/appmsg_edit_v2&action=edit&isNew=1&type=77&createType=8&token={TOKEN}&lang=zh_CN
```

其中 `{TOKEN}` 从当前已登录的公众号后台页面URL中获取。

#### 3.2 逐张添加图片（关键步骤）

**必须逐张添加图片以保证正确顺序。** 批量选择会按素材库grid顺序（上传时间倒序）添加，不是点击顺序。

对每张图片执行以下 JavaScript：

```javascript
async function addImageByIndex(pickerIndex) {
  // 1. 点击"从图片库选择"按钮（第一次添加时可能显示为不同入口）
  const addBtns = document.querySelectorAll('a[href="javascript:;"]');
  // 找到"从图片库选择"按钮并点击

  // 2. 等待图片选择器加载
  await new Promise(r => setTimeout(r, 1500));

  // 3. 点击目标图片缩略图（按pickerIndex）
  // 素材库中图片按上传时间倒序排列（最新在前）
  // 如果上传了6张图，index 0 = 06_尾页, index 5 = 01_封面
  const thumbnails = document.querySelectorAll('.img_item');
  thumbnails[pickerIndex].click();

  // 4. 点击"确定"按钮
  await new Promise(r => setTimeout(r, 500));
  const confirmBtn = /* 找到确定按钮 */;
  confirmBtn.click();

  // 5. 等待图片添加完成
  await new Promise(r => setTimeout(r, 1500));
}
```

**图片顺序逻辑**：
- 素材库中6张图按上传时间倒序：[06_尾页, 05_产品, 04_内容, 03_内容, 02_内容, 01_封面]
- 要正确排序，需依次添加 index 5(封面) → 4(内容) → 3(内容) → 2(内容) → 1(产品) → 0(尾页)
- 即 `for i in range(N-1, -1, -1): addImageByIndex(i)`

**第一次添加图片的特殊处理**：
- 首次打开选择器会弹出"编辑封面"对话框（单选模式，有"下一步"按钮）
- 选择封面图后点击"下一步"确认即可
- 后续添加通过点击底部"从图片库选择"按钮，使用单选+确定模式

#### 3.3 填写标题

贴图标题使用 ProseMirror contenteditable div：

```javascript
const proseElements = document.querySelectorAll('.ProseMirror');
const titleEl = proseElements[0]; // placeholder="请在这里输入标题"
titleEl.focus();
titleEl.innerHTML = '<p>标题文字</p>';
titleEl.dispatchEvent(new Event('input', { bubbles: true }));
```

标题建议：使用文案第一句话或封面关键词相关的hook句，不超过20字。

#### 3.4 填写描述信息

描述使用第二个 ProseMirror div：

```javascript
const descEl = proseElements[1]; // 显示"填写描述信息，让大家了解更多内容"
descEl.focus();
descEl.innerHTML = '<p>描述文字</p>';
descEl.dispatchEvent(new Event('input', { bubbles: true }));
```

描述内容建议：
- 从文案中提取核心内容，精简为2-3句
- 末尾添加话题标签：`#失眠 #线香 #情绪治愈`

#### 3.5 添加话题标签

描述区域下方有系统推荐的话题面板（`js_recommend_topic`），可能默认隐藏：

```javascript
// 显示话题推荐面板
const topicPanel = document.querySelector('.js_recommend_topic');
topicPanel.style.display = 'block';

// 选择推荐话题
const topicItems = document.querySelectorAll('.topic_item_tag');
topicItems[0].click(); // 选择第一个推荐话题
```

也可以在描述文字末尾直接添加 `#话题` 格式的标签。

#### 3.6 保存为草稿

```javascript
const allBtns = document.querySelectorAll('button');
for (const btn of allBtns) {
  if (btn.textContent.trim() === '保存为草稿') {
    btn.click();
    break;
  }
}
```

保存成功后，历史记录面板（`.appmsg_history_popup`）会更新显示"手动保存"。

## 关键技术细节

1. **不要用API的 `draft/add` + `freepublish/submit`**，那样会发成文章格式，不是贴图
2. **图片必须逐张添加**，不能批量选择（批量会打乱顺序）
3. **素材库中图片按上传时间倒序排列**（最新上传的在最前面）
4. **CDP文件上传不可行**，微信上传组件有特殊验证
5. **删除已添加图片**：使用 `.comm_del` class 的按钮
6. **ProseMirror 输入**：不能用 `value` 属性，必须修改 `innerHTML` 并触发 `input` 事件
7. 贴图编辑器URL参数：`type=77&createType=8` 表示贴图类型

## 文案来源

- 文案文件：`/mnt/d/Claude Code Data/全部选题逐字稿文案_v2.md`
- 格式：`### 第N条 | 封面关键词：【关键词】` + 代码块内文案
- `【】` 标记的句子在图片中会加高亮色块
- 最后一行是产品推荐文案

## 生成的标题/描述建议

- **标题**：用文案第一句话（hook句），保持20字以内
- **描述**：精简文案核心内容 + 末尾加话题标签
- **话题标签**：根据内容选择，常用：`#线香` `#情绪治愈` `#居家好物` + 系统推荐话题
