[![Built by 合同会社みやび](https://img.shields.io/badge/Built%20by-合同会社みやび-blue?style=flat-square&logo=github)](https://miyabi-ai.jp)

# Creative Intel Loop

Creative Intel Loop（クリエイティブ インテル ループ）は、AIを活用した広告クリエイティブの自動生成・編集ツールです。OpenAIのGPT-Image-1とO3モデルを使用して、既存の広告素材から新しいバリエーションを生成したり、編集したりすることができます。

## 機能

- **画像分析**: 既存の広告クリエイティブをAIが分析し、デザイン要素とコピーを抽出
- **テンプレート生成**: 分析結果から広告テンプレートを自動生成
- **画像生成・編集**: AIを使った高品質な広告画像の生成と編集
- **複数バリエーション**: 同じテンプレートから複数のバリエーションを簡単に作成
- **広告コピー生成**: AIによる広告コピーの自動生成
- **ユーザーフィードバック**: フィードバックを取り入れた画像の調整
- **マルチインターフェース**: GradioとStreamlitの2種類のUIを提供

## 動作環境

- Python 3.8以上
- OpenAI API Key（GPT-Image-1およびO3モデルへのアクセス権が必要）
- インターネット接続

## インストール方法

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd gpt_image_1
```

### 2. 依存パッケージのインストール

```bash
pip install -r requirements.txt
```

### 3. 環境変数の設定

```bash
# Linuxまたは macOSの場合
export OPENAI_API_KEY=your_api_key_here

# Windowsの場合
set OPENAI_API_KEY=your_api_key_here
```

または、`.env`ファイルをプロジェクトルートに作成し、以下の内容を追加:

```
OPENAI_API_KEY=your_api_key_here
```

## 使用方法

### バックエンドAPIの起動

```bash
python backend_api.py
```

これにより、APIサーバーが起動し、`http://localhost:8000`でアクセスできます。

### Gradioインターフェースの起動

```bash
python gpt_image_app.py
```

### Streamlitインターフェースの起動

```bash
streamlit run streamlit_ad_creator.py
```

## Dockerでの実行

```bash
# イメージの構築
docker build -t creative-intel-loop .

# コンテナの実行
docker run -p 8000:8000 -e OPENAI_API_KEY=your_api_key_here creative-intel-loop
```

## 基本的な使い方

1. Gradioまたは Streamlitインターフェースにアクセス
2. APIキーを設定（環境変数として設定済みでない場合）
3. 既存の広告画像をアップロード
4. 「分析」ボタンをクリックして画像を分析
5. 生成されたテンプレートを確認・編集
6. フィードバックや追加要件を入力
7. 「生成」または「編集」ボタンをクリックして新しい広告画像を作成
8. 結果を確認し、必要に応じてダウンロード

## プロジェクト構造

```
.
├── image_generation_core.py   # 画像生成の中核機能
├── gpt_image_app.py           # Gradioインターフェース
├── streamlit_ad_creator.py    # Streamlitインターフェース
├── backend_api.py             # バックエンドAPI
├── utils.py                   # ユーティリティ関数
├── config.py                  # 設定ファイル
├── image_to_ad.py             # 画像を広告に変換するモジュール
├── ad_template_analyzer.py    # 広告テンプレート分析モジュール
├── requirements.txt           # 依存パッケージリスト
└── Dockerfile                 # Dockerビルド設定
```

## トラブルシューティング

- **APIキーエラー**: 環境変数`OPENAI_API_KEY`が正しく設定されているか確認してください。
- **画像アップロードエラー**: サポートされている画像形式（JPEG、PNG）を使用しているか確認してください。
- **生成エラー**: OpenAI APIの利用制限に達していないか確認してください。
- **モデルアクセスエラー**: OpenAIのアカウントでGPT-Image-1およびO3モデルへのアクセス権があるか確認してください。

## ライセンス

このプロジェクトはMITライセンスの下で提供されています。 