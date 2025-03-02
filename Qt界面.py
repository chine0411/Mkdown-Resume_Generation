import os
import sys
import logging
import json
from jinja2 import Environment, FileSystemLoader
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QDesktopServices
from PyQt5 import QtWidgets, QtCore, QtGui, QtWebEngineWidgets
from ui2 import Ui_Form
from mk_p import parse_markdown_to_json
from threading import Thread


# 自定义日志处理器，用于将日志消息发送到 GUI
class LogHandler(logging.Handler):
    def __init__(self, signal):
        super().__init__()
        self.signal = signal

    def emit(self, record):
        msg = self.format(record)
        self.signal.emit(msg)  # 通过信号将日志发送到主线程


class MyAppWindow(QWidget):
    log_signal = pyqtSignal(str)  # 日志信号
    finished = pyqtSignal(str)  # 处理完成信号

    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  # 创建 UI 对象
        self.ui.setupUi(self)  # 设置 UI
        self.setup_logging()  # 初始化日志系统
        self.templates_file()  # 调用函数加载模板文件
        self.template_path = None
        self.input_path = None
        self.output_path = None

        # 添加外部qss样式文件
        self.load_style("ui.qss")
        # 信号与槽连接
        self.ui.Button_mk.clicked.connect(self.select_input_file)
        self.ui.comboBox_tem.currentIndexChanged.connect(self.on_combobox_changed)
        self.ui.Button_html.clicked.connect(self.process_files)
        self.log_signal.connect(self.ui.log_text.append)  # 将日志信号连接到 UI
        self.ui.Button_op.clicked.connect(self.opne_file)
        self.ui.Button_see.clicked.connect(self.preview_html_file)

    # 加载外部qss样式文件
    def load_style(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    # 选择md文件
    def select_input_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "Markdown Files (*.md);;All Files (*)",
            options=options
        )
        if file_path:
            logging.info(f"文件选择成功：{file_path}")
            self.ui.mk_flie.setText(f"文件路径: {file_path}")
            self.input_path = file_path
        else:
            logging.info(f"用户取消了文件选择")

    # 选择模板文件
    def templates_file(self):
        template_folder = "templates"  # 模板文件夹路径
        if not os.path.exists(template_folder):
            self.ui.comboBox_tem.clear()
            self.ui.comboBox_tem.addItem("模板文件夹不存在")
            logging.warning("模板文件夹不存在")
            return

        files = os.listdir(template_folder)  # 获取文件夹中的文件
        html_files = [file for file in files if file.endswith(".html")]  # 筛选 HTML 文件
        self.ui.comboBox_tem.clear()  # 清空当前的选项
        self.ui.comboBox_tem.addItems(html_files)  # 将文件名添加到 QComboBox 中
        if not html_files:  # 如果没有找到 HTML 文件
            self.ui.comboBox_tem.addItem("没有找到 HTML 文件")
            logging.warning("没有找到模板文件，请检查 templates 目录")
        else:
            logging.info("模板文件加载完成")

    def on_combobox_changed(self, index):
        template_file = self.ui.comboBox_tem.currentText()
        logging.info(f"用户选择了模板：{template_file}")
        self.template_path = os.path.join("templates", template_file)  # 使用完整路径

    def process_files(self):
        if not self.input_path or not self.template_path:
            QMessageBox.warning(self, "错误", "请选择输入文件和模板文件")
            return

        # 提前获取保存路径
        save_path, _ = QFileDialog.getSaveFileName(self, "保存 HTML 文件", "", "HTML files (*.html)")
        if not save_path:
            QMessageBox.warning(self, "错误", "未选择保存路径")
            return

        # 启动线程处理文件
        thread = Thread(target=self._process, args=(self.input_path, self.template_path, save_path))
        thread.start()

    def _process(self, input_path, template_path, save_path):
        try:
            # 解析 Markdown 文件
            with open(input_path, 'r', encoding='utf-8') as file:
                markdown_content = file.read()
            resume_data = parse_markdown_to_json(markdown_content)

            # 数据完整性验证
            required_fields = ['name', 'job_intention', 'personal_info', 'education', 'skills', 'certificates']
            for field in required_fields:
                if field not in resume_data:
                    raise ValueError(f"缺失必要字段: {field}")

            # 生成 HTML 内容
            html_content = self.generate_html(template_path, resume_data)

            # 保存 HTML 文件
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logging.info(f"HTML 文件已保存至: {save_path}")
            self.finished.emit(f"生成完成: {save_path}")
            self.output_path = save_path
        except Exception as e:
            logging.error(f"处理文件时出错: {e}", exc_info=True)
            self.finished.emit(f"错误: {str(e)}")

    def generate_html(self, template_path, data):
        try:
            env = Environment(loader=FileSystemLoader(os.path.dirname(template_path)))
            template = env.get_template(os.path.basename(template_path))
            html_content = template.render(data)
            return html_content
        except Exception as e:
            logging.error(f"生成HTML时出错: {e}", exc_info=True)
            raise RuntimeError(f"生成HTML失败: {str(e)}")

    def opne_file(self):
        # 获取当前选择的文件路径
        print(self.output_path)
        if self.output_path and os.path.exists(self.output_path):
            # 获取文件所在目录
            dir_path = os.path.dirname(self.output_path)
            # 使用 QDesktopServices 打开资源管理器
            QDesktopServices.openUrl(QUrl.fromLocalFile(dir_path))

    def preview_html_file(self):
        """预览 HTML 文件"""
        if self.output_path:
            self.ui.webview_2.load(QUrl.fromLocalFile(self.output_path))  # 加载本地 HTML 文件
        else:
            QtWidgets.QMessageBox.warning(self, "警告", "请先选择一个 HTML 文件！")

    def setup_logging(self):
        log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
        file_handler.setFormatter(log_format)

        gui_handler = LogHandler(self.log_signal)
        gui_handler.setFormatter(log_format)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
        logger.addHandler(gui_handler)

        logger.info("日志系统已启动！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyAppWindow()
    window.show()
    sys.exit(app.exec_())