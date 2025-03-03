import logging
import os
import json
import tkinter as tk
from threading import Thread
from tkinter import filedialog

from jinja2 import Environment, FileSystemLoader

from module.mk_to_json import parse_markdown_file_to_json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('resume_builder.log'), logging.StreamHandler()]
)


class ResumeBuilderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Markdown简历生成器")
        self.root.geometry("800x400")

        # 创建状态栏
        self.status_bar = tk.Label(root, text="就绪", bd=1, relief=tk.SUNKEN, anchor=tk.SE)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # 创建主框架
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 输入文件部分
        self.input_frame = tk.Frame(main_frame)
        self.input_frame.pack(fill=tk.X)

        tk.Label(self.input_frame, text="输入文件:").pack(side=tk.LEFT)

        # 使用StringVar来绑定Entry
        self.input_var = tk.StringVar()
        self.input_entry = tk.Entry(self.input_frame, textvariable=self.input_var, width=60)
        self.input_entry.pack(side=tk.LEFT, fill=tk.X)

        self.browse_input = tk.Button(self.input_frame, text="浏览", command=self.select_input_file)
        self.browse_input.pack(side=tk.LEFT)  # 修正这里：变量名应小写's'

        # 模板文件部分
        self.template_frame = tk.Frame(main_frame)
        self.template_frame.pack(fill=tk.X, pady=10)

        tk.Label(self.template_frame, text="模板文件:").pack(side=tk.LEFT)
        self.template_var = tk.StringVar()
        self.template_entry = tk.Entry(self.template_frame, textvariable=self.template_var, width=60)
        self.template_entry.pack(side=tk.LEFT, fill=tk.X)

        self.browse_template = tk.Button(self.template_frame, text="浏览", command=lambda: self.select_file("template"))
        self.browse_template.pack(side=tk.LEFT)

        # 操作按钮
        self.process_button = tk.Button(main_frame, text="生成HTML", command=self.process_files)
        self.process_button.pack(pady=20)

    def generate_html(self, template_path, data):
        """使用Jinja2模板生成HTML内容"""
        try:
            # 创建模板加载器
            env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))

            # 获取模板对象
            template = env.get_template(os.path.basename(template_path))

            # 渲染模板
            html_content = template.render(data)

            return html_content
        except Exception as e:
            # 记录错误日志
            logging.error(f"生成HTML时出错: {e}", exc_info=True)
            # 抛出异常以便上层处理
            raise RuntimeError(f"生成HTML失败: {str(e)}) from e")

    def select_input_file(self):
        """选择输入文件"""
        path = filedialog.askopenfilename(
            initialdir='.',
            filetypes=[("Markdown files", "*.md")]
        )
        if path:
            self.input_var.set(path)  # 使用StringVar的set方法
            self.status_bar.config(text=f"输入文件: {os.path.basename(path)}")

    def select_file(self, category):
        """通用文件选择方法"""
        if category == "template":
            initial_dir = os.path.join(os.path.dirname(__file__), 'templates')
            file_types = [("HTML files", "*.html")]
        else:
            initial_dir = '.'
            file_types = [("Markdown files", "*.md")]

        path = filedialog.askopenfilename(
            initialdir=initial_dir,
            filetypes=file_types
        )
        if path:
            if category == "template":
                self.template_var.set(path)
            else:
                self.input_var.set(path)
            self.status_bar.config(text=f"{category}文件: {os.path.basename(path)}")

    def process_files(self):
        """处理文件生成流程"""
        input_path = self.input_var.get()  # 使用StringVar的get方法
        template_path = self.template_var.get()

        # 简单验证
        if not input_path or not template_path:
            self.status_bar.config(text="请选择输入文件和模板文件", fg="red")
            return

        self.status_bar.config(text="正在处理...", fg="blue")
        self.process_button.config(state=tk.DISABLED)

        # 使用线程防止界面冻结
        thread = Thread(target=self._process, args=(input_path, template_path))
        thread.start()

    def _process(self, input_path, template_path):
        try:
            # 解析Markdown文件
            resume_data = ''
            try:
                with open(input_path, 'r', encoding='utf-8') as file:
                    markdown_content = file.read()
                resume_data = parse_markdown_file_to_json(markdown_content)
                if resume_data:
                    print(json.dumps(resume_data, ensure_ascii=False, indent=4))
                else:
                    print("解析失败")
                # 测试，是否提取信息
                # print(resume_data, end='\n')
            except Exception as e:
                print(f"处理文件时出现错误:{e}")

            # 数据完整性验证
            required_fields = ['name', 'job_intention', 'personal_info', 'education', 'skills', 'certificates']
            for field in required_fields:
                if field not in resume_data:
                    raise ValueError(f"缺失必要字段: {field}")

            # 打印调试信息（生产环境请删除）
            logging.debug(f"解析后的数据: {json.dumps(resume_data, indent=2)}")

            # 生成HTML内容
            html_content = self.generate_html(template_path, resume_data)

            # 保存HTML文件
            save_path = filedialog.asksaveasfilename(
                defaultextension='.html',
                filetypes=[("HTML files", "*.html")]
            )
            if save_path:
                with open(save_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                logging.info(f"HTML文件已保存至: {save_path}")
                self.status_bar.config(text=f"生成完成: {save_path}", fg="green")
            else:
                self.status_bar.config(text="保存取消", fg="orange")
        except Exception as e:
            logging.error(f"处理文件时出错: {e}", exc_info=True)
            self.status_bar.config(text=f"错误: {str(e)}", fg="red")
        finally:
            self.process_button.config(state=tk.NORMAL)


def main():
    root = tk.Tk()
    app = ResumeBuilderGUI(root)
    root.mainloop()
    quit()


if __name__ == "__main__":
    main()
