import unittest

# 导入您的Dash应用
from player import app

class TestDashApp(unittest.TestCase):

    def setUp(self):
        # 创建Dash应用的测试客户端
        self.app = app.server
        self.client = self.app.test_client()

    def test_media_file_selection(self):
        # 模拟用户选择一个媒体文件
        response = self.client.get("/", data={'media_file_name': 'your_media_file_name.mp4'})
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
