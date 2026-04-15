# 虚拟旅行 SKILL

一个基于 VS Code + GitHub Copilot 的旅行日记生成工具，支持自动下载景点图片、生成精美 PPT 旅行日记。

---

## 功能特性

- 自动从 Wikimedia Commons 下载景点图片
- 生成 16:9 深色主题旅行日记 PPT（含封面、目录、景点介绍、结尾页）
- 支持在 VS Code Chat 中直接展示城市景点图文攻略
- 一键搭建 Python 虚拟环境

---

## 已支持城市

| 城市 | 主要景点 |
|------|----------|
| 上海 | 外滩、东方明珠、豫园 |
| 北京 | 故宫、頸和园、天坛 |
| 南京 | 中山陵、明孝陵、夫子庙秦淮风光带 |
| 洛阳 | 龙门石窟、白马寺、关林 |
| 商丘 | 古城、阀伯台、芒砀山汉梁王陵 |
| 广州 | 广州塔、陈家祠、中山纪念堂 |

---

## 快速开始

在 VS Code Copilot Chat 中，直接说城市名即可：

```
洛阳
```

或者：

```
我想去南京旅游
```

Copilot 会自动检查环境是否就绪：
- **首次使用**：自动检测是否存在虚拟环境，若不存在则自动创建并安装依赖，无需手动操作
- **已有环境**：直接跳过，展示景点图文攻略

**展示完景点后，旅行 PPT 会自动生成**，无需手动触发。生成的文件保存在：

```
旅行日记/{城市}/旅行PPT/{城市}_旅行日记_{日期}.pptx
```

---

## 项目结构

```
Virtual-Travel-Skills-main/
├── skills/
│   └── Virtual-Travel/
│       ├── SKILL.md                    # Copilot Skill 定义
│       ├── assets/
│       │   ├── display-template.md     # 景点展示模板
│       │   └── travel-diary-template.md
│       └── scripts/
│           ├── show_city.py            # 景点图文展示及图片下载
│           ├── generate_travel_ppt.py  # PPT 生成（主要）
│           └── generate_travel_diary.py # PDF 日记生成（备用）
├── requirements.txt                    # Python 依赖
├── setup.ps1                           # 环境搜 建脚本（注意：可能受执行策略限制）
├── .gitignore
└── README.md
```

---

## 依赖说明

| 包 | 版本 | 用途 |
|----|------|------|
| fpdf2 | 2.8.7 | PDF 生成 |
| pillow | 12.2.0 | 图片处理 |
| python-pptx | 1.0.2 | PPT 生成 |
| requests | 2.33.1 | 图片下载 |

---

## 添加新城市

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

> `wikimedia_file` 可在 [Wikimedia Commons](https://commons.wikimedia.org) 搜索景点获取。
>
> ⚠️ 添加新城市时需同步更新以下 **三个脚本**：`show_city.py`、`generate_travel_ppt.py`、`generate_travel_diary.py`
