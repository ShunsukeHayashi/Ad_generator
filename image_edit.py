import os
import base64
import unicodedata
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

# APIキーの確認
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    print("Environment variable OPENAI_API_KEY is not set. Set it with the following command:")
    print("export OPENAI_API_KEY='your-api-key'")
    exit(1)

# OpenAI クライアントの初期化
client = OpenAI()

def normalize_text(text):
    """テキストをUnicode正規化する"""
    return unicodedata.normalize('NFC', text)

def encode_image_to_base64(image_path):
    """画像をbase64エンコードする"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def edit_image(image_path, edit_prompt, output_path=None):
    """
    画像を編集する関数
    
    Args:
        image_path (str): 編集する画像のパス
        edit_prompt (str): 編集指示プロンプト
        output_path (str, optional): 出力先のパス。Noneの場合はデフォルトパスを使用
    
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    # 画像が存在するか確認
    if not os.path.exists(image_path):
        print(f"Source image {image_path} not found.")
        return False
    
    # 出力パスが指定されていない場合のデフォルト設定
    if not output_path:
        output_path = "imgs/edited_image.jpg"
    
    try:
        print("Starting image editing...")
        
        # プロンプトの正規化
        normalized_prompt = normalize_text(edit_prompt)
        
        # GPT-4 Vision APIを使用して画像を編集
        try:
            # 画像ファイルを開く
            with open(image_path, "rb") as image_file:
                # OpenAI APIへのリクエスト
                response = client.images.edit(
                    model="gpt-image-1",
                    image=image_file,
                    prompt=normalized_prompt,
                    size="1024x1024"
                )
            
            # 編集後の画像を保存
            if hasattr(response.data[0], "url") and response.data[0].url:
                # URLから画像をダウンロードして保存
                import requests
                img_url = response.data[0].url
                img_response = requests.get(img_url)
                
                if img_response.status_code == 200:
                    with open(output_path, "wb") as f:
                        f.write(img_response.content)
                    print(f"Image editing completed and saved to {output_path}.")
                    return True
                else:
                    print(f"Failed to download image: {img_response.status_code}")
                    return False
            
            # Base64データがある場合
            elif hasattr(response.data[0], "b64_json") and response.data[0].b64_json:
                image_base64 = response.data[0].b64_json
                image_bytes = base64.b64decode(image_base64)
                
                # 編集後の画像を保存
                edited_image = Image.open(BytesIO(image_bytes))
                edited_image.save(output_path, format="JPEG", quality=95)
                
                print(f"Image editing completed and saved to {output_path}.")
                return True
            else:
                print("No image data found in the response.")
                return False
            
        except Exception as e:
            print(f"Error with edit API: {e}")
            print("Trying alternative approach with image generation API...")
            
            # APIの仕様が異なる場合のフォールバックとして、images.generateを使用
            revised_prompt = f"Edit this image: {normalized_prompt}"
            
            response = client.images.generate(
                model="gpt-image-1",
                prompt=revised_prompt,
                size="1024x1024",
                quality="high"
            )
            
            # 生成された画像を保存
            image_url = response.data[0].url
            
            # URLから画像をダウンロードして保存
            import requests
            response = requests.get(image_url)
            if response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(response.content)
                print(f"Alternative image generation completed and saved to {output_path}.")
                return True
            else:
                print(f"Failed to download image: {response.status_code}")
                return False
            
    except Exception as e:
        print(f"Error occurred: {e}")
        return False

def apply_text_to_image(image_path, text_content, output_path=None):
    """
    画像にテキストをオーバーレイする関数
    
    Args:
        image_path (str): 編集する画像のパス
        text_content (dict): テキスト内容の辞書（例: {"title": "タイトル", "subtitle": "サブタイトル"}）
        output_path (str, optional): 出力先のパス。Noneの場合はデフォルトパスを使用
    
    Returns:
        bool: 成功した場合はTrue、失敗した場合はFalse
    """
    try:
        # 画像が存在するか確認
        if not os.path.exists(image_path):
            print(f"Source image {image_path} not found.")
            return False
        
        # 出力パスが指定されていない場合のデフォルト設定
        if not output_path:
            output_path = "imgs/text_overlay.jpg"
        
        # 画像の読み込み
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # デフォルトフォント（システムにインストールされているフォントを使用）
        try:
            title_font = ImageFont.truetype("Arial", 40)
            normal_font = ImageFont.truetype("Arial", 30)
        except IOError:
            # フォントが見つからない場合はデフォルトフォントを使用
            title_font = ImageFont.load_default()
            normal_font = ImageFont.load_default()
        
        # テキストの描画
        y_position = 50  # 開始位置
        
        if "title" in text_content:
            # テキストの正規化
            title_text = normalize_text(text_content["title"])
            draw.text((50, y_position), title_text, fill="white", font=title_font, stroke_width=2, stroke_fill="black")
            y_position += 60
        
        if "subtitle" in text_content:
            # テキストの正規化
            subtitle_text = normalize_text(text_content["subtitle"])
            draw.text((50, y_position), subtitle_text, fill="white", font=normal_font, stroke_width=1, stroke_fill="black")
            y_position += 40
            
        if "description" in text_content:
            # テキストの正規化
            description = normalize_text(text_content["description"])
            
            # 長いテキストは複数行に分割
            words = description.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + word + " "
                if len(test_line) > 40:  # 1行の最大文字数
                    lines.append(current_line)
                    current_line = word + " "
                else:
                    current_line = test_line
            
            if current_line:
                lines.append(current_line)
            
            for line in lines:
                draw.text((50, y_position), line, fill="white", font=normal_font, stroke_width=1, stroke_fill="black")
                y_position += 35
        
        # 画像の保存
        img.save(output_path)
        print(f"Text overlay completed and saved to {output_path}.")
        return True
        
    except Exception as e:
        print(f"Error occurred during text overlay: {e}")
        return False

def main():
    # 編集元の画像ファイルパス
    source_image_path = "imgs/provision_ad.jpg"
    
    # 編集指示プロンプト
    edit_prompt = """
    Edit this advertisement to add a dark mode version:
    - Change the background to a dark blue gradient
    - Make the text white for better contrast
    - Add a subtle glow effect to the visual elements
    - Keep all the original text and layout
    - Maintain the professional and modern feeling but with a night/dark theme
    """
    
    # 画像の編集
    edit_image(source_image_path, edit_prompt, "imgs/provision_ad_dark.jpg")
    
    # テキストオーバーレイのデモ - 英語バージョン
    text_content_en = {
        "title": "Test Ad Title",
        "subtitle": "Subtitle: Image Test",
        "description": "This is a demo for text overlay. Long text will be automatically split into multiple lines."
    }
    
    apply_text_to_image(source_image_path, text_content_en, "imgs/text_overlay_demo_en.jpg")
    
    # 日本語テキストのテスト - ファイル名は英語に
    text_content_jp = {
        "title": "テスト広告タイトル",
        "subtitle": "サブタイトル: 画像テスト",
        "description": "これはテキストオーバーレイのデモです。長い文章も自動的に複数行に分割されます。"
    }
    
    apply_text_to_image(source_image_path, text_content_jp, "imgs/text_overlay_demo_jp.jpg")

if __name__ == "__main__":
    main() 