#!/usr/bin/env python3
"""
Creative Intel Loop - Backend API Server
バックエンドAPIサーバー: フロントエンドのダッシュボードと連携するREST API
"""

import os
import sys
import json
import base64
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Form, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
import uuid
from datetime import datetime
from PIL import Image
from io import BytesIO

# 既存のモジュールをインポート
sys.path.append(".")
import image_to_ad  # 画像解析と生成処理
from image_template_edit import analyze_image  # テンプレート解析

# FastAPIアプリケーションの初期化
app = FastAPI(
    title="Creative Intel Loop API",
    description="広告クリエイティブのテンプレート抽出と生成を行うAPI",
    version="1.0.0"
)

# CORS設定（フロントエンドからのAPI呼び出しを許可）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では特定のオリジンに制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 静的ファイル（フロントエンド）の提供
app.mount("/", StaticFiles(directory="public", html=True), name="public")

# データモデル定義
class ApiKeyConfig(BaseModel):
    api_key: str

class GenerationRequest(BaseModel):
    template_id: str
    variations: int = 3

class TemplateParameters(BaseModel):
    campaign_theme: str
    product_name: str
    main_message: str
    sub_copy: Optional[str] = ""
    call_to_action: str
    tone_and_manner: Optional[str] = ""
    aspect_ratio: str = "1:1"
    brand_colors: Optional[str] = ""

# 一時データ保存（本番環境ではデータベースを使用すること）
TEMP_STORAGE = {
    "templates": {},
    "generations": {}
}

