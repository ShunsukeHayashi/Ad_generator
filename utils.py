#!/usr/bin/env python3
"""
ユーティリティモジュール
アプリケーション全体で使用される共通ユーティリティ関数を提供
"""

import os
import logging
from datetime import datetime
from pathlib import Path

# ロギング設定
logger = logging.getLogger(__name__)

def generate_timestamp_filename(prefix="image", extension="png"):
    """
    タイムスタンプを含むファイル名を生成する関数
    
    Args:
        prefix (str): ファイル名の接頭辞
        extension (str): ファイルの拡張子（先頭のドットは不要）
    
    Returns:
        str: 生成されたファイル名
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

def ensure_directory(directory_path):
    """
    ディレクトリが存在することを確認し、存在しない場合は作成する関数
    
    Args:
        directory_path (str): 確認/作成するディレクトリのパス
    
    Returns:
        bool: ディレクトリが存在する（または作成された）場合はTrue、失敗した場合はFalse
    """
    try:
        # Pathオブジェクトに変換
        path = Path(directory_path)
        
        # ディレクトリが存在しない場合は作成
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            logger.info(f"ディレクトリを作成しました: {directory_path}")
        
        return True
    except Exception as e:
        logger.error(f"ディレクトリの作成に失敗しました: {e}")
        return False

def save_image_from_url(url, output_path):
    """
    URLから画像をダウンロードして保存する関数
    
    Args:
        url (str): 画像のURL
        output_path (str): 保存先のパス
    
    Returns:
        bool: 保存に成功した場合はTrue、失敗した場合はFalse
    """
    try:
        import requests
        
        # 画像をダウンロード
        response = requests.get(url, stream=True)
        if response.status_code != 200:
            logger.error(f"画像のダウンロードに失敗しました: ステータスコード {response.status_code}")
            return False
        
        # 画像を保存
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"画像を保存しました: {output_path}")
        return True
    except Exception as e:
        logger.error(f"画像の保存に失敗しました: {e}")
        return False

def save_image_from_base64(base64_data, output_path):
    """
    Base64エンコードされた画像データを保存する関数
    
    Args:
        base64_data (str): Base64エンコードされた画像データ
        output_path (str): 保存先のパス
    
    Returns:
        bool: 保存に成功した場合はTrue、失敗した場合はFalse
    """
    try:
        import base64
        
        # Base64データをデコード
        image_data = base64.b64decode(base64_data)
        
        # 画像を保存
        with open(output_path, 'wb') as f:
            f.write(image_data)
        
        logger.info(f"Base64画像を保存しました: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Base64画像の保存に失敗しました: {e}")
        return False

def get_file_extension(filename):
    """
    ファイル名から拡張子を取得する関数
    
    Args:
        filename (str): ファイル名
    
    Returns:
        str: 拡張子（先頭のドットを含まない）
    """
    return os.path.splitext(filename)[1][1:].lower()

def is_image_file(filename):
    """
    ファイルが画像ファイルかどうかを判定する関数
    
    Args:
        filename (str): ファイル名
    
    Returns:
        bool: 画像ファイルの場合はTrue、それ以外の場合はFalse
    """
    image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
    extension = get_file_extension(filename)
    return extension in image_extensions

if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 動作テスト
    print(f"タイムスタンプファイル名: {generate_timestamp_filename()}")
    
    test_dir = "test_output"
    if ensure_directory(test_dir):
        print(f"ディレクトリ '{test_dir}' の確認/作成に成功しました")
    
    print(f"'image.jpg' は画像ファイルですか？ {is_image_file('image.jpg')}")
    print(f"'document.pdf' は画像ファイルですか？ {is_image_file('document.pdf')}")