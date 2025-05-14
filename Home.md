# Ad Creative Template v1.0 ドキュメント

このWikiでは、「Ad Creative Template v1.0」を中核とした広告画像生成プラットフォームの技術仕様と開発計画について詳細に解説します。

## 目次

1. [システムアーキテクチャ](System-Architecture)
2. [コンポーネント詳細仕様](Component-Specifications)
   - [API Gateway](API-Gateway)
   - [ワークフローエンジン](Workflow-Engine)
   - [画像解析サービス](Image-Analysis-Service)
   - [テンプレートサービス](Template-Service)
   - [プロンプト生成サービス](Prompt-Generation-Service)
   - [画像生成サービス](Image-Generation-Service)
   - [認証・認可サービス](Authentication-Service)
3. [データモデルとスキーマ](Data-Models)
4. [APIインターフェース仕様](API-Specifications)
5. [ユーザーインターフェース仕様](UI-Specifications)
6. [セキュリティ仕様](Security-Specifications)
7. [パフォーマンス要件](Performance-Requirements)
8. [テスト仕様](Testing-Specifications)
9. [開発計画](Development-Plan)

## プロジェクト概要

「Ad Creative Template v1.0」は、Mastraフレームワークを活用した広告画像生成プラットフォームです。このプラットフォームは、ユーザーが提供する基本的な広告情報とイメージをもとに、AIを活用して高品質な広告クリエイティブを自動生成します。

主な特徴：

- マイクロサービスアーキテクチャによる拡張性と柔軟性
- Mastraフレームワークを活用したエージェントベースのワークフロー
- OpenAI GPT-Image-1を使用した高品質な画像生成
- テンプレートベースのアプローチによる一貫性と効率性
- ユーザーインテントに基づくカスタマイズ機能

## 技術スタック

- **バックエンド**: TypeScript/Node.js, Express.js, NestJS
- **フロントエンド**: React, Next.js, Material-UI
- **データベース**: LibSQL, MongoDB
- **インフラ**: Docker, Kubernetes
- **AI**: OpenAI API (GPT-4o, GPT-Image-1)
- **フレームワーク**: Mastra Core
