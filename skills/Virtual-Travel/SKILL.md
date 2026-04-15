---
name: Virtual-Travel
description: "虚拟旅行SKILL — 交互式城市旅行探索技能。Use when: 用户想探索某个城市的旅行目的地、查看景点照片、生成旅行日记。涵盖：城市景点搜索、照片展示、交互式游览、精美旅行日记生成。"
argument-hint: "输入城市名称开始旅行探索，例如：巴黎、京都、纽约"
user-invocable: true
---

# 虚拟旅行 SKILL ✈️

## 技能简介

这是一个交互式旅行探索技能。用户输入目标城市后，系统会自动搜索该城市的著名景点照片并展示，同时**自动生成包含图片的精美旅行 PPT（.pptx）**，无需用户手动触发。

---

## 触发场景

- 用户想探索某个城市的旅行目的地
- 用户想看某城市的著名景点照片
- 用户想生成旅行日记或行程规划
- 关键词：旅行、城市、景点、游览、日记、出行、旅游

---

## 执行流程

### 第一步：欢迎与城市输入

如果用户没有在调用时直接提供城市名，则用以下方式欢迎并询问：

```
🌍 欢迎来到「我爱旅行」！

请告诉我您想探索哪座城市？
（例如：巴黎、东京、纽约、成都、迪拜...）
```

### 第二步：检查并准备 Python 环境

收到城市名称后，**在运行任何脚本之前**，先检查虚拟环境是否存在：

在终端执行：
```powershell
Test-Path ".venv\Scripts\python.exe"
```

- 若返回 **True**：环境已就绪，直接进入第三步
- 若返回 **False**：手动创建虚拟环境并安装依赖：
  ```powershell
  python -m venv .venv
  .venv\Scripts\pip install -r requirements.txt
  ```
  等待安装完成后，再进入第三步

> ⚠️ 不要使用 `setup.ps1`，PowerShell 执行策略限制会导致其无法运行。

> 此步骤只需在环境不存在时执行一次，后续调用直接跳过。

### 第三步：下载图片、展示景点，并自动生成 PPT

收到城市名称后，**同时执行以下两件事**：

#### 3-A：下载图片并展示景点

1. **运行图片下载脚本**（在终端中执行）：
   ```
   .venv\Scripts\python.exe "skills/Virtual-Travel/scripts/show_city.py" --city [城市名] --output-dir "c:\Users\Terry\Desktop\Virtual-Travel-Skills-main"
   ```
   脚本输出 JSON，包含每个景点的本地图片路径（`image_local_path`）。

2. **读取 JSON 输出**，提取每个景点的：
   - `name`（景点名）、`description`（简介）、`tips`（贴士）
   - `best_time`（最佳时间）、`ticket`（门票）
   - `image_local_path`（本地图片绝对路径，形如 `C:/Users/.../waitan.jpg`）

3. **使用本地路径展示图片**：将路径转换为 `file:///` URI 格式展示：
   ```markdown
   ![景点名](file:///C:/Users/Terry/Desktop/Virtual-Travel-Skills-main/旅行日记/[城市名]/景点图片/[景点]/xxx.jpg)
   ```

4. **展示格式**参考 [展示模板](./assets/display-template.md)

展示内容应包含：
- 景点名称（中英文）
- 景点简介（2-3 句话，生动有趣）
- 景点图片（使用本地 `file:///` 路径内嵌展示）
- 实用小贴士（最佳游览时间、注意事项等）

**每次展示 2-3 个景点**，信息量适中，不要过于冗长。

> **若城市不在脚本数据中**：先用 `fetch_webpage` 从 Wikipedia/Wikimedia 搜索景点信息，将新城市数据添加到 `ATTRACTION_DATA`（同时更新 `show_city.py` 和 `generate_travel_diary.py`），再运行脚本。

#### 3-B：自动生成旅行日记 PPT（无需等待用户选择）

**每次展示完景点后，立即在终端运行以下命令生成 PPT**（不等待用户选择）：

```
.\.venv\Scripts\python.exe "skills/Virtual-Travel/scripts/generate_travel_ppt.py" --city [城市名] --output-dir "c:\Users\Terry\Desktop\Virtual-Travel-Skills-main"
```

脚本运行完成后，告知用户 PPT 已生成并提供文件路径：

```
✅ 旅行 PPT 已自动生成！
📄 文件路径：旅行日记/[城市名]/旅行PPT/[城市名]_旅行日记_[日期].pptx
```

