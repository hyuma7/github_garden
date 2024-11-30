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
    page.title = "Github_garden"
    page.window.width = 400
    page.window.height = 600  # 高さを増加
    page.padding = 20
    
    # UIコンポーネント
    title = ft.Text("今日のGithubのお庭", size=24, weight=ft.FontWeight.BOLD)
    
    # 初期状態では画像コンポーネントは作成しない
    image_container = ft.Container(height=200)  # 画像用のプレースホルダー

    # 追加: 日付と画像レベルを表示するテキストフィールド
    info_text = ft.Text(value="", size=14, color="gray")
    
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
    
    # 追加: dateとgarden_levelを初期化
    date = ""
    garden_level = 0
    
    # 画像生成処理
    def generate_clicked(e):
        nonlocal result_image
        nonlocal current_image_path
        nonlocal date
        nonlocal garden_level
        print("画像生成ボタンがクリックされました")  # デバッグログ
        generate_btn.disabled = True
        generate_btn.text = "生成中..."
        page.update()
        
        try:
            print("GitHubの貢献情報を取得中...")  # デバッグログ
            contributions: dict = get_github_contributions()
            last_contribution_count = int(contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-1]['contributionDays'][-1]['contributionCount'])
            date = contributions['data']['user']['contributionsCollection']['contributionCalendar']['weeks'][-1]['contributionDays'][-1]['date']
            print(f"最終貢献数: {last_contribution_count}, 日付: {date}")  # デバッグログ
            
            result_image_url = generate_garden(last_contribution_count, date)
            print(f"生成された画像URL: {result_image_url}")  # デバッグログ
            
            # 生成された画像のローカルパスを作成
            image_path = os.path.join(os.path.dirname(__file__), "images", f"generated_image_{date}.png")
            current_image_path = image_path  # パスを保存
            
            new_image = ft.Image(
                src=image_path,
                width=360,
                height=200,
                fit=ft.ImageFit.CONTAIN
            )
            
            image_container.content = new_image
            page.update()
            
            result_image = result_image_url
            share_btn.disabled = False
            
            # 情報テキストの更新
            garden_level = min(last_contribution_count, 5)
            info_text.value = f"日付: {date} | 画像レベル: {garden_level}"
            
            # おめでとうメッセージの追加
            congratulations = ft.Text(
                value="おめでとうございます！\n今日もお疲れさまでした。",
                size=16,
                color="green",
                weight=ft.FontWeight.BOLD
            )
            page.controls.append(congratulations)
            page.update()
            
            print("画像生成完了")  # デバッグログ
        except Exception as err:
            result_text.value = f"エラーが発生しました: {str(err)}"
            result_image = None
            current_image_path = None
            print(f"��ラー: {str(err)}")  # デバッグログ
        finally:
            generate_btn.disabled = False
            generate_btn.text = "お庭を生成"
            page.update()

    # Xでシェア
    def share_clicked(e):
        if current_image_path:
            # URLエンコードを使用して日本語テキストを適切に処理
            tweet_text = urllib.parse.quote(
                f"【今日のお庭】\n\n日付: {date}\n画像レベル: {garden_level}\nGitHubの今日のお庭です:\n#GitHubお庭 #AIお庭ジェネレーター \n\n{result_image}"
            )
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
                ft.Container(height=10),
                info_text,  # 追加: 情報テキストを追加
                ft.Container(height=20),
                share_btn
            ],
            spacing=0,
            alignment=ft.MainAxisAlignment.START
        )
    )

if __name__ == '__main__':
    ft.app(target=main)