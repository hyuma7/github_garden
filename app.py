import flet as ft
import webbrowser
from dotenv import load_dotenv
import os
from image_generater import ImageGenerator, GardenPrompts
from github_connector import get_github_contributions
import urllib.parse

# 環境変数の読み込み
load_dotenv()

def generate_garden(last_contribution_count, date) -> str:
    # GPT-4を使用してダジャレを生成
    generator = ImageGenerator()
    # お庭のレベルを決定（例として貢献数に基づく）
    garden_level = min(last_contribution_count, 5)
    garden_prompt = GardenPrompts.get_prompt(garden_level)
    
    image_url = generator.generate_image(garden_prompt, date)
    
    return image_url


def main(page: ft.Page):
    # ページ設定
    page.title = "AIお庭ジェネレーター"
    page.window.width = 400
    page.window.height = 500
    page.padding = 20
    
    # UIコンポーネント
    title = ft.Text("AIお庭ジェネレーター", size=24, weight=ft.FontWeight.BOLD)
    
    # 初期状態では画像コンポーネントは作成しない
    image_container = ft.Container(height=200)  # 画像用のプレースホルダー

    result_text = ft.TextField(
        label="生成結果",
        read_only=True,
        multiline=True,
        min_lines=2,
        width=360
    )
    
    # result_imageをグローバルスコープで定義
    result_image = None
    
    # 画像パスを保持する変数を追加
    current_image_path = None
    
    # 画像生成処理
    def generate_clicked(e):
        nonlocal result_image  # result_imageを関数内で使用できるように宣言
        nonlocal current_image_path  # image_pathを関数内で使用できるように宣言
        generate_btn.disabled = True
        generate_btn.text = "生成中..."
        page.update()
        
        try:
            # GitHubの貢献情報を取得
            contributions: dict = get_github_contributions()
            last_contribution_count = int(contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-1]['contributionDays'][-1]['contributionCount'])
            date = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-1]['contributionDays'][-1]['date']
            
            # 画像を生成
            result_image_url = generate_garden(last_contribution_count, date)
            
            # 生成された画像のローカルパスを作成
            image_path = f"/Users/hattorihyuma/Desktop/projects/植物inflet/images/generated_image_{date}.png"
            current_image_path = image_path  # パスを保存
            
            # 新しい画像コンポーネントを作成
            new_image = ft.Image(
                src=image_path,
                width=360,
                height=200,
                fit=ft.ImageFit.CONTAIN
            )
            
            # コンテナの中身を更新
            image_container.content = new_image
            page.update()
            
            # result_imageを更新
            result_image = result_image_url  # generate_garden()の戻り値を保存
            
            # シェアボタンを有効化
            share_btn.disabled = False
        except Exception as err:
            result_text.value = f"エラーが発生しました: {str(err)}"
            result_image = None  # エラー時はリセット
            current_image_path = None  # エラー時はリセット
        finally:
            generate_btn.disabled = False
            generate_btn.text = "お庭を生成"
            page.update()

    # Xでシェア
    def share_clicked(e):
        if current_image_path:
            # URLエンコードを使用して日本語テキストを適切に処理
            tweet_text = urllib.parse.quote(f"【今日のお庭】\n\nGitHubの今日のお庭です:\n#GitHubお庭 #AIお庭ジェネレーター \n\n{result_image}")
            url = f"https://twitter.com/intent/tweet?text={tweet_text}"
            webbrowser.open(url)

    # ボタンの作成
    generate_btn = ft.ElevatedButton(
        text="お庭生成",
        width=360,
        on_click=generate_clicked
    )
    
    share_btn = ft.ElevatedButton(
        text="Xでシェア",
        width=360,
        on_click=share_clicked,
        disabled=True  # 初期状態は無効
    )

    # レイアウトの構築
    page.add(
        ft.Column(
            controls=[
                title,
                ft.Container(height=20),
                generate_btn,
                ft.Container(height=20),
                image_container,  # 画像コンテナを追加
                ft.Container(height=20),
                share_btn
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START
        )
    )

if __name__ == '__main__':
    ft.app(target=main)