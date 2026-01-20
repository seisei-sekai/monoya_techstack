# 🦙 Llama 本地 RAG 设置指南

## 📋 功能说明

在日记编辑页面添加了本地 Llama 1B 模型的智能写作建议功能：

- ✅ 读取所有历史日记
- ✅ 基于当前内容生成个性化推荐
- ✅ 完全本地运行，无需 OpenAI API
- ✅ 使用 Ollama 管理模型

---

## 🚀 快速启动

### 1️⃣ 启动所有服务（包括 Ollama）

```bash
cd /Users/benz/Desktop/Stanford/SP26/Monoya/JD_Project
docker compose up --build
```

### 2️⃣ 下载 Llama 模型

在新终端中运行：

```bash
# 进入 Ollama 容器
docker exec -it jd_project-ollama-1 bash

# 下载 Llama 3.2 1B 模型（约 1.3GB）
ollama pull llama3.2:1b

# 验证模型已下载
ollama list

# 退出容器
exit
```

### 3️⃣ 测试功能

1. 访问 http://localhost:5173
2. 创建或编辑一篇日记
3. 写一些内容
4. 点击 **"🦙 获取 Llama 写作建议"** 按钮
5. 等待 5-10 秒，查看推荐

---

## 🔧 技术架构

### 后端新增

**1. Ollama 服务** (`docker-compose.yml`)

```yaml
ollama:
  image: ollama/ollama:latest
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
```

**2. LlamaRAG 服务** (`backend/app/services/llama_rag_service.py`)

- 获取用户所有历史日记
- 构建上下文提示词
- 调用 Ollama API 生成推荐

**3. 新 API 端点**

- `POST /diaries/recommend` - 生成写作推荐
- `GET /diaries/ollama/status` - 检查 Ollama 状态

### 前端新增

**DiaryEditor.jsx**

- 新增 "获取 Llama 写作建议" 按钮
- 显示 Llama 推荐结果
- 绿色主题区分 AI Insight

---

## 📊 模型对比

| 特性 | Llama 3.2 1B (本地) | GPT-3.5 (OpenAI) |
| ---- | ------------------- | ---------------- |
| 大小 | ~1.3GB              | 云端             |
| 速度 | 5-10 秒             | 2-3 秒           |
| 成本 | 免费                | 按使用付费       |
| 隐私 | 完全本地            | 数据上传         |
| 质量 | 中文较好            | 优秀             |

---

## 🎯 使用场景

### Llama 本地推荐

- ✅ 写作过程中的实时建议
- ✅ 基于历史日记的个性化反馈
- ✅ 完全离线可用
- ✅ 无 API 成本

### OpenAI AI Insight

- ✅ 保存后的深度分析
- ✅ 更高质量的反馈
- ✅ 需要 OpenAI API Key

---

## 🐛 故障排查

### 问题 1: "Ollama 服务未启动"

**解决方案**：

```bash
# 检查 Ollama 容器状态
docker ps | grep ollama

# 如果未运行，重启
docker compose restart ollama

# 查看日志
docker logs jd_project-ollama-1
```

### 问题 2: "模型未下载"

**解决方案**：

```bash
docker exec -it jd_project-ollama-1 ollama pull llama3.2:1b
```

### 问题 3: 生成速度慢

**原因**：

- 首次运行需要加载模型（10-15 秒）
- 后续请求会快很多（5-8 秒）

**优化**：

```bash
# 使用更小的模型（更快但质量略低）
docker exec -it jd_project-ollama-1 ollama pull llama3.2:1b
```

### 问题 4: 内存不足

**要求**：

- 最少 4GB RAM
- 推荐 8GB+ RAM

**解决方案**：

```bash
# 使用量化版本（更小）
docker exec -it jd_project-ollama-1 ollama pull llama3.2:1b-q4_0
```

---

## 🔍 检查服务状态

### 方法 1: 通过 API

```bash
curl http://localhost:8000/diaries/ollama/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 方法 2: 直接测试 Ollama

```bash
curl http://localhost:11434/api/tags
```

### 方法 3: 手动测试生成

```bash
docker exec -it jd_project-ollama-1 ollama run llama3.2:1b "你好，请介绍一下自己"
```

---

## 📝 自定义提示词

编辑 `backend/app/services/llama_rag_service.py` 中的 `prompt` 变量：

```python
prompt = f"""你是一个智能日记助手。根据用户的历史日记和当前正在写的内容，提供有帮助的建议和推荐。

{context}

当前正在写的日记：
标题: {current_title}
内容: {current_content}

请提供：
1. 对当前内容的简短评论
2. 基于历史日记的模式或主题观察
3. 1-2条写作建议或思考方向

用中文回复，保持温暖和鼓励的语气，不超过150字。"""
```

---

## 🎨 UI 预览

```
┌─────────────────────────────────────────┐
│ 📝 Diary Editor                         │
├─────────────────────────────────────────┤
│ Title: [我的一天]                        │
│                                         │
│ Content:                                │
│ ┌─────────────────────────────────────┐ │
│ │ 今天天气很好，心情也不错...          │ │
│ │                                     │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ [🦙 获取 Llama 写作建议]                │
│                                         │
│ ┌─────────────────────────────────────┐ │
│ │ 💡 Llama 写作建议                    │ │
│ │ 很高兴看到你今天心情不错！从你的    │ │
│ │ 历史日记来看，天气对你的情绪影响... │ │
│ └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

---

## 🚀 高级配置

### 使用其他模型

```bash
# 更大的模型（更好的质量）
docker exec -it jd_project-ollama-1 ollama pull llama3.2:3b

# 更新配置
# 编辑 .env 文件
OLLAMA_MODEL=llama3.2:3b
```

### 调整生成参数

编辑 `backend/app/services/llama_rag_service.py`：

```python
"options": {
    "temperature": 0.7,  # 创造性 (0-1)
    "num_predict": 200,  # 最大生成长度
    "top_p": 0.9,        # 采样策略
    "top_k": 40          # 采样策略
}
```

---

## 📚 相关资源

- [Ollama 官方文档](https://github.com/ollama/ollama)
- [Llama 3.2 模型卡](https://ollama.com/library/llama3.2)
- [模型列表](https://ollama.com/library)

---

## ✨ 总结

现在你有两个 AI 助手：

1. **🦙 Llama (本地)** - 实时写作建议，完全免费
2. **✨ GPT-3.5 (云端)** - 深度分析，需要 API Key

两者互补，提供最佳的日记写作体验！🎉
