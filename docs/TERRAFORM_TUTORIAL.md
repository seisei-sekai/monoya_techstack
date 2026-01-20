# 🏗️ Terraform 基础设施即代码完全教程

## 📚 目录

1. [Terraform 基础](#terraform-基础)
2. [项目架构](#项目架构)
3. [环境配置](#环境配置)
4. [Provider 配置](#provider-配置)
5. [资源管理](#资源管理)
6. [状态管理](#状态管理)
7. [变量与输出](#变量与输出)
8. [模块化](#模块化)
9. [最佳实践](#最佳实践)
10. [故障排查](#故障排查)

---

## 🎯 Terraform 基础

### 什么是 Terraform？

**Terraform** 是一个基础设施即代码 (Infrastructure as Code, IaC) 工具，用代码管理云资源。

```
传统部署 vs Terraform

传统方式:
1. 打开 GCP Console
2. 点击 "创建 Cloud Run 服务"
3. 填写表单...
4. 点击 "创建"
❌ 问题: 手动、不可重复、难以版本控制

Terraform 方式:
1. 编写 main.tf
2. terraform apply
✅ 优势: 自动化、可重复、版本控制
```

### 核心概念

#### 1. 声明式配置

```hcl
# 描述你想要的最终状态
resource "google_cloud_run_service" "backend" {
  name     = "ai-diary-backend"
  location = "us-central1"
  
  template {
    spec {
      containers {
        image = "gcr.io/my-project/backend:latest"
      }
    }
  }
}

# Terraform 会自动计算需要执行的操作
```

#### 2. 状态管理

```
┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│  Terraform   │       │  State File  │       │  Real Cloud  │
│  Config      │       │  (当前状态)   │       │  Resources   │
│  (.tf 文件)  │       │              │       │  (GCP)       │
└──────────────┘       └──────────────┘       └──────────────┘
       ↓                      ↓                      ↓
    期望状态  →  terraform apply  →  比较差异  →  执行变更
```

#### 3. 资源图

```
frontend → depends_on → backend
                         ↓
                    weaviate
                         ↓
                    firestore
```

Terraform 自动解析依赖关系，并行创建资源。

---

## 🏗️ 项目架构

### 本项目的 GCP 架构

```
┌─────────────────────────────────────────────────────────┐
│                     AI Diary 架构                        │
└─────────────────────────────────────────────────────────┘

Internet
   │
   ├─→ Cloud Run (Frontend)
   │   └─→ Static files (React)
   │
   ├─→ Cloud Run (Backend)
   │   ├─→ FastAPI
   │   ├─→ OpenAI API
   │   └─→ Service Account
   │        ├─→ Firestore (Database)
   │        └─→ Cloud Storage
   │
   └─→ Cloud Run (Weaviate)
       └─→ Vector Database

Docker Images
   └─→ Artifact Registry
       ├─→ frontend:latest
       ├─→ backend:latest
       └─→ weaviate:1.23.0
```

### Terraform 文件结构

```
terraform/
├── main.tf          # 主配置文件（资源定义）
├── variables.tf     # 输入变量
├── outputs.tf       # 输出值
└── terraform.tfvars # 变量值（不提交到 Git）

生成的文件:
├── .terraform/      # Provider 插件
├── terraform.tfstate      # 状态文件（存储在 GCS）
└── .terraform.lock.hcl    # Provider 版本锁定
```

---

## ⚙️ 环境配置

### 1. 安装 Terraform

```bash
# macOS
brew install terraform

# 验证安装
terraform version
# Terraform v1.7.0
```

### 2. 安装 Google Cloud SDK

```bash
# macOS
brew install --cask google-cloud-sdk

# 登录
gcloud auth login

# 设置项目
gcloud config set project YOUR_PROJECT_ID

# 配置 Application Default Credentials
gcloud auth application-default login
```

### 3. 启用必需的 GCP APIs

```bash
# 使用 gcloud 启用
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  firebase.googleapis.com \
  artifactregistry.googleapis.com

# 或者让 Terraform 自动启用（推荐）
```

---

## 🔧 Provider 配置

### 1. Terraform 块

```hcl
# terraform/main.tf
terraform {
  # 要求 Terraform 版本 >= 1.0
  required_version = ">= 1.0"
  
  # 声明需要的 Provider
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"  # 允许 5.x 版本
    }
  }
  
  # 远程状态存储（生产环境）
  backend "gcs" {
    bucket = "ai-diary-terraform-state"
    prefix = "terraform/state"
  }
}
```

**版本约束语法**：

| 约束 | 说明 | 示例 |
|------|------|------|
| `= 1.0.0` | 精确版本 | 只能 1.0.0 |
| `>= 1.0.0` | 最低版本 | 1.0.0, 1.1.0, 2.0.0... |
| `~> 1.0` | 悲观约束 | 1.0, 1.1, 1.9（不含 2.0） |
| `>= 1.0, < 2.0` | 范围 | 1.x 系列 |

---

### 2. Provider 配置

```hcl
provider "google" {
  project = var.project_id  # GCP 项目 ID
  region  = var.region      # 默认区域
}
```

**初始化 Provider**：

```bash
cd terraform/

# 初始化（下载 Provider 插件）
terraform init

# 输出：
# Initializing the backend...
# Initializing provider plugins...
# - Finding hashicorp/google versions matching "~> 5.0"...
# - Installing hashicorp/google v5.11.0...
# Terraform has been successfully initialized!
```

---

## 📦 资源管理

### 1. 启用 GCP APIs

```hcl
# terraform/main.tf

# Cloud Run API
resource "google_project_service" "cloud_run" {
  service = "run.googleapis.com"
  
  # 删除资源时不禁用 API（避免影响其他资源）
  disable_on_destroy = false
}

# Cloud Build API
resource "google_project_service" "cloud_build" {
  service = "cloudbuild.googleapis.com"
  disable_on_destroy = false
}

# Firestore API
resource "google_project_service" "firestore" {
  service = "firestore.googleapis.com"
  disable_on_destroy = false
}

# Artifact Registry API
resource "google_project_service" "artifact_registry" {
  service = "artifactregistry.googleapis.com"
  disable_on_destroy = false
}
```

**为什么需要这个？**

GCP 的 APIs 默认是禁用的，必须先启用才能使用相关服务。

---

### 2. Artifact Registry (Docker 镜像仓库)

```hcl
resource "google_artifact_registry_repository" "docker_repo" {
  location      = var.region         # us-central1
  repository_id = "ai-diary-images"  # 仓库名称
  description   = "Docker repository for AI Diary application"
  format        = "DOCKER"           # 镜像格式
  
  # 依赖关系：必须先启用 API
  depends_on = [google_project_service.artifact_registry]
}
```

**使用示例**：

```bash
# 构建并推送镜像
docker build -t us-central1-docker.pkg.dev/my-project/ai-diary-images/backend:latest ./backend
docker push us-central1-docker.pkg.dev/my-project/ai-diary-images/backend:latest
```

---

### 3. Cloud Run 服务

#### Backend 服务

```hcl
resource "google_cloud_run_service" "backend" {
  name     = "ai-diary-backend"
  location = var.region

  template {
    spec {
      # 容器配置
      containers {
        # 镜像地址（从 Artifact Registry）
        image = "${var.region}-docker.pkg.dev/${var.project_id}/ai-diary-images/backend:latest"
        
        # 环境变量
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }
        
        env {
          name  = "FIREBASE_PROJECT_ID"
          value = var.project_id
        }
        
        # 引用其他资源的输出
        env {
          name  = "WEAVIATE_URL"
          value = google_cloud_run_service.weaviate.status[0].url
        }
        
        # 资源限制
        resources {
          limits = {
            cpu    = "1000m"  # 1 vCPU
            memory = "512Mi"  # 512 MB
          }
        }
        
        # 端口配置
        ports {
          container_port = 8000
        }
      }
      
      # Service Account（权限控制）
      service_account_name = google_service_account.backend_sa.email
    }
    
    # 自动扩缩容配置
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"  # 最多 10 个实例
        "autoscaling.knative.dev/minScale" = "0"   # 可缩到 0（节省成本）
      }
    }
  }

  # 流量分配
  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.cloud_run]
}
```

**资源限制说明**：

| 配置 | CPU | 内存 | 月成本 | 适用场景 |
|------|-----|------|--------|---------|
| **小** | 0.5 vCPU | 256Mi | ~$5-10 | 开发/测试 |
| **中** | 1 vCPU | 512Mi | ~$10-20 | 生产（低流量）✅ |
| **大** | 2 vCPU | 1Gi | ~$20-40 | 生产（高流量） |

---

#### Weaviate 服务

```hcl
resource "google_cloud_run_service" "weaviate" {
  name     = "ai-diary-weaviate"
  location = var.region

  template {
    spec {
      containers {
        # 使用官方 Weaviate 镜像
        image = "semitechnologies/weaviate:1.23.0"
        
        # Weaviate 配置
        env {
          name  = "AUTHENTICATION_ANONYMOUS_ACCESS_ENABLED"
          value = "true"
        }
        
        env {
          name  = "PERSISTENCE_DATA_PATH"
          value = "/var/lib/weaviate"
        }
        
        env {
          name  = "DEFAULT_VECTORIZER_MODULE"
          value = "none"  # 使用自定义向量
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "1Gi"  # Weaviate 需要更多内存
          }
        }
        
        ports {
          container_port = 8080
        }
      }
    }
    
    metadata {
      annotations = {
        # Weaviate 至少保持 1 个实例运行（避免冷启动）
        "autoscaling.knative.dev/minScale" = "1"
        "autoscaling.knative.dev/maxScale" = "5"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.cloud_run]
}
```

---

#### Frontend 服务

```hcl
resource "google_cloud_run_service" "frontend" {
  name     = "ai-diary-frontend"
  location = var.region

  template {
    spec {
      containers {
        image = "${var.region}-docker.pkg.dev/${var.project_id}/ai-diary-images/frontend:latest"
        
        # 前端需要后端 URL
        env {
          name  = "VITE_API_URL"
          value = google_cloud_run_service.backend.status[0].url
        }
        
        env {
          name  = "VITE_FIREBASE_API_KEY"
          value = var.firebase_api_key
        }
        
        env {
          name  = "VITE_FIREBASE_AUTH_DOMAIN"
          value = "${var.project_id}.firebaseapp.com"
        }
        
        resources {
          limits = {
            cpu    = "1000m"
            memory = "256Mi"  # 前端需要更少内存
          }
        }
        
        ports {
          container_port = 5173
        }
      }
    }
    
    metadata {
      annotations = {
        "autoscaling.knative.dev/maxScale" = "10"
        "autoscaling.knative.dev/minScale" = "0"
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
  
  depends_on = [google_project_service.cloud_run]
}
```

---

### 4. IAM 权限管理

#### Service Account

```hcl
# 为后端创建专用 Service Account
resource "google_service_account" "backend_sa" {
  account_id   = "ai-diary-backend-sa"
  display_name = "AI Diary Backend Service Account"
}

# 授予 Firestore 访问权限
resource "google_project_iam_member" "backend_firestore" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}

# 授予 Cloud Storage 访问权限
resource "google_project_iam_member" "backend_storage" {
  project = var.project_id
  role    = "roles/storage.objectViewer"
  member  = "serviceAccount:${google_service_account.backend_sa.email}"
}
```

**最小权限原则**：

```
❌ 不好：授予 roles/owner（所有权限）
✅ 好：只授予需要的权限
   - datastore.user（Firestore 读写）
   - storage.objectViewer（Cloud Storage 读取）
```

---

#### 公开访问

```hcl
# 允许所有人访问前端
resource "google_cloud_run_service_iam_member" "frontend_public" {
  service  = google_cloud_run_service.frontend.name
  location = google_cloud_run_service.frontend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# 允许所有人访问后端（实际应用中可能需要更严格的控制）
resource "google_cloud_run_service_iam_member" "backend_public" {
  service  = google_cloud_run_service.backend.name
  location = google_cloud_run_service.backend.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

# Weaviate 只允许后端访问
resource "google_cloud_run_service_iam_member" "weaviate_backend" {
  service  = google_cloud_run_service.weaviate.name
  location = google_cloud_run_service.weaviate.location
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.backend_sa.email}"
}
```

---

### 5. Firestore 数据库

```hcl
resource "google_firestore_database" "database" {
  project     = var.project_id
  name        = "(default)"
  location_id = var.firestore_location  # us-central
  type        = "FIRESTORE_NATIVE"
  
  depends_on = [google_project_service.firestore]
}
```

**Firestore 位置选择**：

| 位置 | 多区域 | 延迟 | 成本 |
|------|--------|------|------|
| `us-central` | ✅ | 中 | 低 ✅ |
| `us-east1` | ❌ | 低 | 低 |
| `asia-northeast1` | ❌ | 低（亚洲）| 中 |

---

## 📂 状态管理

### 1. 本地状态（开发）

```bash
# 默认存储在本地
terraform/
└── terraform.tfstate  # JSON 文件
```

**问题**：
- ❌ 无法团队协作
- ❌ 容易丢失
- ❌ 无版本历史

---

### 2. 远程状态（生产）

```hcl
# terraform/main.tf
terraform {
  backend "gcs" {
    bucket = "ai-diary-terraform-state"
    prefix = "terraform/state"
  }
}
```

**设置步骤**：

```bash
# 1. 创建 GCS bucket
gsutil mb gs://ai-diary-terraform-state

# 2. 启用版本控制
gsutil versioning set on gs://ai-diary-terraform-state

# 3. 初始化后端
terraform init

# 4. 迁移现有状态（如果有）
# Terraform 会询问是否迁移本地状态到 GCS
# Do you want to copy existing state to the new backend?
#   Enter a value: yes
```

**优势**：
- ✅ 团队协作（多人可访问）
- ✅ 状态锁定（防止并发修改）
- ✅ 版本历史（可恢复）
- ✅ 加密存储

---

### 3. 状态锁定

```bash
# 当有人运行 terraform apply 时
# Terraform 会在 GCS 中创建锁文件

# 如果另一个人同时运行，会看到：
Error: Error acquiring the state lock

Error message: ConditionalCheckFailedException
Lock Info:
  ID:        abc123
  Path:      ai-diary-terraform-state/terraform/state/default.tflock
  Operation: OperationTypeApply
  Who:       user@example.com
  Version:   1.7.0
  Created:   2026-01-17 10:00:00 UTC
```

---

## 🔢 变量与输出

### 1. 输入变量 (variables.tf)

```hcl
# terraform/variables.tf

variable "project_id" {
  description = "GCP Project ID"
  type        = string
  # 必填，无默认值
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"  # 可选，有默认值
}

variable "openai_api_key" {
  description = "OpenAI API key"
  type        = string
  sensitive   = true  # 敏感信息，不显示在日志中
}
```

**变量类型**：

| 类型 | 示例 | 说明 |
|------|------|------|
| `string` | `"us-central1"` | 字符串 |
| `number` | `10` | 数字 |
| `bool` | `true` | 布尔值 |
| `list(string)` | `["a", "b"]` | 字符串列表 |
| `map(string)` | `{key = "value"}` | 键值对 |
| `object({...})` | 复杂对象 | 结构化数据 |

---

### 2. 变量赋值方式

#### 方式 1: terraform.tfvars 文件

```hcl
# terraform/terraform.tfvars (不提交到 Git)
project_id      = "my-gcp-project"
region          = "us-central1"
openai_api_key  = "sk-xxx"
firebase_api_key = "AIzaXXX"
```

```bash
# .gitignore
terraform/terraform.tfvars
terraform/*.tfvars
```

---

#### 方式 2: 命令行参数

```bash
terraform apply \
  -var="project_id=my-gcp-project" \
  -var="openai_api_key=sk-xxx"
```

---

#### 方式 3: 环境变量

```bash
export TF_VAR_project_id="my-gcp-project"
export TF_VAR_openai_api_key="sk-xxx"

terraform apply
```

---

#### 方式 4: 交互式输入

```bash
terraform apply
# var.project_id
#   GCP Project ID
#   Enter a value: my-gcp-project
```

---

### 3. 输出值 (outputs.tf)

```hcl
# terraform/outputs.tf

output "backend_url" {
  description = "URL of the backend Cloud Run service"
  value       = google_cloud_run_service.backend.status[0].url
}

output "frontend_url" {
  description = "URL of the frontend Cloud Run service"
  value       = google_cloud_run_service.frontend.status[0].url
}

output "weaviate_url" {
  description = "URL of the Weaviate Cloud Run service"
  value       = google_cloud_run_service.weaviate.status[0].url
}

output "backend_service_account" {
  description = "Email of the backend service account"
  value       = google_service_account.backend_sa.email
}
```

**使用输出**：

```bash
# 查看所有输出
terraform output

# 输出：
# backend_url = "https://ai-diary-backend-xxx-uc.a.run.app"
# frontend_url = "https://ai-diary-frontend-xxx-uc.a.run.app"
# weaviate_url = "https://ai-diary-weaviate-xxx-uc.a.run.app"

# 查看单个输出
terraform output frontend_url
# "https://ai-diary-frontend-xxx-uc.a.run.app"

# 使用 JSON 格式（便于脚本处理）
terraform output -json

# 在脚本中使用
FRONTEND_URL=$(terraform output -raw frontend_url)
curl $FRONTEND_URL
```

---

## 🛠️ Terraform 命令

### 1. 初始化

```bash
terraform init

# 重新初始化（更新 Provider）
terraform init -upgrade
```

---

### 2. 格式化代码

```bash
# 格式化所有 .tf 文件
terraform fmt

# 检查格式（不修改）
terraform fmt -check

# 递归格式化
terraform fmt -recursive
```

---

### 3. 验证配置

```bash
# 检查语法错误
terraform validate

# 输出：
# Success! The configuration is valid.
```

---

### 4. 预览变更

```bash
# 查看将要执行的操作
terraform plan

# 保存计划到文件
terraform plan -out=tfplan

# 使用保存的计划
terraform apply tfplan
```

**Plan 输出解读**：

```
Terraform will perform the following actions:

  # google_cloud_run_service.backend will be created
  + resource "google_cloud_run_service" "backend" {
      + name     = "ai-diary-backend"
      + location = "us-central1"
      ...
    }

  # google_cloud_run_service.weaviate will be updated in-place
  ~ resource "google_cloud_run_service" "weaviate" {
        name     = "ai-diary-weaviate"
      ~ memory   = "512Mi" -> "1Gi"
    }

  # google_firestore_database.old will be destroyed
  - resource "google_firestore_database" "old" {
      - name = "old-db"
    }

Plan: 1 to add, 1 to change, 1 to destroy.
```

**符号说明**：
- `+` 创建
- `~` 修改
- `-` 删除
- `-/+` 删除后重建

---

### 5. 应用变更

```bash
# 交互式确认
terraform apply

# 自动确认（CI/CD）
terraform apply -auto-approve

# 只应用特定资源
terraform apply -target=google_cloud_run_service.backend
```

---

### 6. 销毁资源

```bash
# 销毁所有资源
terraform destroy

# 销毁特定资源
terraform destroy -target=google_cloud_run_service.backend
```

---

### 7. 状态管理

```bash
# 查看状态
terraform state list

# 输出：
# google_cloud_run_service.backend
# google_cloud_run_service.frontend
# google_cloud_run_service.weaviate
# google_service_account.backend_sa
# ...

# 查看特定资源
terraform state show google_cloud_run_service.backend

# 移动资源（重命名）
terraform state mv google_cloud_run_service.old google_cloud_run_service.new

# 删除资源（从状态中移除，但不删除真实资源）
terraform state rm google_cloud_run_service.backend

# 导入现有资源
terraform import google_cloud_run_service.backend projects/my-project/locations/us-central1/services/ai-diary-backend
```

---

## 📦 模块化

### 1. 创建模块

```
terraform/
├── main.tf
├── modules/
│   └── cloud_run_service/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
```

```hcl
# modules/cloud_run_service/main.tf
resource "google_cloud_run_service" "service" {
  name     = var.service_name
  location = var.region

  template {
    spec {
      containers {
        image = var.image
        
        dynamic "env" {
          for_each = var.env_vars
          content {
            name  = env.key
            value = env.value
          }
        }
        
        resources {
          limits = var.resource_limits
        }
      }
    }
  }
}
```

```hcl
# modules/cloud_run_service/variables.tf
variable "service_name" {
  type = string
}

variable "region" {
  type = string
}

variable "image" {
  type = string
}

variable "env_vars" {
  type    = map(string)
  default = {}
}

variable "resource_limits" {
  type = map(string)
  default = {
    cpu    = "1000m"
    memory = "512Mi"
  }
}
```

---

### 2. 使用模块

```hcl
# main.tf
module "backend" {
  source = "./modules/cloud_run_service"
  
  service_name = "ai-diary-backend"
  region       = var.region
  image        = "${var.region}-docker.pkg.dev/${var.project_id}/ai-diary-images/backend:latest"
  
  env_vars = {
    OPENAI_API_KEY       = var.openai_api_key
    FIREBASE_PROJECT_ID  = var.project_id
  }
  
  resource_limits = {
    cpu    = "2000m"
    memory = "1Gi"
  }
}

module "frontend" {
  source = "./modules/cloud_run_service"
  
  service_name = "ai-diary-frontend"
  region       = var.region
  image        = "${var.region}-docker.pkg.dev/${var.project_id}/ai-diary-images/frontend:latest"
  
  env_vars = {
    VITE_API_URL = module.backend.service_url
  }
}

# 引用模块输出
output "backend_url" {
  value = module.backend.service_url
}
```

---

## ✅ 最佳实践

### 1. 文件组织

```
✅ 好的结构
terraform/
├── main.tf          # 核心资源
├── variables.tf     # 所有变量
├── outputs.tf       # 所有输出
├── versions.tf      # Provider 版本
├── backend.tf       # 后端配置
└── modules/         # 可复用模块

❌ 不好的结构
terraform/
└── everything.tf    # 所有内容在一个文件
```

---

### 2. 命名规范

```hcl
# ✅ 使用有意义的名称
resource "google_cloud_run_service" "backend" {
  name = "ai-diary-backend"
}

# ❌ 避免无意义的名称
resource "google_cloud_run_service" "service1" {
  name = "svc1"
}
```

---

### 3. 使用 locals

```hcl
locals {
  # 项目名称前缀
  prefix = "ai-diary"
  
  # 公共标签
  common_labels = {
    project     = "ai-diary"
    environment = var.environment
    managed_by  = "terraform"
  }
  
  # 镜像仓库前缀
  image_prefix = "${var.region}-docker.pkg.dev/${var.project_id}/ai-diary-images"
}

resource "google_cloud_run_service" "backend" {
  name = "${local.prefix}-backend"
  
  template {
    spec {
      containers {
        image = "${local.image_prefix}/backend:latest"
      }
    }
    
    metadata {
      labels = local.common_labels
    }
  }
}
```

---

### 4. 敏感信息管理

```hcl
# ❌ 不要硬编码密钥
resource "google_cloud_run_service" "backend" {
  template {
    spec {
      containers {
        env {
          name  = "OPENAI_API_KEY"
          value = "sk-xxx"  # ❌ 危险！
        }
      }
    }
  }
}

# ✅ 使用变量
variable "openai_api_key" {
  type      = string
  sensitive = true
}

resource "google_cloud_run_service" "backend" {
  template {
    spec {
      containers {
        env {
          name  = "OPENAI_API_KEY"
          value = var.openai_api_key
        }
      }
    }
  }
}

# ✅ 更好：使用 Secret Manager
resource "google_secret_manager_secret" "openai_key" {
  secret_id = "openai-api-key"
  
  replication {
    automatic = true
  }
}

resource "google_cloud_run_service" "backend" {
  template {
    spec {
      containers {
        env {
          name = "OPENAI_API_KEY"
          value_from {
            secret_key_ref {
              name = google_secret_manager_secret.openai_key.secret_id
              key  = "latest"
            }
          }
        }
      }
    }
  }
}
```

---

### 5. 依赖管理

```hcl
# 显式依赖
resource "google_cloud_run_service" "backend" {
  # ...
  
  depends_on = [
    google_project_service.cloud_run,
    google_service_account.backend_sa
  ]
}

# 隐式依赖（推荐）
resource "google_cloud_run_service" "backend" {
  # ...
  
  # 引用其他资源会自动创建依赖
  service_account_name = google_service_account.backend_sa.email
}
```

---

### 6. 使用 count 和 for_each

```hcl
# count - 创建多个相同资源
resource "google_project_service" "services" {
  count = length(var.gcp_services)
  
  service = var.gcp_services[count.index]
  disable_on_destroy = false
}

variable "gcp_services" {
  default = [
    "run.googleapis.com",
    "cloudbuild.googleapis.com",
    "firestore.googleapis.com"
  ]
}

# for_each - 创建命名资源（推荐）
resource "google_project_service" "services" {
  for_each = toset(var.gcp_services)
  
  service = each.value
  disable_on_destroy = false
}
```

---

## 🔍 故障排查

### 1. 常见错误

#### 错误 1: Provider 未初始化

```bash
Error: Plugin did not respond

Solution:
terraform init
```

---

#### 错误 2: 状态锁定

```bash
Error: Error acquiring the state lock

Solution:
# 确认没有其他 terraform 进程在运行
# 如果确认可以强制解锁
terraform force-unlock LOCK_ID
```

---

#### 错误 3: 权限不足

```bash
Error: Error creating Service: googleapi: Error 403: Permission denied

Solution:
# 检查 Service Account 权限
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:YOUR_SA"

# 添加所需权限
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:YOUR_SA" \
  --role="roles/run.admin"
```

---

#### 错误 4: API 未启用

```bash
Error: Error 403: Cloud Run API has not been used in project

Solution:
gcloud services enable run.googleapis.com
```

---

### 2. 调试技巧

```bash
# 详细日志
export TF_LOG=DEBUG
terraform apply

# 只输出特定级别
export TF_LOG=TRACE  # TRACE, DEBUG, INFO, WARN, ERROR

# 日志保存到文件
export TF_LOG_PATH=terraform.log
terraform apply

# 禁用日志
unset TF_LOG
```

---

### 3. 查看资源

```bash
# 查看 Cloud Run 服务
gcloud run services list --platform managed

# 查看服务详情
gcloud run services describe ai-diary-backend \
  --platform managed \
  --region us-central1

# 查看 Artifact Registry 镜像
gcloud artifacts docker images list \
  us-central1-docker.pkg.dev/YOUR_PROJECT/ai-diary-images
```

---

## 🚀 完整工作流程

### 1. 初始部署

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/ai-diary.git
cd ai-diary/terraform

# 2. 创建 terraform.tfvars
cat > terraform.tfvars <<EOF
project_id       = "my-gcp-project"
region           = "us-central1"
openai_api_key   = "sk-xxx"
firebase_api_key = "AIzaXXX"
EOF

# 3. 初始化
terraform init

# 4. 预览
terraform plan

# 5. 应用
terraform apply

# 6. 获取 URL
terraform output frontend_url
```

---

### 2. 更新资源

```bash
# 修改 main.tf
# 例如：增加 backend 内存

resource "google_cloud_run_service" "backend" {
  # ...
  resources {
    limits = {
      memory = "1Gi"  # 从 512Mi 增加到 1Gi
    }
  }
}

# 预览变更
terraform plan

# 应用变更
terraform apply
```

---

### 3. 销毁资源

```bash
# 销毁所有资源
terraform destroy

# 确认
# Do you really want to destroy all resources?
#   Enter a value: yes
```

---

## 📚 学习资源

- [Terraform 官方文档](https://www.terraform.io/docs)
- [Google Provider 文档](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [Terraform Best Practices](https://www.terraform-best-practices.com/)
- [本项目架构文档](./ARCHITECTURE_CN.md)

---

## ✅ 总结

本教程展示了 Terraform 在真实项目中的应用：

✅ **基础**: Provider 配置、资源定义、依赖管理  
✅ **状态**: 本地状态、远程状态、状态锁定  
✅ **变量**: 输入变量、输出值、敏感信息  
✅ **模块**: 模块化设计、代码复用  
✅ **最佳实践**: 命名规范、文件组织、安全管理  
✅ **故障排查**: 常见错误、调试技巧  

现在你可以：
1. 使用 Terraform 管理 GCP 资源
2. 编写可维护的 IaC 代码
3. 安全地管理敏感信息
4. 团队协作部署基础设施

Happy Terraforming! 🏗️

