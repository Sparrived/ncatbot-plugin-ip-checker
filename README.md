
# IPChecker 插件

一个用于检测并通知宿主机公网 IPv4 地址变化的 NcatBot 插件。插件支持手动查询当前 IP、查询上一次记录的 IP、以及订阅/退订 IP 变更通知（私聊/群聊）。

## 功能亮点

- 获取当前公网 IPv4（通过 https://ipv4.icanhazip.com）
- 支持记录并返回上一次检测到的 IP
- 支持定时检查并在 IP 发生变化时向订阅的群或私聊发送通知
- 提供命令行接口，管理订阅和查看 IP

## 安装

将 `ip_checker` 文件夹放到你的插件目录（`plugins/`）下。

## 配置

配置项如下：

```yaml

last_ip: 127.0.0.1 # 上一次获取的ip进行本地持久化保存
check_interval: 30 # ip检测间隔，建议在10-30s
notify: # ip变化时播送提醒
  enabled: true # 播送开关，false为关闭
  private: # 私聊播送给用户
  - 1234567
  group: # 播送到群
  - 1234567

```
## 使用说明（命令）

命令注册为 `ipc`（别名 `ipcheck`），需要**管理员权限**：

- 查询当前公网 IP：

```bash
/ipc
```

- 查询上一次记录的 IP：

```bash
/ipc -l
/ipc --last
```

以上指令选择其一使用。

- 订阅或取消订阅当前会话（群或私聊）IP 变更通知：

```bash
/ipc -s
/ipc --subscribe
```
以上指令选择其一使用。

> 如果 `-s/--subscribe` 在群聊中使用，将在 `notify.group` 中添加/移除该群；在私聊中使用则添加/移除私聊用户 ID。插件会在订阅或退订时回复确认信息。

示例回复：

- 当前 IP："当前宿主机IP为 1.2.3.4"
- 上一次记录："记录的前一次宿主机IP为 127.0.0.1"
- 订阅成功："已订阅当前宿主机IP变更通知。"
- 取消订阅："已取消订阅当前宿主机IP变更通知。"

## 定时检测与通知

当 `notify.enabled` 为 `True` 时，插件会调用 `add_scheduled_task` 注册一个名为 `ip_change_detector` 的定时任务，间隔是 `check_interval` 秒。

任务流程：

1. 调用 `fetch_ip()` 获取当前 IP。
2. 若与 `self._last_ip` 不同：
	 - 记录日志
	 - 调用 `_notify_subscribers(ip)` 向订阅的用户/群发送通知
	 - 更新 `self._last_ip` 和配置中的 `last_ip`

通知示例：

"提醒一下！宿主机IP已从 1.2.3.4 更改为 5.6.7.8。"

## 实现

- `fetch_ip()`：通过 `requests.get('https://ipv4.icanhazip.com')` 获取 IP 文本，校验为合法 IPv4 后返回。
- IP 校验由 `_is_ipv4()` 完成，检查点分四段且每段 0-255。
- 插件在 `on_load` 中调用 `init_config()` 和 `init_scheduler()` 完成配置注册与任务初始化。

## 许可

本项目采用 MIT 许可证。详见仓库根目录中的 `LICENSE` 文件。

## 贡献

通过 issue 或 pr 进行贡献，感谢！
