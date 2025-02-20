import json

from jinja2 import Environment, FileSystemLoader
import os
import tkinter as tk
from tkinter import filedialog
from markdown_parser import parse_markdown_to_json

def select_file():
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    file_path = filedialog.askopenfilename(filetypes=[("Markdown files", "*.md")])
    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()
            result = parse_markdown_to_json(markdown_content)
            return result
        except Exception as e:
            print(f"处理文件时出现错误: {e}")
    else:
        print("未选择文件。")
    return None

if __name__ == "__main__":
    resume_data = select_file()
    if resume_data:
        json_output = json.dumps(resume_data, indent=4, ensure_ascii=False)
        print(json_output)

# 设置Jinja2环境
env = Environment(loader=FileSystemLoader('.'))
template = env.get_template('模板1.html')

#生成HTML
output_html = template.render(resume_data)

# 保存结果
with open('resume.html', 'w', encoding='utf-8') as f:
    f.write(output_html)

print("简历已生成：resume.html")
