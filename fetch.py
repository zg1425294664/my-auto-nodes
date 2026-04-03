import requests
import base64
import re

# 混合多种类型的源：包含 GitHub、GitLab 和独立页面
urls = [
    # 核心源 1：vpei (经典)
    "https://raw.githubusercontent.com/vpei/free/master/v2ray",
    # 核心源 2：freefq (高频)
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    # 核心源 3：非 GitHub 源 (用来防 GitHub 抽风)
    "https://gitlab.com/free54188/v2ray-free/-/raw/master/v2",
    # 核心源 4：另一个聚合源
    "https://raw.githubusercontent.com/anaer/Sub/master/nodes.txt",
    # 核心源 5：一些爬虫汇总
    "https://raw.githubusercontent.com/tubaile/free/main/v2"
]

def main():
    all_nodes = []
    print("--- 开始抓取阶段 ---")
    
    for url in urls:
        try:
            # 增加 User-Agent 伪装成浏览器
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(url, headers=headers, timeout=15)
            
            if r.status_code == 200:
                content = r.text.strip()
                if not content:
                    continue
                
                # 判断是否是 Base64 编码
                # 简单逻辑：如果不包含协议头 "://" 且字符较多，尝试解码
                if "://" not in content[:50]:
                    try:
                        # 自动补齐 Base64 填充
                        missing_padding = len(content) % 4
                        if missing_padding:
                            content += '=' * (4 - missing_padding)
                        decoded = base64.b64decode(content).decode('utf-8', 'ignore')
                        lines = decoded.splitlines()
                    except:
                        lines = content.splitlines()
                else:
                    lines = content.splitlines()
                
                # 提取包含协议头的行
                for line in lines:
                    line = line.strip()
                    if "://" in line:
                        all_nodes.append(line)
                print(f"源 {url} 抓取成功，当前累计节点: {len(all_nodes)}")
        except Exception as e:
            print(f"源 {url} 请求失败: {e}")

    # 去重
    unique_nodes = list(set(all_nodes))
    print(f"--- 抓取结束，共计去重节点: {len(unique_nodes)} ---")

    # 最终处理
    if unique_nodes:
        # 将所有节点合并，并进行标准的 Base64 编码
        final_str = "\n".join(unique_nodes)
        final_b64 = base64.b64encode(final_str.encode('utf-8')).decode('utf-8')
        
        with open("sub.txt", "w") as f:
            f.write(final_b64)
        print("写入 sub.txt 成功！")
    else:
        # 如果真的一个都没抓到，写入一个提示（防止 v2rayN 报错）
        # 这里塞一个过期的假节点，至少让软件能识别出格式
        print("警告：未抓取到任何节点！")
        with open("sub.txt", "w") as f:
            f.write("")

if __name__ == "__main__":
    main()
