# 介绍

这是一个用于单词和句子提取的桌面小应用。可以实现提取所遇见的单词和句子，通过接入deepseek的api进行查询prompt中所自定义的内容（比如kk音标，例句，近义词，形近词等）。查询的数据保存为CSV文件可以直接导入到Anki中快速制作卡片。

<img src="D:\desktop\英语单词提取app\仓库\EnglishText_Extractor_app\figure\image-20250417155619662.png" alt="image-20250417155619662" style="zoom:50%;" />





# 使用方法

1. **配置api和快捷键**：点击菜单，打开设置，输入deepseek的api并保存。设置相关快接键

   <img src="D:\desktop\英语单词提取app\仓库\EnglishText_Extractor_app\figure\image-20250417155058076.png" alt="image-20250417155058076" style="zoom: 50%;" />

2. **配置prompt**：在prompt中修改相应内容自定义需要deepseek回复的信息，并对相应回复内容做出要求

   ![image-20250417155449794](D:\desktop\英语单词提取app\仓库\EnglishText_Extractor_ap\figurep\image-20250417155449794.png)

   

3. **添加单词**：选择单词或句子->按下相应快捷键对单词或句子进行提取，**按下“添加单词”或快捷键进行添加**。

4. **模型查询**按下模型查询可以调用deepseek，根据prompt的信息进行查询（查询期间不能点击保存记录和保存退出）

5. **保存记录**：点击保存记录会将已经添加的单词保存在当前文件夹的csv类型文档中。（**点击保存记录后会清楚菜单->单词列表内的单词**）

6. **保存退出**：点击保存退出会先查询添加的单词，然后保存退出

7. **查看已添加单词**:已经添加的单词可以在菜单->单词列表中查看，误添加单词可以选择并删除。

   <img src="D:\desktop\英语单词提取app\仓库\EnglishText_Extractor_app\figure\image-20250417160010561.png" alt="image-20250417160010561" style="zoom: 50%;" />