import keyboard



class HotkeyManager:
    def __init__(self, app):
        self.app = app


    def setup_hotkeys(self):
        """配置全局热键"""
        self.hotkeys = {
            self.app.config["hotkeys"]["get_word_hotkey"]: self.app.capture_word,
            self.app.config["hotkeys"]["get_sentence_hotkey"]: self.app.capture_sentence,
            self.app.config["hotkeys"]["add_data"]: self.app.add_word
        }
        for hotkey, callback in self.hotkeys.items():
            keyboard.add_hotkey(hotkey, callback, suppress=True)
        print("程序已启动，使用 Ctrl+C 捕获单词 | Ctrl+S 捕获句子 | Ctrl+D 添加单词")

    def remove_hotkeys(self):
        """移除所有热键"""
        for hotkey in self.hotkeys.keys():
            keyboard.remove_hotkey(hotkey)

    def change_hotkey(self,old_hotkey, new_hotkey, callback):
        """更改热键"""
        keyboard.remove_hotkey(old_hotkey)
        keyboard.add_hotkey(new_hotkey, callback, suppress=True)