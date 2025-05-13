import os
import sys
import base64
import json
import tempfile
import locale
from pathlib import Path
import streamlit as st
from openai import OpenAI
from PIL import Image
from io import BytesIO
import datetime

# エンコーディング設定
import sys
sys.stdout.reconfigure(encoding='utf-8')
sys.stdin.reconfigure(encoding='utf-8')

# ロケール設定
try:
    locale.setlocale(locale.LC_ALL, 'ja_JP.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'Japanese_Japan.932')
    except:
        pass

# ページ設定
st.set_page_config(
    page_title="Creative Intel Loop | 広告画像分析・編集ツール", 
    page_icon="🎨", 
    layout="wide", 
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Creative Intel Loop - AIを活用した広告クリエイティブ編集ツール"
    }
)

# スタイル設定
st.markdown("""
<style>
    /* 全体レイアウト */
    .main {
        padding: 1.5rem 2rem;
        max-width: 1200px;
        margin: 0 auto;
    }
    
    /* ヘッダーとサブヘッダーのスタイル */
    h1 {
        color: #1E3A8A;
        font-size: 2.2rem;
        margin-bottom: 0.8rem;
        font-weight: 600;
        border-bottom: 2px solid #3B82F6;
        padding-bottom: 0.5rem;
    }
    h2 {
        color: #1E40AF;
        font-size: 1.8rem;
        margin: 1.5rem 0 1rem 0;
        font-weight: 500;
    }
    h3 {
        color: #2563EB;
        font-size: 1.4rem;
        margin: 1.2rem 0 0.8rem 0;
        font-weight: 500;
    }
    
    /* ボタンスタイル */
    .stButton > button {
        width: 100%;
        font-weight: 500;
        border-radius: 6px;
        height: 2.5rem;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* プライマリーボタン */
    .stButton > [data-testid="baseButton-primary"] {
        background-color: #3B82F6 !important;
    }
    .stButton > [data-testid="baseButton-primary"]:hover {
        background-color: #2563EB !important;
    }
    
    /* セカンダリーボタン */
    .stButton > [data-testid="baseButton-secondary"] {
        border: 1px solid #3B82F6 !important;
        color: #3B82F6 !important;
    }
    .stButton > [data-testid="baseButton-secondary"]:hover {
        background-color: rgba(59, 130, 246, 0.1) !important;
    }
    
    /* 画像表示エリア */
    .uploaded-image, .edited-image {
        max-width: 100%;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        transition: transform 0.3s ease;
    }
    .uploaded-image:hover, .edited-image:hover {
        transform: scale(1.02);
    }
    
    /* カード風のコンテナ */
    .css-ocqkz7 [data-testid="stExpander"] {
        border: 1px solid #E5E7EB;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        margin-bottom: 1rem;
    }
    
    /* 入力フィールド */
    .stTextInput input, .stTextArea textarea {
        border-radius: 6px;
        border: 1px solid #D1D5DB;
        padding: 0.5rem;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3B82F6;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
    }
    
    /* タブのスタイル */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        white-space: pre-wrap;
        border-radius: 6px 6px 0 0;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: rgba(59, 130, 246, 0.1);
        color: #2563EB !important;
    }
    
    /* JSONとコードブロックの表示 */
    .stJson, pre {
        border-radius: 8px;
        max-height: 300px;
        overflow-y: auto;
    }
    
    /* プログレスバーとスピナー */
    .stProgress .st-bo {
        background-color: #3B82F6;
    }
    
    /* ステップカードのスタイル */
    .step-card {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border: 1px solid #E5E7EB;
    }
    
    /* ステップの説明テキスト */
    .step-description {
        color: #6B7280;
        font-size: 1rem;
        margin: -0.5rem 0 1rem 0;
    }
    
    /* アクションボタンコンテナ */
    .action-button-container {
        margin: 1.5rem 0;
        padding: 1rem;
        background-color: #F3F4F6;
        border-radius: 8px;
    }
    
    /* サブアクションボタン */
    .sub-action-button {
        margin: 1rem 0;
    }
    
    /* 最終アクションボタン */
    .final-action-button {
        margin: 1.5rem 0;
        padding: 0.5rem;
        background-color: #F0F9FF;
        border-radius: 8px;
        border: 1px dashed #3B82F6;
    }
    
    /* モバイル対応 */
    @media (max-width: 768px) {
        .main {
            padding: 1rem;
        }
        h1 {
            font-size: 1.8rem;
        }
        h2 {
            font-size: 1.5rem;
        }
        h3 {
            font-size: 1.2rem;
        }
        .stButton > button {
            height: 3rem;
        }
        .step-card {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# サイドバーにタイトルと説明を追加
st.sidebar.title("Creative Intel Loop")
with st.sidebar.container():
    st.image("https://img.icons8.com/fluency/96/000000/artificial-intelligence.png", width=80)
    st.markdown("""
    ## AI搭載広告編集ツール
    
    このアプリは画像を分析して広告パラメータを抽出し、GPT-Image-1を使用して広告画像を編集または新規作成します。
    """)
    
    st.markdown("---")
    
    st.markdown("""
    ### 使い方
    1. 画像をアップロード（任意）
    2. フィードバックを入力（任意）
    3. 「分析と編集を実行」ボタンをクリック
    """)

# APIキーの設定
with st.sidebar.expander("📋 API設定", expanded=False):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        api_key = st.text_input("OpenAI APIキーを入力してください", type="password", help="APIキーはOpenAIのウェブサイトで取得できます。")
        if not api_key:
            st.warning("⚠️ APIキーが設定されていません。環境変数として設定するか、上のフィールドで入力してください。")
    else:
        st.success("✅ APIキーを環境変数から読み込みました")

    # APIモデルバージョン情報
    st.info("🤖 使用モデル: o3 (画像分析)、GPT-Image-1 (画像生成)")

# ヘッダー
st.title("Creative Intel Loop")
st.write("プロのデザイナーのようにAIを使って広告画像を分析・編集・生成しましょう。")

# OpenAI クライアントの初期化
@st.cache_resource(show_spinner=False)
def get_client(api_key):
    try:
        client = OpenAI(api_key=api_key)
        return client
    except Exception as e:
        st.error(f"OpenAIクライアントの初期化に失敗しました: {str(e)}")
        return None

# 画像をbase64エンコードする関数
def encode_image_to_base64(image_path):
    try:
        # ファイルパスをUTF-8エンコーディングで処理
        if isinstance(image_path, str):
            image_path = Path(image_path)
        
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except UnicodeEncodeError as e:
        st.error(f"エンコーディングエラーが発生しました: {str(e)}")
        st.write("ファイル名に非ASCII文字が含まれています:", str(image_path))
        
        # ファイル名を安全な形式に変換
        safe_path = Path(tempfile.mkdtemp()) / "temp_image.jpg"
        try:
            # ファイルをコピー
            import shutil
            shutil.copy2(image_path, safe_path)
            st.info(f"ファイルを安全な名前にコピーしました: {safe_path}")
            
            # 安全な名前でエンコード
            with open(safe_path, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as copy_err:
            st.error(f"ファイルコピー中にエラーが発生しました: {str(copy_err)}")
            return None
    except Exception as e:
        st.error(f"画像エンコード中にエラーが発生しました: {str(e)}")
        return None

# 画像を分析して広告パラメータを抽出する関数
def analyze_image_with_o3(client, image_path: Path): # モデル名を関数名に反映, Path型を明示
    if not client: return None
    try:
        with st.spinner("画像を分析中 (o3)..."):
            base64_image = encode_image_to_base64(image_path)
            if base64_image is None:
                return None
            
            analysis_prompt = """
            この広告画像を分析し、以下のフォーマットでパラメータを抽出してください。
            結果はJSON形式で返してください。キーは英語でお願いします。

            ================= ユーザー入力フォーマット =================
            1. Campaign Thema（キャンペーン名・ファイル名の基礎になります）: [抽出結果]
            2. 目的（例：認知／獲得／リターゲティング など）: [抽出結果]
            3. 商品・サービス名: [抽出結果]
            4. メインメッセージ（最大25字程度）: [抽出結果]
            5. サブコピー（任意、最大60字程度）: [抽出結果]
            6. コールトゥアクション（例：今すぐ購入／無料で体験 など）: [抽出結果]
            7. 参考にしたいトーン＆マナー（例：ポップ／高級感／ミニマル など）: [抽出結果]
            8. キービジュアルの説明（被写体・シーンなど）: [抽出結果]
            9. ブランドカラー・指定フォント（あれば）: [抽出結果]
            10. 仕上がりサイズ or アスペクト比（例：1080×1080 / 9:16 / 16:9 など）: 画像から推定できるアスペクト比
            11. 追加で写したい要素／NG 要素（任意）: [抽出結果]
            ===========================================================

            JSONフォーマット (キーは英語で):
            {
              "campaign_theme": "キャンペーン名",
              "purpose": "目的",
              "product_name": "商品・サービス名",
              "main_message": "メインメッセージ",
              "sub_copy": "サブコピー",
              "call_to_action": "コールトゥアクション",
              "tone_and_manner": "トーン＆マナー",
              "key_visual_description": "キービジュアルの説明",
              "brand_colors_fonts": "ブランドカラー・フォント",
              "size_aspect_ratio": "サイズ・アスペクト比",
              "additional_elements": "追加要素",
              "ng_elements": "NG要素"
            }
            """
            
            response = client.chat.completions.create(
                model="o3", # 正しいモデル名
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": analysis_prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}" # アップロード形式に応じて変更も検討
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"} # JSONモードを指定
            )
            
            result_text = response.choices[0].message.content
            try:
                template_params = json.loads(result_text)
                return template_params
            except json.JSONDecodeError:
                st.error("画像分析結果のJSON解析に失敗しました。")
                st.code(result_text, language="json")
                return None
            
    except UnicodeEncodeError as e: # このエラーは通常 response_format="json_object" で回避されるはずだが念のため
        st.error(f"画像分析中にエンコーディングエラーが発生しました: {str(e)}")
        return None
    except Exception as e:
        st.error(f"画像分析中に予期せぬエラーが発生しました: {str(e)}")
        return None

# テンプレートを生成する関数 (変更なし)
def generate_ad_creative_template(params):
    campaign_theme = params.get("campaign_theme", "未指定")
    product_name = params.get("product_name", "未指定")
    main_message = params.get("main_message", "未指定")
    sub_copy = params.get("sub_copy", "")
    call_to_action = params.get("call_to_action", "未指定")
    tone_and_manner = params.get("tone_and_manner", "ブランドに合わせた")
    
    target_audience = "マーケティング担当者" 
    if "target" in params:
        target_audience = params.get("target", target_audience)
    elif "purpose" in params:
        purpose_val = params.get("purpose", "")
        if "認知" in purpose_val:
            target_audience = "新規顧客"
        elif "獲得" in purpose_val:
            target_audience = "見込み客"
        elif "リターゲティング" in purpose_val:
            target_audience = "既存顧客"
    
    template = f"""
Ad Creative Template v1.0:{campaign_theme}
# このテンプレートは、広告クリエイティブ生成のためのパラメータを定義します。
# ファイル名はキャンペーンテーマに基づき自動生成されます。

# === Core Copy / CTA ===
core_content:
  product_name: "{product_name}"
  target_audience: "{target_audience}"
  brand_tone: "{tone_and_manner}"
  key_message: "{main_message}"
  usp: ""
  
  # --- 詳細コピー要素 ---
  ad_format: "{params.get('size_aspect_ratio', '1024x1024')}" # DALL-E 3 デフォルトサイズ候補
  headlines:
    primary: "{main_message}"
    secondary: "{sub_copy}"
  body_text: |
    {sub_copy}
  
  # --- アクション促進要素 ---
  call_to_action: "{call_to_action}"
  cta_button_label: "{call_to_action}"

# === Design Style ===
design_style:
  style_preset:
    source: "image_analysis"
    source_image_reference: "input_image" 
    detail:
      color_scheme:
        primary: ""
        accent1: ""
        accent2: ""
        copy_color: ""
      mood: "{tone_and_manner}"
      style: "Clean and Professional"
      composition: "Balance text and visuals"
      format: "{params.get('size_aspect_ratio', '1024x1024')}"
"""
    return template

# 編集プロンプトを生成する関数 (変更なし)
def generate_edit_prompt(template, user_feedback=None):
    lines = template.split('\n')
    campaign_theme = ""
    product_name = ""
    key_message = ""
    call_to_action = ""
    
    for i, line in enumerate(lines):
        if "Ad Creative Template v1.0:" in line:
            campaign_theme = line.split(":", 1)[1].strip()
        elif "product_name:" in line:
            product_name = line.split(":", 1)[1].strip().strip('"')
        elif "key_message:" in line:
            key_message = line.split(":", 1)[1].strip().strip('"')
        elif "call_to_action:" in line and "cta_button_label" not in line:
            call_to_action = line.split(":", 1)[1].strip().strip('"')
    
    prompt = f"""
広告画像を生成または編集します。

【基本情報】
キャンペーン: {campaign_theme}
商品/サービス: {product_name}
メインメッセージ: {key_message}
コールトゥアクション: {call_to_action}

【指示】
1. 商品/サービスの特徴を視覚的に伝える魅力的な広告画像を作成
2. メインメッセージが目立つように配置
3. コールトゥアクションボタンを明確に表示
4. 全体的に洗練された印象で、ターゲットユーザーに訴求力のあるデザイン
"""
    
    if user_feedback and user_feedback.strip():
        prompt += f"""
【ユーザーフィードバック】
{user_feedback}
"""
    return prompt

# 画像を編集する関数
def edit_image(client, source_image_path, edit_prompt):
    try:
        with st.spinner("画像編集を実行中..."):
            # 入力画像が存在するかチェック
            if not source_image_path or not os.path.exists(source_image_path):
                # 入力画像が存在しない場合は新規生成
                st.info("入力画像が見つからないため、新規に生成します。")
                
                try:
                    # 詳細なログを表示
                    st.write("生成プロンプト:")
                    st.code(edit_prompt, language="text")
                    
                    # 新しいGPT-Image-1 API形式で画像生成
                    response = client.images.generate(
                        model="gpt-image-1",
                        prompt=edit_prompt,
                        n=1
                    )
                    
                    # レスポンスの確認
                    if response and hasattr(response, 'data') and len(response.data) > 0:
                        # デバッグ情報
                        st.write("APIレスポンス情報:")
                        st.json({
                            "created": response.created if hasattr(response, 'created') else None,
                            "data_length": len(response.data) if hasattr(response, 'data') else 0,
                            "has_b64_json": hasattr(response.data[0], 'b64_json') if (hasattr(response, 'data') and len(response.data) > 0) else False,
                            "usage": response.usage if hasattr(response, 'usage') else None
                        })
                        
                        # 生成された画像を保存
                        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                            image_base64 = response.data[0].b64_json
                            image_bytes = base64.b64decode(image_base64)
                            
                            try:
                                edited_image = Image.open(BytesIO(image_bytes))
                                temp_dir = tempfile.mkdtemp()
                                edited_image_path = os.path.join(temp_dir, "generated_ad.jpg")
                                edited_image.save(edited_image_path, format="JPEG", quality=95)
                                
                                return edited_image_path, image_bytes
                            except Exception as img_error:
                                st.error(f"画像の処理中にエラーが発生しました: {str(img_error)}")
                                st.write("デバッグ情報:", type(image_bytes), len(image_bytes) if image_bytes else "None")
                                return None, None
                        else:
                            st.error("APIからの応答に画像データが含まれていません。")
                            st.write("APIレスポンス:", response)
                            return None, None
                    else:
                        st.error("APIからの応答が不正です。")
                        st.write("APIレスポンス:", response)
                        return None, None
                        
                except Exception as api_error:
                    st.error(f"OpenAI API呼び出し中にエラーが発生しました: {str(api_error)}")
                    return None, None
                
            else:
                try:
                    # 画像をbase64エンコード
                    base64_image = encode_image_to_base64(source_image_path)
                    if base64_image is None:
                        st.error("画像のエンコードに失敗しました。")
                        return None, None
                    
                    # 詳細なログを表示
                    st.write("編集プロンプト:")
                    st.code(edit_prompt, language="text")
                    
                    # 編集用のプロンプト
                    revised_prompt = f"""
                    Create an improved version of this advertisement based on the following instructions:
                    
                    {edit_prompt}
                    
                    Important: This is based on an existing ad concept, so maintain the core elements and brand identity while making the requested improvements.
                    """
                    
                    # GPT-Image-1 APIで画像生成
                    response = client.images.generate(
                        model="gpt-image-1",
                        prompt=revised_prompt,
                        n=1
                    )
                    
                    # レスポンスの確認
                    if response and hasattr(response, 'data') and len(response.data) > 0:
                        # デバッグ情報
                        st.write("APIレスポンス情報:")
                        st.json({
                            "created": response.created if hasattr(response, 'created') else None,
                            "data_length": len(response.data) if hasattr(response, 'data') else 0,
                            "has_b64_json": hasattr(response.data[0], 'b64_json') if (hasattr(response, 'data') and len(response.data) > 0) else False,
                            "usage": response.usage if hasattr(response, 'usage') else None
                        })
                        
                        # 生成された画像を保存
                        if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                            image_base64 = response.data[0].b64_json
                            image_bytes = base64.b64decode(image_base64)
                            
                            temp_dir = tempfile.mkdtemp()
                            # ファイル名を安全に処理
                            safe_basename = "".join([c if ord(c) < 128 else "_" for c in os.path.basename(source_image_path)])
                            edited_image_path = os.path.join(temp_dir, f"edited_{safe_basename}")
                            
                            try:
                                edited_image = Image.open(BytesIO(image_bytes))
                                edited_image.save(edited_image_path, format="JPEG", quality=95)
                                
                                return edited_image_path, image_bytes
                            except Exception as img_error:
                                st.error(f"画像の処理中にエラーが発生しました: {str(img_error)}")
                                st.write("デバッグ情報:", type(image_bytes), len(image_bytes) if image_bytes else "None")
                                return None, None
                        else:
                            st.error("APIからの応答に画像データが含まれていません。")
                            st.write("APIレスポンス:", response)
                            return None, None
                    else:
                        st.error("APIからの応答が不正です。")
                        st.write("APIレスポンス:", response)
                        return None, None
                
                except UnicodeEncodeError as e:
                    st.error(f"エンコーディングエラーが発生しました: {str(e)}")
                    return None, None
                except Exception as e:
                    st.error(f"画像編集中にエラーが発生しました: {str(e)}")
                    return None, None
                    
    except Exception as e:
        st.error(f"画像編集プロセスでエラーが発生しました: {str(e)}")
        return None, None

# コンテキストからテキストを生成する関数
def generate_ad_copy_from_context(client, params):
    if not client: return None
    try:
        with st.spinner("広告テキストを生成中 (o3)..."):
            context_lines = []
            # パラメータの日本語ラベルと英語キーのマッピング (順序を定義)
            param_labels = {
                "campaign_theme": "キャンペーン名", "purpose": "広告目的", "product_name": "製品/サービス名",
                "main_message": "メインメッセージ", "sub_copy": "サブコピー", "call_to_action": "コールトゥアクション",
                "tone_and_manner": "トーン＆マナー", "key_visual_description": "キービジュアル",
                "brand_colors_fonts": "ブランドカラー・フォント", "size_aspect_ratio": "サイズ・アスペクト比",
                "additional_elements": "追加要素", "ng_elements": "NG要素"
            }
            for key, label in param_labels.items():
                value = params.get(key)
                if value and isinstance(value, str) and value.strip(): # 値が存在し、文字列型で、空でない場合
                    context_lines.append(f"{label}: {value}")
            
            full_context = "\n".join(context_lines)
            if not full_context:
                full_context = "広告コンテキストに関する具体的な情報はありません。"

            copy_prompt = f"""
            あなたは広告コピーの専門家です。以下の広告コンテキストをもとに魅力的な広告テキストを生成してください。

            【広告コンテキスト】
            {full_context}

            【必要なテキスト要素】
            1. メインメッセージ（最大25文字、製品の魅力を簡潔に表現）
            2. サブコピー（最大60文字、製品の詳細や特徴を補足）
            3. コールトゥアクション（行動喚起フレーズ、10〜15文字）

            それぞれ、3つのバリエーションを提案してください。
            結果は以下のJSON形式で返してください:

            {{
              "main_messages": ["メッセージ1", "メッセージ2", "メッセージ3"],
              "sub_copies": ["サブコピー1", "サブコピー2", "サブコピー3"],
              "call_to_actions": ["CTA1", "CTA2", "CTA3"]
            }}
            """
            
            response = client.chat.completions.create(
                model="o3", # 正しいモデル名
                messages=[
                    {"role": "system", "content": "あなたは広告コピーライティングの専門家です。"},
                    {"role": "user", "content": copy_prompt}
                ],
                response_format={"type": "json_object"} # JSONモードを指定
            )
            
            result_text = response.choices[0].message.content
            try:
                copy_suggestions = json.loads(result_text)
                return copy_suggestions
            except json.JSONDecodeError:
                st.error("テキスト生成結果のJSON解析に失敗しました。")
                st.code(result_text, language="json")
                return None
            
    except Exception as e:
        st.error(f"テキスト生成中にエラーが発生しました: {str(e)}")
        return None

# メイン処理
def main():
    # APIキーのチェック
    if not api_key:
        st.error("APIキーが設定されていません。サイドバーで入力するか、環境変数として設定してください。")
        st.stop()
    
    # OpenAIクライアントの初期化
    client = get_client(api_key)
    if not client:
        st.error("OpenAIクライアントの初期化に失敗しました。APIキーを確認してください。")
        st.stop()
    
    # モデル設定と問題の確認
    try:
        # クライアントが正常に動作するか簡単な確認
        models = client.models.list()
        # モデル名の処理をセーフに行う
        has_o3 = False
        has_image1 = False
        
        try:
            for model in models:
                model_id = str(model.id) if hasattr(model, 'id') else ""
                if "gpt-4o" in model_id:
                    has_o3 = True
                if "gpt-image-1" in model_id:
                    has_image1 = True
        except Exception as model_err:
            st.warning(f"モデル情報の解析中にエラーが発生しました: {str(model_err)}")
        
        if not has_o3:
            st.warning("o3モデルにアクセスできない可能性があります。他のモデルで代替することがあります。")
        
        if not has_image1:
            st.warning("GPT-Image-1モデルにアクセスできない可能性があります。画像生成に問題が発生する場合があります。")
    except Exception as e:
        st.warning(f"モデル情報の取得中にエラーが発生しました: {str(e)}")
        st.info("エラーが発生しましたが、処理を続行します。使用中に問題が発生する場合はAPIキーを確認してください。")
    
    # タブを作成
    tab1, tab2 = st.tabs(["広告分析・編集", "複数画像編集"])
    
    with tab1:
        # 既存の広告分析・編集機能
        run_ad_analysis_tab(client)
    
    with tab2:
        # 新しい複数画像編集機能
        run_multi_image_edit_tab(client)

# 複数画像編集用の関数
def run_multi_image_edit_tab(client):
    import time
    
    st.header("複数画像を使用した編集")
    st.write("複数の画像をアップロードし、それらを組み合わせた画像を生成します。")
    
    # ステップガイド
    st.markdown("""
    <div style="background-color:#F3F4F6; padding:1rem; border-radius:8px; margin-bottom:1.5rem;">
        <h3 style="margin-top:0; color:#1E3A8A;">🔄 複数画像の編集プロセス</h3>
        <ol style="margin-bottom:0;">
            <li>最大4枚の画像をアップロードします</li>
            <li>画像をどのように編集・合成したいかプロンプトを入力します</li>
            <li>「画像編集を実行」ボタンをクリックします</li>
            <li>AIが複数の画像を参考にして新しい画像を生成します</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # 複数画像のアップロード - カードスタイルの適用
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.header("📤 STEP 1: 画像をアップロード")
        st.markdown('<p class="step-description">参考にしたい既存画像（最大4枚）をアップロードしてください</p>', unsafe_allow_html=True)
        
        uploaded_images = st.file_uploader(
            "複数の画像をアップロード（最大4枚）", 
            type=["jpg", "jpeg", "png"], 
            accept_multiple_files=True,
            key="multi_images",
            help="JPG、JPEG、PNGフォーマットの画像をアップロードしてください。一度に最大4枚まで処理できます。"
        )
        
        # アップロードされた画像のプレビュー
        if uploaded_images:
            st.markdown("### アップロードされた画像のプレビュー")
            image_cols = st.columns(min(4, len(uploaded_images)))
            for i, img in enumerate(uploaded_images[:4]):
                with image_cols[i]:
                    st.image(img, caption=f"画像 {i+1}", use_column_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # プロンプト入力
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.header("💬 STEP 2: 生成プロンプトを入力")
        st.markdown('<p class="step-description">AIに対して、アップロードした画像をどのように組み合わせるか指示します</p>', unsafe_allow_html=True)
        
        prompt = st.text_area(
            "生成プロンプト", 
            placeholder="例: これらの商品を使用したギフトバスケットを作成してください。背景は白で、商品を美しく配置してください。",
            help="画像の組み合わせ方や、追加したい要素について具体的に指示すると良い結果が得られます。"
        )
        
        # プロンプト例
        with st.expander("💡 プロンプト例を見る"):
            st.markdown("""
            #### プロンプト例
            
            - **商品を組み合わせる**: これらの商品を1つのフラットレイ写真に美しく配置してください。明るい自然光で、ミニマルな背景を使用してください。
            - **別の環境に配置**: これらの商品を豪華なリビングルームのコーヒーテーブルの上に配置してください。
            - **季節感を追加**: これらの商品を使った秋のテーマのディスプレイを作成してください。オレンジと赤の葉を背景に使い、温かみのある雰囲気にしてください。
            - **特定のスタイルで統一**: これらの画像を使って、モノクロームでミニマルなスタイルの広告バナーを作成してください。
            """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 実行ボタン - 目立つデザイン
    st.markdown('<div class="action-button-container">', unsafe_allow_html=True)
    execute_button = st.button("🎨 画像編集を実行", key="multi_edit_button", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 実行ボタンが押された場合
    if execute_button:
        if not uploaded_images:
            st.warning("⚠️ 少なくとも1枚の画像をアップロードしてください。", icon="⚠️")
            return
        
        if len(uploaded_images) > 4:
            st.warning("⚠️ 一度に処理できる画像は最大4枚です。最初の4枚を使用します。", icon="⚠️")
            uploaded_images = uploaded_images[:4]
        
        if not prompt:
            st.warning("⚠️ プロンプトを入力してください。", icon="⚠️")
            return
        
        # 画像の処理 - プログレスバーを追加
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        with st.spinner("画像を処理中..."):
            # ステータス更新
            status_text.text("画像を準備中...")
            progress_bar.progress(10)
            
            # 画像を一時ファイルに保存
            temp_dir = tempfile.mkdtemp()
            image_paths = []
            
            for i, img in enumerate(uploaded_images):
                # ファイル名を安全にする（ASCII範囲外の文字を置換）
                safe_filename = f"input_{i}.jpg"
                temp_file_path = os.path.join(temp_dir, safe_filename)
                with open(temp_file_path, "wb") as f:
                    f.write(img.getbuffer())
                image_paths.append(temp_file_path)
            
            # ステータス更新
            status_text.text("AIによる画像編集中...")
            progress_bar.progress(30)
            
            # 画像編集実行
            result = edit_multiple_images(client, image_paths, prompt)
            
            if result:
                edited_image_path, edited_image_bytes = result
                
                # ステータス更新
                status_text.text("画像を最終処理中...")
                progress_bar.progress(90)
                
                # ステータス完了
                progress_bar.progress(100)
                status_text.success("✅ 画像生成が完了しました！")
                
                # 結果表示エリア - デザイン改善
                st.markdown("""
                <div style="margin-top:2rem; text-align:center;">
                    <h2 style="color:#1E3A8A;">🎉 生成された画像</h2>
                </div>
                """, unsafe_allow_html=True)
                
                # 画像とダウンロードボタンを並べて表示
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.image(edited_image_path, caption="生成された画像", use_column_width=True)
                with col2:
                    st.markdown("### ダウンロード")
                    st.download_button(
                        label="📥 画像をダウンロード",
                        data=edited_image_bytes,
                        file_name=f"combined_image_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    
                    # メタデータ表示
                    st.markdown("#### 画像情報")
                    st.markdown(f"""
                    - **使用画像数**: {len(image_paths)}枚
                    - **生成日時**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
                    """)
                    
                    # プロンプト表示
                    st.markdown("#### 使用プロンプト")
                    st.markdown(f"""
                    <div style="padding:0.7rem; background-color:#F9FAFB; border-radius:6px; font-size:0.9em;">
                        {prompt}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # エラー処理
                progress_bar.empty()
                status_text.error("❌ 画像の生成に失敗しました。")
                st.error("画像の処理中にエラーが発生しました。別のプロンプトや画像で再試行してください。")

# 複数画像編集用の関数
def edit_multiple_images(client, image_paths, prompt):
    try:
        # 新しいエンドポイント用のコード
        st.write("複数画像編集機能を実行中...")
        
        # APIキーがある場合は実際のAPIコール
        if hasattr(client, 'api_key') and client.api_key:
            import requests
            
            api_key = client.api_key
            url = "https://api.openai.com/v1/images/edits"
            
            # multipart/form-dataリクエストの作成
            files = []
            for i, img_path in enumerate(image_paths):
                try:
                    # 安全なファイル名に変換
                    safe_filename = f'image_{i}.png'
                    with open(img_path, 'rb') as img_file:
                        img_data = img_file.read()
                    files.append(('image[]', (safe_filename, img_data, 'image/png')))
                except Exception as file_err:
                    st.error(f"ファイル {img_path} の処理中にエラーが発生しました: {str(file_err)}")
                    continue
            
            payload = {
                'model': 'gpt-image-1',
                'prompt': prompt
            }
            
            headers = {
                'Authorization': f'Bearer {api_key}'
            }
            
            # 実際のAPI呼び出し
            st.write("OpenAI APIを呼び出し中...")
            response = requests.post(url, headers=headers, data=payload, files=files)
            
            if response.status_code == 200:
                # APIレスポンスをOpenAIライブラリの形式に合わせる
                result_json = response.json()
                
                # OpenAIのレスポンス構造に近い形でオブジェクトを作成
                from types import SimpleNamespace
                
                data_items = []
                for item in result_json.get('data', []):
                    data_obj = SimpleNamespace()
                    data_obj.b64_json = item.get('b64_json')
                    data_items.append(data_obj)
                
                result = SimpleNamespace()
                result.created = result_json.get('created')
                result.data = data_items
                
                return result
            else:
                st.error(f"API呼び出しエラー: {response.status_code}")
                st.json(response.json())
                return None
                
        # APIキーがない場合はダミーレスポンス
        else:
            st.warning("APIキーが設定されていないためダミーレスポンスを返します。")
            from types import SimpleNamespace
            import time
            
            # ダミーデータ
            dummy_data = SimpleNamespace()
            dummy_data.created = int(time.time())
            
            # ダミー画像生成
            dummy_image = Image.new('RGB', (512, 512), color='purple')
            img_buffer = BytesIO()
            dummy_image.save(img_buffer, format='PNG')
            img_bytes = img_buffer.getvalue()
            b64_encoded = base64.b64encode(img_bytes).decode('utf-8')
            
            data_item = SimpleNamespace()
            data_item.b64_json = b64_encoded
            
            dummy_data.data = [data_item]
            
            return dummy_data
    except Exception as e:
        st.error(f"複数画像編集処理中にエラーが発生しました: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return None

# 既存の広告分析・編集機能
def run_ad_analysis_tab(client):
    # セッション状態の管理
    if "analyzed" not in st.session_state:
        st.session_state.analyzed = False
    if "template_params" not in st.session_state:
        st.session_state.template_params = None
    if "template" not in st.session_state:
        st.session_state.template = None
    if "edited_image_path" not in st.session_state:
        st.session_state.edited_image_path = None
    if "edited_image_bytes" not in st.session_state:
        st.session_state.edited_image_bytes = None
    if "copy_suggestions" not in st.session_state:
        st.session_state.copy_suggestions = None
    
    # ステップごとのUI改善
    st.markdown("""
    <div style="background-color:#F3F4F6; padding:1rem; border-radius:8px; margin-bottom:1.5rem;">
        <h3 style="margin-top:0; color:#1E3A8A;">📋 プロセスの流れ</h3>
        <ol style="margin-bottom:0;">
            <li>画像をアップロード（新規作成の場合は不要）</li>
            <li>フィードバックや要望を入力</li>
            <li>分析と編集を実行</li>
            <li>必要に応じてパラメータを調整</li>
            <li>最終的な画像を生成</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)
    
    # 入力エリア - カードスタイルの適用
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.header("📤 STEP 1: 画像をアップロード")
        st.markdown('<p class="step-description">既存の広告画像をアップロードするか、新規作成の場合はスキップできます</p>', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "広告画像をアップロード", 
            type=["jpg", "jpeg", "png"], 
            key="ad_image",
            help="JPG、JPEG、PNGフォーマットの画像をアップロードしてください。"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # テンプレート設定とフィードバック
    with st.container():
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.header("💬 STEP 2: フィードバックを入力")
        st.markdown('<p class="step-description">AIに伝えたい希望や指示を入力してください</p>', unsafe_allow_html=True)
        
        user_feedback = st.text_area(
            "編集指示やフィードバック", 
            placeholder="例: より鮮やかな色合いで、モダンな印象にしてください。背景を明るくして、商品をより目立たせたいです。",
            help="色調やレイアウト、フォント、全体の印象など、具体的な指示を入力すると良い結果が得られます。"
        )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # 実行ボタン - 目立つデザイン
    st.markdown('<div class="action-button-container">', unsafe_allow_html=True)
    execute_button = st.button("📊 分析と編集を実行", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 実行ボタンが押された場合
    if execute_button:
        # 入力確認
        if uploaded_file is None:
            st.info("📝 画像が入力されていません。新規に広告画像を生成します。", icon="ℹ️")
            
            # デザインを改善したデフォルトパラメータセクション
            with st.expander("✨ 新規広告パラメータ", expanded=True):
                # デフォルトのパラメータを設定
                default_params = {
                    "campaign_theme": "新規広告キャンペーン",
                    "purpose": "認知",
                    "product_name": "プロダクト名",
                    "main_message": "メインメッセージ",
                    "sub_copy": "サブコピー",
                    "call_to_action": "詳細はこちら",
                    "tone_and_manner": "プロフェッショナル",
                    "key_visual_description": "",
                    "brand_colors_fonts": "",
                    "size_aspect_ratio": "1:1",
                    "additional_elements": "",
                    "ng_elements": ""
                }
                
                # パラメータ編集エリア - レイアウト改善
                st.markdown("#### 基本情報")
                col1, col2 = st.columns(2)
                with col1:
                    campaign_theme = st.text_input("キャンペーン名", default_params["campaign_theme"],
                                                help="キャンペーンの名前（ファイル名の基礎になります）")
                    purpose_options = ["認知", "獲得", "リターゲティング", "その他"]
                    purpose = st.selectbox("広告目的", purpose_options, 
                                        help="広告の主な目的を選択してください")
                    default_params["purpose"] = purpose
                    
                with col2:
                    product_name = st.text_input("製品/サービス名", default_params["product_name"],
                                                help="広告で紹介する製品やサービスの名前")
                    size_ratio_options = ["1:1 (正方形)", "4:5 (Instagram推奨)", "16:9 (ランドスケープ)", "9:16 (ポートレート)"]
                    size_ratio = st.selectbox("サイズ・アスペクト比", size_ratio_options,
                                            help="生成する画像のアスペクト比を選択してください")
                    default_params["size_aspect_ratio"] = size_ratio.split(" ")[0]
                
                st.markdown("#### コピーと表現")
                col1, col2 = st.columns(2)
                with col1:
                    main_message = st.text_input("メインメッセージ (最大25文字)", default_params["main_message"],
                                                help="広告の主要なメッセージ・キャッチコピー")
                    call_to_action = st.text_input("コールトゥアクション", default_params["call_to_action"],
                                                help="ユーザーに促したいアクション（例: 今すぐ購入、詳細を見る）")
                with col2:
                    sub_copy = st.text_area("サブコピー (最大60文字)", default_params["sub_copy"], height=95,
                                            help="メインメッセージを補足する追加テキスト")
                    tone_manner_options = ["プロフェッショナル", "カジュアル", "高級感", "親しみやすい", "シンプル", "ポップ", "ミニマル"]
                    tone_and_manner = st.selectbox("トーン＆マナー", tone_manner_options,
                                                help="広告の全体的な雰囲気やスタイル")
                    default_params["tone_and_manner"] = tone_and_manner
                
                st.markdown("#### ビジュアル要素")
                col1, col2 = st.columns(2)
                with col1:
                    key_visual = st.text_area("キービジュアルの説明", default_params["key_visual_description"], height=80,
                                            help="メイン画像に含めたい要素や被写体の説明")
                    default_params["key_visual_description"] = key_visual
                    
                    additional_elements = st.text_area("追加で欲しい要素", default_params["additional_elements"], height=80,
                                                    help="追加したい要素があれば記入してください")
                    default_params["additional_elements"] = additional_elements
                    
                with col2:
                    brand_colors = st.text_input("ブランドカラー・フォント", default_params["brand_colors_fonts"],
                                                help="特定の色やフォントがあれば指定してください（例: 赤と黒、ゴシック体）")
                    default_params["brand_colors_fonts"] = brand_colors
                    
                    ng_elements = st.text_area("NG要素", default_params["ng_elements"], height=80,
                                            help="避けたい要素があれば記入してください")
                    default_params["ng_elements"] = ng_elements
                
                # パラメータの更新
                default_params["campaign_theme"] = campaign_theme
                default_params["product_name"] = product_name
                default_params["main_message"] = main_message
                default_params["sub_copy"] = sub_copy
                default_params["call_to_action"] = call_to_action
                
                # ユーザーが画像分析結果を確認したことをマーク
                st.session_state.analyzed = True
                st.session_state.template_params = default_params
            
            # UIの区切り線
            st.markdown("---")
            
            # テキスト生成ボタン - 目立つデザイン
            st.markdown('<div class="sub-action-button">', unsafe_allow_html=True)
            generate_text_button = st.button("✨ コンテキストからテキスト生成", use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            if generate_text_button:
                with st.spinner("テキストを生成中..."):
                    copy_suggestions = generate_ad_copy_from_context(client, default_params)
                    if copy_suggestions:
                        st.session_state.copy_suggestions = copy_suggestions
                        
                        # テキスト候補を表示 - カード形式で表示改善
                        st.success("✅ テキスト候補が生成されました。お好みのテキストを選択してください。")
                        
                        # タブで表示するようにUI改善
                        text_tabs = st.tabs(["📣 メインメッセージ", "📝 サブコピー", "🔔 コールトゥアクション"])
                        
                        # メインメッセージ選択
                        with text_tabs[0]:
                            st.markdown("#### メインメッセージの候補")
                            main_message_options = copy_suggestions.get("main_messages", [])
                            for i, msg in enumerate(main_message_options):
                                col1, col2 = st.columns([8, 2])
                                with col1:
                                    st.markdown(f"""
                                    <div style="padding:0.7rem; background-color:#F9FAFB; border-radius:6px; margin-bottom:0.5rem;">
                                        {msg}
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    if st.button(f"選択", key=f"main_msg_new_{i}"):
                                        default_params["main_message"] = msg
                                        st.session_state.template_params = default_params
                                        st.success(f"メインメッセージを「{msg}」に設定しました")
                        
                        # サブコピー選択
                        with text_tabs[1]:
                            st.markdown("#### サブコピーの候補")
                            sub_copy_options = copy_suggestions.get("sub_copies", [])
                            for i, copy in enumerate(sub_copy_options):
                                col1, col2 = st.columns([8, 2])
                                with col1:
                                    st.markdown(f"""
                                    <div style="padding:0.7rem; background-color:#F9FAFB; border-radius:6px; margin-bottom:0.5rem;">
                                        {copy}
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    if st.button(f"選択", key=f"sub_copy_new_{i}"):
                                        default_params["sub_copy"] = copy
                                        st.session_state.template_params = default_params
                                        st.success(f"サブコピーを設定しました")
                        
                        # コールトゥアクション選択
                        with text_tabs[2]:
                            st.markdown("#### コールトゥアクションの候補")
                            cta_options = copy_suggestions.get("call_to_actions", [])
                            for i, cta in enumerate(cta_options):
                                col1, col2 = st.columns([8, 2])
                                with col1:
                                    st.markdown(f"""
                                    <div style="padding:0.7rem; background-color:#F9FAFB; border-radius:6px; margin-bottom:0.5rem;">
                                        {cta}
                                    </div>
                                    """, unsafe_allow_html=True)
                                with col2:
                                    if st.button(f"選択", key=f"cta_new_{i}"):
                                        default_params["call_to_action"] = cta
                                        st.session_state.template_params = default_params
                                        st.success(f"コールトゥアクションを「{cta}」に設定しました")
            
            # テンプレート生成
            template = generate_ad_creative_template(default_params)
            st.session_state.template = template
            
            # テンプレートを表示 - 折りたたみ可能に
            with st.expander("🧩 生成されたテンプレート（詳細）", expanded=False):
                st.code(template, language="yaml")
            
            # 続行確認（新規パターン）
            if uploaded_file is None:
                # 編集プロンプト生成
                edit_prompt = generate_edit_prompt(template, user_feedback)
                
                # 編集プロンプトを表示 - 折りたたみ可能に
                with st.expander("🔍 生成されたプロンプト（詳細）", expanded=False):
                    st.code(edit_prompt)
                
                # 最終生成ボタン - 目立つデザイン
                st.markdown('<div class="final-action-button">', unsafe_allow_html=True)
                proceed_new = st.button("🎨 広告画像を生成", type="primary", key="proceed_new", use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                if proceed_new:
                    # 画像生成中のプログレスバーと状態表示
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # 各ステップの進捗表示
                    status_text.text("画像生成を準備中...")
                    progress_bar.progress(10)
                    
                    status_text.text("画像生成中...")
                    progress_bar.progress(30)
                    
                    # 画像生成
                    edited_image_path, edited_image_bytes = edit_image(client, "", edit_prompt)
                    progress_bar.progress(80)
                    
                    if edited_image_path and edited_image_bytes:
                        status_text.text("画像を処理中...")
                        progress_bar.progress(90)
                        
                        st.session_state.edited_image_path = edited_image_path
                        st.session_state.edited_image_bytes = edited_image_bytes
                        
                        # プログレス完了
                        progress_bar.progress(100)
                        status_text.success("✅ 画像生成が完了しました！")
                        
                        # 結果表示エリア - デザイン改善
                        st.markdown("""
                        <div style="margin-top:2rem; text-align:center;">
                            <h2 style="color:#1E3A8A;">🎉 生成された広告画像</h2>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # 画像とダウンロードボタンを並べて表示
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.image(edited_image_path, caption="AI生成広告画像", use_column_width=True)
                        with col2:
                            st.markdown("### ダウンロード")
                            st.download_button(
                                label="📥 画像をダウンロード",
                                data=edited_image_bytes,
                                file_name=f"{default_params['campaign_theme'].replace(' ', '_')}_ad.png",
                                mime="image/png",
                                use_container_width=True
                            )
                            
                            # メタデータ表示
                            st.markdown("#### 画像情報")
                            st.markdown(f"""
                            - **キャンペーン**: {default_params['campaign_theme']}
                            - **サイズ**: {default_params['size_aspect_ratio']}
                            - **生成日時**: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}
                            """)
                    else:
                        progress_bar.empty()
                        status_text.error("❌ 画像の生成に失敗しました。")
                        st.error("画像の生成中にエラーが発生しました。別のプロンプトや設定で再試行してください。")

if __name__ == "__main__":
    main()
