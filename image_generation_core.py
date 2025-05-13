#!/usr/bin/env python3
"""
画像生成コアモジュール
OpenAI GPT-Image-1を使用した画像生成の中核機能を提供
"""

import os
import sys
import json
import logging
import base64
import requests
import unicodedata
from datetime import datetime
from pathlib import Path
from openai import OpenAI

# 自作モジュールのインポート
from utils import generate_timestamp_filename, ensure_directory, save_image_from_url, save_image_from_base64

# ロギング設定 - デフォルトエンコーディングを設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding='utf-8'  # エンコーディングを明示的に設定
)
logger = logging.getLogger(__name__)

# エンコーディング問題のワークアラウンド
import locale
if locale.getpreferredencoding() == 'ASCII':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

class ImageGenerationCore:
    """
    画像生成の中核機能を提供するクラス
    OpenAI GPT-Image-1を使用して画像を生成する
    """
    
    def __init__(self, api_key=None):
        """
        初期化メソッド
        
        Args:
            api_key (str, optional): OpenAI APIキー。指定しない場合は環境変数から取得
        """
        # APIキーの設定
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        # OpenAIクライアントの初期化
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            self.client = None
            logger.warning("API key is not set. Please use validate_api_key() to verify.")
    
    def validate_api_key(self):
        """
        APIキーの有効性を確認するメソッド
        
        Returns:
            bool: APIキーが有効な場合はTrue、無効な場合はFalse
        """
        if not self.api_key:
            logger.error("API key is not set")
            return False
        
        # APIキーが設定されている場合はクライアントを初期化
        if not self.client:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error("Failed to initialize OpenAI client: {}".format(e))
                return False
        
        return True
    
    def normalize_text(self, text):
        """
        日本語テキストの正規化を行うメソッド
        
        Args:
            text (str): 正規化するテキスト
            
        Returns:
            str: 正規化されたテキスト
        """
        # Unicode正規化フォームNFCを使用
        return unicodedata.normalize('NFC', text)
    
    def generate_image(self, prompt, model="gpt-image-1", size="1024x1024", quality="high", style=None, n=1):
        """
        画像を生成するメソッド
        
        Args:
            prompt (str): 画像生成のためのプロンプト
            model (str, optional): 使用するモデル。デフォルトは"gpt-image-1"
            size (str, optional): 画像サイズ。デフォルトは"1024x1024"
            quality (str, optional): 画像品質。デフォルトは"high"
            style (str, optional): 画像スタイル。デフォルトはNone
            n (int, optional): 生成する画像の数。デフォルトは1
        
        Returns:
            tuple: (画像データのリスト, 画像URLのリスト, メッセージ)
        """
        # APIキーの確認
        if not self.validate_api_key():
            return [], [], "Invalid API key"
        
        # プロンプトの正規化
        normalized_prompt = self.normalize_text(prompt)
        
        # 画像生成パラメータの設定
        params = {
            "model": model,
            "prompt": normalized_prompt,
            "n": n,
            "size": size,
            "quality": quality
        }
        
        # スタイルが指定されている場合は追加
        if style:
            params["style"] = style
        
        try:
            # 画像生成リクエスト
            logger.info("Starting image generation... (model: {})".format(model))
            response = self.client.images.generate(**params)
            
            # 結果の処理
            images = []
            urls = []
            
            for data in response.data:
                # URLの取得
                if hasattr(data, "url") and data.url:
                    urls.append(data.url)
                
                # Base64データの取得
                if hasattr(data, "b64_json") and data.b64_json:
                    images.append(data.b64_json)
            
            if urls:
                logger.info("Image generation completed. {} images were generated.".format(len(urls)))
                return images, urls, "Image generation completed. {} images were generated.".format(len(urls))
            else:
                logger.error("No image URLs found")
                return [], [], "No image URLs found"
                
        except Exception as e:
            logger.error("Error during image generation: {}".format(str(e)))
            import traceback
            traceback.print_exc()
            return [], [], "Error during image generation: {}".format(str(e))
    
    def save_images(self, images, urls=None, prefix="generated", output_dir="output"):
        """
        生成された画像を保存するメソッド
        
        Args:
            images (list): Base64エンコードされた画像データのリスト
            urls (list, optional): 画像URLのリスト。Base64データがない場合に使用
            prefix (str, optional): ファイル名の接頭辞。デフォルトは"generated"
            output_dir (str, optional): 出力ディレクトリ。デフォルトは"output"
        
        Returns:
            list: 保存されたファイルパスのリスト
        """
        # 出力ディレクトリの確認/作成
        ensure_directory(output_dir)
        
        saved_paths = []
        
        # Base64データから画像を保存
        for i, image_data in enumerate(images):
            try:
                # ファイル名の生成
                filename = generate_timestamp_filename("{}_{:02d}".format(prefix, i+1), "png")
                filepath = os.path.join(output_dir, filename)
                
                # 画像の保存
                if save_image_from_base64(image_data, filepath):
                    saved_paths.append(filepath)
                    logger.info("Image saved: {}".format(filepath))
            except Exception as e:
                logger.error("Error saving base64 image: {}".format(str(e)))
        
        # URLから画像を保存（Base64データがない場合）
        if not saved_paths and urls:
            for i, url in enumerate(urls):
                try:
                    # ファイル名の生成
                    filename = generate_timestamp_filename("{}_{:02d}".format(prefix, i+1), "png")
                    filepath = os.path.join(output_dir, filename)
                    
                    # 画像の保存
                    if save_image_from_url(url, filepath):
                        saved_paths.append(filepath)
                        logger.info("Image saved: {}".format(filepath))
                except Exception as e:
                    logger.error("Error saving URL image: {}".format(str(e)))
        
        return saved_paths
    
    def edit_image(self, image_path, prompt, model="gpt-image-1", size="1024x1024", quality="high"):
        """
        画像を編集するメソッド（将来的な拡張用）
        
        Args:
            image_path (str): 編集する画像のパス
            prompt (str): 編集のためのプロンプト
            model (str, optional): 使用するモデル。デフォルトは"gpt-image-1"
            size (str, optional): 画像サイズ。デフォルトは"1024x1024"
            quality (str, optional): 画像品質。デフォルトは"high"
        
        Returns:
            tuple: (画像データのリスト, 画像URLのリスト, メッセージ)
        """
        # 現在のGPT-Image-1では画像編集機能は提供されていないため、
        # 代わりに新しい画像を生成する
        logger.warning("Direct image editing is not supported in GPT-Image-1. Generating a new image instead.")
        
        # プロンプトの正規化
        normalized_prompt = self.normalize_text(prompt)
        
        # 元の画像の情報をプロンプトに追加
        enhanced_prompt = "Based on the original image: {}".format(normalized_prompt)
        
        # 新しい画像を生成
        return self.generate_image(enhanced_prompt, model, size, quality)

if __name__ == "__main__":
    # 動作テスト
    image_gen = ImageGenerationCore()
    
    # APIキーの確認
    if not image_gen.validate_api_key():
        logger.error("Invalid API key. Please check your OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # テストプロンプト
    test_prompt = """
    Create a simple test image with a blue background and a yellow circle in the center.
    """
    
    # 画像生成
    images, urls, message = image_gen.generate_image(test_prompt)
    logger.info(message)
    
    # 画像の保存
    if images or urls:
        saved_paths = image_gen.save_images(images, urls, prefix="test")
        if saved_paths:
            logger.info("Test images saved: {}".format(", ".join(saved_paths)))