import sys
from PyQt5.QtWidgets import QApplication, QWidget
from ui2 import Ui_Form  # 请将此行替换为实际UI文件路径


class MyAppWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # 添加外部qss样式文件
        self.load_style("ui.qss")

    # 加载外部qss样式文件
    def load_style(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyAppWindow()
    window.show()
    sys.exit(app.exec_())
