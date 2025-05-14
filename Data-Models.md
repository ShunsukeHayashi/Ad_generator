# データモデルとスキーマ

このページでは、「Ad Creative Template v1.0」で使用されるデータモデルとスキーマについて説明します。

## テンプレートモデル

テンプレートは、広告の基本構造とスタイルを定義します。

```typescript
// テンプレートスキーマ
const TemplateSchema = z.object({
  campaign_thema: z.string(),
  core_content: z.object({
    product_name: z.string(),
    target_audience: z.string(),
    brand_tone: z.string(),
    key_message: z.string(),
    usp: z.string(),
    call_to_action: z.string()
  }),
  design_style: z.object({
    style_preset: z.object({
      source: z.string(),
      name: z.string(),
      detail: z.object({
        color_scheme: z.object({
          primary: z.string(),
          secondary: z.string().optional(),
          accent1: z.string().optional(),
          accent2: z.string().optional()
        }),
        mood: z.string(),
        style: z.string(),
        format: z.string()
      })
    }),
    custom_style: z.object({
      // カスタムスタイル属性
    }).optional()
  }),
  dynamic_variables: z.record(z.string(), z.any()).optional(),
  brand_assets: z.array(z.any()).optional(),
  created_at: z.date().optional(),
  updated_at: z.date().optional(),
  version: z.number().optional()
});
```
