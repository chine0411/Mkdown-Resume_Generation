from PyQt5 import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QDesktopServices


class AboutWindow(QWidget):
    """关于界面"""
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("关于")
        self.resize(400, 300)  # 设置窗口大小
        self.center()  # 调用方法使窗口居中

        layout = QVBoxLayout()

        # 添加项目介绍部分
        intro_label = self.create_intro_label()
        layout.addWidget(intro_label)

        # 按钮区域
        button_layout = QHBoxLayout()

        # 新手教程按钮
        tutorial_button = QPushButton("新手教程")
        tutorial_button.clicked.connect(self.open_tutorial)
        tutorial_button.setStyleSheet("font-size: 14px; padding: 8px;")
        button_layout.addWidget(tutorial_button)

        # 我是老手按钮
        expert_button = QPushButton("我是老手")
        expert_button.clicked.connect(self.go_to_main)
        expert_button.setStyleSheet("font-size: 14px; padding: 8px;")
        button_layout.addWidget(expert_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

        # 设置窗口背景颜色
        self.setStyleSheet("background-color: #f5f5f5;")

    def create_intro_label(self):
        """创建项目介绍的 QLabel"""
        intro_text = """
        <html>
        <body style="font-family: 'Microsoft YaHei', sans-serif; font-size: 14px; color: #333; text-align: left; padding: 20px;">
            <h3 style="color: #4CAF50; font-size: 18px; text-align: center;">Markdown 简历生成器</h3>
            <p><strong>开发者：</strong><a href="https://github.com/chine0411" style="color: #007BFF; text-decoration: none;">姜秋郁</a></p>
            <p><strong>开源地址：</strong>
            <a href="https://github.com/chine0411/Mkdown-Resume_Generation" style="color: #007BFF; text-decoration: none;">Github</a></p>
            <a href="https://gitee.com/yuxin_wurenhui/Mkdown-Resume_Generation" style="color: #007BFF; text-decoration: none;">Gitee</a></p>
            <p><strong>项目简介：</strong><br>
            这是一个基于 PyQt5 的桌面应用程序，用于将 Markdown 文件转换为 HTML 格式的简历。它支持 Markdown 文件解析、模板渲染、日志记录和 PDF 导出等功能。</p>
            <p><strong>使用方法：</strong><br>
            1. 点击“选择文件”按钮，选择包含简历内容的 Markdown 文件。<br>
            2. 从下拉菜单中选择一个 HTML 模板。<br>
            3. 点击“生成 HTML”按钮，选择保存路径后生成 HTML 文件。<br>
            4. 支持预览生成的 HTML 文件，并可将其导出为 PDF。</p>
        </body>
        </html>
        """
        intro_label = QLabel(intro_text)
        intro_label.setWordWrap(True)  # 允许自动换行
        intro_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)  # 文本靠左对齐
        intro_label.setStyleSheet("padding: 20px;")
        intro_label.setOpenExternalLinks(True)  # 允许 QLabel 打开超链接
        return intro_label

    def center(self):
        """使窗口在屏幕上下左右居中，并稍微往上调整"""
        qr = self.frameGeometry()  # 获取窗口的几何形状
        cp = QDesktopWidget().availableGeometry().center()  # 获取屏幕中心点
        qr.moveCenter(cp)  # 将窗口的中心点移动到屏幕中心点

        # 调整窗口的垂直位置，使其稍微往上移动
        qr.moveTop(qr.top() - 150)  # 例如往上移动 50 像素

        self.move(qr.topLeft())  # 移动窗口到计算后的位置

    def open_tutorial(self):
        """打开新手教程（B站账号）"""
        QDesktopServices.openUrl(QUrl("https://space.bilibili.com/673605760?spm_id_from=333.1007.0.0"))

    def go_to_main(self):
        """进入主程序"""
        self.close()  # 关闭当前窗口
        self.main_window.show()  # 显示主窗口