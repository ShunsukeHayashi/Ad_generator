#!/usr/bin/env python3
"""
設定管理モジュール
アプリケーション全体の設定を一元管理するためのモジュール
"""

import os
import json
import logging
from pathlib import Path

# ロギング設定
logger = logging.getLogger(__name__)

# デフォルト設定
DEFAULT_CONFIG = {
    # 画像生成設定
    "default_model": "gpt-image-1",
    "default_size": "1024x1024",
    "default_quality": "high",
    "default_style": "natural",
    
    # API設定
    "api_base_url": "http://localhost:8000",
    
    # ファイルパス設定
    "output_dir": "output",
    "test_image": "imgs/provision_ad.jpg",
    
    # ログ設定
    "log_level": "INFO",
    "log_format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
}

# 設定ファイルパス
CONFIG_FILE = "app_config.json"

def get_config():
    """
    設定を取得する関数
    
    設定ファイルが存在する場合はそこから読み込み、
    存在しない場合はデフォルト設定を返す
    
    Returns:
        dict: 設定情報を含む辞書
    """
    config = DEFAULT_CONFIG.copy()
    
    # 設定ファイルが存在する場合は読み込む
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                file_config = json.load(f)
                config.update(file_config)
            logger.info(f"設定ファイル '{CONFIG_FILE}' を読み込みました")
        except Exception as e:
            logger.error(f"設定ファイルの読み込みに失敗しました: {e}")
    
    # 環境変数から設定を上書き
    # 例: OPENAI_MODEL環境変数があれば、default_modelを上書き
    if os.environ.get("OPENAI_MODEL"):
        config["default_model"] = os.environ.get("OPENAI_MODEL")
    
    if os.environ.get("OPENAI_SIZE"):
        config["default_size"] = os.environ.get("OPENAI_SIZE")
    
    if os.environ.get("OPENAI_QUALITY"):
        config["default_quality"] = os.environ.get("OPENAI_QUALITY")
    
    if os.environ.get("OUTPUT_DIR"):
        config["output_dir"] = os.environ.get("OUTPUT_DIR")
    
    return config

def save_config(config):
    """
    設定を保存する関数
    
    Args:
        config (dict): 保存する設定情報
    
    Returns:
        bool: 保存に成功した場合はTrue、失敗した場合はFalse
    """
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        logger.info(f"設定を '{CONFIG_FILE}' に保存しました")
        return True
    except Exception as e:
        logger.error(f"設定の保存に失敗しました: {e}")
        return False

if __name__ == "__main__":
    # ロギング設定
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 設定を取得して表示
    config = get_config()
    print("現在の設定:")
    for key, value in config.items():
        print(f"  {key}: {value}")