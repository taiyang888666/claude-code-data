# 微信公众号工作流程

## 账号信息
- 公众号名称：青澜传媒
- 操作人：太阳🌞（Sampson Song）

## 用户偏好
- 贴图发布：只保存为草稿，用户自己手动发布
- 文案要求：符合平台规则，不使用违规词（如医学诊断术语等）
- 标题限制：20字以内
- 文案风格：用中式/诗意表达，不用直白的数字化表述
  - 例：用"一炷香的时间"（约45分钟~2小时）代替"20分钟"
  - 避免过于西式/直白的表达，保持意境感
  - 时间表述优先用意象化语言（如一炷香、一盏茶等），不写具体分钟数

## 贴图图片路径
- 基础路径：`D:\Claude Code Data\公众号图片\`
- 第001条_焦虑：01_封面.png, 02_内容.png, 03_产品.png, 04_尾页.png（已完成，保存为草稿）
- 第002条_失眠：同样4张图结构
- 第003条_角落：同样4张图结构
- 所有图片尺寸：1080x1440 竖版

## 设计参考
- 详见 `design_reference.md`（C-C Studio 小红书配色教学账号分析）
- 关键风格：复古风（最受欢迎）、多巴胺风（活力主题）、暗黑系（情绪主题）
- 标题格式参考：`主题｜吸引点`，简洁有力

## 技术方案（自动上传图片到微信贴图编辑器）
1. 在 127.0.0.1 启动 HTTP 服务器，serve 图片目录
2. 从微信编辑器页面 fetch http://127.0.0.1:port/图片路径（Chrome 允许 HTTPS→127.0.0.1 HTTP）
3. 将 fetch 到的 blob 转为 File 对象
4. 通过 Vue 组件树找到 `mp-upload` 组件的 WebUploader 实例
5. 调用 `uploader.addFile(file)` 添加文件（auto-upload 会自动上传到 CDN）
6. 标题通过 `.js_title_main .ProseMirror` contentEditable div 设置
7. 描述通过 `#guide_words_main .ProseMirror` contentEditable div 设置
8. 同步 Vue data: `vue.$data.articleData.title` 和 `vue.$data.articleData.digest`
