import tkinter as tk
from tkinter import ttk, scrolledtext

class WindowManager:
    def __init__(self, app):
        self.app = app
        self.root = tk.Tk()
        self.max_history_lines = 1000
        self.word_var = tk.StringVar()
        self.sentence_var = tk.StringVar()
        self.hotkey_word_var = tk.StringVar()
        self.hotkey_sentence_var = tk.StringVar()
        self.hotkey_add_data_var = tk.StringVar()
        self.output_filename_var = tk.StringVar()
        self.api_key_var = tk.StringVar(value=self.app.config["api"]["api_key"])
        self.prompt_text =None
        # self.console_text = scrolledtext.ScrolledText(self.root, state='disabled', height=10, wrap='word', font=("微软雅黑", 10))
    def configure_window(self):
        """配置主窗口外观"""
        self.root.title("📚 单词管理工具 v1.0")
        self.root.geometry("300x400-0+0")
        self.root.configure(bg='#f0f0f0')
        self.root.attributes('-topmost', True)

        # 创建菜单栏
        self.create_menu()

        # 网格布局配置
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(3, weight=1)
        
        # 现代主题样式
        self.configure_styles()
       

    def create_menu(self):
        """创建菜单栏"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # 添加设置菜单
        settings_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="设置", menu=settings_menu)
        settings_menu.add_command(label="选项", command=self.show_settings_dialog)

    def show_hotkeys_and_prompt(self):
        """显示设置中的热键和prompt"""
        config = self.app.config
        self.output_filename_var.set(config["file"]["output_name"])
        self.hotkey_word_var.set(config["hotkeys"]["get_word_hotkey"])
        self.hotkey_sentence_var.set(config["hotkeys"]["get_sentence_hotkey"])
        self.hotkey_add_data_var.set(config["hotkeys"]["add_data"])
        self.api_key_var.set(config["api"]["api_key"])  # 新增：显示API Key
        if self.app.config.has_section('prompt') and 'default' in self.app.config['prompt']:
            self.prompt_text.insert("1.0", self.app.config['prompt']['default'])

    def show_settings_dialog(self):
        """显示空设置对话框"""
        dialog = tk.Toplevel(self.root)
        dialog.title("设置")
        dialog.geometry("400x600")  # 增加高度以容纳新控件
        
        # 计算对话框位置
        screen_width = dialog.winfo_screenwidth()
        screen_height = dialog.winfo_screenheight()
        dialog_width = 400
        dialog_height = 600
        x = (screen_width - dialog_width) // 2
        y = (screen_height - dialog_height) // 2
        
        # 设置对话框位置
        dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
        
        # 创建框架用于布局
        frame = ttk.Frame(dialog)
        frame.pack(padx=20, pady=20, fill='both', expand=True)

        # 原有热键设置控件，行号保持不变
        ttk.Label(frame, text="设置热键和Prompt:回车修改", font=("微软雅黑", 12)).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky='w')

        ttk.Label(frame, text="文件名称", font=("微软雅黑", 11)).grid(row=1, column=0, padx=5, pady=5, sticky='e')
        hotkey_word_entry = ttk.Entry(frame, font=("微软雅黑", 11), textvariable=self.output_filename_var)
        hotkey_word_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        hotkey_word_entry.bind('<Return>', lambda e: self.reset_output_name())

        ttk.Label(frame, text="API Key", font=("微软雅黑", 11)).grid(row=2, column=0, padx=5, pady=5, sticky='e')
        api_key_entry = ttk.Entry(frame, font=("微软雅黑", 11), textvariable=self.api_key_var)
        api_key_entry.grid(row=2, column=1, padx=5, pady=5, sticky='ew')
        api_key_entry.bind('<Return>', lambda e: self.save_api_key())

        ttk.Label(frame, text="提取单词", font=("微软雅黑", 11)).grid(row=3, column=0, padx=5, pady=5, sticky='e')
        hotkey_word_entry = ttk.Entry(frame, font=("微软雅黑", 11), textvariable=self.hotkey_word_var)
        hotkey_word_entry.grid(row=3, column=1, padx=5, pady=5, sticky='ew')
        hotkey_word_entry.bind('<Return>', lambda e: self.app.reset_hotkey(
            self.app.config["hotkeys"]["get_word_hotkey"],
            self.hotkey_word_var.get(),
            self.app.capture_word
        ))

        # 提取句子
        ttk.Label(frame, text="提取句子", font=("微软雅黑", 11)).grid(row=4, column=0, padx=5, pady=5, sticky='e')
        hotkey_sentence_entry = ttk.Entry(frame, font=("微软雅黑", 11), textvariable=self.hotkey_sentence_var)
        hotkey_sentence_entry.grid(row=4, column=1, padx=5, pady=5, sticky='ew')
        hotkey_sentence_entry.bind('<Return>', lambda e: self.app.reset_hotkey(
            self.app.config["hotkeys"]["get_sentence_hotkey"],
            self.hotkey_sentence_var.get(),
            self.app.capture_sentence
        ))
        
        # 添加数据
        ttk.Label(frame, text="添加数据", font=("微软雅黑", 11)).grid(row=5, column=0, padx=5, pady=5, sticky='e')
        hotkey_add_data_entry = ttk.Entry(frame, font=("微软雅黑", 11), textvariable=self.hotkey_add_data_var)
        hotkey_add_data_entry.grid(row=5, column=1, padx=5, pady=5, sticky='ew')
        hotkey_add_data_entry.bind('<Return>', lambda e: self.app.reset_hotkey(
            self.app.config["hotkeys"]["add_data"],
            self.hotkey_add_data_var.get(),
            self.app.add_word
        ))

        # 添加Prompt文本框
        ttk.Label(frame, text="Prompt", font=("微软雅黑", 11)).grid(row=6, column=0, padx=5, pady=5, sticky='nw')
        self.prompt_text = scrolledtext.ScrolledText(frame, height=12, wrap=tk.WORD, font=("微软雅黑", 11))
        self.prompt_text.grid(row=7, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
        
        
        # 初始化内容
        
        self.show_hotkeys_and_prompt()
        # 绑定回车键事件
        self.prompt_text.bind('<Return>', lambda e: self.reset_prompt())
        
        # 配置列权重
        frame.columnconfigure(1, weight=1)

    def configure_styles(self):
        """配置样式"""
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("TLabel", font=("微软雅黑", 11), padding=8, background='#f0f0f0', foreground='#333')
        style.configure("TEntry", font=("微软雅黑", 11), relief='flat', fieldbackground='white')
        style.configure("TButton", font=("微软雅黑", 10, "bold"), padding=6, borderwidth=1, relief='flat')
        style.map('TButton',
                foreground=[('active', 'white'), ('!active', 'white')],
                background=[('active', '#45a7ff'), ('!active', '#2d7ff2')])


    def create_widgets(self):
        """创建界面组件"""
        self.create_input_area()
        self.create_buttons()
        self.create_console()

    def create_input_area(self):
        # 输入区域框架
        input_frame = ttk.Frame(self.root, padding=(10, 15))
        input_frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

        # 单词输入
        ttk.Label(input_frame, text="📖 单词：").grid(row=0, column=0, sticky="e", padx=8, pady=8)
        word_entry = ttk.Entry(input_frame, width=20, textvariable=self.word_var)
        word_entry.grid(row=0, column=1, sticky="ew", padx=1, pady=8)
        word_entry.bind('<Return>', lambda e: self.app.on_word_entry_enter())
        
        # 句子输入
        ttk.Label(input_frame, text="📝 句子：").grid(row=1, column=0, sticky="e", padx=8, pady=8)
        sentence_entry = ttk.Entry(input_frame, width=20, textvariable=self.sentence_var)
        sentence_entry.grid(row=1, column=1, sticky="ew", padx=1, pady=8)
        sentence_entry.bind('<Return>', lambda e: self.app.on_sentence_entry_enter())

    def create_buttons(self):
       # 功能按钮
        # 按钮容器框架
        btn_container = ttk.Frame(self.root)
        btn_container.grid(row=1, column=0, columnspan=2, pady=5, sticky='ew')
        
        # 按钮组框架 - 两行两列布局
        btn_frame = ttk.Frame(btn_container)
        btn_frame.pack(expand=True, fill='both')
        
        # 配置行列权重
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.rowconfigure(0, weight=1)
        btn_frame.rowconfigure(1, weight=1)
        
        # 第一行按钮
        ttk.Button(btn_frame, text="📥 添加单词", command=self.app.add_word).grid(row=0, column=0, padx=5, pady=3, sticky='nsew')
        ttk.Button(btn_frame, text="🤖 模型查词", command=self.app.model_query).grid(row=0, column=1, padx=5, pady=3, sticky='nsew')
        
        # 第二行按钮
        ttk.Button(btn_frame, text="💾 保存记录", command=self.app.save_record).grid(row=1, column=0, padx=5, pady=3, sticky='nsew')
        ttk.Button(btn_frame, text="❌ 保存退出", command=self.app.exit).grid(row=1, column=1, padx=5, pady=3, sticky='nsew')

    def create_console(self):
        # 控制台输出区域
        console_frame = ttk.Frame(self.root)
        console_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", padx=10, pady=(0,10))
        
        self.console = scrolledtext.ScrolledText(console_frame, height=10, wrap=tk.WORD, state=tk.DISABLED)
        self.console.pack(fill=tk.BOTH, expand=True)
    def disable_controls(self):
        """禁用所有控件"""
        try:
            # 获取按钮容器
            btn_container = self.root.winfo_children()[1]
            btn_frame = btn_container.winfo_children()[0]
            
            # 遍历所有按钮并禁用
            for btn in btn_frame.winfo_children():
                btn.config(state='disabled')
        except (IndexError, AttributeError) as e:
            self.log_message(f"禁用控件时出错: {str(e)}")

    def enable_controls(self):
        """启用所有控件"""
        try:
            # 获取按钮容器
            btn_container = self.root.winfo_children()[1]
            btn_frame = btn_container.winfo_children()[0]
            
            # 遍历所有按钮并启用
            for btn in btn_frame.winfo_children():
                btn.config(state='normal')
        except (IndexError, AttributeError) as e:
            self.log_message(f"启用控件时出错: {str(e)}")

    def log_message(self, message):
            """在控制台输出消息"""
            self.console.config(state=tk.NORMAL)
            self.console.insert(tk.END, f"{message}\n")
            
            # 限制历史记录行数
            lines = int(self.console.index('end-1c').split('.')[0])
            if lines > self.max_history_lines:
                self.console.delete(1.0, f"{lines-self.max_history_lines}.0")
            
            self.console.see(tk.END)  # 自动滚动到底部
            self.console.config(state=tk.DISABLED)
    def reset_prompt(self):
        """重置prompt"""
        # 获取prompt_text的内容
        new_prompt = self.prompt_text.get("1.0", tk.END).strip()
        
        # 更新配置文件
        self.app.config.set('prompt', "default", new_prompt)
        with open('config.ini', 'w', encoding='utf-8') as f:
            self.app.config.write(f)
        
        # 记录日志
        self.log_message(f"prompt已重置为 {new_prompt}")
        self.show_hotkeys_and_prompt()


    def reset_output_name(self):
        """重置output_name"""
        # 更新配置文件
        self.app.config.set('prompt', "output_name", self.output_filename_var.get())
        with open('config.ini', 'w', encoding='utf-8') as f:
            self.app.config.write(f)
        
        # 记录日志
        self.log_message(f"输出文件名称已重置为 {self.output_filename_var.get()}")
        self.show_hotkeys_and_prompt()
    def save_api_key(self):
        """保存API Key"""
        api_key = self.api_key_var.get().strip()
        if api_key:
            self.app.config.set('api', 'api_key', api_key)
            with open('config.ini', 'w', encoding='utf-8') as f:
                self.app.config.write(f)
            self.log_message("API Key已保存")
        else:
            self.log_message("错误: API Key不能为空")