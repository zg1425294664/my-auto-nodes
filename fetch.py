import requests
import base64
import re

# 改进后的源（这些源目前相对活跃，建议经常更换）
urls = [
    "https://raw.githubusercontent.com/vpei/free/master/v2ray",
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/aiboboxx/v2rayfree/main/v2",
    "https://raw.githubusercontent.com/Leon406/SubCrawler/main/sub/share/all",
    "https://raw.githubusercontent.com/anaer/Sub/master/nodes.txt"
]
def main():
    combined_list = []
    for url in urls:
        try:
            print(f"正在抓取: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # 1. 尝试 Base64 解码获取原始链接
                raw_text = response.text.strip()
                try:
                    # 补充可能缺失的补丁符号
                    missing_padding = len(raw_text) % 4
                    if missing_padding:
                        raw_text += '=' * (4 - missing_padding)
                    decoded = base64.b64decode(raw_text).decode('utf-8')
                    # 2. 按行分割并清理
                    nodes = decoded.splitlines()
                    for node in nodes:
                        if node.strip(): # 只保留非空行
                            combined_list.append(node.strip())
                except:
                    # 如果本身不是 Base64 编码，则直接按行处理
                    nodes = raw_text.splitlines()
                    for node in nodes:
                        if "://" in node: # 只保留包含协议头的行
                            combined_list.append(node.strip())
        except Exception as e:
            print(f"抓取失败: {e}")

    # 3. 去重
    unique_nodes = list(set(combined_list))
    print(f"总计有效节点数: {len(unique_nodes)}")

    # 4. 重新组合并进行 Base64 编码输出
    if unique_nodes:
        final_text = "\n".join(unique_nodes)
        final_b64 = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w") as f:
            f.write(final_b64)
    else:
        print("未抓取到任何有效节点")

if __name__ == "__main__":
    main()
