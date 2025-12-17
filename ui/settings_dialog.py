from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QFileDialog,
    QGroupBox, QFormLayout
)
from PySide6.QtCore import Qt, Signal


class SettingsDialog(QDialog):
    """设置对话框"""

    # 设置保存信号
    settings_saved = Signal(dict)

    def __init__(self, parent=None, current_settings=None):
        super().__init__(parent)
        self.current_settings = current_settings or {}
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        self.setWindowTitle("设置")
        self.setFixedSize(400, 350)

        layout = QVBoxLayout(self)

        # ===== 宠物设置 =====
        pet_group = QGroupBox("宠物设置")
        pet_layout = QFormLayout()

        # 宠物名字
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("给宠物起个名字")
        pet_layout.addRow("宠物名字:", self.name_input)

        # 宠物图片
        image_layout = QHBoxLayout()
        self.image_path = QLineEdit()
        self.image_path.setReadOnly(True)
        self.image_path.setPlaceholderText("选择宠物图片")
        self.image_btn = QPushButton("浏览...")
        self.image_btn.clicked.connect(self.select_image)
        image_layout.addWidget(self.image_path)
        image_layout.addWidget(self.image_btn)
        pet_layout.addRow("宠物图片:", image_layout)

        pet_group.setLayout(pet_layout)
        layout.addWidget(pet_group)

        # ===== LLM 设置 =====
        llm_group = QGroupBox("大模型设置")
        llm_layout = QFormLayout()

        # 模型选择
        self.model_combo = QLineEdit()
        self.model_combo.setPlaceholderText("选择模型")
        llm_layout.addRow("模型:", self.model_combo)

        # API URL
        self.api_url_input = QLineEdit()
        self.api_url_input.setPlaceholderText("输入url")
        llm_layout.addRow("API URL:", self.api_url_input)

        # API Key
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("输入 API Key")
        llm_layout.addRow("API Key:", self.api_key_input)

        llm_group.setLayout(llm_layout)
        layout.addWidget(llm_group)

        # ===== 按钮 =====
        btn_layout = QHBoxLayout()

        self.save_btn = QPushButton("保存")
        self.save_btn.clicked.connect(self.save_settings)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def select_image(self):
        """选择图片文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "选择宠物图片",
            "",
            "图片文件 (*.png *.jpg *.gif)"
        )
        if file_path:
            self.image_path.setText(file_path)

    def load_settings(self):
        """加载当前设置"""
        if self.current_settings:
            self.name_input.setText(self.current_settings.get("pet_name", ""))
            self.image_path.setText(self.current_settings.get("pet_image", ""))
            self.model_combo.setText(self.current_settings.get("model", ""))
            self.api_url_input.setText(self.current_settings.get("api_url", ""))
            self.api_key_input.setText(self.current_settings.get("api_key", ""))

    def save_settings(self):
        """保存设置"""
        settings = {
            "pet_name": self.name_input.text(),
            "pet_image": self.image_path.text(),
            "model": self.model_combo.text(),
            "api_url": self.api_url_input.text(),
            "api_key": self.api_key_input.text()
        }
        self.settings_saved.emit(settings)
        self.accept()

    def get_settings(self):
        """获取设置"""
        return {
            "pet_name": self.name_input.text(),
            "pet_image": self.image_path.text(),
            "model": self.model_combo.text(),
            "api_url": self.api_url_input.text(),
            "api_key": self.api_key_input.text()
        }