from PySide6.QtWidgets import (QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout, 
                              QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
                              QMenuBar, QMenu, QTabWidget, QScrollArea, QFrame, QApplication,
                              QListWidget, QListWidgetItem, QCheckBox, QSizePolicy)  # 添加QSizePolicy

from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QIcon, QKeySequence, QShortcut, QTextCursor

class WindowManagerQt(QMainWindow):
    word_changed = Signal(str)
    sentence_changed = Signal(str)
    log_signal = Signal(str)

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.word_list_window = None
        self.max_history_lines = 1000
        self._init_ui()
        self._setup_signals()

    def _init_ui(self):
        # 主窗口配置
        self.setWindowTitle("📚 单词管理工具 Qt版 v1.0")
        # 获取屏幕尺寸并计算右上角位置
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        window_width = 300
        window_height = 400
        x_pos = screen_geometry.width() - window_width - 20  # 右边距20像素
        self.setGeometry(x_pos, 20, window_width, window_height)  # 上边距20像素
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # 中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 创建菜单
        self._create_menu_bar()
        
        # 输入区域
        input_group = QWidget()
        input_layout = QGridLayout(input_group)
        input_layout.setContentsMargins(10, 10, 10, 10)
        
        self.word_input = QLineEdit()
        self.sentence_input = QLineEdit()
        
        input_layout.addWidget(QLabel("📖 单词："), 0, 0)
        input_layout.addWidget(self.word_input, 0, 1)
        input_layout.addWidget(QLabel("📝 句子："), 1, 0)
        input_layout.addWidget(self.sentence_input, 1, 1)
        
        main_layout.addWidget(input_group)

        # 按钮区域
        btn_group = QWidget()
        btn_layout = QGridLayout(btn_group)
        btn_layout.setContentsMargins(5, 5, 5, 5)
        
        self.add_word_btn = QPushButton("📥 添加单词")
        self.query_btn = QPushButton("🤖 模型查词")
        self.save_btn = QPushButton("💾 保存记录")
        self.exit_btn = QPushButton("❌ 保存退出")
        
        btn_layout.addWidget(self.add_word_btn, 0, 0)
        btn_layout.addWidget(self.query_btn, 0, 1)
        btn_layout.addWidget(self.save_btn, 1, 0)
        btn_layout.addWidget(self.exit_btn, 1, 1)
        
        main_layout.addWidget(btn_group)

        # 控制台
        self.console = QTextEdit()
        self.console.setReadOnly(True)
        self.console.setMinimumHeight(150)
        main_layout.addWidget(self.console)

        # 应用样式
        self._apply_styles()

    def _create_menu_bar(self):
        menu_bar = QMenuBar()
        settings_menu = menu_bar.addMenu("菜单")
        
        settings_action = QAction("设置", self)
        settings_action.triggered.connect(self.show_settings_dialog)
        settings_menu.addAction(settings_action)
        
        word_list_action = QAction("单词列表", self)
        word_list_action.triggered.connect(self.show_word_list)
        settings_menu.addAction(word_list_action)
        
        self.setMenuBar(menu_bar)

    def _setup_signals(self):
        self.word_input.returnPressed.connect(self.app.on_word_entry_enter)
        self.sentence_input.returnPressed.connect(self.app.on_sentence_entry_enter)
        self.add_word_btn.clicked.connect(self.app.add_word)
        self.query_btn.clicked.connect(self.app.model_query)
        self.save_btn.clicked.connect(self.app.save_record)
        self.exit_btn.clicked.connect(self.app.exit)
        self.log_signal.connect(self._update_log)
        
        # 初始化显示热键配置
        self.show_hotkeys_and_prompt()

    def show_hotkeys_and_prompt(self):
        """显示当前热键和提示信息"""
        hotkey_info = f"""
当前热键配置：
- 提取单词: {self.app.config['hotkeys']['get_word_hotkey']}
- 提取句子: {self.app.config['hotkeys']['get_sentence_hotkey']}
- 添加数据: {self.app.config['hotkeys']['add_data']}

当前Prompt提示词：
{self.app.config['prompt'].get('default', '')}
"""
        self.console.setPlainText(hotkey_info)
        self.console.moveCursor(QTextCursor.End)

    def _apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
                font-family: "微软雅黑";
            }
            QLineEdit, QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                font-size: 8pt;
            }
            QPushButton {
                background-color: #2d7ff2;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #45a7ff;
            }
        """)

    @Slot(str)
    def _update_log(self, message):
        self.console.moveCursor(QTextCursor.End)
        self.console.insertPlainText(f"{message}\n")
        
        # 保持历史记录行数限制
        line_count = self.console.document().lineCount()
        if line_count > self.max_history_lines:
            cursor = self.console.textCursor()
            cursor.movePosition(QTextCursor.Start)
            cursor.select(QTextCursor.LineUnderCursor)
            for _ in range(line_count - self.max_history_lines):
                cursor.deleteChar()

    def show_word_list(self):
        if not self.word_list_window:
            self.word_list_window = WordListWindow(self)
        self.word_list_window._load_data()  # 总是先刷新数据
        self.word_list_window.show()       # 再显示窗口

    def show_settings_dialog(self):
        dialog = SettingsDialog(self.app, self)
        dialog.exec()

class SettingsDialog(QDialog):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setWindowTitle("设置")
        self.resize(400, 600)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 输入字段
        self.output_name_edit = QLineEdit()
        self.api_key_edit = QLineEdit()
        self.word_hotkey_edit = QLineEdit()
        self.sentence_hotkey_edit = QLineEdit()
        self.add_data_hotkey_edit = QLineEdit()
        self.prompt_edit = QTextEdit()
        
        form_layout = QGridLayout()
        form_layout.addWidget(QLabel("文件名称"), 0, 0)
        form_layout.addWidget(self.output_name_edit, 0, 1)
        form_layout.addWidget(QLabel("API Key"), 1, 0)
        form_layout.addWidget(self.api_key_edit, 1, 1)
        form_layout.addWidget(QLabel("提取单词"), 2, 0)
        form_layout.addWidget(self.word_hotkey_edit, 2, 1)
        form_layout.addWidget(QLabel("提取句子"), 3, 0)
        form_layout.addWidget(self.sentence_hotkey_edit, 3, 1)
        form_layout.addWidget(QLabel("添加数据"), 4, 0)
        form_layout.addWidget(self.add_data_hotkey_edit, 4, 1)
        
        layout.addLayout(form_layout)
        layout.addWidget(QLabel("Prompt"))
        layout.addWidget(self.prompt_edit)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        
        save_btn.clicked.connect(self.save_settings)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        # 加载当前配置
        self._load_settings()

    def save_settings(self):
        """保存配置到文件"""
        try:
            # 更新配置对象
            self.app.config["file"]["output_name"] = self.output_name_edit.text()
            self.app.config["api"]["api_key"] = self.api_key_edit.text()
            self.app.config["hotkeys"]["get_word_hotkey"] = self.word_hotkey_edit.text()
            self.app.config["hotkeys"]["get_sentence_hotkey"] = self.sentence_hotkey_edit.text()
            self.app.config["hotkeys"]["add_data"] = self.add_data_hotkey_edit.text()
            self.app.config["prompt"]["default"] = self.prompt_edit.toPlainText()
            
            
            # 更新热键
            self.app.reset_hotkey(
                self.app.config["hotkeys"]["get_word_hotkey"], 
                self.word_hotkey_edit.text(),
                self.app.capture_word
            )
            self.app.reset_hotkey(
                self.app.config["hotkeys"]["get_sentence_hotkey"], 
                self.sentence_hotkey_edit.text(),
                self.app.capture_sentence
            )
            
            # 写入配置文件
            with open('config.ini', 'w', encoding='utf-8') as f:
                self.app.config.write(f)
                
            self.app.window_manager.log_signal.emit("配置已成功保存")
            self.accept()
            
        except Exception as e:
            self.app.window_manager.log_signal.emit(f"保存配置失败: {str(e)}")

    def _load_settings(self):
        config = self.app.config
        self.output_name_edit.setText(config["file"]["output_name"])
        self.api_key_edit.setText(config["api"]["api_key"])
        self.word_hotkey_edit.setText(config["hotkeys"]["get_word_hotkey"])
        self.sentence_hotkey_edit.setText(config["hotkeys"]["get_sentence_hotkey"])
        self.add_data_hotkey_edit.setText(config["hotkeys"]["add_data"])
        self.prompt_edit.setPlainText(config["prompt"].get("default", ""))

class WordListWindow(QDialog):
    def __init__(self, app, parent=None):
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                font-size: 8pt;
            }
            QLabel {
                margin-left: 10px;
                font-size: 8pt;  # 新增字体大小设置
            }
            QCheckBox {
                margin: 5px;
            }
            QLabel {
                margin-left: 10px;
                /* 缺少明确的字体大小设置 */
            }
        """)

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.setWindowTitle("单词列表")
        self.resize(600, 600)  # 增加窗口高度
        self.app = app  # 直接接收app引用
        self._init_ui()
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                font-size: 8pt;
            }
            QCheckBox {
                margin: 1px;
                        
            }
            QLabel {
                margin-left: 5px;
               min-height: 10px;
            }
        """)

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        # 列表控件
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.list_widget.setMinimumHeight(500)
        self.list_widget.setMinimumWidth(550)  # 增加最小宽度
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 设置尺寸策略
        layout.addWidget(self.list_widget)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.delete_btn = QPushButton("🗑️ 删除选中")
        self.refresh_btn = QPushButton("🔄 刷新列表")
        
        self.delete_btn.clicked.connect(self._delete_selected_items)
        self.refresh_btn.clicked.connect(self._load_data)
        
        btn_layout.addWidget(self.delete_btn)
        btn_layout.addWidget(self.refresh_btn)
        layout.addLayout(btn_layout)
        
        self._load_data()

    def _load_data(self):
        """加载数据到列表"""
        self.list_widget.clear()
        for idx, item in enumerate(self.app.app.data):
            list_item = QListWidgetItem()
            widget = QWidget()
            item_layout = QHBoxLayout(widget)
            
            # 复选框
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  # 新增：垂直方向扩展
            
            # 显示内容
            content = QLabel(f"{idx+1}. 单词: {item['单词']}\n   例句: {item['例句']}")
            content.setWordWrap(True)
            content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 新增：双向扩展
            
            item_layout.addWidget(checkbox)
            item_layout.addSpacing(20)
            item_layout.addWidget(content)
            widget.setLayout(item_layout)
            
            # 设置列表项的最小高度
            list_item.setSizeHint(QSize(0, 60))  # 新增：设置列表项最小高度为60像素
            
            self.list_widget.addItem(list_item)
            self.list_widget.setItemWidget(list_item, widget)

        # 新增：确保列表控件自动调整大小
        self.list_widget.setSizeAdjustPolicy(QListWidget.AdjustToContents)

    def _delete_selected_items(self):
        """删除选中项"""
        selected_indices = []
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            widget = self.list_widget.itemWidget(item)
            checkbox = widget.findChild(QCheckBox)
            if checkbox.isChecked():
                selected_indices.append(i)
        
        # 反向删除避免索引错乱
        if selected_indices:
            # 调用主程序的删除方法
            for idx in reversed(sorted(selected_indices)):
                self.app.app.delete_word(idx)
            
            # 保存更改并刷新界面
            self.app.app.save_record(append_mode=False)
            self._load_data()
            self.app.window_manager.log_signal.emit(f"成功删除 {len(selected_indices)} 条记录")
        else:
            self.app.window_manager.log_signal.emit("请先选择要删除的条目")
