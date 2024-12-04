import flet as ft
import webbrowser
from dotenv import load_dotenv
from image_generator import ImageGenerator, GardenPrompts
from github_connector import get_github_contributions
import urllib.parse
import logging
import os
from datetime import datetime

# ロギングの設定
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

log_file = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()
logger.info("Environment variables loaded")

class GardenApp:
    def __init__(self):
        logger.info("Initializing GardenApp")
        self.result_image_url = None
        self.current_image_path = None
        self.image_generator = ImageGenerator()

    def generate_garden(self, last_contribution_count, date) -> str:
        logger.info(f"Generating garden for date: {date} with contribution count: {last_contribution_count}")
        garden_level = min(last_contribution_count, 5)
        garden_prompt = GardenPrompts.get_prompt(garden_level)
        logger.debug(f"Using garden prompt for level {garden_level}")
        image_url = self.image_generator.generate_image(garden_prompt, date)
        return image_url

    def build_ui(self, page: ft.Page):
        logger.info("Building UI components")
        # ページ設定
        page.title = "AIお庭ジェネレーター"
        page.window.width = 400
        page.window.height = 500
        page.padding = 20
        
        # UIコンポーネント
        self.title = ft.Text("AIお庭ジェネレーター", size=24, weight=ft.FontWeight.BOLD)
        self.image_container = ft.Container(height=200)
        
        self.generate_btn = ft.ElevatedButton(
            text="お庭生成",
            width=360,
            on_click=self.generate_clicked
        )
        
        self.share_btn = ft.ElevatedButton(
            text="Xでシェア",
            width=360,
            on_click=self.share_clicked,
            disabled=True
        )

        # レイアウトの構築
        page.add(
            ft.Column(
                controls=[
                    self.title,
                    ft.Container(height=20),
                    self.generate_btn,
                    ft.Container(height=20),
                    self.image_container,
                    ft.Container(height=20),
                    self.share_btn
                ],
                spacing=0,
                alignment=ft.MainAxisAlignment.START
            )
        )
        logger.info("UI components built successfully")

    def generate_clicked(self, e):
        logger.info("Generate button clicked")
        self.generate_btn.disabled = True
        self.generate_btn.text = "生成中..."
        e.page.update()
        
        try:
            # GitHubの貢献情報を取得
            logger.info("Fetching GitHub contributions")
            contributions: dict = get_github_contributions()
            last_contribution_count = int(contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-1]['contributionDays'][-1]['contributionCount'])
            date = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-1]['contributionDays'][-1]['date']
            logger.info(f"Retrieved contributions for date: {date}")
            
            # 画像を生成
            self.result_image_url = self.generate_garden(last_contribution_count, date)
            logger.info("Image generated successfully")
            
            # 生成された画像のローカルパスを作成
            current_path = os.path.dirname(os.path.abspath(__file__))
            self.current_image_path = os.path.join(current_path, f"images/generated_image_{date}.png")
            logger.debug(f"Image path: {self.current_image_path}")
            
            new_image = ft.Image(
                src=self.current_image_path,
                width=360,
                height=200,
                fit=ft.ImageFit.CONTAIN
            )
            
            # コンテナの中身を更新
            self.image_container.content = new_image
            self.share_btn.disabled = False
            logger.info("UI updated with new image")
            
        except Exception as err:
            logger.error(f"Error generating garden: {str(err)}", exc_info=True)
            self.result_image_url = None
            self.current_image_path = None
            
        finally:
            self.generate_btn.disabled = False
            self.generate_btn.text = "お庭を生成"
            e.page.update()
            logger.info("Generate button restored to initial state")

    def share_clicked(self, e):
        logger.info("Share button clicked")
        if self.current_image_path:
            tweet_text = urllib.parse.quote(f"【今日のお庭】\n\nGitHubの今日のお庭です:\n#GitHubお庭 #AIお庭ジェネレーター \n\n{self.result_image_url}")
            url = f"https://twitter.com/intent/tweet?text={tweet_text}"
            webbrowser.open(url)
            logger.info("Opened share URL in browser")
        else:
            logger.warning("Share attempted but no image path available")

def main(page: ft.Page):
    logger.info("Starting application")
    app = GardenApp()
    app.build_ui(page)

if __name__ == '__main__':
    ft.app(target=main)