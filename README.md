# wechat-publisher-local

一个本地安全版的微信公众号草稿发布技能，用于把 Markdown 或 HTML 内容创建为微信公众号草稿。

这个仓库的目标不是“自动群发”，而是：

- 自动创建草稿
- 自动处理封面
- 自动把 Markdown 转成微信兼容 HTML
- 尽量减少密钥暴露风险

---

## 特点

- 从 Markdown 创建公众号草稿
- 支持直接输入标题 + HTML 内容创建草稿
- 本地优先读取配置文件
- 不在控制台回显 AppSecret
- 只创建草稿，不自动群发发布

---

## 仓库内容

```text
wechat-publisher-local/
├── README.md
├── .gitignore
└── skill/
    └── wechat-publisher/
        ├── SKILL.md
        ├── .gitignore
        └── scripts/
            └── publisher.py
```

---

## 配置说明

本仓库**不包含**任何真实 AppID / AppSecret。

本地建议通过单独配置文件提供，例如：

```text
/home/xp/openclaw/config/wechat-publisher/config.json
```

格式如下：

```json
{
  "appid": "YOUR_APPID",
  "secret": "YOUR_SECRET",
  "author": "YourName"
}
```

---

## 用法

### 1）只检查 token

```bash
python3 skill/wechat-publisher/scripts/publisher.py --check-token
```

### 2）从 Markdown 创建公众号草稿

```bash
python3 skill/wechat-publisher/scripts/publisher.py \
  --article /path/to/article.md \
  --author "YourName" \
  --no-cover
```

### 3）直接输入标题和 HTML 内容

```bash
python3 skill/wechat-publisher/scripts/publisher.py \
  --title "测试标题" \
  --content "<section>测试内容</section>" \
  --author "YourName" \
  --no-cover
```

---

## 注意事项

- 本工具只创建草稿，不自动发布
- 若微信接口报 IP 白名单错误，需要将实际出口 IP 加到公众号后台白名单
- 建议不要把配置文件提交到 git

---

## 适合的工作流

1. 先用热榜技能找热点
2. 再用选题助手生成公众号选题
3. 最后用这个发布器把成稿送进公众号草稿箱

---

## License

MIT