# 一時ファイル保存用ディレクトリの作成
UPLOAD_DIR = Path("./uploads")
RESULTS_DIR = Path("./results")
UPLOAD_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# ヘルパー関数
def save_uploaded_file(file: UploadFile) -> Path:
    """アップロードされたファイルを一時ディレクトリに保存し、ファイルパスを返す"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{uuid.uuid4().hex[:8]}_{file.filename}"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(file.file.read())
    
    return file_path

async def process_image_template(image_path: Path, background_tasks: BackgroundTasks) -> str:
    """画像からテンプレートパラメータを抽出し、テンプレートIDを返す"""
    # 画像分析処理
    try:
        template_params = analyze_image(str(image_path))
        if not template_params:
            raise HTTPException(status_code=422, detail="テンプレートパラメータの抽出に失敗しました")
        
        # テンプレートIDの生成
        template_id = f"tpl_{uuid.uuid4().hex[:16]}"
        
        # テンプレートの保存
        TEMP_STORAGE["templates"][template_id] = {
            "params": template_params,
            "source_image": str(image_path),
            "created_at": datetime.now().isoformat()
        }
        
        return template_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"テンプレート処理エラー: {str(e)}")

async def generate_ad_variations(template_id: str, variations: int = 3) -> tuple[str, List[str]]:
    """テンプレートからバリエーションを生成し、生成されたファイルパスのリストを返す"""
    if template_id not in TEMP_STORAGE["templates"]:
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")
    
    template_data = TEMP_STORAGE["templates"][template_id]
    template_params = template_data["params"]
    source_image = template_data["source_image"]
    
    # テンプレートからAd Creative Templateを生成
    template = image_to_ad.generate_ad_creative_template(template_params)
    
    # 編集プロンプト生成
    edit_prompt = image_to_ad.generate_edit_prompt(template)
    
    # バリエーション生成
    result_files = []
    for i in range(variations):
        # バリエーションごとに微調整したプロンプト
        variation_prompt = f"{edit_prompt}\n\nバリエーション {i+1}: 同じブランドイメージを保ちながら、レイアウトや表現を少し変えてください。"
        
        try:
            # 画像編集・生成の実行
            result_image_path = RESULTS_DIR / f"{template_id}_variant_{i+1}.jpg"
            # モック処理（本番環境では実際の画像生成を行う）
            # image_to_ad.edit_image(source_image, variation_prompt, output_path=str(result_image_path))
            
            # テスト用にサンプル画像をコピー
            import shutil
            shutil.copy(source_image, result_image_path)
            
            result_files.append(str(result_image_path))
        except Exception as e:
            print(f"画像生成エラー: {e}")
    
    # 結果の保存
    generation_id = f"gen_{uuid.uuid4().hex[:16]}"
    TEMP_STORAGE["generations"][generation_id] = {
        "template_id": template_id,
        "result_files": result_files,
        "created_at": datetime.now().isoformat()
    }
    
    return generation_id, result_files

# APIエンドポイント
@app.get("/")
async def read_root():
    """ルートエンドポイント - API稼働確認用"""
    return {"status": "ok", "message": "Creative Intel Loop API is running"}

@app.post("/api/config/apikey")
async def set_api_key(config: ApiKeyConfig):
    """OpenAI APIキーを設定する（実際にはクライアントでのみ保存し、サーバーには送信しない実装を推奨）"""
    # 注意: この実装はデモ用。実際にはAPIキーはクライアント側で保管するか、
    # 適切な暗号化とアクセス制御を実装したサーバー側ストレージを使用する
    return {"status": "ok", "message": "API key configuration received"}

@app.post("/api/upload")
async def upload_image(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    """画像をアップロードしてテンプレート解析を行う"""
    if not file:
        raise HTTPException(status_code=400, detail="ファイルがアップロードされていません")
    
    # 画像ファイルかどうかの確認
    content_type = file.content_type
    if not content_type or "image" not in content_type:
        raise HTTPException(status_code=400, detail="アップロードされたファイルは画像ではありません")
    
    # ファイルの保存
    file_path = save_uploaded_file(file)
    
    # 画像処理の開始（バックグラウンドタスクとして実行可能）
    template_id = await process_image_template(file_path, background_tasks)
    
    return {
        "status": "success", 
        "message": "画像が正常にアップロードされ、テンプレート抽出が完了しました",
        "template_id": template_id
    }

@app.get("/api/template/{template_id}")
async def get_template(template_id: str):
    """テンプレートパラメータを取得する"""
    if template_id not in TEMP_STORAGE["templates"]:
        raise HTTPException(status_code=404, detail="テンプレートが見つかりません")
    
    template_data = TEMP_STORAGE["templates"][template_id]
    
    return {
        "status": "success",
        "template_id": template_id,
        "parameters": template_data["params"],
        "created_at": template_data["created_at"]
    }

@app.post("/api/generate")
async def generate_variations(request: GenerationRequest, background_tasks: BackgroundTasks):
    """テンプレートからバリエーションを生成する"""
    try:
        generation_id, result_files = await generate_ad_variations(request.template_id, request.variations)
        
        return {
            "status": "success",
            "message": f"{len(result_files)}個のバリエーションが生成されました",
            "generation_id": generation_id,
            "variation_count": len(result_files)
        }
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成プロセスエラー: {str(e)}")

@app.get("/api/results/{generation_id}")
async def get_results(generation_id: str):
    """生成結果を取得する"""
    if generation_id not in TEMP_STORAGE["generations"]:
        raise HTTPException(status_code=404, detail="生成結果が見つかりません")
    
    generation_data = TEMP_STORAGE["generations"][generation_id]
    
    # 画像ファイルのURLを構築
    image_urls = [f"/api/image/{Path(file_path).name}" for file_path in generation_data["result_files"]]
    
    return {
        "status": "success",
        "generation_id": generation_id,
        "template_id": generation_data["template_id"],
        "created_at": generation_data["created_at"],
        "images": image_urls
    }

@app.get("/api/image/{filename}")
async def get_image(filename: str):
    """生成された画像ファイルを取得する"""
    file_path = RESULTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="画像ファイルが見つかりません")
    
    return FileResponse(str(file_path))

# メイン実行関数
if __name__ == "__main__":
    import sys
    
    # 環境変数のチェック
    if not os.environ.get("OPENAI_API_KEY"):
        print("警告: OPENAI_API_KEY環境変数が設定されていません。")
        print("export OPENAI_API_KEY='your-api-key' で設定してください。")
    
    # サーバー起動
    host = os.environ.get("HOST", "0.0.0.0")
    port = int(os.environ.get("PORT", 8000))
    
    print(f"Creative Intel Loop APIサーバーを起動しています...")
    print(f"サーバーURL: http://{host}:{port}")
    uvicorn.run("backend_api:app", host=host, port=port, reload=True) 