### 第四步：交互选择

景点展示完（PPT 已自动生成）后，询问用户：

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📍 您已探索了 [城市名] 的 [已看景点数] 个景点
✅ 旅行 PPT 已自动生成至：旅行日记/[城市名]/旅行PPT/

请选择：
  🔍 [1] 继续探索更多景点（并更新旅行日记）
  🏙️  [2] 换一座城市

您的选择：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- 选 **1（继续）**：搜索该城市**其他**著名景点（避免重复），展示后再次自动重新生成 PPT（包含所有已游览景点）
- 选 **2（换城市）**：清空本次记录，从第一步重新开始

### 第五步：生成精美旅行日记（PDF + 本地文件）

**此步骤现已改为自动触发**，在第三步 3-B 中每次均会自动执行，无需用户手动选择。

脚本执行内容：
1. **运行生成脚本**（在终端中执行）：
   ```
   .venv\Scripts\python.exe "skills/Virtual-Travel/scripts/generate_travel_ppt.py" --city [城市名] --output-dir "c:\Users\Terry\Desktop\Virtual-Travel-Skills-main"
   ```
   脚本会自动完成：
   - 通过 **Wikimedia Commons API** 下载景点高清图片到本地
   - 创建结构化文件夹（见下方文件夹结构）
   - 生成包含图片的 **PPTX 旅行日记**

2. **自动创建的文件夹结构**：
   ```
   旅行日记/
   └── [城市名]/
       ├── 景点图片/
       │   ├── [景点1]/  ← 包含该景点的本地图片
       │   ├── [景点2]/
       │   └── [景点3]/
       └── 旅行PPT/
           └── [城市名]_旅行日记_[日期].pptx  ← 生成的 PPT
   ```

3. **PPT 内容包含**：
   - 城市封面（标题 + 副标题 + 日期）
   - 每个景点幻灯片（含本地图片、简介、贴士、最佳时间、门票信息）
   - 结尾致谢页

> **注意**：如需为新城市添加景点数据，必须同步更新以下 **三个脚本** 中的 `ATTRACTION_DATA` 字典：
> - `scripts/show_city.py`
> - `scripts/generate_travel_ppt.py`
> - `scripts/generate_travel_diary.py`
>
> 每个景点需提供 `wikimedia_file`（Wikimedia Commons 文件名）用于自动获取图片直链。

---

## 重要规范

### 图片处理
- **必须先运行 `show_city.py` 下载图片到本地**，再展示
- 使用 `file:///` 本地路径格式展示：`![景点名](file:///C:/Users/.../xxx.jpg)`
- 禁止直接使用 Wikimedia/Wikipedia 的远程 URL 展示图片（在 VS Code Chat 中无法渲染）
- 若某景点图片下载失败（`image_ok: false`），使用文字描述替代，不要使用占位图

### 景点搜索
- 每次展示不少于 2 个、不超过 3 个景点
- 每次搜索应返回**不同**的景点（记录已展示过的景点列表）
- 优先展示世界知名、具有代表性的景点

### 语言风格
- 全程使用**中文**交流
- 语言**生动有趣**，富有旅行感染力
- 日记部分使用**文学化**写作风格，充满情感

---

## 状态追踪

在整个对话过程中，需要在内存中追踪以下状态：

```
当前城市：[城市名]
已展示景点：[景点1, 景点2, ...]
展示轮次：[数字]
游览开始时间：[日期]
```

---

## 示例交互

**用户**：`/Virtual-Travel 巴黎`

**技能响应**：

> 🗼 **欢迎探索巴黎！**
>
> 正在下载巴黎景点图片...
>（运行 `show_city.py --city 巴黎`，获取本地路径）
>
> ---
> ### 🏛️ 埃菲尔铁塔（Tour Eiffel）
> ![埃菲尔铁塔](file:///C:/Users/Terry/Desktop/Virtual-Travel-Skills-main/旅行日记/巴黎/景点图片/埃菲尔铁塔/eiffel_tower.jpg)
>
> 埃菲尔铁塔是法国巴黎的标志性建筑...
>
> 💡 **贴士**：建议傍晚时分前往，日落时分的铁塔格外迷人...
>
> ✅ 旅行 PPT 已自动生成：旅行日记/巴黎/旅行PPT/巴黎_旅行日记_20260415.pptx
>
> ---
> 请选择：[1] 继续探索更多景点 [2] 换城市
