import requests
from bs4 import BeautifulSoup
import json
import os

# ========== 配置区 ==========
URL = "https://www.baoan.gov.cn/bajshej/gkmlpt/index"
KEYWORDS = ["保障性租赁住房", "保租房", "配租通告", "认租", "万科未来之光"]
EXCLUDE = ["人才住房", "配售", "征求意见", "政策解读", "菁英人才"]
GIST_ID = os.getenv("GIST_ID")
GIST_TOKEN = os.getenv("GIST_TOKEN")
GIST_API = f"https://api.github.com/gists/{GIST_ID}"
# ============================

def load_history_from_gist():
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    resp = requests.get(GIST_API, headers=headers)
    data = resp.json()
    raw = data["files"]["history.json"]["content"]
    return set(json.loads(raw))

def save_history_to_gist(history_set):
    headers = {"Authorization": f"token {GIST_TOKEN}"}
    payload = {
        "files": {
            "history.json": {
                "content": json.dumps(list(history_set), ensure_ascii=False, indent=2)
            }
        }
    }
    requests.patch(GIST_API, headers=headers, json=payload)

def main():
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}
    resp = requests.get(URL, headers=headers, timeout=20)
    resp.encoding = "utf-8"
    soup = BeautifulSoup(resp.text, "html.parser")

    history = load_history_from_gist()
    new_items = []

    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        link = a.get("href","")
        if not title:
            continue
        item_id = f"{title}|{link}"
        if item_id in history:
            continue
        # 过滤排除词
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
    # 更新Gist历史
    save_history_to_gist(history)

    if new_items:
        email_content = "【宝安住建局保租房监控 · 新公告】\n\n"
        for idx,item in enumerate(new_items,1):
            email_content += f"{idx}. 标题：{item['title']}\n链接：{item['url']}\n\n"
        print(email_content)
        # 输出到环境变量，给action邮件步骤读取
        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as f:
            f.write(f"EMAIL_BODY<<EOF\n{email_content}\nEOF\n")
    else:
        print("✅今日无匹配新公告")
        with open(os.environ["GITHUB_ENV"], "a", encoding="utf-8") as f:
            f.write("EMAIL_BODY<<EOF\n【宝安监控】今日没有发现宝安保租房新公告\nEOF\n")

if __name__ == "__main__":
    main()
