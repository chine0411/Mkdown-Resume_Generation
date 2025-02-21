import os
import shutil
from dotenv import load_dotenv


class StaticResourceManager:
    """静态资源路径管理类"""

    def __init__(self, project_root: str):
        self.project_root = project_root
        self.load_env()

        # 静态资源目录配置
        self.static_dir = os.path.join(self.project_root, "static")
        self.base_url = os.getenv("STATIC_BASE_URL", "/static/")  # 可通过环境变量配置

    def load_env(self):
        """加载环境变量配置"""
        load_dotenv()  # 自动加载 .env 文件

    def get_resource_url(self, resource_type: str, filename: str) -> str:
        """生成静态资源URL"""
        return f"{self.base_url}{resource_type}/{filename}"

    def get_filesystem_path(self, resource_type: str, filename: str) -> str:
        """获取静态资源文件系统路径"""
        return os.path.join(self.static_dir, resource_type, filename)

    def copy_resources(self, output_dir: str):
        """将静态资源复制到输出目录"""
        static_assets = {
            "css": ["template1.css"],
            "images": ["profile_pic.jpg", "logo.png"],
            "fonts": ["roboto.ttf", "iconfont.ttf"]
        }

        for folder, files in static_assets.items():
            dest_path = os.path.join(output_dir, folder)
            os.makedirs(dest_path, exist_ok=True)

            for file in files:
                src_path = self.get_filesystem_path(folder, file)
                if not os.path.exists(src_path):
                    print(f"警告: 资源文件缺失 - {src_path}")
                    continue

                dest_path = os.path.join(dest_path, file)
                try:
                    shutil.copy(src_path, dest_path)
                    print(f"已复制: {src_path} → {dest_path}")
                except Exception as e:
                    print(f"复制错误: {e}")

    @staticmethod
    def get_project_root() -> str:
        """获取项目根目录路径"""
        return os.path.dirname(os.path.abspath(__file__))


# 创建全局实例（可选）
static_manager = StaticResourceManager(StaticResourceManager.get_project_root())
