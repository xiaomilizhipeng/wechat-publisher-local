---
name: wechat-publisher
description: 微信公众号草稿发布助手。本地安全版：从 Markdown 或 HTML 创建微信公众号草稿，优先从本地配置读取 AppID/AppSecret，不在控制台回显密钥。用户提到“公众号草稿、微信发布、发布到草稿箱、发布 Markdown 到公众号”时使用。
---

# WeChat Publisher

优先运行本地安全版脚本。

## 脚本

主脚本：`/home/xp/openclaw/skills/wechat-publisher/scripts/publisher.py`

## 本地配置

默认从这里读取配置：

```text
/home/xp/openclaw/config/wechat-publisher/config.json
```

## 用法

### 只检查 token

```bash
python3 /home/xp/openclaw/skills/wechat-publisher/scripts/publisher.py --check-token
```

### 从 Markdown 创建公众号草稿

```bash
python3 /home/xp/openclaw/skills/wechat-publisher/scripts/publisher.py \
  --article /path/to/article.md \
  --author "佳佳子" \
  --no-cover
```

### 直接输入标题和 HTML 内容

```bash
python3 /home/xp/openclaw/skills/wechat-publisher/scripts/publisher.py \
  --title "测试标题" \
  --content "<section>测试内容</section>" \
  --author "佳佳子" \
  --no-cover
```

## 说明

- 本地安全版不会在日志中打印 AppSecret。
- 本地安全版只创建草稿，不自动群发发布。
- 若微信接口报 IP 白名单错误，需要将实际出口 IP 加到公众号后台白名单。
