import requests
import base64
import re
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

# 精简源：只保留几个响应最快的
urls = [
    "https://raw.githubusercontent.com/vpei/free/master/v2ray",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/anaer/Sub/master/nodes.txt"
]

def check_node(node_str):
    """极速检测：仅 1 秒超时"""
    try:
        node = node_str.strip()
        if not node or "://" not in node: return None
        
        # 提取地址和端口的通用正则
        match = re.search(r'@?([a-zA-Z0-9.-]+):([0-9]+)', node)
        if match:
            addr, port = match.group(1), int(match.group(2))
            # 使用最基础的 socket，设置 1 秒硬性超时
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0) 
                if s.connect_ex((addr, port)) == 0:
                    return node
    except:
        pass
    return None

def main():
    print("--- 开始抓取阶段 ---")
    raw_nodes = []
    for url in urls:
        try:
            r = requests.get(url, timeout=5)
            content = r.text
            # 自动处理 Base64
            try:
                content = base64.b64decode(content + '===').decode('utf-8', 'ignore')
            except:
                pass
            raw_nodes.extend(content.splitlines())
            print(f"成功获取源: {url}")
        except:
            print(f"跳过失效源: {url}")

    # 去重并初步清理
    unique_nodes = list(set([n.strip() for n in raw_nodes if "://" in n]))[:200] # 限制前200个，防止任务过重
    print(f"待测节点总数: {len(unique_nodes)}")

    print("--- 开始极速过滤阶段 ---")
    valid_nodes = []
    # 降低并发到 20，避免触发 GitHub 网络保护
    with ThreadPoolExecutor(max_workers=20) as executor:
        future_to_node = {executor.submit(check_node, n): n for n in unique_nodes}
        for future in as_completed(future_to_node):
            res = future.result()
            if res:
                valid_nodes.append(res)
                if len(valid_nodes) >= 50: break # 抓够 50 个就收工，防止后面卡死

    print(f"过滤完成！找到有效节点: {len(valid_nodes)}")

    # 最终写入
    if valid_nodes:
        output = base64.b64encode("\n".join(valid_nodes).encode()).decode()
        with open("sub.txt", "w") as f:
            f.write(output)
    else:
        with open("sub.txt", "w") as f: f.write("")

if __name__ == "__main__":
    main()
