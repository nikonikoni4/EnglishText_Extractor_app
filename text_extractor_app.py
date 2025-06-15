# 优化导入语句
from pyexpat import model
from re import T
import sys
import time
import threading
import configparser
import win32clipboard
import keyboard
import pandas as pd
import os
from hotkey_manager import HotkeyManager
from window_manager_qt import WindowManagerQt
from model_api import ask_model 
class TextExtractorApp:
    def __init__(self):
        self.word = ""
        self.sentence = ""
        # self.data = []
        self.word_list = []
        self.data_lock = threading.Lock()  # 初始化线程锁
        self.config = self.load_config()
        self.required_keys = self.get_required_keys()
        self.temp_file = os.path.join(os.path.dirname(__file__), "temp_words.csv")
        self.file_operation = self.QueryFileOperation(self.temp_file)  # 初始化文件锁
        self.window_manager=WindowManagerQt(self)
        # 初始化管理器（延迟到QApplication创建后）
        self.window_manager = None
        self.hotkey_manager = HotkeyManager(self)

    class QueryFileOperation:
        def __init__(self, file_path, timeout=10, retry_interval=0.1):
            self.file_path = file_path
            self.lock_file = f"{file_path}.lock"
            self.timeout = timeout
            self.retry_interval = retry_interval
            self.fd = None
            
        def acquire(self):
            start_time = time.time()
            while True:
                try:
                    # Windows文件锁实现
                    self.fd = os.open(self.lock_file, os.O_CREAT|os.O_EXCL|os.O_RDWR)
                    return True
                except FileExistsError:
                    if time.time() - start_time > self.timeout:
                        return False
                    time.sleep(self.retry_interval)
                    
        def release(self):
            if self.fd:
                os.close(self.fd)
            if os.path.exists(self.lock_file):
                os.remove(self.lock_file)
            
        def __enter__(self):
            if self.acquire():
                return self
            raise TimeoutError(f"获取文件锁超时 ({self.timeout}s)")
            
        def __exit__(self, exc_type, exc_val, exc_tb):
            self.release()
        
        
    # 读取配置文件等相关操作
    def get_required_keys(self):
        """从配置中精确提取JSON字段列表"""
        import re
        try:
            # 合并所有prompt内容
            prompt_text = " ".join(self.config['prompt'].values())
            
            # 精确匹配关键指令段落
            match = re.search(r'json的key必须为([^。\n]+)', prompt_text, re.IGNORECASE)
            if not match:
                raise ValueError("配置中未找到'json的key必须为'关键指令")
            
            # 提取并清洗key列表
            key_instruction = match.group(1)
            keys = re.split(r'[:,，]+', key_instruction)  # 兼容中英文标点
            cleaned_keys = []
            for k in keys:
                # 多级清洗：去空白、去换行、去冒号
                key = k.strip().replace('\n', '').rstrip(':：').strip()
                if key and key not in cleaned_keys:
                    cleaned_keys.append(key)
            
            # 防御性检查必要字段
            required = ['单词', '例句']
            missing = [k for k in required if k not in cleaned_keys]
            # if missing:
            #     raise ValueError(f"配置缺少必要字段: {missing}，请检查prompt设置")
                
            return cleaned_keys
            
        except Exception as e:
            raise ValueError(f"解析配置失败: {str(e)}\n请确保配置包含'json的key必须为'指令并遵循格式要求")

    def load_config(self, config_path='config.ini'):
        """读取配置文件并返回配置对象"""
        import os
        # 检查当前目录
        if not os.path.exists(config_path):
            # 检查exe所在目录
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(exe_dir, config_path)
        
        config = configparser.ConfigParser()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config.read_file(f)
            return config
        except Exception as e:
            print(f"读取配置文件失败: {str(e)}")
            self.window_manager._update_log(f"读取配置文件失败: {str(e)}")
            return configparser.ConfigParser()  # 返回空配置对象

    def reset_hotkey(self, hotkey, new_hotkey, callback):
        """重置热键"""
        self.hotkey_manager.change_hotkey(hotkey, new_hotkey, callback)
        self.window_manager._update_log(f"热键已重置为 {new_hotkey}")
        print(f"热键已重置为 {new_hotkey}")  # 调试输出
        if callback==self.add_word :
            self.config.set('hotkeys', "add_data", new_hotkey)  # 更新配置文件
        elif callback == self.capture_word :
            self.config.set('hotkeys', "get_word_hotkey", new_hotkey)  # 更新配置文件
        elif callback == self.capture_sentence :
            self.config.set('hotkeys', "get_sentence_hotkey", new_hotkey)  # 更新配置文件

        with open('config.ini', 'w', encoding='utf-8') as f:  # 保存配置文件
            self.config.write(f)
        self.window_manager.show_hotkeys_and_prompt()

    def run(self):
        """启动程序"""
        # 确保在QApplication上下文中创建窗口
        self.window_manager = WindowManagerQt(self)
        threading.Thread(target=self.hotkey_manager.setup_hotkeys, daemon=True).start()
        self.window_manager.show()

    def get_clipboard_text(self):
        """剪贴板操作封装方法"""
        for _ in range(3):
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
                
                keyboard.send('ctrl+c')
                time.sleep(0.2)
                
                win32clipboard.OpenClipboard()
                text = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                
                if text.strip():
                    return text.strip()
            except Exception as e:
                print(f"剪贴板操作失败: {str(e)}")
                # self.window_manager._update_log(f"剪贴板操作失败: {str(e)}")
                time.sleep(0.1)
        self.window_manager._update_log("错误: 无法获取剪贴板内容")
        return None

    def capture_word(self):
        """捕获单词功能"""
        print(f"检测到{self.config['hotkeys']['get_word_hotkey']}组合键")
        self.window_manager._update_log(f"操作日志: 检测到{self.config['hotkeys']['get_word_hotkey']}组合键")
        time.sleep(0.1)
        self.word = self.get_clipboard_text()
        if self.word:
            self.window_manager.word_input.setText(self.word)
            self.window_manager.log_signal.emit(f"捕获单词: {self.word}")
        else:
            print("未检测到有效文本")
            self.window_manager._update_log("警告: 未检测到有效文本")

    def capture_sentence(self):
        """捕获句子功能"""
        print(f"检测到{self.config['hotkeys']['get_sentence_hotkey']}组合键")
        self.window_manager._update_log(f"操作日志: 检测到{self.config['hotkeys']['get_sentence_hotkey']}组合键")
        time.sleep(0.1)
        self.sentence = self.get_clipboard_text()
        if self.sentence:
            self.window_manager.sentence_input.setText(self.sentence)
            self.window_manager.log_signal.emit(f"捕获句子: {self.sentence}")
        else:
            print("未检测到有效文本")
            self.window_manager._update_log("警告: 未检测到有效句子")

    def load_config(self, config_path='config.ini'):
        """读取配置文件并返回配置对象"""
        import os
        # 检查当前目录
        if not os.path.exists(config_path):
            # 检查exe所在目录
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            config_path = os.path.join(exe_dir, config_path)
        
        config = configparser.ConfigParser()
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config.read_file(f)
            return config
        except Exception as e:
            self.window_manager._update_log(f"错误: 读取配置文件失败: {str(e)}")
            return configparser.ConfigParser()  # 返回空配置对象

    def get_temp_data(self)->list:
        """获得临时文件中的数据"""
        with self.file_operation:
            try:
                if os.path.exists(self.temp_file):
                    # 检查文件是否为空
                    if os.path.getsize(self.temp_file) == 0:
                        self.window_manager._update_log("临时文件为空，返回空列表")
                        return []
                    try:
                        df = pd.read_csv(self.temp_file)
                        return df.to_dict('records')
                    except pd.errors.EmptyDataError:
                        # 处理空文件情况
                        self.window_manager._update_log("临时文件为空数据，返回空列表")
                        return []
                    except Exception as e:
                        # 文件格式错误，删除并创建新文件
                        self.window_manager._update_log(f"临时文件格式错误，正在重置: {str(e)}")
                        os.remove(self.temp_file)
                        return []
                else:
                    return []
            except Exception as e:
                self.window_manager._update_log(f"同步临时文件失败: {str(e)}")
                return []

    def save_add_data(self,data:list):
        """将temp_data保存到临时文件,保存形式是追加和去重"""
        try:
            with self.file_operation:
                file_exists = os.path.exists(self.temp_file)
                df_temp = pd.DataFrame() # 读取临时文件
                df_data = pd.DataFrame(data) # 当前已添加的单词列表
                if file_exists:
                    try:
                        # 检查文件是否为空
                        if os.path.getsize(self.temp_file) == 0:
                            # 文件为空，直接写入新数据
                            pass
                        else:
                            df_temp = pd.read_csv(self.temp_file)
                            # 如果df_temp的单词中存在着与df_data相同的单词，则用df_data
                            df_data = pd.concat([df_data,df_temp],ignore_index=True)
                            # 保存已经查询过的数据
                            df_data = df_data.sort_values('query_flag', ascending=False)
                            df_data = df_data.drop_duplicates(subset=['单词'], keep='first')
                    except Exception as e:
                        self.window_manager._update_log(f"读取临时文件失败，将创建新文件: {str(e)}")
                        # 文件可能损坏，继续使用新数据
                df_data.to_csv(
                    self.temp_file,
                    header=True,
                    index=False
                )
        except TimeoutError:
            self.window_manager._update_log("错误: 获取文件锁超时，保存临时数据失败")
        except Exception as e:
            self.window_manager._update_log(f"保存临时文件失败: {str(e)}")
            print(f"保存临时文件失败: {str(e)}")
    def cover_temp_data(self,data:list):
        pd.DataFrame(data).to_csv(self.temp_file,mode='w',index=False,header=True)
    def del_query_data(self):
        """将temp_data保存到临时文件"""
        try:
            with self.file_operation:
                file_exists = os.path.exists(self.temp_file)
                if file_exists:
                    df_temp = pd.read_csv(self.temp_file)
                    df_temp.query('query_flag == 0').to_csv(self.temp_file,index=False,header=True)
               
        except TimeoutError:
            self.window_manager._update_log("错误: 获取文件锁超时，保存临时数据失败")
        except Exception as e:
            self.window_manager._update_log(f"保存临时文件失败: {str(e)}")
            print(f"保存临时文件失败: {str(e)}")
    def add_word(self):
        """添加单词功能"""
        print(f"检测到{self.config['hotkeys']['add_data']}组合键")
        self.window_manager._update_log(f"操作日志: 检测到{self.config['hotkeys']['add_data']}组合键")
        self.word = self.window_manager.word_input.text()
        self.sentence = self.window_manager.sentence_input.text()
        if self.word:
            data = {
                "单词": self.word,
                "例句": self.sentence,
                "query_flag": 0
            }
            # 补充其他必填字段
            for key in self.required_keys:
                if key not in data:
                    data[key] = ""
            self.save_add_data([data])  # 保存到临时文件
            
            self.window_manager.word_input.clear()
            self.window_manager.sentence_input.clear()

    def display_query_result(self, data_item):
        """显示查询结果"""
        keys = list(data_item.keys())
        values = list(data_item.values())
        
        display_info = "查询完成:\n"
        for key, value in zip(keys, values):
            display_info += f"{key}: {value}\n"
        
        self.window_manager._update_log(display_info)

    def model_query(self):
        """模型查词回调函数"""

        query_data = self.get_temp_data()  # 查询前同步最新数据
        # 获得未查询的单词
        query_data = [item for item in query_data if item.get("query_flag", 1) == 0]
        
        def disable_controls():
            """禁用控件"""
            # self.window_manager.log_signal.emit("禁用热键和控件")
            # 禁用按钮并设置灰色样式
            self.window_manager.save_btn.setEnabled(False)
            self.window_manager.save_btn.setStyleSheet("background-color: #cccccc; color: #666666;")
            self.window_manager.exit_btn.setEnabled(False)
            self.window_manager.exit_btn.setStyleSheet("background-color: #cccccc; color: #666666;")
            self.window_manager.query_btn.setEnabled(False)
            self.window_manager.query_btn.setStyleSheet("background-color: #cccccc; color: #666666;")
        def enable_controls():
            """启用控件"""
            # self.hotkey_manager.setup_hotkeys()
            # 启用按钮并恢复原样式
            self.window_manager.save_btn.setEnabled(True)
            self.window_manager.save_btn.setStyleSheet("")
            self.window_manager.exit_btn.setEnabled(True)
            self.window_manager.exit_btn.setStyleSheet("")
            self.window_manager.query_btn.setEnabled(True)
            self.window_manager.query_btn.setStyleSheet("")
            # self.window_manager.log_signal.emit("启用热键和控件")
        
        def query_task(query_data:list):

            try:
                disable_controls()
                api_key = self.config["api"]["api_key"]
                self.window_manager._update_log("开始模型查询...")
                for i in range(0,len(query_data)):
                    self.window_manager._update_log(f"查询单词: {query_data[i]['单词']}")
                    data = ask_model(api_key, word=query_data[i]["单词"], sentence=query_data[i]["例句"], config=self.config)
                    if data is None:
                        self.window_manager._update_log("api调用失败，检查：1.api_key是否正确，2.使用VPN可能会导致调用失败")
                        break
                    # 逐个更新键值而不是直接覆盖
                    for key in data:
                        query_data[i][key] = data[key]
                    query_data[i]["query_flag"] = 1  # 保持查询标志设置
                    self.window_manager.log_signal.emit(f"查询结果: {query_data[i]}")
                    
                self.save_add_data(query_data)  # 保存更新后的查询状态
                self.window_manager._update_log("模型查询完成")
            except Exception as e:
                error_message = f"查询错误: {str(e)}"
                self.window_manager.log_signal.emit(error_message)
            finally:
                enable_controls()
                # 设置查询完成标志
                self._query_complete = True

        if query_data:
            self._query_complete = False  # 新增：查询完成标志
            threading.Thread(target=query_task, args=(query_data,), daemon=True).start()
        else:
            self.window_manager.log_signal.emit(f"无有效查询数据")
            print(f"无有效查询数据")

    def exit(self):
        """查询按钮点击事件"""
        self.window_manager._update_log("操作日志: 正在保存数据...")
        
        # 启动查询
        # self.model_query()
        
        # 等待查询完成
        # while not getattr(self, '_query_complete', True):
        #     time.sleep(0.1)
        #     self.window_manager.repaint()  # 强制重绘界面保持响应
        
        # 保存数据
        self.save_record()
        self.window_manager._update_log("操作日志: 退出程序")
        self.del_query_data()  # 删除已经查询过的数据
        # 关闭窗口
        self.window_manager.close()



    def on_word_entry_enter(self):
        """单词输入框回车事件处理"""
        word = self.window_manager.word_input.text().strip()
        if word:
            self.word=word
            self.window_manager._update_log(f"已确认单词: {word}")
            self.window_manager.word_input.clearFocus()  # 移除输入框焦点
        else:
            self.window_manager._update_log("错误: 单词不能为空")

    def on_sentence_entry_enter(self):
        """句子输入框回车事件处理"""
        sentence = self.window_manager.sentence_input.text().strip()
        if sentence:
            self.sentence=sentence
            self.window_manager._update_log(f"已确认句子: {sentence}")
            self.window_manager.sentence_input.clearFocus()  # 移除输入框焦点
        else:
            self.window_manager._update_log("错误: 句子不能为空")

    def save_record(self):
        """保存记录到文件(支持追加模式)"""
        import pandas as pd
        temp_data = self.get_temp_data()  # 查询前同步最新数据
        # 保存所有查询完毕的单词
        save_data = [item for item in temp_data if item.get("query_flag", 0) == 1]
        if not save_data:
            self.window_manager._update_log("警告: 没有数据可保存")
            return
        
        try:
            csv_filename = self.config["file"]["output_name"] + ".csv"
            if os.path.exists(csv_filename):
                # 读取最终文件中的数据
                df = pd.read_csv(self.config["file"]["output_name"] + ".csv", encoding='utf-8-sig')
                # 合并数据
                df = pd.concat([df, pd.DataFrame(save_data)], ignore_index=True)
            else :
                df = pd.DataFrame(save_data)
            # 去重
            df = df.drop_duplicates(subset=['单词'], keep='first')
            # 保存
            df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
            self.window_manager._update_log(f"✓ 成功保存到 {os.path.abspath(csv_filename)}")
            

            


        # if not save_data:
        #     self.window_manager._update_log("警告: 没有数据可保存")
        #     return
    
        # try:
        #     # 使用pandas保存CSV
        #     csv_filename = self.config["file"]["output_name"] + ".csv"
        #     file_exists = os.path.exists(csv_filename)
            
        #     # 动态生成字段列表
        #     if file_exists:
        #         # 读取已有文件的列名
        #         existing_columns = pd.read_csv(csv_filename, nrows=0).columns.tolist()
        #         # 过滤数据只保留已有列
        #         filtered_data = []
        #         for item in save_data:
        #             filtered_item = {k: v for k, v in item.items() if k in existing_columns}
        #             filtered_data.append(filtered_item)
        #     else:
        #         # 新文件时使用全部字段
        #         all_keys = set().union(*(d.keys() for d in save_data))
        #         fieldnames = [k for k in self.required_keys if k in all_keys] + \
        #                     [k for k in all_keys if k not in self.required_keys and k != 'query_flag'] + \
        #                     ['query_flag']
        #         filtered_data = save_data
            
        #     # 转换为DataFrame并保存
        #     df = pd.DataFrame(filtered_data)
        #     df.to_csv(csv_filename, mode='a', index=False, 
        #              header=not file_exists, encoding='utf-8-sig')
                    
        #     self.window_manager._update_log(f"✓ 成功保存到 {os.path.abspath(csv_filename)}")

        #     # 删除以保留的临时文件
        #     self.save_add_data()  # 重新加载最新数据
        except Exception as e:
            self.window_manager._update_log(f"保存失败: {str(e)}")



from PySide6.QtWidgets import QApplication
import sys

if __name__ == "__main__":
    qt_app = QApplication(sys.argv)
    app = TextExtractorApp()
    app.run()
    sys.exit(qt_app.exec())