import os
import json
import re
from typing import List, Dict

# 配置区
CONFIG = {
    "wallpaper": "http://饭太硬.top/深色壁纸/api.php",
    "logo": "https://raw.giteeusercontent.com/xuelong88/xiaosa_box/raw/master/pg.gif",
    "spider": "https://raw.giteeusercontent.com/xuelong88/pg_box/raw/master/pg.jar",
    # 关键修改：默认输出到仓库根目录的 pg.json
    "output_path": os.environ.get(
        "PG_OUTPUT",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "pg.json",
        ),
    ),
    "exclude_names": [
       "推荐","TG","本地","急救","知识","直播","推送","123","PikPak","商店" 
    ],

    "lives": [
        {
            "name": "移动8m",
            "type": 0,
            "url": "https://gh-proxy.com/https://raw.githubusercontent.com/xuelong876/mybox_PG/refs/heads/main/live/YD8M.m3u",
            "playerType": 2,
            "ua": "okhttp/3.12.13",
            "logo": "https://cdn.jsdelivr.net/gh/xuelong876/channal_logo2@master/{name}.png",
            "epg": "http://cdn.1678520.xyz/epg/?ch={name}&date={date}",
        },
        {
            "name": "刺桐自营",
            "type": 0,
            "url": "https://www.cttv.vip/ys/json/ctzb.txt",
            "playerType": 2,
            "ua": "okhttp/3.12.13",
            "logo": "https://cdn.jsdelivr.net/gh/xuelong876/channal_logo2@master/{name}.png",
            "epg": "http://cdn.1678520.xyz/epg/?ch={name}&date={date}",
        },
    ],
}

# --- 名称美化（添加Emoji）---
def add_emoji_to_name(name: str) -> str:
    """添加Emoji到名称，按列表顺序依次判断，命中第一条即返回"""
    rules = [
        ("startswith", "豆瓣", "🏠豆瓣 • PG👨"),
        ("startswith", "网盘及弹幕", "⚙️网盘及弹幕配置👌"),
        ("startswith", "B站", "🅱️{name}👌"),
        ("startswith", "分享", "☁{name}👌"),
        ("endswith", ("分享","网盘", "搜索", "云搜"), "☁{name}👌"),
        ("endswith", ("磁力", "磁"), "🧲{name}👌")
        
    ]

    if not isinstance(name, str) or not name:
        return ""

    for match_type, match_val, template in rules:
        if match_type == "startswith":
            if name.startswith(match_val):
                return template.format(name=name) if "{name}" in template else template
        elif match_type == "endswith":
            if isinstance(match_val, tuple):
                if any(name.endswith(val) for val in match_val):
                    return template.format(name=name)
            elif name.endswith(match_val):
                return template.format(name=name)

    return f"👌{name}👌"

def remove_json_comments(json_str):
    """移除JSON中的单行和多行注释"""
    pattern = r'//.*?$|/\*.*?\*/|\'(?:\\.|[^\\\'])*\'|"(?:\\.|[^\\"])*"'
    replacer = lambda match: match.group(0) if match.group(0)[0] == '"' or match.group(0)[0] == "'" else ''
    return re.sub(pattern, replacer, json_str, flags=re.MULTILINE | re.DOTALL)

def load_json_with_comments(file_path):
    """加载带注释的JSON文件"""
    with open(file_path, "r", encoding="utf-8") as f:
        json_str = f.read()
    # 移除注释
    json_str_clean = remove_json_comments(json_str)
    return json.loads(json_str_clean)
# ... existing code ...
def main():
    """
    1. 读取接口 JSON
    2. 修改壁纸、logo、spider
    3. 替换 lives
    4. 过滤 sites 中的站点
    5. 给站点 name 加 Emoji
    6. 追加 add_site
    7. 保存到指定路径
    """
    try:
        data = load_json_with_comments("jsm.json")# 读取jsm.json文件

        # 修改基本字段
        data["wallpaper"] = CONFIG["wallpaper"]
        data["logo"] = CONFIG["logo"]
        data["spider"] = CONFIG["spider"]

        # 替换 lives
        data["lives"] = CONFIG["lives"]

        # 过滤 + 美化 sites
        if "sites" in data and isinstance(data["sites"], list):
            data["sites"] = [
                site
                for site in data["sites"]
                if not any(
                    exclude_name in site.get("name", "")
                    for exclude_name in CONFIG["exclude_names"]
                )
            ]

            for site in data["sites"]:
                name = site.get("name", "")
                if name:
                    site["name"] = add_emoji_to_name(name)
                site["changeable"] = 0
        else:
            data["sites"] = []

        

        # 确保输出目录存在
        output_path = CONFIG["output_path"]
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        # 写文件
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"处理完成，文件已保存到：{output_path}")

   
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误：{e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"处理过程中发生错误：{e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
