from PySide6.QtWidgets import QWidget, QLabel, QApplication, QMenu, QSystemTrayIcon
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPixmap, QAction, QIcon
from core.chat_window import ChatBubble
from ui.settings_dialog import SettingsDialog
from core.config_manager import load_config, save_config
from core.subtitle_window import SubtitleWindow

class PetWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.drag_position = QPoint()
        self.chat_bubble = None
        self.subtitle = None  # 字幕窗口
        self.use_subtitle = True  # 是否使用字幕模式
        self.use_subtitle_mode = True  # False=对话框模式, True=字幕模式
        from core.llm_service import LLMService
        self.llm = LLMService()
        self.settings = {
            "pet_name": "gmds",
            "pet_image": "assets/images/idle/default.png",
            "model": "",
            "api_url": "",
            "api_key": ""
        } | load_config()
        self.init_ui()
        self.init_tray()


    """------界面------"""

    """主窗口"""
    def init_ui(self):
        #设置窗口尺寸
        self.resize(200,200)

        #设置窗口：无边框+置顶
        self.setWindowFlags(
            Qt.FramelessWindowHint |  # 无边框
            Qt.WindowStaysOnTopHint  # 窗口置顶
        )

        #背景透明
        self.setAttribute(Qt.WA_TranslucentBackground)

        #创建label显示图片
        self.image_label = QLabel(self)

        #加载图片
        picture = QPixmap("assets/images/idle/gmds.png")
        self.image_label.setPixmap(picture)

        #根据图片大小调整窗口
        self.resize(picture.size())

    """------移动------"""

    """记录按下鼠标位置"""
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.pos()
            event.accept()

    """移动拖拽"""

    def mouseMoveEvent(self, event):
        """鼠标移动：拖拽窗口"""
        if event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.update_chat_position()

            # 更新字幕位置
            if self.subtitle and self.subtitle.isVisible():
                self.subtitle.update_position()

        event.accept()

    """对话框移动跟随"""
    def update_chat_position(self):
        """更新气泡框位置"""
        if self.chat_bubble and self.chat_bubble.isVisible():
            pet_pos = self.pos()
            pet_size = self.size()
            x = pet_pos.x() + pet_size.width() // 2 - self.chat_bubble.width() // 2
            y = pet_pos.y() - self.chat_bubble.height() - 10
            self.chat_bubble.move(x, y)

    """结束拖拽"""
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            event.accept()

    """------宠物菜单栏------"""

    """右键菜单栏"""
    def contextMenuEvent(self, event):
        #右键菜单
        menu = QMenu(self)

        #添加菜单项
        action_chat = QAction("对话",self)
        action_mode = QAction("切换字幕模式" if not self.use_subtitle_mode else "切换对话框模式", self)
        action_hide = QAction("隐藏",self)
        action_quit = QAction("退出",self)

        #绑定事件
        action_chat.triggered.connect(self.open_chat)
        action_mode.triggered.connect(self.toggle_chat_mode)
        action_hide.triggered.connect(self.hide)
        action_quit.triggered.connect(QApplication.quit)

        #添加到菜单
        menu.addAction(action_chat)
        menu.addAction(action_mode)
        menu.addAction(action_hide)
        menu.addSeparator()     #分隔线
        menu.addAction(action_quit)

        #显示菜单
        menu.exec_(event.globalPos())

    def toggle_chat_mode(self):
        """切换对话模式"""
        # 隐藏当前模式的窗口
        if self.chat_bubble and self.chat_bubble.isVisible():
            self.chat_bubble.hide()
        if self.subtitle and self.subtitle.isVisible():
            self.subtitle.hide()

        # 切换模式
        self.use_subtitle_mode = not self.use_subtitle_mode

        # 自动打开新模式的对话
        self.open_chat()

        mode_name = "字幕模式" if self.use_subtitle_mode else "对话框模式"
        print(f"已切换到{mode_name}")

    """对话功能"""
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.open_chat()
            event.accept()

    def open_chat(self):
        """打开对话（根据模式选择对话框或字幕）"""
        # 更新 LLM 配置
        self.llm.set_config(
            api_key=self.settings.get("api_key", ""),
            base_url=self.settings.get("api_url", ""),
            model=self.settings.get("model", "")
        )
        if self.use_subtitle_mode:
            # 字幕模式
            if self.subtitle is None:
                self.subtitle = SubtitleWindow(self)
                self.subtitle.message_sent.connect(self.handle_subtitle_message)

            if self.subtitle.isVisible():
                self.subtitle.hide()
            else:
                self.subtitle.show_input()
        else:
            # 对话框模式
            if self.chat_bubble is None:
                self.chat_bubble = ChatBubble(self)
                self.chat_bubble.llm = self.llm  # 使用统一的 LLM

            if self.chat_bubble.isVisible():
                self.chat_bubble.hide()
            else:
                self.chat_bubble.show_near_pet()

    def handle_subtitle_message(self, text):
        """处理字幕模式的消息"""
        self.llm.set_config(
            api_key=self.settings.get("api_key", ""),
            base_url=self.settings.get("api_url", ""),
            model=self.settings.get("model", "")
        )

        reply = self.llm.chat(text)
        self.subtitle.show_subtitle(reply)

        # 确保对话框存在，再同步记录
        if self.chat_bubble is None:
            self.chat_bubble = ChatBubble(self)
            self.chat_bubble.llm = self.llm
        
        pet_name = self.settings.get("pet_name", "宠物")
        self.chat_bubble.chat_display.append(f"你: {text}")
        self.chat_bubble.chat_display.append(f"{pet_name}: {reply}")

    """------系统托盘------"""

    """系统托盘"""
    def init_tray(self):
        #托盘图标
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon("assets/icons/gmds_icons.png"))
        self.tray_icon.setToolTip("桌面宠物")

        #托盘菜单
        tray_menu = QMenu()
        action_show = QAction("显示宠物",self)
        action_hide = QAction("隐藏宠物",self)
        action_quit = QAction("退出",self)
        action_settings = QAction("设置",self)

        action_show.triggered.connect(self.show_pet)
        action_settings.triggered.connect(self.open_settings)
        action_hide.triggered.connect(self.hide)
        action_quit.triggered.connect(QApplication.quit)

        tray_menu.addAction(action_show)
        tray_menu.addAction(action_hide)
        tray_menu.addAction(action_settings)
        tray_menu.addSeparator()
        tray_menu.addAction(action_quit)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_activated)
        self.tray_icon.show()

    """显示桌面宠物"""
    def show_pet(self):
        self.show()
        self.activateWindow()

    """托盘图标被点击"""
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:  # 单击
            if self.isVisible():
                self.hide()
            else:
                self.show_pet()

    """设置功能"""
    def open_settings(self):
        """打开设置界面"""
        dialog = SettingsDialog(self, self.settings)
        dialog.settings_saved.connect(self.apply_settings)
        dialog.exec()

    def apply_settings(self, new_settings):
        """应用新设置"""
        self.settings = new_settings
        save_config(new_settings)
        # 更新宠物图片
        if new_settings.get("pet_image"):
            pixmap = QPixmap(new_settings["pet_image"])
            self.image_label.setPixmap(pixmap)
            self.resize(pixmap.size())

        # 更新气泡框的 LLM 配置
        if self.chat_bubble:
            self.chat_bubble.llm.set_config(
                api_key=new_settings.get("api_key", ""),
                base_url=new_settings.get("api_url", ""),
                model=new_settings.get("model", "")
            )

        # 更新托盘提示
        self.tray_icon.setToolTip(new_settings.get("pet_name", "桌面宠物"))

        print(f"设置已保存: {new_settings}")

    def show_subtitle(self, text):
        """显示字幕"""
        if self.subtitle is None:
            self.subtitle = SubtitleWindow(self)
        self.subtitle.show_subtitle(text, interval=2000)