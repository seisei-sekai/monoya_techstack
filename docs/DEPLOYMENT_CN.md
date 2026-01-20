# 部署指南

本指南提供将AI日记应用部署到Google Cloud Platform的详细说明。

## 前置要求

开始之前，请确保：

1. **Google Cloud Platform账号**
   - 已启用计费的GCP项目
   - 项目具有所有者或编辑者角色

2. **已安装本地工具**
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - [Terraform](https://www.terraform.io/downloads) (v1.0+)
   - [Docker](https://docs.docker.com/get-docker/)
   - Git

3. **API密钥和凭据**
   - OpenAI API密钥
   - 已设置Firebase项目

## 初始GCP设置

### 1. 创建GCP项目

```bash
# 设置项目ID
export PROJECT_ID="ai-diary-$(date +%s)"

# 创建项目
gcloud projects create $PROJECT_ID --name="AI Diary"

# 设为默认项目
gcloud config set project $PROJECT_ID

# 启用计费（必须通过控制台完成）
echo "为项目 $PROJECT_ID 启用计费，访问："
echo "https://console.cloud.google.com/billing/linkedaccount?project=$PROJECT_ID"
```

### 2. 启用必需的API

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com \
  cloudresourcemanager.googleapis.com
```

### 3. 创建服务账号

```bash
# Cloud Run后端的服务账号
gcloud iam service-accounts create ai-diary-backend-sa \
  --display-name="AI Diary Backend Service Account"

# 授予必要权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/storage.objectViewer"

# GitHub Actions的服务账号
gcloud iam service-accounts create github-actions-sa \
  --display-name="GitHub Actions Service Account"

# 授予部署权限
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# 下载GitHub Actions的密钥
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com
```

### 4. 设置Firebase

1. 访问 [Firebase控制台](https://console.firebase.google.com)
2. 将Firebase添加到现有GCP项目
3. 启用身份验证：
   - 转到 Authentication > Sign-in method
   - 启用"Email/Password"
4. 创建Firestore数据库：
   - 转到 Firestore Database
   - 以生产模式创建数据库
   - 选择位置（例如：us-central）
5. 设置Firestore安全规则：

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 日记集合
    match /diaries/{diaryId} {
      // 仅当用户已认证且拥有该文档时允许读写
      allow read, write: if request.auth != null 
                         && request.auth.uid == resource.data.userId;
      // 仅当用户已认证且设置正确的userId时允许创建
      allow create: if request.auth != null 
                    && request.auth.uid == request.resource.data.userId;
    }
  }
}
```

6. 下载服务账号密钥：
   - 转到项目设置 > 服务账号
   - 点击"生成新的私钥"
   - 保存为 `service-account.json`

## Terraform部署

### 1. 准备Terraform后端

```bash
# 为Terraform状态创建GCS存储桶
gsutil mb gs://$PROJECT_ID-terraform-state

# 启用版本控制
gsutil versioning set on gs://$PROJECT_ID-terraform-state
```

### 2. 配置Terraform变量

```bash
cd terraform

# 复制示例tfvars
cp terraform.tfvars.example terraform.tfvars

# 使用你的值编辑
nano terraform.tfvars
```

示例 `terraform.tfvars`：
```hcl
project_id         = "ai-diary-123456"
region             = "us-central1"
firestore_location = "us-central"
openai_api_key     = "sk-..."
firebase_api_key   = "AIza..."
```

### 3. 初始化并应用Terraform

```bash
# 初始化Terraform
terraform init

# 查看计划
terraform plan

# 应用配置
terraform apply

# 保存输出
terraform output -json > ../terraform-outputs.json
```

## 构建和部署应用

### 1. 构建Docker镜像

```bash
# 使用Artifact Registry进行身份验证
gcloud auth configure-docker us-central1-docker.pkg.dev

# 构建后端镜像
cd ../backend
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest

# 构建前端镜像
cd ../frontend
docker build \
  --build-arg VITE_API_URL=$(terraform output -raw backend_url) \
  --build-arg VITE_FIREBASE_API_KEY=$FIREBASE_API_KEY \
  --build-arg VITE_FIREBASE_AUTH_DOMAIN=$PROJECT_ID.firebaseapp.com \
  --build-arg VITE_FIREBASE_PROJECT_ID=$PROJECT_ID \
  -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest .
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest
```

### 2. 部署到Cloud Run

服务应该通过Terraform自动部署，但你也可以手动更新：

```bash
# 部署Weaviate
gcloud run deploy ai-diary-weaviate \
  --image=semitechnologies/weaviate:1.23.0 \
  --platform=managed \
  --region=us-central1 \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=5

# 获取Weaviate URL
WEAVIATE_URL=$(gcloud run services describe ai-diary-weaviate \
  --region=us-central1 \
  --format='value(status.url)')

# 部署后端
gcloud run deploy ai-diary-backend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --set-env-vars="OPENAI_API_KEY=$OPENAI_API_KEY,FIREBASE_PROJECT_ID=$PROJECT_ID,WEAVIATE_URL=$WEAVIATE_URL" \
  --service-account=ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

# 获取后端URL
BACKEND_URL=$(gcloud run services describe ai-diary-backend \
  --region=us-central1 \
  --format='value(status.url)')

# 部署前端
gcloud run deploy ai-diary-frontend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/frontend:latest \
  --platform=managed \
  --region=us-central1 \
  --allow-unauthenticated \
  --memory=256Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10

# 获取前端URL
FRONTEND_URL=$(gcloud run services describe ai-diary-frontend \
  --region=us-central1 \
  --format='value(status.url)')

echo "部署完成！"
echo "前端: $FRONTEND_URL"
echo "后端: $BACKEND_URL"
```

## GitHub Actions CI/CD设置

### 1. 配置GitHub Secrets

在GitHub仓库中，转到 Settings > Secrets and variables > Actions，添加：

- `GCP_PROJECT_ID`：你的GCP项目ID
- `GCP_SA_KEY`：`github-actions-key.json` 的内容
- `OPENAI_API_KEY`：你的OpenAI API密钥
- `VITE_API_URL`：Cloud Run后端URL
- `VITE_FIREBASE_API_KEY`：Firebase API密钥
- `VITE_FIREBASE_AUTH_DOMAIN`：`your-project-id.firebaseapp.com`
- `VITE_FIREBASE_PROJECT_ID`：Firebase项目ID

### 2. 启用GitHub Actions

工作流已在 `.github/workflows/` 中配置。只需推送到 `main` 分支即可触发部署：

```bash
git add .
git commit -m "初始部署"
git push origin main
```

## 部署后配置

### 1. 配置自定义域名（可选）

```bash
# 将自定义域名映射到前端
gcloud run domain-mappings create \
  --service=ai-diary-frontend \
  --domain=yourdomain.com \
  --region=us-central1

# 按照说明配置DNS
```

### 2. 设置监控

```bash
# 启用Cloud Logging
gcloud services enable logging.googleapis.com

# 查看日志
gcloud run logs read ai-diary-backend --limit=50
gcloud run logs read ai-diary-frontend --limit=50

# 设置警报（通过控制台）
echo "在以下位置配置警报: https://console.cloud.google.com/monitoring/alerting"
```

### 3. 配置Firestore索引

为更好的查询性能创建索引：

```bash
# 为日记创建复合索引
gcloud firestore indexes composite create \
  --collection-group=diaries \
  --field-config=field-path=userId,order=ascending \
  --field-config=field-path=createdAt,order=descending
```

## 监控和维护

### 查看日志

```bash
# 后端日志
gcloud run logs read ai-diary-backend --limit=100

# 前端日志
gcloud run logs read ai-diary-frontend --limit=100

# Weaviate日志
gcloud run logs read ai-diary-weaviate --limit=100
```

### 检查服务状态

```bash
# 列出所有服务
gcloud run services list

# 描述特定服务
gcloud run services describe ai-diary-backend --region=us-central1
```

### 更新服务

```bash
# 构建并推送新镜像
docker build -t us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:v2 ./backend
docker push us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:v2

# 更新Cloud Run服务
gcloud run services update ai-diary-backend \
  --image=us-central1-docker.pkg.dev/$PROJECT_ID/ai-diary-images/backend:v2 \
  --region=us-central1
```

### 成本管理

```bash
# 查看当前成本
gcloud billing accounts list
gcloud billing projects describe $PROJECT_ID

# 通过控制台设置预算警报
echo "在以下位置设置预算: https://console.cloud.google.com/billing/budgets"
```

## 回滚

如果需要回滚到之前的版本：

```bash
# 列出版本
gcloud run revisions list --service=ai-diary-backend --region=us-central1

# 回滚到之前的版本
gcloud run services update-traffic ai-diary-backend \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1
```

## 清理

删除所有资源：

```bash
# 使用Terraform
cd terraform
terraform destroy

# 或手动删除服务
gcloud run services delete ai-diary-backend --region=us-central1 --quiet
gcloud run services delete ai-diary-frontend --region=us-central1 --quiet
gcloud run services delete ai-diary-weaviate --region=us-central1 --quiet

# 删除Artifact Registry仓库
gcloud artifacts repositories delete ai-diary-images --location=us-central1 --quiet

# 删除服务账号
gcloud iam service-accounts delete ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com --quiet
gcloud iam service-accounts delete github-actions-sa@$PROJECT_ID.iam.gserviceaccount.com --quiet
```

## 故障排除

### 服务无法启动

1. 查看日志：`gcloud run logs read SERVICE_NAME`
2. 验证环境变量设置正确
3. 确保服务账号具有适当权限
4. 检查所有依赖服务是否运行

### 身份验证问题

1. 验证Firebase配置正确
2. 检查服务账号密钥是否有效
3. 确保Firestore安全规则配置正确
4. 验证JWT令牌正确发送

### 数据库连接问题

1. 检查Firestore是否启用且可访问
2. 验证服务账号具有 `datastore.user` 角色
3. 检查服务之间的网络连接

### 高成本

1. 将开发环境的min-instances设为0
2. 启用基于请求的自动扩展
3. 设置适当的内存/CPU限制
4. 使用Cloud Logging过滤器减少日志量

## 性能优化

### 减少冷启动时间

```bash
# 设置最小实例（会增加成本）
gcloud run services update ai-diary-backend \
  --min-instances=1 \
  --region=us-central1
```

### 优化内存使用

```bash
# 根据实际使用调整内存
gcloud run services update ai-diary-backend \
  --memory=256Mi \  # 如果足够
  --region=us-central1
```

### 配置并发

```bash
# 增加每个实例的并发请求数
gcloud run services update ai-diary-backend \
  --concurrency=80 \
  --region=us-central1
```

## 安全最佳实践

### 1. 密钥管理

```bash
# 使用Secret Manager（推荐用于生产）
gcloud secrets create openai-api-key --data-file=-

# 授予服务账号访问权限
gcloud secrets add-iam-policy-binding openai-api-key \
  --member="serviceAccount:ai-diary-backend-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 2. 网络安全

```bash
# 限制Cloud Run入口（仅内部流量）
gcloud run services update ai-diary-backend \
  --ingress=internal \
  --region=us-central1
```

### 3. 身份验证

```bash
# 移除公共访问（需要身份验证）
gcloud run services remove-iam-policy-binding ai-diary-backend \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=us-central1
```

## 备份策略

### Firestore备份

```bash
# 手动导出
gcloud firestore export gs://$PROJECT_ID-backups

# 计划备份（通过控制台）
echo "在控制台设置自动备份"
```

### Terraform状态备份

```bash
# 备份Terraform状态
gsutil cp gs://$PROJECT_ID-terraform-state/terraform/state/default.tfstate \
  ./backup-$(date +%Y%m%d).tfstate
```

## 多环境部署

### 开发环境

```bash
# 创建开发项目
export DEV_PROJECT_ID="ai-diary-dev"
gcloud projects create $DEV_PROJECT_ID

# 使用不同的tfvars部署
terraform workspace new dev
terraform apply -var-file="dev.tfvars"
```

### 生产环境

```bash
# 生产项目
export PROD_PROJECT_ID="ai-diary-prod"

terraform workspace new prod
terraform apply -var-file="prod.tfvars"
```

## 监控仪表板

### 创建自定义仪表板

1. 访问 Cloud Console > Monitoring
2. 创建新仪表板
3. 添加图表：
   - Cloud Run请求计数
   - 响应时间
   - 错误率
   - CPU和内存使用
   - 成本趋势

### 设置警报策略

```bash
# 示例：高错误率警报
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="High Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05
```

## 支持

针对GCP部署的特定问题，请查阅：
- [Cloud Run文档](https://cloud.google.com/run/docs)
- [Terraform GCP Provider文档](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCP支持](https://cloud.google.com/support)

## 检查清单

部署前：
- [ ] GCP项目已创建并启用计费
- [ ] 所有必需的API已启用
- [ ] Firebase项目已设置
- [ ] 服务账号已创建并授权
- [ ] 环境变量已配置
- [ ] Terraform已初始化

部署后：
- [ ] 所有服务运行正常
- [ ] 可以访问前端URL
- [ ] API健康检查通过
- [ ] 可以创建账号和登录
- [ ] 日记功能正常工作
- [ ] AI洞察生成正常
- [ ] 日志和监控已设置
- [ ] 警报已配置
- [ ] 备份策略已实施

## 常见问题

**Q: 部署需要多长时间？**
A: 首次完整部署通常需要10-15分钟。

**Q: 每月成本是多少？**
A: 对于小流量，预计$20-60/月。使用量增加时成本会增长。

**Q: 可以使用其他云提供商吗？**
A: 可以，但需要调整Terraform配置和部署脚本。

**Q: 如何实现零停机部署？**
A: Cloud Run自动支持零停机部署，使用流量分割逐步迁移。

**Q: 支持自动扩展吗？**
A: 是的，Cloud Run根据流量自动扩展（0-10实例可配置）。

祝部署顺利！🚀

