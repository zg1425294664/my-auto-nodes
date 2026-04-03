import requests
import base64

# 这里是公开的节点源列表，你可以根据需要增删
urls = [
    "https://raw.githubusercontent.com/freefq/free/master/v2",
    "https://raw.githubusercontent.com/ssrsub/ssr/master/ssrsub",
    "https://raw.githubusercontent.com/Pawdroid/Free-V2ray-Nodes/master/v2ray.txt"
]

def main():
    combined_content = ""
    for url in urls:
        try:
            # 爬取网页内容
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 尝试解码 Base64（大多数订阅源都是 base64 编码的）
                decoded_data = base64.b64decode(response.text).decode('utf-8')
                combined_content += decoded_data + "\n"
                print(f"成功抓取: {url}")
        except Exception as e:
            print(f"抓取失败 {url}: {e}")

    if combined_content:
        # 将合并后的内容重新进行 Base64 编码，生成标准的订阅格式
        final_b64 = base64.b64encode(combined_content.encode('utf-8')).decode('utf-8')
        with open("sub.txt", "w") as f:
            f.write(final_b64)
        print("订阅文件 sub.txt 已更新")

if __name__ == "__main__":
    main()
