# 画像生成フレームワーク 使用ガイド

このドキュメントでは、リファクタリングされた画像生成フレームワークの使用方法について説明します。

## 概要

このフレームワークは、OpenAI GPT-Image-1を使用した画像生成機能を提供します。コードはモジュール化され、再利用可能なコンポーネントに分割されています。

主要なモジュールは以下の通りです：

1. `image_generation_core.py` - 画像生成の中核機能を提供するクラス
2. `config.py` - 設定管理モジュール
3. `utils.py` - 共通ユーティリティ関数

## 前提条件

- Python 3.8以上
- OpenAI APIキー（環境変数 `OPENAI_API_KEY` に設定）

## インストール

必要なパッケージをインストールします：

```bash
pip install openai requests
```

## 基本的な使用方法

### 1. 画像生成

```python
from image_generation_core import ImageGenerationCore
from config import get_config

# 設定の取得
config = get_config()

# 画像生成コアの初期化
image_gen = ImageGenerationCore()

# APIキーの検証
if not image_gen.validate_api_key():
    print("APIキーが無効です。環境変数OPENAI_API_KEYを確認してください。")
    exit(1)

# プロンプト
prompt = "青い背景に黄色い円がある単純なテスト画像を作成してください。"

# 画像生成
images, urls, message = image_gen.generate_image(
    prompt=prompt,
    model=config.get("default_model", "gpt-image-1"),
    size=config.get("default_size", "1024x1024"),
    quality=config.get("default_quality", "high"),
    n=1
)

print(message)

# 画像の保存
if images or urls:
    output_dir = config.get("output_dir", "output")
    saved_paths = image_gen.save_images(images, urls, prefix="test", output_dir=output_dir)
    if saved_paths:
        print(f"画像を保存しました: {', '.join(saved_paths)}")
```

### 2. シェルスクリプトからの使用

`generate_image.sh` スクリプトを使用して、コマンドラインから画像を生成できます：

```bash
./generate_image.sh
```

### 3. APIテスト

`test_api.py` スクリプトを使用して、バックエンドAPIをテストできます：

```bash
python test_api.py
```

## モジュールの詳細

### ImageGenerationCore クラス

`image_generation_core.py` モジュールの `ImageGenerationCore` クラスは、画像生成の中核機能を提供します。

主要なメソッド：

- `validate_api_key()` - APIキーの有効性を確認
- `generate_image(prompt, model, size, quality, style, n)` - 画像を生成
- `save_images(images, urls, prefix, output_dir)` - 生成された画像を保存
- `edit_image(image_path, prompt, model, size, quality)` - 画像を編集（将来的な拡張用）

### 設定管理

`config.py` モジュールは、アプリケーション全体の設定を一元管理します。

主要な関数：

- `get_config()` - 設定を取得
- `save_config(config)` - 設定を保存

デフォルト設定：

```python
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
```

### ユーティリティ関数

`utils.py` モジュールは、共通ユーティリティ関数を提供します。

主要な関数：

- `generate_timestamp_filename(prefix, extension)` - タイムスタンプを含むファイル名を生成
- `ensure_directory(directory_path)` - ディレクトリが存在することを確認し、存在しない場合は作成
- `save_image_from_url(url, output_path)` - URLから画像をダウンロードして保存
- `save_image_from_base64(base64_data, output_path)` - Base64エンコードされた画像データを保存
- `get_file_extension(filename)` - ファイル名から拡張子を取得
- `is_image_file(filename)` - ファイルが画像ファイルかどうかを判定

## 高度な使用方法

### カスタム設定の使用

```python
from config import get_config, save_config

# 設定の取得
config = get_config()

# 設定の変更
config["default_model"] = "gpt-image-1"
config["default_size"] = "1792x1024"
config["default_quality"] = "high"
config["output_dir"] = "custom_output"

# 設定の保存
save_config(config)
```

### 複数の画像生成

```python
from image_generation_core import ImageGenerationCore

# 画像生成コアの初期化
image_gen = ImageGenerationCore()

# プロンプト
prompt = "青い背景に黄色い円がある単純なテスト画像を作成してください。"

# 複数の画像を生成
images, urls, message = image_gen.generate_image(
    prompt=prompt,
    model="gpt-image-1",
    size="1024x1024",
    quality="high",
    n=3  # 3枚の画像を生成
)

print(message)

# 画像の保存
if images or urls:
    saved_paths = image_gen.save_images(images, urls, prefix="multiple", output_dir="output")
    if saved_paths:
        print(f"画像を保存しました: {', '.join(saved_paths)}")
```

## トラブルシューティング

### APIキーの問題

APIキーが設定されていない場合は、以下のコマンドで設定してください：

```bash
export OPENAI_API_KEY='your-api-key'
```

### 画像生成の失敗

画像生成に失敗した場合は、以下を確認してください：

1. APIキーが正しく設定されているか
2. インターネット接続が正常か
3. OpenAI APIの利用制限に達していないか

### ログの確認

ログを確認することで、問題の原因を特定できます：

```python
import logging

# ロギング設定
logging.basicConfig(
    level=logging.DEBUG,  # DEBUGレベルに設定
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## 拡張と貢献

このフレームワークは拡張可能に設計されています。新機能の追加や改善のための貢献を歓迎します。

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。