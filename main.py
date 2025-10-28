from ncatbot.plugin_system import NcatBotPlugin, admin_filter, command_registry, option, param
from ncatbot.utils import get_log
from ncatbot.core import BaseMessageEvent, GroupMessageEvent, PrivateMessageEvent

from .utils import fetch_ip

class IPChecker(NcatBotPlugin):
    name = "IPChecker"
    version = "1.0.1"
    description = "一个用于检查机器人宿主机IP地址的插件，支持定时检查并播送到指定群聊/个人。"
    log = get_log(name)

    def init_config(self):
        """注册配置项"""
        self.register_config("last_ip", "127.0.0.1", value_type=str) # 上一次获取的IP
        self.register_config("check_interval", 30, value_type=int) # 检查间隔
        self.register_config("notify", {"enabled": False, "private": [], "group": []}, value_type=dict) # 订阅信息的群/个人
        self._last_ip = self.config["last_ip"]
        self._notify = self.config["notify"]

    def init_scheduler(self):
        """初始化定时任务"""
        if self._notify["enabled"]:
            self.add_scheduled_task(
                job_func=self._task_check,
                name="ip_change_detector",
                interval=f"{self.config['check_interval']}s",
            )
            self.log.info(f"IP 变更检测任务已启动，当前设置为每 {self.config['check_interval']} 秒检测一次。")
            return
        self.log.info("IP 变更检测任务未启动，如需启用请修改 notify.enabled 为 True。")

    # ======== 初始化插件 ========
    async def on_load(self):
        self.init_config()
        self.init_scheduler()

    # ======== 注册指令 ========
    @admin_filter
    @command_registry.command("ipc", aliases=["ipcheck"], description="获取当前机器人宿主机IP地址")
    @option("l", "last", "获取上一次的IP地址") # -l --last
    @option("s", "subscribe", "订阅或取消订阅IP变更通知") # -s --subscribe
    async def cmd_ipc(self, event: BaseMessageEvent, last: bool = False, subscribe: bool = False):
        """获取当前机器人宿主机IP地址，或上一次记录的IP地址。"""
        if subscribe:
            """ 处理订阅指令 """
            is_remove = False
            if isinstance(event, GroupMessageEvent):
                if event.group_id not in self._notify["group"]:
                    self._notify["group"].append(event.group_id)
                else:
                    self._notify["group"].remove(event.group_id)
                    is_remove = True
            elif isinstance(event, PrivateMessageEvent):
                if event.sender.user_id not in self._notify["private"]:
                    self._notify["private"].append(event.sender.user_id)
                else:
                    self._notify["private"].remove(event.sender.user_id)
                    is_remove = True
            if is_remove:
                await event.reply("已取消订阅当前宿主机IP变更通知。")
            else:
                await event.reply("已订阅当前宿主机IP变更通知。")
            return
        if last:
            await event.reply(f"记录的前一次宿主机IP为 {self._last_ip}")
            return
        ip = fetch_ip()
        await event.reply(f"当前宿主机IP为 {ip}")

    # ======== 内部函数 ========
    def _task_check(self):
        ip = fetch_ip()
        if ip != self._last_ip:
            self.log.info(f"检测到宿主机IP已从 {self._last_ip} 更改为 {ip}。")
            self._notify_subscribers(ip)
            self._update_last_ip(ip)

    def _update_last_ip(self, ip: str):
        self._last_ip = ip
        self.config["last_ip"] = ip

    def _notify_subscribers(self, ip: str):
        if not self.config["notify"]["enabled"]:
            return
        notify_str = f"提醒一下！宿主机IP已从 {self._last_ip} 更改为 {ip}。"
        for user_id in self._notify["private"]:
            self.api.post_private_msg_sync(user_id, notify_str)
        for group_id in self._notify["group"]:
            self.api.post_group_msg_sync(group_id, notify_str)