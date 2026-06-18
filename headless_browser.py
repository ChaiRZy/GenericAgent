"""
后台独立浏览器工具 - 用于本地原型截图（无需登录态的场景）
底层用Selenium + headless Chrome，完全独立于用户浏览器

使用场景:
  - ✅ 本地原型截图 (localhost)
  - ✅ 无需登录的公开网页
  - ⚠️ 需要登录态的系统 → 回退用 tmwebDriver（用户浏览器插件）

原理：
  启动独立 Chrome 进程（头less或有头），通过 Selenium 操控，
  与你正在使用的 Chrome 完全隔离，互不干扰。
"""
import os, subprocess, time, atexit, base64
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 独立用户数据目录，不干扰你的Chrome
USER_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_data")


class HeadlessBrowser:
    """后台独立浏览器"""

    def __init__(self, headless=True, window_size=(1920, 1080)):
        self.driver = None
        self.headless = headless
        self.window_size = window_size

    def start(self):
        if self._is_running():
            return True
        options = Options()
        if self.headless:
            options.add_argument('--headless=new')
        options.add_argument('--no-first-run')
        options.add_argument('--no-default-browser-check')
        options.add_argument('--disable-gpu')
        options.add_argument(f'--window-size={self.window_size[0]},{self.window_size[1]}')
        options.add_argument(f'--user-data-dir={USER_DATA_DIR}')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-sync')
        # 确保中文显示
        options.add_argument('--lang=zh-CN')
        options.add_experimental_option('prefs', {
            'intl.accept_languages': 'zh-CN,zh',
        })

        self.driver = webdriver.Chrome(options=options)
        print(f"HeadlessBrowser started (headless={self.headless})")
        return True

    def _is_running(self):
        if self.driver is None:
            return False
        try:
            _ = self.driver.title
            return True
        except:
            return False

    def navigate(self, url, wait_sec=2):
        """访问URL"""
        self.driver.get(url)
        time.sleep(wait_sec)
        return True

    def execute_js(self, code):
        """执行JS，返回结果"""
        return self.driver.execute_script(code)

    def get_page_size(self):
        """获取页面实际尺寸"""
        w = self.driver.execute_script(
            "return Math.max(document.documentElement.scrollWidth, document.body.scrollWidth)")
        h = self.driver.execute_script(
            "return Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)")
        return w, h

    def screenshot_fullpage(self, output_path=None):
        """
        全页截图
        返回: PIL Image对象（若output_path则同时保存文件）
        """
        w, h = self.get_page_size()
        # 需要先设置窗口适应全页
        self.driver.set_window_size(w, h)
        time.sleep(0.3)

        png_data = self.driver.get_screenshot_as_png()

        from PIL import Image
        import io
        img = Image.open(io.BytesIO(png_data))

        if output_path:
            img.save(output_path)
            print(f"  Screenshot saved: {output_path} ({img.size[0]}x{img.size[1]}, {os.path.getsize(output_path)//1024}KB)")

        # 恢复窗口
        self.driver.set_window_size(*self.window_size)
        return img

    def screenshot_visible(self, output_path=None):
        """可见区域截图"""
        png_data = self.driver.get_screenshot_as_png()

        if output_path:
            with open(output_path, 'wb') as f:
                f.write(png_data)
            print(f"  Screenshot saved: {output_path} ({os.path.getsize(output_path)//1024}KB)")

        from PIL import Image
        import io
        return Image.open(io.BytesIO(png_data))

    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args):
        self.close()


# ========== 全局单例 ==========
_global_browser = None

def get_browser(headless=True):
    global _global_browser
    if _global_browser is None:
        _global_browser = HeadlessBrowser(headless=headless)
        _global_browser.start()
        atexit.register(_global_browser.close)
    return _global_browser


if __name__ == '__main__':
    # 测试
    with HeadlessBrowser(headless=False) as b:
        b.navigate("http://127.0.0.1:5501/index.html", wait_sec=3)
        img = b.screenshot_visible("test_visible.png")
        print(f"Visible area: {img.size}")
        img = b.screenshot_fullpage("test_fullpage.png")
        print(f"Full page: {img.size}")
        print("✅ Test OK")
