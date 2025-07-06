from PySide6.QtWidgets import (QMainWindow, QWidget, QDialog, QVBoxLayout, QHBoxLayout, 
                              QGridLayout, QLabel, QLineEdit, QPushButton, QTextEdit,
                              QMenuBar,QApplication, QFileDialog,
                              QListWidget, QListWidgetItem, QCheckBox, QSizePolicy)  # 添加QSizePolicy

from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, Signal, Slot, QSize
from PySide6.QtGui import QTextCursor

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
        self.setWindowTitle("📚 单词管理工具 v2.0")
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
        self.path_setting_btn = QPushButton("📁 设置路径")
        
        btn_layout.addWidget(self.add_word_btn, 0, 0)
        btn_layout.addWidget(self.query_btn, 0, 1)
        btn_layout.addWidget(self.save_btn, 1, 0)
        btn_layout.addWidget(self.exit_btn, 1, 1)
        btn_layout.addWidget(self.path_setting_btn, 2, 0, 1, 2)  # 跨两列
        
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
        self.path_setting_btn.clicked.connect(self.show_path_setting_dialog)
        self.log_signal.connect(self._update_log)
        
        # 初始化显示热键配置
        self.show_hotkeys_and_prompt()
        
        # 检查必需字段
        required_keys = self.app.required_keys
        if '单词' not in required_keys or '例句' not in required_keys:
            warning = "警告: prompt中必须包含'单词'和'例句'字段！\n当前检测到的字段: {}".format(required_keys)
            self.log_signal.emit(warning)

    def show_hotkeys_and_prompt(self):
        """显示当前热键配置"""
        hotkey_info = f"""
当前热键配置：
- 提取单词: {self.app.config['hotkeys']['get_word_hotkey']}
- 提取句子: {self.app.config['hotkeys']['get_sentence_hotkey']}
- 添加数据: {self.app.config['hotkeys']['add_data']}
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
    
    def show_path_setting_dialog(self):
        """显示路径设置对话框"""
        from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QMessageBox
        
        dialog = QDialog(self)
        dialog.setWindowTitle("设置存储路径")
        dialog.setFixedSize(500, 150)
        
        layout = QVBoxLayout(dialog)
        
        # 当前路径显示
        current_path = self.app.config["file"].get("absolute_path", "")
        path_layout = QHBoxLayout()
        path_label = QLabel("当前路径:")
        path_display = QLineEdit(current_path)
        path_display.setReadOnly(True)
        browse_btn = QPushButton("浏览...")
        
        path_layout.addWidget(path_label)
        path_layout.addWidget(path_display)
        path_layout.addWidget(browse_btn)
        
        # 按钮区域
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(path_layout)
        layout.addLayout(btn_layout)
        
        def browse_path():
            selected_path = QFileDialog.getExistingDirectory(dialog, "选择存储路径", current_path)
            if selected_path:
                path_display.setText(selected_path)
        
        def save_path():
            new_path = path_display.text().strip()
            if new_path:
                try:
                    # 更新配置
                    self.app.config["file"]["absolute_path"] = new_path
                    
                    # 更新应用中的临时文件路径
                    import os
                    self.app.temp_file = os.path.join(new_path, "temp_words.csv")
                    self.app.file_operation = self.app.QueryFileOperation(self.app.temp_file)
                    
                    # 保存配置到文件
                    with open(self.app.config_file, 'w', encoding='utf-8') as f:
                        self.app.config.write(f)
                    
                    self.log_signal.emit(f"路径已更新为: {new_path}")
                    QMessageBox.information(dialog, "成功", "路径设置已保存！")
                    dialog.accept()
                except Exception as e:
                    QMessageBox.warning(dialog, "错误", f"保存路径失败: {str(e)}")
            else:
                QMessageBox.warning(dialog, "警告", "请选择一个有效的路径！")
        
        browse_btn.clicked.connect(browse_path)
        save_btn.clicked.connect(save_path)
        cancel_btn.clicked.connect(dialog.reject)
        
        dialog.exec()

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
        
        # 路径设置相关
        self.path_display = QLineEdit()
        self.path_display.setReadOnly(True)
        self.path_btn = QPushButton("选择路径")
        
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
        
        # 路径设置行
        form_layout.addWidget(QLabel("存储路径"), 5, 0)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.path_display)
        path_layout.addWidget(self.path_btn)
        path_widget = QWidget()
        path_widget.setLayout(path_layout)
        form_layout.addWidget(path_widget, 5, 1)
        
        # 连接路径选择按钮
        self.path_btn.clicked.connect(self.select_path)
        
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
    
    def select_path(self):
        """选择存储路径"""
        current_path = self.path_display.text() or self.app.config["file"].get("absolute_path", "")
        selected_path = QFileDialog.getExistingDirectory(
            self, 
            "选择存储路径", 
            current_path
        )
        if selected_path:
            self.path_display.setText(selected_path)
            self.app.window_manager.log_signal.emit(f"已选择路径: {selected_path}")

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
            
            # 更新路径配置
            new_path = self.path_display.text().strip()
            if new_path:
                self.app.config["file"]["absolute_path"] = new_path
                # 更新应用中的临时文件路径
                import os
                self.app.temp_file = os.path.join(new_path, "temp_words.csv")
                self.app.file_operation = self.app.QueryFileOperation(self.app.temp_file)
            
            
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
        
        # 加载路径配置
        current_path = config["file"].get("absolute_path", "")
        self.path_display.setText(current_path)

class WordListWindow(QDialog):
    def __init__(self, main_window, parent=None):
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

    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.setWindowTitle("单词列表")
        self.resize(600, 600)
        self.main_window = main_window
        self._init_ui()
        # 统一设置样式
        self.setStyleSheet("""
            QListWidget {
                border: 1px solid #ddd;
                font-size: 8pt;
            }
            QCheckBox {
                margin: 5px;
            }
            QLabel {
                margin-left: 10px;
                font-size: 8pt;
                min-height: 20px;
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
        word_list = self.main_window.app.get_temp_data()
        for idx, item in enumerate(word_list):
            list_item = QListWidgetItem()
            widget = QWidget()
            item_layout = QHBoxLayout(widget)
            
            # 复选框
            checkbox = QCheckBox()
            checkbox.setChecked(False)
            checkbox.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)  # 新增：垂直方向扩展
            
            # 显示内容
            content = QLabel(f"{idx+1}. 单词: {item['单词']}  例句: {item['例句']}")
            content.setWordWrap(True)
            content.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # 新增：双向扩展
            
            item_layout.addWidget(checkbox)
            item_layout.addSpacing(20)
            item_layout.addWidget(content)
            widget.setLayout(item_layout)
            
            # 设置列表项的最小高度
            list_item.setSizeHint(QSize(0, 80))  # 新增：设置列表项最小高度为60像素
            
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
            # 去读临时文件
            word_list = self.main_window.app.get_temp_data()
            # 直接删除数据并保存到临时文件
            for idx in reversed(sorted(selected_indices)):
                if 0 <= idx < len(word_list):
                    del word_list[idx]
            
            self.main_window.app.cover_temp_data(word_list)  # 强制保存到临时文件
            self._load_data()
            self.main_window.app.window_manager.log_signal.emit(f"已删除{len(selected_indices)}条记录并更新临时文件")
        else:
            self.main_window.app.window_manager.log_signal.emit("请先选择要删除的条目")
