import os
import requests
from openai import OpenAI


#プロンプトリスト
class GardenPrompts:
    PROMPTS = [
        "A desolate garden with dry, cracked soil and withered plants, scattered dead leaves, and an old, broken wooden bench. The trees are bare, and the atmosphere feels abandoned and lifeless, under a cloudy and overcast sky.",
        "A modest garden showing signs of recovery, with a few patches of green grass and small budding plants. The wooden bench has been cleaned up, and a light drizzle creates a refreshing atmosphere under a slightly clearer sky.",
        "A neat garden with evenly trimmed grass, blooming flowers in pastel colors, and a small stone path leading to a clean wooden bench. A gentle sunlight filters through the partially cloudy sky, bringing warmth to the scene.",
        "A vibrant garden filled with a variety of colorful flowers, lush green grass, and a well-maintained pond with clear water. Butterflies and birds flutter around, and a small gazebo stands in the center, surrounded by neatly arranged flower beds under a sunny sky.",
        "An extravagant garden with cascading fountains, intricately designed flower beds, and exotic plants. Marble pathways wind through the area, leading to a luxurious seating area adorned with elegant sculptures. The sky is bright and clear, enhancing the opulence of the garden.",
        "A magical garden bursting with life and vibrant colors, featuring adorable creatures like a chubby squirrel wearing a tiny hat, a playful bunny with a flower crown, and a cheerful bird holding a tiny envelope in its beak. The garden has sparkling ponds, glowing flowers, and a whimsical treehouse, creating a fairytale-like atmosphere under a radiant sky."
    ]

    @staticmethod
    def get_prompt(index):
        if 0 <= index < len(GardenPrompts.PROMPTS):
            return GardenPrompts.PROMPTS[index]
        else:
            raise ValueError("Invalid prompt index. Please choose a number between 0 and 5.")


class ImageGenerator:
    def __init__(self):
        # OpenAI clientの初期化
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_image(self, prompt, date) -> str:
        # GPT-4を使用して画像を生成
        response = self.client.images.generate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        
        if response and hasattr(response, 'data') and response.data:
            image_url = response.data[0].url
            self.save_image(image_url, f"generated_image_{date}.png")
            return image_url
        else:
            raise Exception("画像生成に失敗しました")

    def save_image(self, url, filename):
        # 画像をダウンロードして保存
        response = requests.get(url)
        if response.status_code == 200:
            image_path = os.path.join("/Users/hattorihyuma/Desktop/projects/植物inflet/images", filename)
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"Image saved to {image_path}")
        else:
            raise Exception("画像のダウンロードに失敗しました")


if __name__ == "__main__":
    generator = ImageGenerator()
    image_url = generator.generate_image("A beautiful landscape with a river and mountains in the background")
    print(image_url)
