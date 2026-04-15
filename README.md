<div align="center">

# 🗺️ Virtual Travel Skill

**用 AI 开启一段旅程，足不出户探索中国**

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![VS Code](https://img.shields.io/badge/VS%20Code-Copilot-007ACC?style=for-the-badge&logo=visualstudiocode&logoColor=white)](https://code.visualstudio.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Cities](https://img.shields.io/badge/已支持城市-6+-orange?style=for-the-badge&logo=googlemaps&logoColor=white)]()

> 🤖 基于 **VS Code + GitHub Copilot** 的虚拟旅行助手  
> 自动下载景点图片 · 生成精美 PPT 旅行日记 · 一句话触发全流程

</div>

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| 🖼️ **智能图片获取** | 自动从 Wikimedia Commons 下载高清景点图片 |
| 📊 **PPT 自动生成** | 16:9 深色主题，含封面、目录、景点介绍、结尾页 |
| 💬 **Chat 内展示** | 在 VS Code Copilot Chat 中直接呈现图文攻略 |
| ⚡ **零配置启动** | 自动检测并创建 Python 虚拟环境，依赖一键安装 |

---

## 🏙️ 已支持城市

<div align="center">

| 🏙️ 城市 | 🎯 主要景点 |
|:------:|:----------|
| 🔴 **上海** | 外滩、东方明珠广播电视塔、豫园 |
| 🟡 **北京** | 故宫（紫禁城）、颐和园、天坛 |
| 🟢 **南京** | 中山陵、明孝陵、夫子庙秦淮风光带 |
| 🔵 **洛阳** | 龙门石窟、白马寺、关林 |
| 🟠 **商丘** | 商丘古城、阏伯台、芒砀山汉梁王陵 |
| 🟣 **广州** | 广州塔、陈家祠、中山纪念堂 |
| 🌊 **青岛** | 栈桥、崂山、八大关景区 |

</div>

---

## 🚀 快速开始

### 第一步：在 Copilot Chat 中输入城市名

```
洛阳
```

或者更自然地说：

```
我想去南京旅游
```

### 第二步：坐等 AI 帮你搞定一切 ✅

```
✔ 检测 Python 虚拟环境（不存在则自动创建）
✔ 安装所需依赖包
✔ 下载景点高清图片
✔ 在 Chat 中展示图文攻略
✔ 自动生成旅行 PPT
```

### 第三步：查看生成的旅行 PPT 📂

```
旅行日记/{城市}/旅行PPT/{城市}_旅行日记_{日期}.pptx
```

---

## 📁 项目结构

```
Virtual-Travel-Skills/
├── 🗂️ skills/
│   └── Virtual-Travel/
│       ├── SKILL.md                     ← Copilot Skill 定义文件
│       ├── assets/
│       │   ├── display-template.md      ← 景点展示模板
│       │   └── travel-diary-template.md ← 旅行日记模板
│       └── scripts/
│           ├── show_city.py             ← 景点图文展示 & 图片下载
│           ├── generate_travel_ppt.py   ← PPT 生成（主要）
│           └── generate_travel_diary.py ← PDF 日记生成（备用）
├── 🗂️ 旅行日记/                          ← 生成内容输出目录
│   └── {城市}/
│       ├── 景点图片/
│       └── 旅行PPT/
├── 📄 requirements.txt                  ← Python 依赖清单
├── ⚙️ setup.ps1                         ← 环境搭建脚本
├── .gitignore
└── README.md
```

---

## 📦 依赖说明

| 包 | 版本 | 用途 |
|:--|:--:|:--|
| `python-pptx` | 1.0.2 | PPT 生成 |
| `pillow` | 12.2.0 | 图片处理 |
| `requests` | 2.33.1 | 图片下载 |
| `fpdf2` | 2.8.7 | PDF 生成 |

---

## ➕ 添加新城市

在 `show_city.py` 和 `generate_travel_ppt.py` 的 `ATTRACTION_DATA` 字典中新增城市条目：

```python
"城市名": {
    "景点名": {
        "name_en": "English Name",
        "description": "景点介绍...",
        "tips": "游览小贴士...",
        "best_time": "最佳游览时间",
        "ticket": "门票价格",
        "wikimedia_file": "Commons上的文件名.jpg",
        "image_filename": "本地保存文件名.jpg"
    }
}
```

> 💡 `wikimedia_file` 可在 [Wikimedia Commons](https://commons.wikimedia.org) 搜索景点名称获取。
>
> ⚠️ 添加新城市时需同步更新以下 **三个脚本**：`show_city.py`、`generate_travel_ppt.py`、`generate_travel_diary.py`

---

<div align="center">

**Made with ❤️ + 🤖 GitHub Copilot**

</div>
