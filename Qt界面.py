import sys
import logging
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtCore import Qt
from ui2 import Ui_Form


# 自定义日志处理器，用于将日志消息发送到 GUI
class LogHandler(logging.Handler):
    def __init__(self, text_edit):
        # 初始化父类
        super().__init__()
        # 将日志消息发送到的文本框
        self.text_edit = text_edit

    def emit(self, record):
        # 将日志记录格式化为字符串
        msg = self.format(record)
        # 将日志消息追加到文本框中
        self.text_edit.append(msg)


class MyAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()  # 创建 UI 对象
        self.ui.setupUi(self)  # 设置 UI
        self.setup_logging()  # 初始化日志系统

        # 添加外部qss样式文件
        self.load_style("ui.qss")
        # 信号与槽连接
        self.ui.Button_mk.clicked.connect(self.select_input_file)

    # 加载外部qss样式文件
    def load_style(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def select_input_file(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择文件",
            "",
            "All Files (*);;Python Files (*.py)",
            options=options
        )

        # 更新标签显示路径
        if file_path:
            logging.info(f"文件选择成功：{file_path}")
            self.ui.mk_flie.setText(f"文件路径: {file_path}")
        else:
            logging.info(f"用户取消了文件选择")

        # 设置日志系统的函数

    def setup_logging(self):
        # 配置日志格式
        log_format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        # 创建文件日志处理器，将日志保存到 app.log 文件
        file_handler = logging.FileHandler("app.log", mode="a", encoding="utf-8")
        # 设置文件日志处理器的格式
        file_handler.setFormatter(log_format)

        # 创建自定义日志处理器，将日志发送到 GUI
        gui_handler = LogHandler(self.ui.log_text)
        # 设置自定义日志处理器的格式
        gui_handler.setFormatter(log_format)

        # 获取根日志器
        logger = logging.getLogger()
        # 设置日志级别为 DEBUG
        logger.setLevel(logging.DEBUG)
        # 添加文件日志处理器到根日志器
        logger.addHandler(file_handler)
        # 添加自定义日志处理器到根日志器
        logger.addHandler(gui_handler)

        # 测试日志消息
        logger.info("日志系统已启动！")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyAppWindow()
    window.show()
    sys.exit(app.exec_())
