# wechat-publisher-local

一个本地安全版的微信公众号草稿发布技能。

## 特点

- 从 Markdown 创建公众号草稿
- 支持直接输入标题 + HTML 内容创建草稿
- 本地优先读取配置文件
- 不在控制台回显 AppSecret
- 只创建草稿，不自动群发发布

## 仓库内容

- `skill/wechat-publisher/`：OpenClaw Skill

## 配置说明

本仓库**不包含**你的真实 AppID/AppSecret。
本地建议通过单独配置文件提供，例如：

```text
/home/xp/openclaw/config/wechat-publisher/config.json
```

格式：

```json
{
  "appid": "YOUR_APPID",
  "secret": "YOUR_SECRET",
  "author": "YourName"
}
```

## 用法

```bash
python3 skill/wechat-publisher/scripts/publisher.py --check-token
```

```bash
python3 skill/wechat-publisher/scripts/publisher.py \
  --article /path/to/article.md \
  --author "YourName" \
  --no-cover
```
