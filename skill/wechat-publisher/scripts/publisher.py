#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import argparse
import json
import os
import sys
import tempfile
from typing import Optional

import requests

CONFIG_PATH = "/home/xp/openclaw/config/wechat-publisher/config.json"


class WeChatPublisher:
    def __init__(self, appid: str, secret: str, quiet: bool = False):
        self.appid = appid
        self.secret = secret
        self.quiet = quiet
        self.access_token: Optional[str] = None
        self.base_url = "https://api.weixin.qq.com/cgi-bin"

    def log(self, *args, **kwargs):
        if not self.quiet:
            print(*args, **kwargs)

    def get_access_token(self) -> Optional[str]:
        self.log("🔑 正在获取 access_token...")
        url = f"{self.base_url}/token"
        params = {"grant_type": "client_credential", "appid": self.appid, "secret": self.secret}
        try:
            response = requests.get(url, params=params, timeout=30)
            data = response.json()
            if "access_token" in data:
                self.access_token = data["access_token"]
                expires_in = data.get("expires_in", 7200)
                self.log(f"✅ access_token 获取成功（有效期 {expires_in//60} 分钟）")
                return self.access_token
            error_code = data.get("errcode", "Unknown")
            error_msg = data.get("errmsg", "Unknown error")
            self.log(f"❌ access_token 获取失败：{error_code} - {error_msg}")
            return None
        except requests.RequestException as e:
            self.log(f"❌ 网络请求失败：{e}")
            return None
        except Exception as e:
            self.log(f"❌ 未知错误：{e}")
            return None

    def upload_image(self, image_path: str) -> Optional[str]:
        if not self.access_token:
            self.log("❌ 请先获取 access_token")
            return None
        self.log(f"🖼️ 正在上传封面图片：{image_path}")
        url = f"https://api.weixin.qq.com/cgi-bin/material/add_material?access_token={self.access_token}&type=image"
        try:
            with open(image_path, 'rb') as f:
                response = requests.post(url, files={"media": f}, timeout=30)
                data = response.json()
            if "media_id" in data:
                media_id = data["media_id"]
                self.log(f"✅ 封面图片上传成功！media_id: {media_id}")
                return media_id
            self.log(f"❌ 封面图片上传失败：{data.get('errcode')} - {data.get('errmsg')}")
            return None
        except Exception as e:
            self.log(f"❌ 请求失败：{e}")
            return None

    def upload_default_cover(self) -> Optional[str]:
        try:
            response = requests.get("https://picsum.photos/900/500", timeout=30)
            if response.status_code == 200:
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
                    f.write(response.content)
                    temp_path = f.name
                media_id = self.upload_image(temp_path)
                os.unlink(temp_path)
                if media_id:
                    return media_id
        except Exception as e:
            self.log(f"⚠️ 在线获取封面失败：{e}，使用本地生成...")

        try:
            width, height = 900, 500
            row_size = (width * 3 + 3) & ~3
            image_size = row_size * height
            file_size = 54 + image_size
            bmp_header = bytes([
                0x42, 0x4D,
                file_size & 0xFF, (file_size >> 8) & 0xFF, (file_size >> 16) & 0xFF, (file_size >> 24) & 0xFF,
                0x00, 0x00, 0x00, 0x00,
                0x36, 0x00, 0x00, 0x00,
                0x28, 0x00, 0x00, 0x00,
                width & 0xFF, (width >> 8) & 0xFF, (width >> 16) & 0xFF, (width >> 24) & 0xFF,
                height & 0xFF, (height >> 8) & 0xFF, (height >> 16) & 0xFF, (height >> 24) & 0xFF,
                0x01, 0x00, 0x18, 0x00,
                0x00, 0x00, 0x00, 0x00,
                image_size & 0xFF, (image_size >> 8) & 0xFF, (image_size >> 16) & 0xFF, (image_size >> 24) & 0xFF,
                0x13, 0x0B, 0x00, 0x00,
                0x13, 0x0B, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00,
                0x00, 0x00, 0x00, 0x00,
            ])
            blue_pixel = bytes([0x80, 0x40, 0x20])
            padding = bytes([0x00] * (row_size - width * 3))
            row = blue_pixel * width + padding
            with tempfile.NamedTemporaryFile(suffix='.bmp', delete=False) as f:
                f.write(bmp_header)
                for _ in range(height):
                    f.write(row)
                temp_path = f.name
            media_id = self.upload_image(temp_path)
            os.unlink(temp_path)
            return media_id
        except Exception as e:
            self.log(f"❌ 默认封面生成失败：{e}")
            return None

    def upload_draft(self, title: str, content: str, author: str = None, digest: str = "", thumb_media_id: str = None) -> Optional[str]:
        if not self.access_token:
            self.log("❌ 请先获取 access_token")
            return None
        self.log(f"📝 正在上传草稿：{title}")
        url = f"{self.base_url}/draft/add?access_token={self.access_token}"
        safe_title = title[:64] if len(title) > 64 else title
        safe_digest = digest[:120] if digest and len(digest) > 120 else (digest or "")
        payload = {
            "articles": [{
                "title": safe_title,
                "author": author or "佳佳子",
                "digest": safe_digest,
                "content": content,
                "content_source_url": "",
                "thumb_media_id": thumb_media_id,
                "show_cover_pic": 1,
                "need_open_comment": 0,
                "only_fans_can_comment": 0,
            }]
        }
        try:
            response = requests.post(
                url,
                data=json.dumps(payload, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'},
                timeout=30,
            )
            data = response.json()
            if data.get("media_id"):
                media_id = data["media_id"]
                self.log(f"✅ 草稿上传成功！media_id: {media_id}")
                return media_id
            self.log(f"❌ 草稿上传失败：{data.get('errcode')} - {data.get('errmsg')}")
            return None
        except Exception as e:
            self.log(f"❌ 请求失败：{e}")
            return None

    def markdown_to_html(self, markdown: str) -> str:
        lines = markdown.split('\n')
        html_parts = []
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith('# '):
                html_parts.append(f'<section style="font-size:20px;font-weight:bold;margin:20px 0 10px;color:#333;">{line[2:]}</section>')
            elif line.startswith('## '):
                html_parts.append(f'<section style="font-size:18px;font-weight:bold;margin:16px 0 8px;color:#333;">{line[3:]}</section>')
            elif line.startswith('### '):
                html_parts.append(f'<section style="font-size:16px;font-weight:bold;margin:12px 0 6px;color:#333;">{line[4:]}</section>')
            elif line.startswith('> '):
                html_parts.append(f'<section style="border-left:4px solid #ddd;padding-left:12px;margin:12px 0;color:#666;font-style:italic;">{line[2:]}</section>')
            elif line.startswith('- ') or line.startswith('* '):
                html_parts.append(f'<section style="margin:6px 0;padding-left:20px;">• {line[2:]}</section>')
            else:
                html_parts.append(f'<section style="font-size:17px;line-height:1.75;color:#333;margin:12px 0;word-break:break-word;">{line}</section>')
        return '\n'.join(html_parts)

    def publish_from_markdown(self, markdown_file: str, title: str = None, author: str = "佳佳子", no_cover: bool = True, image: str = None) -> Optional[str]:
        if not os.path.exists(markdown_file):
            self.log(f"❌ 文件不存在：{markdown_file}")
            return None
        with open(markdown_file, 'r', encoding='utf-8') as f:
            content = f.read()
        if not title:
            for line in content.split('\n'):
                if line.startswith('# '):
                    title = line[2:].strip()
                    break
            if not title:
                title = os.path.basename(markdown_file).replace('.md', '')

        if not self.get_access_token():
            return None
        thumb_media_id = None
        if image and os.path.exists(image):
            thumb_media_id = self.upload_image(image)
        elif no_cover:
            self.log("📌 使用默认封面...")
            thumb_media_id = self.upload_default_cover()

        html_content = self.markdown_to_html(content)
        return self.upload_draft(title=title, content=html_content, author=author, digest="", thumb_media_id=thumb_media_id)


def load_config(path: str = CONFIG_PATH) -> dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def main():
    parser = argparse.ArgumentParser(description='微信公众号草稿助手（本地安全版）')
    parser.add_argument('--appid', type=str, help='微信公众号 AppID')
    parser.add_argument('--secret', type=str, help='微信公众号 AppSecret')
    parser.add_argument('--article', type=str, metavar='FILE', help='Markdown 文章文件路径')
    parser.add_argument('--title', type=str, metavar='TITLE', help='文章标题')
    parser.add_argument('--content', type=str, metavar='CONTENT', help='文章内容（HTML）')
    parser.add_argument('--author', type=str, default=None, help='作者名')
    parser.add_argument('--image', type=str, metavar='IMAGE_FILE', help='自定义封面图片路径')
    parser.add_argument('--no-cover', action='store_true', help='使用默认封面')
    parser.add_argument('--quiet', action='store_true', help='静默模式')
    parser.add_argument('--check-token', action='store_true', help='只检查 access_token 是否可获取')
    args = parser.parse_args()

    cfg = load_config()
    appid = args.appid or cfg.get('appid')
    secret = args.secret or cfg.get('secret')
    author = args.author or cfg.get('author') or '佳佳子'
    if not appid or not secret:
        print('❌ 缺少 appid/secret，请通过参数或 config 提供')
        sys.exit(1)

    publisher = WeChatPublisher(appid, secret, quiet=args.quiet)

    if args.check_token:
        ok = publisher.get_access_token()
        print('TOKEN_OK' if ok else 'TOKEN_FAIL')
        return

    if args.article:
        media_id = publisher.publish_from_markdown(args.article, title=args.title, author=author, no_cover=args.no_cover or True, image=args.image)
        print(f'MEDIA_ID={media_id}' if media_id else 'PUBLISH_FAIL')
        return

    if args.title and args.content:
        if not publisher.get_access_token():
            print('PUBLISH_FAIL')
            return
        thumb_media_id = None
        if args.image and os.path.exists(args.image):
            thumb_media_id = publisher.upload_image(args.image)
        elif args.no_cover:
            thumb_media_id = publisher.upload_default_cover()
        media_id = publisher.upload_draft(title=args.title, content=args.content, author=author, thumb_media_id=thumb_media_id)
        print(f'MEDIA_ID={media_id}' if media_id else 'PUBLISH_FAIL')
        return

    print('❌ 请提供 --article 或 --title + --content')
    sys.exit(1)


if __name__ == '__main__':
    main()
