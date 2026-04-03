import requests
import base64
import re
import socket
from concurrent.futures import ThreadPoolExecutor

# 推荐的节点源
urls = [
    "https://raw.githubusercontent.com/vpei/free/master/v2ray",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/all"
]

# TCP 端口连接测试函数
def check_node(node_str):
    try:
        addr, port = None, None
        # 处理 vmess 协议 (Base64 JSON)
        if node_str.startswith("vmess://"):
            import json
            v_data = json.loads(base64.b64decode(node_str[8:]).decode('utf-8'))
            addr, port = v_data.get('add'), v_data.get('port')
        # 处理 ss/vless/trojan 协议 (正则提取地址和端口)
        else:
            match = re.search(r'@?([a-zA-Z0-9.-]+):([0-9]+)', node_str)
            if match:
                addr, port = match.group(1), int(match.group(2))
        
        if addr and port:
            # 尝试建立 TCP 连接，超时时间设为 2 秒
            s = socket.create_connection((addr, int(port)), timeout=2)
            s.close()
            return node_str # 连接成功，返回节点
    except:
        pass
    return None # 连接失败

def main():
    all_nodes = []
    for url in urls:
        try:
            res = requests.get(url, timeout=10)
            # 兼容 Base64 和明文格式
            content = res.text
            try:
                # 补齐 Base64 填充
                content = base64.b64decode(content + '=' * (-len(content) % 4)).decode('utf-8')
            except:
                pass
            all_nodes.extend(content.splitlines())
        except:
            continue

    # 去重并清理
    unique_nodes = list(set([n.strip() for n in all_nodes if "://" in n]))
    print(f"抓取完成，共 {len(unique_nodes)} 个节点。开始测速过滤...")

    # 使用多线程进行测速（开启 50 个线程）
    valid_nodes = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(check_node, unique_nodes)
        for r in results:
            if r:
                valid_nodes.append(r)

    print(f"测速完成！存活节点数: {len(valid_nodes)}")

    # 重新 Base64 编码并保存
    if valid_nodes:
        final_b64 = base64.b64encode("\n".join(valid_nodes).encode()).decode()
        with open("sub.txt", "w") as f:
            f.write(final_b64)

if __name__ == "__main__":
    main()
