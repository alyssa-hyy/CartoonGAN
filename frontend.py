import sys
import os
import requests
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QPushButton, QLabel, QFileDialog, QMessageBox, QProgressDialog, QSplitter, QAction, QStatusBar
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal

# 自定义支持拖拽的 QLabel
class DragDropLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                if os.path.splitext(url.toLocalFile())[1].lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            file_path = event.mimeData().urls()[0].toLocalFile()
            if os.path.splitext(file_path)[1].lower() in ['.png', '.jpg', '.jpeg', '.bmp']:
                self.setPixmap(QPixmap(file_path).scaled(self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                # 调用父级窗口的方法更新上传图片路径
                self.parent().parent().set_uploaded_image(file_path)
                event.acceptProposedAction()
            else:
                event.ignore()
        else:
            event.ignore()

# 定义后台处理线程，避免阻塞 UI
class ProcessWorker(QThread):
    # finished_signal: status_code, response_content, error_message
    finished_signal = pyqtSignal(int, bytes, str)

    def __init__(self, file_path, url):
        super().__init__()
        self.file_path = file_path
        self.url = url

    def run(self):
        try:
            with open(self.file_path, "rb") as f:
                files = {"file": f}
                response = requests.post(self.url, files=files)
            self.finished_signal.emit(response.status_code, response.content, "")
        except Exception as e:
            self.finished_signal.emit(0, b"", str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("图像处理前端")
        self.setGeometry(100, 100, 1100, 750)

        # 用于存储上传的图片路径和后端返回的图片数据
        self.input_image_path = None
        self.processed_image_data = None

        self.init_ui()

    def init_ui(self):
        # 菜单栏
        menubar = self.menuBar()
        file_menu = menubar.addMenu("菜单栏")
        open_action = QAction("打开图片", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.upload_image)
        file_menu.addAction(open_action)
        save_action = QAction("保存图片", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)
        file_menu.addSeparator()
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 标题
        title_label = QLabel("图像卡通化")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        # 按钮布局：左右伸缩使按钮居中
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        button_layout.addStretch(1)

        self.upload_btn = QPushButton("上传图片")
        self.upload_btn.setToolTip("点击上传图片或拖拽图片到左侧区域")
        self.upload_btn.setStyleSheet(
            "background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 14px;"
        )
        self.upload_btn.clicked.connect(self.upload_image)
        button_layout.addWidget(self.upload_btn)

        self.delete_btn = QPushButton("删除上传图片")
        self.delete_btn.setToolTip("删除当前上传的图片")
        self.delete_btn.setStyleSheet(
            "background-color: #f44336; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 14px;"
        )
        self.delete_btn.clicked.connect(self.delete_uploaded_image)
        button_layout.addWidget(self.delete_btn)

        self.process_btn = QPushButton("处理图片")
        self.process_btn.setToolTip("发送图片到后端处理")
        self.process_btn.setStyleSheet(
            "background-color: #2196F3; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 14px;"
        )
        self.process_btn.clicked.connect(self.process_image)
        button_layout.addWidget(self.process_btn)

        self.save_btn = QPushButton("保存图片")
        self.save_btn.setToolTip("保存处理后的图片到本地")
        self.save_btn.setStyleSheet(
            "background-color: #FF9800; color: white; padding: 10px 20px; border: none; border-radius: 5px; font-size: 14px;"
        )
        self.save_btn.clicked.connect(self.save_image)
        button_layout.addWidget(self.save_btn)

        button_layout.addStretch(1)
        main_layout.addLayout(button_layout)

        # 使用 QSplitter 实现左右图片区域可调节大小
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        main_layout.addWidget(splitter)

        # 左侧：用户上传图片区域（支持拖拽）
        input_group = QGroupBox("用户上传图片")
        input_group.setStyleSheet(
            "QGroupBox { font-size: 16px; font-weight: bold; border: 1px solid #aaa; border-radius: 5px; margin-top: 10px; }"
        )
        input_layout = QVBoxLayout()
        input_group.setLayout(input_layout)
        self.input_label = DragDropLabel("请上传图片")
        self.input_label.setFixedSize(500, 550)
        self.input_label.setAlignment(Qt.AlignCenter)
        self.input_label.setStyleSheet("border: 2px dashed #aaa;")
        input_layout.addWidget(self.input_label)
        splitter.addWidget(input_group)

        # 右侧：后端处理后图片展示区域
        output_group = QGroupBox("处理后图片")
        output_group.setStyleSheet(
            "QGroupBox { font-size: 16px; font-weight: bold; border: 1px solid #aaa; border-radius: 5px; margin-top: 10px; }"
        )
        output_layout = QVBoxLayout()
        output_group.setLayout(output_layout)
        self.output_label = QLabel("处理后的图片将显示在此")
        self.output_label.setFixedSize(500, 550)
        self.output_label.setAlignment(Qt.AlignCenter)
        self.output_label.setStyleSheet("border: 2px dashed #aaa;")
        output_layout.addWidget(self.output_label)
        splitter.addWidget(output_group)

        splitter.setSizes([550, 550])

    def set_uploaded_image(self, file_path):
        """供拖拽时设置上传的图片路径，并更新状态栏"""
        self.input_image_path = file_path
        self.statusBar.showMessage("图片已上传: " + file_path, 3000)

    def upload_image(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_name:
            self.input_image_path = file_name
            pixmap = QPixmap(file_name)
            self.input_label.setPixmap(
                pixmap.scaled(self.input_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.statusBar.showMessage("图片已上传: " + file_name, 3000)

    def delete_uploaded_image(self):
        if self.input_image_path:
            self.input_image_path = None
            self.input_label.clear()
            self.input_label.setText("请上传图片")
            self.statusBar.showMessage("已删除上传的图片", 3000)
        else:
            QMessageBox.information(self, "提示", "当前没有上传的图片可供删除。")

    def process_image(self):
        if not self.input_image_path:
            QMessageBox.warning(self, "警告", "请先上传图片！")
            return

        self.statusBar.showMessage("正在处理图片，请稍候...", 0)
        self.process_btn.setEnabled(False)

        # 显示进度对话框
        progress = QProgressDialog("正在处理图片，请稍候...", "取消", 0, 0, self)
        progress.setWindowTitle("请稍候")
        progress.setWindowModality(Qt.WindowModal)
        progress.setCancelButton(None)
        progress.show()

        # 创建后台线程处理请求
        self.worker = ProcessWorker(self.input_image_path, "http://localhost:5000/process")
        self.worker.finished_signal.connect(lambda status, content, error: self.on_process_finished(status, content, error, progress))
        self.worker.start()

    def on_process_finished(self, status, content, error, progress_dialog):
        progress_dialog.close()
        self.process_btn.setEnabled(True)
        if status == 200:
            self.processed_image_data = content
            pixmap = QPixmap()
            pixmap.loadFromData(self.processed_image_data)
            self.output_label.setPixmap(
                pixmap.scaled(self.output_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            )
            self.statusBar.showMessage("处理完成", 3000)
        else:
            msg = f"处理图片失败，状态码: {status}" if status else f"发生异常：{error}"
            QMessageBox.warning(self, "错误", msg)
            self.statusBar.showMessage(msg, 3000)

    def save_image(self):
        if not self.processed_image_data:
            QMessageBox.warning(self, "警告", "没有处理后的图片可供保存！")
            return

        save_path, _ = QFileDialog.getSaveFileName(self, "保存图片", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if save_path:
            try:
                with open(save_path, "wb") as f:
                    f.write(self.processed_image_data)
                self.statusBar.showMessage("图片已成功保存！", 3000)
                QMessageBox.information(self, "保存成功", "图片已成功保存！")
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存图片失败：{str(e)}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
