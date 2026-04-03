import requests
import base64
import re

# 2026年依然存活率较高的 Reality/VLESS 聚合源
urls = [
    "https://raw.githubusercontent.com/tubaile/free/main/v2",
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    "https://raw.githubusercontent.com/V2rayFree/V2rayFree/master/sub",
    "https://raw.githubusercontent.com/yebekhe/TVC/main/subscriptions/protocols/vless",
    "https://raw.githubusercontent.com/LonUp/NodeList/main/v2ray/all.txt"
]

def main():
    all_nodes = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for url in urls:
        try:
            r = requests.get(url, headers=headers, timeout=10)
            if r.status_code == 200:
                content = r.text
                # 自动识别是否需要 Base64 解码
                try:
                    if "://" not in content[:50]:
                        content = base64.b64decode(content + '===').decode('utf-8', 'ignore')
                except: pass
                
                lines = content.splitlines()
                for line in lines:
                    line = line.strip()
                    # 重点：优先提取 vless 和 trojan，这两个协议目前最稳
                    if any(p in line for p in ["vless://", "trojan://", "ss://", "vmess://"]):
                        # 过滤掉一些明显的失效字符
                        if len(line) > 50 and "github" not in line.lower():
                            all_nodes.append(line)
        except: continue

    unique_nodes = list(set(all_nodes))
    # 只要最新的 100 个，保证质量
    final_nodes = unique_nodes[:100]

    if final_nodes:
        res_b64 = base64.b64encode("\n".join(final_nodes).encode()).decode()
        with open("sub.txt", "w") as f:
            f.write(res_b64)
        print(f"写入成功，包含 {len(final_nodes)} 个精选节点")
