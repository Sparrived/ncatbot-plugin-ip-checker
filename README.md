
<div align="center">
<h1>✨ncatbot - IPChecker 插件✨</h1>

一个用于检测并通知宿主机公网 IPv4 地址变化的 NcatBot 插件，支持定时监控、实时查询和订阅通知。


[![License](https://img.shields.io/badge/License-MIT_License-green.svg)](https://github.com/Sparrived/ncatbot-plugin-ip-checker/blob/master/LICENSE)
[![ncatbot version](https://img.shields.io/badge/ncatbot->=4.2.9-blue.svg)](https://github.com/liyihao1110/ncatbot)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/Sparrived/ncatbot-plugin-ip-checker/releases)


</div>


---

## 🌟 功能亮点

- ✅ **实时查询** - 手动查询当前公网 IPv4 地址（通过 https://ipv4.icanhazip.com）
- ✅ **历史记录** - 查看上一次检测到的 IP 地址
- ✅ **定时监控** - 定时检查 IP 变化，自动检测宿主机 IP 是否发生变更
- ✅ **订阅通知** - 支持群聊和私聊订阅，IP 变化时自动推送通知
- ✅ **灵活配置** - 自定义检测间隔，控制通知开关
- ✅ **智能验证** - 自动校验 IPv4 格式，确保数据准确性

## ⚙️ 配置项

配置文件位于 `data/IPChecker/IPChecker.yaml`

| 配置键 | 类型 | 默认值 | 说明 |
| --- | --- | --- | --- |
| `last_ip` | `str` | `"127.0.0.1"` | 上一次获取的 IP 地址，用于持久化保存。 |
| `check_interval` | `int` | `30` | IP 检测间隔（秒），建议设置在 10-30 秒之间。 |
| `notify.enabled` | `bool` | `false` | 是否启用 IP 变更通知功能。 |
| `notify.private` | `List[int]` | `[]` | 接收私聊通知的用户 QQ 号列表。 |
| `notify.group` | `List[int]` | `[]` | 接收群聊通知的群号列表。 |

**配置示例:**
```yaml
last_ip: 127.0.0.1
check_interval: 30
notify:
  enabled: true
  private:
    - 1234567890
    - 9876543210
  group:
    - 123456789
```

> **提示:** 配置文件可通过 NcatBot 的统一配置机制进行覆盖。建议使用 `/ipc -s` 命令动态订阅/取消订阅，避免手动修改配置后需要重启机器人。

## 🚀 快速开始

### 依赖要求

- Python >= 3.8
- NcatBot >= 4.2.9
- requests（HTTP 请求库）

### 使用 Git

```bash
git clone https://github.com/Sparrived/ncatbot-plugin-ip-checker.git
cd ncatbot-plugin-ip-checker
cp -r ip_checker /path/to/your/ncatbot/plugins/
```

> 请将 `/path/to/your/ncatbot/plugins/` 替换为机器人实际的插件目录。

### 自主下载

1. 将本插件目录置于 `plugins/ip_checker`。
2. 根据实际需要调整 `check_interval` 和 `notify` 等配置项。
3. 重启 NcatBot，插件将自动加载。

### 插件指令

> **注意事项:**
> - 所有指令仅限 NcatBot 管理员用户使用（`admin_filter` 限制）
> - 订阅功能支持群聊和私聊两种场景
> - IP 变更通知会同时发送到所有订阅的群组和私聊用户

| 指令 | 参数 | 说明 | 示例 |
| --- | --- | --- | --- |
| `/ipc` 或 `/ipcheck` | 无 | 查询当前宿主机的公网 IPv4 地址 | `/ipc`<br>`/ipcheck` |
| `/ipc -l\|--last` | `-l/--last`：查询历史 IP | 查询上一次记录的 IP 地址 | `/ipc -l`<br>`/ipc --last` |
| `/ipc -s\|--subscribe` | `-s/--subscribe`：订阅/取消订阅 | 订阅或取消订阅当前会话的 IP 变更通知<br>在群聊中使用则订阅该群，在私聊中使用则订阅该用户 | `/ipc -s`<br>`/ipc --subscribe` |

**命令响应示例:**

```
# 查询当前 IP
当前宿主机IP为 123.45.67.89

# 查询历史 IP
记录的前一次宿主机IP为 123.45.67.88

# 订阅通知
已订阅当前宿主机IP变更通知。

# 取消订阅
已取消订阅当前宿主机IP变更通知。
```

## 🧠 运作逻辑

### 定时监控机制
- 当 `notify.enabled` 为 `true` 时，插件会自动启动定时任务 `ip_change_detector`
- 任务每隔 `check_interval` 秒执行一次 IP 检测
- 检测到 IP 变化时，自动向所有订阅者发送通知并更新记录

### IP 检测流程
1. 调用 `fetch_ip()` 函数向 https://ipv4.icanhazip.com 发送 GET 请求
2. 获取响应文本并去除首尾空白字符
3. 使用 `_is_ipv4()` 验证返回值是否为合法的 IPv4 地址（点分四段，每段 0-255）
4. 验证通过后返回 IP 地址，否则抛出异常

### 订阅管理
- **群聊订阅**: 在群内使用 `/ipc -s` 会将该群号添加到 `notify.group` 列表
- **私聊订阅**: 在私聊中使用 `/ipc -s` 会将用户 QQ 号添加到 `notify.private` 列表
- **取消订阅**: 重复执行订阅命令即可取消订阅（toggle 机制）

### 变更通知
当检测到 IP 变化时，插件会：
1. 记录日志：`检测到宿主机IP已从 {旧IP} 更改为 {新IP}`
2. 调用 `_notify_subscribers()` 向所有订阅者发送通知消息
3. 更新 `last_ip` 配置项，持久化保存新 IP

**通知消息格式:**
```
提醒一下！宿主机IP已从 123.45.67.88 更改为 123.45.67.89。
```

## 🪵 日志与排错

插件使用 NcatBot 的统一日志系统，所有操作都会记录详细日志。

### 查看日志
```bash
# 日志文件位置
logs/bot.log.YYYY_MM_DD

# 筛选 IPChecker 相关日志
grep "IPChecker" logs/bot.log.2025_10_29
```

### 常见问题

**Q: 为什么定时检测没有启动？**
- 检查 `notify.enabled` 配置是否为 `true`
- 查看日志，确认是否有 "IP 变更检测任务已启动" 的提示
- 如果显示 "未启动"，需要修改配置并重启机器人

**Q: IP 查询失败怎么办？**
- 检查网络连接，确保能访问 https://ipv4.icanhazip.com
- 查看日志中是否有 "Request timeout" 或 HTTP 错误
- 可以尝试手动访问该 URL 测试网络连通性

**Q: 订阅后没有收到通知？**
- 确认 `notify.enabled` 已设置为 `true`
- 检查订阅列表（`notify.private` 或 `notify.group`）中是否包含目标 QQ/群号
- 确认 IP 确实发生了变化（可通过 `/ipc` 和 `/ipc -l` 对比）

**Q: 检测间隔如何设置最合理？**
- 建议设置在 10-30 秒之间
- 间隔过短可能导致频繁请求，影响性能
- 间隔过长可能导致 IP 变化通知不及时

## 🤝 贡献

欢迎通过 Issue 或 Pull Request 分享改进建议、提交补丁！

### 贡献指南
1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

### 代码规范
- 遵循 PEP 8 Python 代码风格
- 添加必要的注释和文档字符串
- 确保代码通过基本功能验证

## 🙏 致谢

感谢以下项目和贡献者：

- [NcatBot](https://github.com/liyihao1110/ncatbot) - 提供稳定易用的 OneBot11 Python SDK
- [icanhazip.com](https://icanhazip.com/) - 提供免费的公网 IP 查询服务
- 社区测试者与维护者 - 提交 Issue、Pull Request 以及改进建议

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源协议。

---

<div align="center">

如果本插件帮助到了你，欢迎为项目点亮 ⭐ Star！

[报告问题](https://github.com/Sparrived/ncatbot-plugin-ip-checker/issues) · [功能建议](https://github.com/Sparrived/ncatbot-plugin-ip-checker/issues) · [查看发布](https://github.com/Sparrived/ncatbot-plugin-ip-checker/releases)

</div>
