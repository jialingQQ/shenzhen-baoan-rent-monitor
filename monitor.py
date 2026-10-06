import requests
from bs4 import BeautifulSoup
import re
import json

# 配置
URL = "https://www.baoan.gov.cn/bajshej/gkmlpt/index"
KEYWORDS = ["保障性租赁住房", "保租房", "配租", "认租"]
EXCLUDE = ["人才住房", "配售", "征求意见", "政策解读", "菁英人才"]
# 记录已看过的公告，存在json文件
RECORD_FILE = "history.json"

def load_history():
    try:
        with open(RECORD_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_history(data):
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(list(data), f, ensure_ascii=False, indent=2)

def main():
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    history = load_history()
    new_items = []

    # 遍历页面所有链接标题
    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        link = a.get("href","")
        if not title:
            continue
        item_id = f"{title}|{link}"
        if item_id in history:
            continue
        # 排除词过滤
        skip = False
        for ex in EXCLUDE:
            if ex in title:
                skip=True
                break
        if skip:
            continue
        # 匹配关键词
        for kw in KEYWORDS:
            if kw in title:
                new_items.append({"title":title,"url":link})
                history.add(item_id)
                break

    save_history(history)
    if new_items:
        print("✅【发现新的保租房公告！】")
        for item in new_items:
            print(f"标题：{item['title']}")
            print(f"链接：{item['url']}\n")
    else:
        print("❌ 今日没有发现匹配的新公告")

if __name__ == "__main__":
    main()
