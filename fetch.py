import requests
import base64

# 增加更多非 GitHub 的聚合源，提高存活率
urls = [
    "https://raw.githubusercontent.com/vpei/free/master/v2ray",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/all_extracted_configs.txt",
    "https://gitlab.com/free54188/v2ray-free/-/raw/master/v2",
    "https://fastly.jsdelivr.net/gh/aiboboxx/v2rayfree@main/v2" # 使用 jsdelivr 加速
]

def main():
    all_nodes = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=15)
            if r.status_code == 200:
                content = r.text.strip()
                # 尝试解码
                try:
                    decoded = base64.b64decode(content + '===').decode('utf-8', 'ignore')
                    lines = decoded.splitlines()
                except:
                    lines = content.splitlines()
                
                for line in lines:
                    # 只抓取包含主流协议头的行，并排除掉一些明显是广告的行
                    if any(prot in line for prot in ["vmess://", "vless://", "ss://", "trojan://"]):
                        if len(line) > 30: # 过滤掉太短的无效链接
                            all_nodes.append(line.strip())
        except:
            continue

    unique_nodes = list(set(all_nodes))
    
    if unique_nodes:
        # 重点：为了提高成功率，我们只取前 150 个（最新的通常在前面）
        # 太多节点会导致 v2rayN 测速时直接把你的网络卡死
        final_list = unique_nodes[:150]
        final_b64 = base64.b64encode("\n".join(final_list).encode()).decode()
        with open("sub.txt", "w") as f:
            f.write(final_b64)
        print(f"成功写入 {len(final_list)} 个节点")
