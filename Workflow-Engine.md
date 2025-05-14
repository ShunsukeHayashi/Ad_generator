# ワークフローエンジン

## 概要

ワークフローエンジンは、Mastraフレームワークを使用して広告生成ワークフローを管理します。ワークフローの定義、実行、状態管理、エラーハンドリングを担当します。

## 責務

- ワークフローの定義と管理
- ワークフローの実行と監視
- ステップ間のデータ受け渡し
- エラーハンドリングとリトライ
- 状態の永続化

## 技術スタック

- **フレームワーク**: Mastra Core
- **言語**: TypeScript
- **状態管理**: LibSQL
- **メッセージング**: RabbitMQ

## ワークフロー定義

```typescript
// 広告生成ワークフローの定義例
import { Workflow } from '@mastra/core/workflows';
import {
  analyzeImageStep,
  generateTemplateStep,
  applyUserIntentStep,
  generatePromptStep,
  generateImageStep
} from './steps';

export const adGenerationWorkflow = new Workflow({
  id: 'ad-generation',
  steps: [
    {
      id: 'analyze-image',
      step: analyzeImageStep,
      next: 'generate-template'
    },
    {
      id: 'generate-template',
      step: generateTemplateStep,
      next: 'apply-user-intent'
    },
    {
      id: 'apply-user-intent',
      step: applyUserIntentStep,
      next: 'generate-prompt'
    },
    {
      id: 'generate-prompt',
      step: generatePromptStep,
      next: 'generate-image'
    },
    {
      id: 'generate-image',
      step: generateImageStep,
      next: null
    }
  ],
  conditions: [
    {
      id: 'check-user-intent',
      condition: (context) => !!context.userIntent,
      ifTrue: 'apply-user-intent',
      ifFalse: 'generate-prompt'
    }
  ],
  parameters: {
    timeout: 300000, // 5分
    retries: 3,
    retryDelay: 5000 // 5秒
  }
});
```

## ワークフローステップ

### 1. 画像解析ステップ

入力画像の特徴（色彩、スタイル、構図など）を抽出します。

### 2. テンプレート生成ステップ

画像解析結果とキャンペーンデータに基づいて広告テンプレートを生成します。

### 3. ユーザーインテント適用ステップ

ユーザーの意図や要望に基づいてテンプレートをカスタマイズします。

### 4. プロンプト生成ステップ

テンプレートとユーザーインテントに基づいて、画像生成に最適化されたプロンプトを生成します。

### 5. 画像生成ステップ

最適化されたプロンプトを使用してOpenAI GPT-Image-1 APIを呼び出し、広告画像を生成します。
