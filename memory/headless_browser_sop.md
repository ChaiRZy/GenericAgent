# HeadlessBrowser SOP

## 用途
后台独立 Chrome 浏览器（Selenium + headless），**不需要用户登录态**的场景。

## 与 tmwebDriver 的对比

| 特性 | HeadlessBrowser | tmwebDriver |
|------|----------------|-------------|
| 浏览器 | 后台独立 Chrome | 用户正在用的 Chrome |
| 影响用户 | ❌ 零影响 | ⚠️ 可能冲突 |
| 需要插件 | ❌ 不需要 | ✅ tmwd_cdp_bridge 扩展 |
| 登录态 | ❌ 无（空白浏览器） | ✅ 继承你的 Cookie |
| 截图方式 | Selenium 原生截图 | html2canvas / CDP |
| 适合场景 | 本地原型、公开网页 | OA/内网等需登录的系统 |

## 快速开始

```python
from headless_browser import HeadlessBrowser

# 方式一：上下文管理器（推荐）
with HeadlessBrowser(headless=True) as b:
    b.navigate("http://127.0.0.1:5501/index.html", wait_sec=3)
    img = b.screenshot_fullpage("output.png")
    
# 方式二：全局单例（长时间复用）
from headless_browser import get_browser
b = get_browser(headless=True)
b.navigate("http://example.com")
title = b.execute_js("return document.title")
```

## 常用方法

| 方法 | 说明 |
|------|------|
| `navigate(url, wait_sec=2)` | 访问页面 |
| `execute_js(code)` | 执行 JS 并返回结果 |
| `screenshot_fullpage(path)` | 全页截图（自动调整窗口高度） |
| `screenshot_visible(path)` | 可见区域截图 |
| `get_page_size()` | 获取页面实际宽高 |

## 注意事项
- headless=True 时看不到窗口；headless=False 可观察操作过程
- 第一次启动会创建 chrome_data 目录用于缓存
- 如果本地原型更新了，需要重新 navigate 刷新页面
