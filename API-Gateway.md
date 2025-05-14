# API Gateway

## 概要

API Gatewayは、クライアントからのすべてのリクエストのエントリーポイントとして機能し、適切なマイクロサービスにルーティングします。

## 責務

- リクエストのルーティング
- 認証・認可
- レート制限
- リクエスト/レスポンスの変換
- API文書化

## 技術スタック

- **フレームワーク**: Express.js
- **言語**: TypeScript
- **ドキュメント**: OpenAPI (Swagger)
- **認証**: JWT
- **レート制限**: express-rate-limit

## 主要コンポーネント

```typescript
// API Gatewayのルーティング設定例
import express from 'express';
import { authenticateJWT } from './middleware/auth';
import { rateLimit } from './middleware/rateLimit';

const app = express();

// ミドルウェア
app.use(express.json());
app.use(authenticateJWT);
app.use(rateLimit);

// ルーティング
app.use('/api/workflows', require('./routes/workflows'));
app.use('/api/templates', require('./routes/templates'));
app.use('/api/images', require('./routes/images'));
app.use('/api/auth', require('./routes/auth'));

// エラーハンドリング
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

export default app;
```

## エンドポイント一覧

| エンドポイント | メソッド | 説明 | 認証 |
|--------------|---------|------|------|
| `/api/auth/login` | POST | ユーザー認証 | 不要 |
| `/api/auth/register` | POST | ユーザー登録 | 不要 |
| `/api/workflows` | GET | ワークフロー一覧取得 | 必要 |
| `/api/workflows/:id` | GET | ワークフロー詳細取得 | 必要 |
| `/api/workflows` | POST | ワークフロー作成 | 必要 |
| `/api/templates` | GET | テンプレート一覧取得 | 必要 |
| `/api/templates/:id` | GET | テンプレート詳細取得 | 必要 |
| `/api/templates` | POST | テンプレート作成 | 必要 |
| `/api/images/analyze` | POST | 画像解析 | 必要 |
| `/api/images/generate` | POST | 画像生成 | 必要 |

## セキュリティ対策

- JWT認証
- レート制限（IP単位、ユーザー単位）
- CORS設定
- Helmet（セキュリティヘッダー設定）
- 入力バリデーション
