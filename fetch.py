import requests
import base64
import re
import socket
from concurrent.futures import ThreadPoolExecutor

# 精简后的高质量源，去掉了容易卡死的源
# 2026 高质量、高频更新源列表
urls = [
    # Epodonios 聚合源（每5分钟更新，量大管饱）
    "https://raw.githubusercontent.com/Epodonios/v2ray-configs/main/All_Configs_Sub.txt",
    
    # EbraSha 自动清理源（每15分钟更新，自动剔除失效节点）
    "https://raw.githubusercontent.com/ebrasha/free-v2ray-public-list/main/all_extracted_configs.txt",
    
    # Barry-Far 协议分类源（订阅1，稳定性较好）
    "https://raw.githubusercontent.com/barry-far/V2ray-config/main/Sub1.txt",
    
    # Pawdroid 长期维护源（6小时更新，质量较高）
    "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
    
    # vpei 经典源（老牌稳定）
    "https://raw.githubusercontent.com/vpei/free/master/v2ray"
]

def check_node(node_str):
    """测试节点是否存活，严格限制在 1.5 秒内"""
    try:
        node_str = node_str.strip()
        if not node_str: return None
        
        # 简单提取 IP/域名 和 端口
        # 匹配格式如 @address:port
        match = re.search(r'@?([a-zA-Z0-9.-]+):([0-9]+)', node_str)
        if match:
            addr = match.group(1)
            port = int(match.group(2))
            # 核心改进：socket 测试增加极短的 timeout
            with socket.create_connection((addr, port), timeout=1.5) as s:
                return node_str
    except:
        pass
    return None

def main():
    all_nodes = []
    # 1. 抓取阶段：增加 stream=True 和 timeout 防止下载大文件卡死
    for url in urls:
        try:
            print(f"正在抓取: {url}")
            with requests.get(url, timeout=5, stream=True) as r:
                r.raise_for_status()
                text = r.text
                # 尝试 Base64 解码
                try:
                    # 自动补齐 Base64 填充并解码
                    decoded = base64.b64decode(text + '=' * (-len(text) % 4)).decode('utf-8', 'ignore')
                    all_nodes.extend(decoded.splitlines())
                except:
                    all_nodes.extend(text.splitlines())
        except Exception as e:
            print(f"跳过源 {url}: {e}")

    # 2. 清洗数据
    unique_nodes = list(set([n.strip() for n in all_nodes if "://" in n]))
    print(f"原始节点总数: {len(unique_nodes)}，开始快速过滤...")

    # 3. 过滤阶段：限制最大线程数，防止被 GitHub 判定为攻击
    valid_nodes = []
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(check_node, unique_nodes))
        valid_nodes = [r for r in results if r]

    print(f"过滤完成！存活节点: {len(valid_nodes)}")

    # 4. 写入文件
    if valid_nodes:
        final_b64 = base64.b64encode("\n".join(valid_nodes).encode()).decode()
        with open("sub.txt", "w") as f:
            f.write(final_b64)
    else:
        # 如果全部失败，至少创建一个空文件防止 Actions 报错
        with open("sub.txt", "w") as f:
            f.write("")

if __name__ == "__main__":
    main()
