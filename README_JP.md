# RAG AI ノートシステム

React | FastAPI | Firebase | Weaviate | OpenAI | Terraform | GCP

セマンティック検索とAI搭載の洞察機能を備えたフルスタック Retrieval-Augmented Generation ノートシステム

---

## 免責事項

本プロジェクトは、以下の Monoya 求人職種の技術的デモンストレーションとして構築された、トイ RAG フルスタックプロジェクトです:
- フルスタックエンジニア: https://www.tokyodev.com/companies/monoya/jobs/full-stack-engineer
- AI/機械学習エンジニア: https://www.tokyodev.com/companies/monoya/jobs/ai-machine-learning-engineer

本プロジェクトは、実際の製品、サービス、またはビジネス運営を反映するものではありません。純粋に教育的かつ実証的な実装です。

---

## 概要

AI 日記は、個人的な日記作成と人工知能を組み合わせた最新のウェブアプリケーションです。本システムは、Retrieval-Augmented Generation (RAG) 技術を使用して、日記の履歴に基づいた文脈的な洞察を提供します。

### 主要機能

- ユーザー認証と安全なアクセス制御
- 日記エントリの作成、読み取り、更新、削除
- 日記履歴に基づくAI搭載のパーソナライズされた洞察
- ベクトル埋め込みを使用したセマンティック検索
- モダンでレスポンシブなユーザーインターフェース
- 水平スケーラビリティを備えたクラウドネイティブアーキテクチャ

### 技術スタック

**フロントエンド**
- React と Vite ビルドシステム
- スタイリングに Tailwind CSS
- Firebase Authentication SDK
- 状態管理に Zustand
- HTTP 通信に Axios

**バックエンド**
- FastAPI Python フレームワーク
- Firebase Admin SDK
- OpenAI API 統合
- Weaviate ベクトルデータベース
- データ永続化に Google Firestore

**インフラストラクチャ**
- Docker コンテナ化
- Google Cloud Platform デプロイメント
- Terraform インフラストラクチャコード
- GitHub Actions CI/CD パイプライン

---

## 始め方

### 前提条件

- Node.js 20 以上
- Python 3.11 以上
- Docker と Docker Compose
- Google Cloud Platform アカウント
- Firebase プロジェクト
- OpenAI API キー

### ローカル開発

1. リポジトリのクローン

```bash
git clone <repository-url>
cd JD_Project
```

2. 環境変数の設定

```bash
cp env.example .env
```

`.env` ファイルを編集し、以下の認証情報を設定:
- Firebase 設定
- OpenAI API キー
- Weaviate 設定
- バックエンド API URL

3. Firebase のセットアップ

- https://console.firebase.google.com でプロジェクトを作成
- メール/パスワードプロバイダーで認証を有効化
- Firestore データベースを有効化
- サービスアカウントキーを `service-account.json` としてダウンロード
- Firebase 設定を `.env` ファイルに追加

4. アプリケーションの起動

```bash
docker-compose up --build
```

アプリケーションへのアクセス:
- フロントエンド: http://localhost:5173
- バックエンド API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs
- Weaviate コンソール: http://localhost:8080

### 手動セットアップ

**バックエンド**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

**フロントエンド**

```bash
cd frontend
npm install
npm run dev
```

---

## プロジェクト構造

```
JD_Project/
├── frontend/                 React アプリケーション
│   ├── src/
│   │   ├── api/             API クライアント層
│   │   ├── config/          設定ファイル
│   │   ├── pages/           ページコンポーネント
│   │   └── store/           状態管理
│   ├── Dockerfile
│   └── package.json
│
├── backend/                  FastAPI アプリケーション
│   ├── app/
│   │   ├── api/             ルートハンドラー
│   │   ├── core/            コア設定
│   │   ├── models/          データモデル
│   │   └── services/        ビジネスロジック
│   ├── Dockerfile
│   └── requirements.txt
│
├── terraform/                Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
│
├── docs/                     ドキュメント
└── scripts/                  デプロイメントスクリプト
```

---

## API ドキュメント

### エンドポイント

**日記管理**
- `GET /diaries` - すべての日記エントリを取得
- `POST /diaries` - 新しい日記エントリを作成
- `GET /diaries/{id}` - 特定の日記を取得
- `PUT /diaries/{id}` - 日記エントリを更新
- `DELETE /diaries/{id}` - 日記エントリを削除

**AI 機能**
- `POST /diaries/{id}/ai-insight` - AI 洞察を生成

すべてのエンドポイントは Firebase JWT トークンによる認証が必要です。

完全な API ドキュメントは、バックエンド実行時の `/docs` エンドポイントで利用可能です。

---

## デプロイメント

### Google Cloud Platform

1. Terraform の初期化

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# terraform.tfvars を編集して値を設定
terraform init
terraform plan
terraform apply
```

2. Docker イメージのビルドとプッシュ

```bash
export PROJECT_ID=your-project-id
gcloud auth configure-docker us-central1-docker.pkg.dev

# バックエンド
cd backend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest

# フロントエンド
cd frontend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest
```

3. GitHub Actions の設定

以下のリポジトリシークレットを設定:
- `GCP_PROJECT_ID`
- `GCP_SA_KEY`
- `OPENAI_API_KEY`
- `VITE_API_URL`
- `VITE_FIREBASE_API_KEY`
- `VITE_FIREBASE_AUTH_DOMAIN`
- `VITE_FIREBASE_PROJECT_ID`

`main` ブランチへのプッシュで自動デプロイメントがトリガーされます。

---

## ドキュメント

`docs/` ディレクトリに包括的なドキュメントが用意されています:

- アーキテクチャ概要とシステム設計
- GCP デプロイメントガイド
- ローカル開発セットアップ
- Weaviate 設定チュートリアル
- Terraform インフラストラクチャガイド
- RAG フロー説明

---

## テスト

**フロントエンド**

```bash
cd frontend
npm run lint
npm run build
```

**バックエンド**

```bash
cd backend
pip install pytest pytest-asyncio
pytest
```

---

## セキュリティに関する考慮事項

- ID 管理のための Firebase Authentication
- すべての API エンドポイントでの JWT トークン検証
- 最小権限の原則に基づくサービスアカウント
- シークレットの環境変数管理
- データアクセス制御のための Firestore セキュリティルール

---

## 貢献

貢献を歓迎します。以下の手順に従ってください:

1. リポジトリをフォーク
2. フィーチャーブランチを作成
3. 明確なメッセージでコミット
4. フォークにプッシュ
5. プルリクエストを提出

---

## ライセンス

このプロジェクトは MIT ライセンスの下でライセンスされています。詳細は LICENSE ファイルを参照してください。

---

## サポート

問題や質問については、GitHub イシュートラッカーをご利用ください。

---

## 参考資料

- React: https://react.dev
- FastAPI: https://fastapi.tiangolo.com
- Firebase: https://firebase.google.com/docs
- OpenAI: https://platform.openai.com/docs
- Weaviate: https://weaviate.io/developers/weaviate
- Terraform: https://registry.terraform.io/providers/hashicorp/google/latest/docs
- Google Cloud Run: https://cloud.google.com/run/docs

