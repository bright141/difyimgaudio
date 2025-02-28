import re
import json
import os
from mirai import MessageChain, Image, Voice
from pkg.plugin.context import register, handler, llm_func, BasePlugin, APIHost, EventContext
from pkg.plugin.events import *  # 导入事件类

# 读取配置文件
config_path = os.path.join('data', 'config', 'provider.json')
try:
    # 首先尝试使用UTF-8编码读取
    with open(config_path, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
except UnicodeDecodeError:
    # 如果UTF-8失败，尝试使用GBK编码读取
    with open(config_path, 'r', encoding='gbk') as config_file:
        config = json.load(config_file)

# 从配置文件中获取dify地址并去除 "/v1" 部分
url = config["dify-service-api"]["base-url"].rstrip("/v1")

# 注册插件
@register(name="difyimgaudio", description="适用于dify对话器的发送图片和语音", version="0.1", author="bright")
class MyPlugin(BasePlugin):

    # 插件加载时触发
    def __init__(self, host: APIHost):
        self.host = host

    # 异步初始化
    async def initialize(self):
        pass

    # 插件卸载时触发
    def __del__(self):
        pass

    @handler(NormalMessageResponded)
    async def on_normal_message_responded(self, ctx: EventContext):
        content = ctx.event.response_text
        target_type = ctx.event.launcher_type  # 获取目标类型
        target_id = str(ctx.event.launcher_id)  # 获取目标ID并转换为字符串

        # 使用官方dify时提取完整图片URL
        new_match = re.search(r"\[.*?\]\((https://upload\.dify\.ai/files/tools/.*?\.png\?timestamp=.*?)\)", content)
        if new_match:
            image_url = new_match.group(1)
            message = MessageChain([Image(url=image_url)])
            await ctx.send_message(target_type, target_id, message)
            ctx.prevent_default()
            return

        # 提取图片URL
        match = re.search(r"\[.*?\]\((/files/tools/.*?\.png\?timestamp=.*?)\)", content)
        if match:
            image_url = url + match.group(1)
            message = MessageChain([Image(url=image_url)])
            await ctx.send_message(target_type, target_id, message)
            ctx.prevent_default()  # 新增：阻止默认回复
            return

        # 使用官方dify时提取完整语音文件URL
        match = re.search(r"\[.*?\]\((https://upload\.dify\.ai/files/tools/.*?\.bin\?timestamp=.*?)\)", content)
        if match:
            audio_url = match.group(1)
            message = MessageChain([Voice(url=audio_url)])
            await ctx.send_message(target_type, target_id, message)
            ctx.prevent_default()
            return

        # 提取语音URL
        match = re.search(r"\[.*?\]\((/files/tools/.*?\.bin\?timestamp=.*?)\)", content)
        if match:
            audio_url = url + match.group(1)
            message = MessageChain([Voice(url=audio_url)])
            await ctx.send_message(target_type, target_id, message)
            ctx.prevent_default()  # 新增：阻止默认回复
            return
