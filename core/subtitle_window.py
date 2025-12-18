import re
import random
from PySide6.QtCore import Qt, QTimer, Signal, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QHBoxLayout, QGraphicsOpacityEffect
from PySide6.QtGui import QFont


class SubtitleLabel(QWidget):
    """字幕标签（独立窗口）"""

    def __init__(self, parent=None):
        super().__init__(None)
        self.parent_pet = parent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel {
                background: rgba(0, 0, 0, 100);
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 5px 10px;
                border-radius: 8px;
            }
        """)
        self.label.setFont(QFont("Comic Sans MS", 12))
        self.label.setMaximumWidth(400)

        # 透明度效果
        self.opacity_effect = QGraphicsOpacityEffect(self.label)
        self.label.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)

        # 淡入动画
        self.fade_in = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_in.setDuration(300)
        self.fade_in.setStartValue(0.0)
        self.fade_in.setEndValue(1.0)
        self.fade_in.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # 淡出动画
        self.fade_out = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_out.setDuration(300)
        self.fade_out.setStartValue(1.0)
        self.fade_out.setEndValue(0.0)
        self.fade_out.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_out.finished.connect(self._do_hide)

    def _do_hide(self):
        """实际隐藏"""
        super().hide()

    def set_text(self, text):
        self.label.setText(text)
        self.label.adjustSize()
        self.resize(self.label.size())

    def show(self):
        super().show()
        self.fade_in.start()

    def hide(self):
        self.fade_out.start()


class SubtitleInput(QWidget):
    """字幕输入框（独立窗口）"""

    message_sent = Signal(str)

    def __init__(self, parent=None):
        super().__init__(None)  # 无父窗口，独立显示
        self.parent_pet = parent
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("说点什么...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 150);
                border: 1px solid rgba(200, 200, 200, 150);
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 12px;
            }
        """)
        self.input_field.setFixedWidth(150)
        self.input_field.returnPressed.connect(self.send_message)

        self.send_btn = QPushButton("→")
        self.send_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(76, 175, 80, 150);
                color: white;
                border: none;
                border-radius: 10px;
                padding: 5px 10px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: rgba(69, 160, 73, 180);
            }
        """)
        self.send_btn.setFixedSize(30, 25)
        self.send_btn.clicked.connect(self.send_message)

        layout.addWidget(self.input_field)
        layout.addWidget(self.send_btn)

    def send_message(self):
        text = self.input_field.text().strip()
        if text:
            self.input_field.clear()
            self.message_sent.emit(text)

    def focus_input(self):
        self.input_field.setFocus()


class SubtitleWindow:
    """字幕模式管理器"""

    def __init__(self, parent=None):
        self.parent_pet = parent
        self.subtitle_label = SubtitleLabel(parent)
        self.input_widget = SubtitleInput(parent)

        self.sentences = []
        self.current_index = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.show_next_sentence)

    @property
    def message_sent(self):
        return self.input_widget.message_sent

    def split_text(self, text):
        """按标点符号分割文本"""
        sentences = re.split(r'([，。！？,!?])', text)
        result = []
        temp = ""
        for part in sentences:
            if part in '，。！？,!?':
                temp += part
                if temp.strip():
                    result.append(temp.strip())
                temp = ""
            else:
                temp = part
        if temp.strip():
            result.append(temp.strip())
        return result

    def show_subtitle(self, text, interval=2500):
        """显示字幕"""
        self.sentences = self.split_text(text)
        self.current_index = 0

        if self.sentences:
            self.show_sentence(self.sentences[0])
            if len(self.sentences) > 1:
                self.timer.start(interval)

    def show_sentence(self, text):
        """显示单句字幕"""
        # 先淡出再显示新内容
        if self.subtitle_label.isVisible():
            self.subtitle_label.opacity_effect.setOpacity(0)

        self.subtitle_label.set_text(text)
        self.update_position()
        self.subtitle_label.show()  # 会自动触发淡入

    def show_next_sentence(self):
        """显示下一句"""
        self.current_index += 1
        if self.current_index < len(self.sentences):
            self.show_sentence(self.sentences[self.current_index])
        else:
            self.timer.stop()
            QTimer.singleShot(3000, self.subtitle_label.hide)

    def update_position(self):
        """更新位置"""
        if self.parent_pet:
            pet_pos = self.parent_pet.pos()
            pet_size = self.parent_pet.size()

            # 字幕在宠物右上角（加随机偏移）
            random_x = random.randint(-20, 30)  # 水平随机偏移
            random_y = random.randint(-30, 20)  # 垂直随机偏移

            self.subtitle_label.move(
                pet_pos.x() + pet_size.width() + 5 + random_x,
                pet_pos.y() + random_y
            )

            # 输入框在宠物下方居中（位置固定，不随机）
            input_x = pet_pos.x() + pet_size.width() // 2 - self.input_widget.width() // 2
            input_y = pet_pos.y() + pet_size.height() + 5
            self.input_widget.move(input_x, input_y)

    def show_input(self):
        """显示输入框"""
        self.input_widget.show()
        self.input_widget.adjustSize()  # 先调整大小
        self.update_position()  # 再更新位置
        self.input_widget.focus_input()

    def hide(self):
        """隐藏所有"""
        self.timer.stop()
        self.subtitle_label.hide()  # 淡出隐藏
        self.input_widget.hide()

    def isVisible(self):
        return self.input_widget.isVisible()

    def stop(self):
        """停止字幕"""
        self.timer.stop()
        self.subtitle_label.hide()  # 淡出隐藏