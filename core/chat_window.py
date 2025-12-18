from PySide6.QtWidgets import QWidget, QVBoxLayout, QTextEdit,QLineEdit, QPushButton, QHBoxLayout,QSizeGrip
from PySide6.QtCore import Qt
from core.llm_service import LLMService

class ChatBubble(QWidget):
    """气泡对话框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_pet = parent  # 宠物窗口引用
        self.resizing = False  # 是否正在调整大小
        self.resize_edge = 10  # 边缘检测范围
        self.llm = None
        self.init_ui()

    def init_ui(self):
        # 无边框 + 置顶 + 透明背景
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool  # 不在任务栏显示
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMinimumSize(250, 150)
        self.setMaximumSize(600, 500)
        self.resize(300, 200)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)

        # 聊天记录显示区
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setPlaceholderText("和宠物聊天吧...")
        self.chat_display.setStyleSheet("""
            QTextEdit {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid #ccc;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
            }
        """)

        # 输入区域
        input_layout = QHBoxLayout()

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("输入消息...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #ccc;
                border-radius: 5px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        self.input_field.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("发送")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.send_btn.clicked.connect(self.send_message)

        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)

        layout.addWidget(self.chat_display)
        layout.addLayout(input_layout)

        self.size_grip = QSizeGrip(self)
        self.size_grip.setFixedSize(16, 16)

    def resizeEvent(self, event):
        """窗口大小改变时，更新把手位置"""
        super().resizeEvent(event)
        self.size_grip.move(
            self.width() - self.size_grip.width(),
            self.height() - self.size_grip.height()
        )

    def send_message(self):
        """发送消息"""
        text = self.input_field.text().strip()
        if not text:
            return

        self.chat_display.append(f"你: {text}")
        self.input_field.clear()

        reply = self.llm.chat(text)

        pet_name = "宠物"
        if self.parent_pet and hasattr(self.parent_pet, 'settings'):
            pet_name = self.parent_pet.settings.get("pet_name", "宠物")

        self.chat_display.append(f"{pet_name}: {reply}")

    def show_near_pet(self):
        """显示在宠物旁边"""
        if self.parent_pet:
            pet_pos = self.parent_pet.pos()
            pet_size = self.parent_pet.size()
            # 显示在宠物上方
            x = pet_pos.x() + pet_size.width() // 2 - self.width() // 2
            y = pet_pos.y() - self.height() - 10
            self.move(x, y)
        self.show()
        self.input_field.setFocus()

    def is_on_edge(self, pos):
        """判断鼠标是否在边缘"""
        rect = self.rect()
        x, y = pos.x(), pos.y()

        on_right = rect.width() - x < self.resize_edge
        on_bottom = rect.height() - y < self.resize_edge

        return on_right or on_bottom, on_right, on_bottom

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            on_edge, on_right, on_bottom = self.is_on_edge(event.position().toPoint())
            if on_edge:
                self.resizing = True
                self.resize_start = event.globalPosition().toPoint()
                self.resize_origin = self.size()
            event.accept()

    def mouseMoveEvent(self, event):
        pos = event.position().toPoint()
        on_edge, on_right, on_bottom = self.is_on_edge(pos)

        # 更新鼠标样式
        if on_right and on_bottom:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        elif on_right:
            self.setCursor(Qt.CursorShape.SizeHorCursor)
        elif on_bottom:
            self.setCursor(Qt.CursorShape.SizeVerCursor)
        else:
            self.setCursor(Qt.CursorShape.ArrowCursor)

        # 调整大小
        if self.resizing:
            delta = event.globalPosition().toPoint() - self.resize_start
            new_width = self.resize_origin.width() + delta.x()
            new_height = self.resize_origin.height() + delta.y()
            self.resize(new_width, new_height)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.resizing = False
        event.accept()