from datetime import datetime

from agent.deepseek import send_messages

def get_intent(user_query: str):
    prompt = """
            你的任务是根据用户在语音交互中的指令，识别其所属的意图类别，并返回对应的意图分类的英文字符串。有时一条指令可能涉及多个意图，请确保每个意图用 " - " 分隔。以下是意图分类的类别和示例：

            - **AppControl**: 用于打开、关闭或操作应用程序。
              - 示例: "打开相机", "关闭音乐播放器", "启动微信", "打开支付宝扫码功能", "关闭地图应用"。

            - **Settings**: 用于调整手机系统设置，如亮度、音量或网络连接。
              - 示例: "将屏幕亮度调到50%", "打开飞行模式", "关闭蓝牙", "开启Wi-Fi", "把手机调到静音模式"。

            - **Weather**: 用于查询当前或未来的天气信息。
              - 示例: "今天的天气怎么样？", "明天会下雨吗？", "查看未来一周的天气", "上海今天气温多少？","今天上午的天气怎么样“。

            - **Alarm**: 用于设置、修改或取消闹钟和提醒。
              - 示例: "设置一个明早7点的闹钟", "提醒我明天去开会", "删除下午2点的闹钟", "把闹钟推迟10分钟"。

            - **TimeDate**: 用于查询当前时间、日期或节日信息。
              - 示例: "现在几点了？", "今天是星期几？", "今年的中秋节是哪一天？", "今年农历春节是几月几号？"。

            - **Calendar**: 用于查询或管理日历事件和日程安排。
              - 示例: "今天我的日程安排是什么？", "帮我在明天下午3点加一个会议", "取消本周五所有的日程", "添加一个周六下午的健身计划"。

            - **Music**: 用于控制音乐播放、暂停或切换歌曲。
              - 示例: "播放周杰伦的《晴天》", "下一首歌", "暂停音乐", "播放流行歌单", "把音量调到最大"。

            - **Communication**: 用于拨打电话、发送短信或即时消息。
              - 示例: "给张三打电话", "发短信给李四，内容是‘我晚点到’", "给王五发个微信", "拨打妈妈的手机", "用QQ给小明发个文件"。

            - **Navigation**: 用于导航到指定地点或查询附近位置。
              - 示例: "导航到最近的加油站", "从这里到南京路怎么走？", "显示附近的咖啡店", "去浦东机场的最快路线", "找最近的地铁站"。

            - **Information**: 用于查询知识、定义或其他信息。
              - 示例: "苹果公司的CEO是谁？", "世界上最高的山是什么？", "‘人工智能’的定义是什么？", "找到中国历史上最长的朝代"。

            - **Shopping**: 用于查询商品、价格或下单购物。
              - 示例: "查一下最新款iPhone的价格", "帮我买一盒牛奶", "看看淘宝上有什么打折", "京东上现在的热销商品是什么？"。

            - **News**: 用于查询头条新闻或特定类别新闻。
              - 示例: "今天的头条新闻是什么？", "最近的国际新闻怎么样？", "上海的本地新闻有哪些？", "科技圈有什么新动态？"。

            - **Health**: 用于查询健康数据或设置健身计划。
              - 示例: "今天我走了多少步？", "我的心率是多少？", "设置一个健身计划", "最近的睡眠质量如何？"。

            - **Entertainment**: 用于轻松互动，例如讲笑话、推荐电影或播放短视频。
              - 示例: "讲个笑话吧", "推荐一部好电影", "找一些搞笑的视频", "播放猫咪的短视频"。

            - **Translation**: 用于翻译内容或语言学习。
              - 示例: "‘你好’用英语怎么说？", "把‘我想去旅行’翻译成法语", "如何用日语说‘谢谢’？", "帮我翻译‘今天天气不错’成西班牙语"。

            - **Finance**: 用于查询汇率、记录支出或检查财务信息。
              - 示例: "查询人民币对美元的汇率", "记录我花了200元吃饭", "现在比特币的价格是多少？", "查询股票市场的最新动态"。

            - **Home**: 用于控制智能家居设备，如灯光、空调或锁具。
              - 示例: "打开客厅的灯", "把空调调到26度", "检查门是否锁上了", "关闭卧室的窗帘"。

            - **Travel**: 用于查询景点、酒店或票务信息。
              - 示例: "查一下北京的景点有哪些", "去东京的机票多少钱？", "找一家附近的酒店", "推荐一个周边游的好去处"。

            - **Food**: 用于查询附近餐厅、菜品推荐或饮食建议。
              - 示例: "附近有哪些好吃的？", "订一桌火锅餐", "查一下减肥餐怎么做", "找一家米其林餐厅"。

            - **Guide**: 提供设备的使用指南或操作提示。
              - 示例: "为什么我的手机发热？", "如何重启手机？", "如何设置我的新应用？", "教我清理手机缓存"。

            ### 说明
            以上示例语句翻译成中文后，适当扩展了例句内容以增加分类的覆盖面，提高模型分类的精准度。

            根据每条用户指令识别其意图，并返回每个意图分类的英文字符串，用 " - " 分隔。例如：

            指令: "打开空调并播放周杰伦的歌曲"
            意图分类: Home - Music

            指令: "明天早上叫我起床并发送消息给李四说我会晚点到"
            意图分类: Alarm - Communication

            请根据上述指令生成多个英文意图分类结果，并用 " - " 分隔。 上面是一个prompt，帮我吧Example中的语句转换成对应的汉语，可以适当扩充example的句子以让模型的分类更加精准
            以下是需要分类的指令：
                    """

    messages = [
        {"role": "system", "content": "不要输出任何markdown格式数据" +
                                      prompt +
                                      f"现在的时间是 {datetime.now().strftime('%Y-%m-%d-%h')}. 当需要用到时间时候请参照今天"},
        {"role": "user", "content": user_query}
    ]

    message = send_messages(messages)
    print(message)
    return message.content