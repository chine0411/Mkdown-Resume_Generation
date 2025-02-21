import json
import os
import logging
from tkinter import filedialog, messagebox
from jinja2 import Environment, FileSystemLoader
from mk_p import parse_markdown_to_json
import argparse

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('resume_builder.log'), logging.StreamHandler()]
)


def get_file_path(initial_dir='.'):
    """显示文件选择对话框并返回选中的文件路径"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    file_path = filedialog.askopenfilename(
        initialdir=initial_dir,
        filetypes=[("Markdown files", "*.md")]
    )

    if not file_path:
        logging.warning("未选择任何文件")
        return None

    return file_path


def process_markdown(file_path):
    """解析Markdown文件并转换为JSON数据"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        data = parse_markdown_to_json(content)
        logging.info(f"成功解析文件: {file_path}")
        return data
    except Exception as e:
        logging.error(f"解析文件时出错: {e}", exc_info=True)
        raise


def generate_html(template_path, data):
    """使用Jinja2模板生成HTML内容"""
    try:
        env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
        template = env.get_template(os.path.basename(template_path))
        html = template.render(data)
        return html
    except Exception as e:
        logging.error(f"生成HTML时出错: {e}", exc_info=True)
        raise


def save_html(html_content):
    """保存生成的HTML文件"""
    save_path = filedialog.asksaveasfilename(
        defaultextension='.html',
        filetypes=[("HTML files", "*.html")]
    )

    if not save_path:
        logging.warning("未选择保存位置")
        return False

    try:
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logging.info(f"HTML文件已保存至: {save_path}")
        return True
    except Exception as e:
        logging.error(f"保存HTML文件时出错: {e}", exc_info=True)
        raise


def main():
    # 处理命令行参数
    parser = argparse.ArgumentParser(description="Markdown简历生成器")
    parser.add_argument('-i', '--input', help='输入Markdown文件路径')
    parser.add_argument('-t', '--template', help='Jinja2模板路径')
    args = parser.parse_args()

    input_path = args.input if args.input else None
    template_path = args.template if args.template else 'template/模板1.html'

    # 选择输入文件
    if input_path is None:
        input_path = get_file_path()

    if not input_path:
        messagebox.showerror("错误", "没有选择有效的输入文件")
        return

    # 解析Markdown文件
    try:
        resume_data = process_markdown(input_path)
    except Exception as e:
        messagebox.showerror("解析错误", f"无法解析文件: {str(e)}")
        return

    # 生成HTML内容
    try:
        html_content = generate_html(template_path, resume_data)
    except Exception as e:
        messagebox.showerror("生成错误", f"无法生成HTML文件: {str(e)}")
        return

    # 保存HTML文件
    if not save_html(html_content):
        return

    # 显示完成提示
    messagebox.showinfo("完成", "简历已成功生成！")


if __name__ == "__main__":
    main()
