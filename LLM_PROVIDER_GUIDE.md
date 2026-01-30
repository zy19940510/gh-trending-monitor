# LLM Provider 配置指南

本项目现在支持多个 LLM 提供商，可以通过环境变量 `LLM_PROVIDER` 进行切换。

项目使用 **python-dotenv** 自动从 `.env` 文件加载环境变量，无需手动设置系统环境变量。

## 支持的提供商

### 1. 智谱 AI (zhipu) - 默认
使用智谱 AI 的 Claude API 代理服务。

### 2. LB One API (one)
使用 LongBridge One API 服务。

## 快速配置

### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

这会自动安装 `python-dotenv` 和其他所需依赖。

### 步骤 2: 创建 .env 文件

复制示例文件并编辑：

```bash
cp .env.example .env
```

### 步骤 3: 配置环境变量

#### 使用 LB One API (推荐)

在 `.env` 文件中添加：

```bash
# 选择提供商
LLM_PROVIDER=one

# LB One API 配置
ONE_API_KEY=sk-your-api-key-here
ONE_BASE_URL=https://lboneapi.longbridge-inc.com
ONE_MODEL=claude-sonnet-4-5-20250929
```

**重要**: `ONE_BASE_URL` **不要包含** `/v1` 路径，Anthropic SDK 会自动添加。

#### 使用智谱 AI

在 `.env` 文件中添加：

```bash
# 选择提供商
LLM_PROVIDER=zhipu

# 智谱配置
ZHIPU_API_KEY=your_zhipu_api_key_here
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/anthropic
ZHIPU_MODEL=claude-3-5-sonnet-20241022
```

**提示**: 项目会自动从 `.env` 文件加载这些变量，无需设置系统环境变量或手动 export。

## 配置说明

### 环境变量详解

| 变量名 | 说明 | 可选值 | 默认值 |
|--------|------|--------|--------|
| `LLM_PROVIDER` | LLM 提供商 | `zhipu`, `one` | `zhipu` |
| `ONE_API_KEY` | LB One API 密钥 | - | - |
| `ONE_BASE_URL` | LB One API 地址 | - | `https://lboneapi.longbridge-inc.com` |
| `ONE_MODEL` | LB One 使用的模型 | - | `claude-sonnet-4-5-20250929` |
| `ZHIPU_API_KEY` | 智谱 API 密钥 | - | - |
| `ZHIPU_BASE_URL` | 智谱 API 地址 | - | `https://open.bigmodel.cn/api/anthropic` |
| `ZHIPU_MODEL` | 智谱使用的模型 | - | `claude-3-5-sonnet-20241022` |

**注意**: 所有 `BASE_URL` 配置都**不应包含 API 路径**（如 `/v1` 或 `/v1/messages`），SDK 会自动添加。

## 代码示例

### 使用默认提供商（从环境变量读取）

```python
from src.claude_summarizer import ClaudeSummarizer

# 自动使用 LLM_PROVIDER 环境变量指定的提供商
summarizer = ClaudeSummarizer()
results = summarizer.summarize_and_classify(repos)
```

### 显式指定提供商

```python
from src.claude_summarizer import ClaudeSummarizer

# 强制使用 LB One API
summarizer = ClaudeSummarizer(provider="one")
results = summarizer.summarize_and_classify(repos)

# 强制使用智谱
summarizer = ClaudeSummarizer(provider="zhipu")
results = summarizer.summarize_and_classify(repos)
```

### 自定义配置

```python
from src.claude_summarizer import ClaudeSummarizer

# 使用自定义 API Key 和 Base URL
summarizer = ClaudeSummarizer(
    provider="one",
    api_key="sk-custom-key",
    base_url="https://custom-api.example.com"
)
```

## GitHub Actions 配置

在 GitHub Actions 中使用 LB One API，需要设置以下 Secrets：

1. 进入仓库的 Settings → Secrets and variables → Actions
2. 添加以下 secrets:
   - `ONE_API_KEY`: 你的 LB One API Key
   - `LLM_PROVIDER`: 设置为 `one`

在 `.github/workflows/github-trending.yml` 中添加环境变量：

```yaml
env:
  LLM_PROVIDER: ${{ secrets.LLM_PROVIDER || 'one' }}
  ONE_API_KEY: ${{ secrets.ONE_API_KEY }}
  # 其他环境变量...
```

## 测试配置

测试配置是否正确：

```bash
# 测试当前配置（使用 .env 文件中的设置）
python -c "from src.claude_summarizer import ClaudeSummarizer; ClaudeSummarizer()"

# 或者运行主程序查看
python src/main.py --help
```

成功输出示例：
```
✅ Claude 客户端初始化成功 (提供商: LB One API, 模型: claude-sonnet-4-5-20250929)
```

## 常见问题

### Q: 如何知道当前使用的是哪个提供商？
A: 初始化时会打印提供商信息，例如：
```
✅ Claude 客户端初始化成功 (提供商: LB One API, 模型: claude-sonnet-4-5-20250929)
```

### Q: 可以同时配置多个提供商吗？
A: 可以。你可以在 `.env` 中同时配置多个提供商的 API Key，通过 `LLM_PROVIDER` 变量切换使用哪一个。

### Q: 提供商切换后需要重启吗？
A: 需要。环境变量在程序启动时从 `.env` 文件读取，修改 `.env` 文件后需要重新运行程序。

### Q: 如果 API Key 未设置会怎样？
A: 程序会抛出错误并提示具体缺少哪个提供商的 API Key。

### Q: .env 文件在哪里？
A: `.env` 文件应该放在项目根目录下（与 `requirements.txt` 同级）。可以复制 `.env.example` 文件来创建。

### Q: python-dotenv 是如何工作的？
A: 项目在 `src/config.py` 中自动加载 `.env` 文件：
```python
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env')
```
所有导入 config 的模块都会自动获取环境变量。

### Q: 为什么出现 "Invalid URL (POST /v1/v1/messages)" 错误？
A: 这是因为 `BASE_URL` 配置包含了 `/v1` 路径。正确的配置应该是：
```bash
# ❌ 错误
ONE_BASE_URL=https://lboneapi.longbridge-inc.com/v1

# ✅ 正确
ONE_BASE_URL=https://lboneapi.longbridge-inc.com
```

Anthropic SDK 会自动在 base_url 后面添加 `/v1/messages`，如果你的 base_url 已经包含 `/v1`，就会变成 `/v1/v1/messages`。

### Q: API 调用失败时会怎样？
A: 项目有完善的降级机制：
1. 如果 AI 调用失败，会自动使用规则分类
2. 仍然会生成基本的仓库摘要
3. 邮件和网页仍然能够正常生成

## 迁移指南

### 从旧配置迁移到新配置

如果你之前使用的是旧的配置方式（只有 `ZHIPU_API_KEY`），不需要任何修改，旧配置会自动向后兼容。

建议迁移到新配置：

**旧配置 (仍然有效):**
```bash
ZHIPU_API_KEY=xxx
ANTHROPIC_BASE_URL=https://open.bigmodel.cn/api/anthropic
```

**新配置 (推荐):**
```bash
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=xxx
ZHIPU_BASE_URL=https://open.bigmodel.cn/api/anthropic
ZHIPU_MODEL=claude-3-5-sonnet-20241022
```

## 技术细节

### 提供商选择逻辑

1. 检查 `LLM_PROVIDER` 环境变量
2. 如果设置为 `"one"`，使用 LB One API 配置
3. 否则使用智谱 AI 配置（默认）
4. 加载对应的 API Key、Base URL 和 Model

### API 兼容性

两个提供商都使用 Anthropic SDK 的 `messages.create()` API，因此代码逻辑完全相同，只是配置不同。

```python
response = self.client.messages.create(
    model=self.model,  # 根据提供商自动选择模型
    max_tokens=self.max_tokens,
    temperature=0.3,
    messages=[...]
)
```

### URL 配置说明

Anthropic SDK 会在初始化时将完整的 API URL 构造为：

```
{base_url}/v1/messages
```

因此：
- 如果 `base_url = "https://lboneapi.longbridge-inc.com"`
- 实际调用的 URL 是 `https://lboneapi.longbridge-inc.com/v1/messages` ✅

- 如果 `base_url = "https://lboneapi.longbridge-inc.com/v1"`
- 实际调用的 URL 是 `https://lboneapi.longbridge-inc.com/v1/v1/messages` ❌

## 错误排查

### 1. 401 错误 - 无效的令牌
```
Error code: 401 - {'error': {'message': '无效的令牌'}}
```
**解决方法**: 检查 API Key 是否正确，确保复制时没有多余的空格。

### 2. 404 错误 - Invalid URL
```
Error code: 404 - {'error': {'message': 'Invalid URL (POST /v1/v1/messages)'}}
```
**解决方法**: `BASE_URL` 不应包含 `/v1` 路径，参考上面的 URL 配置说明。

### 3. NoneType 错误
```
AttributeError: 'NoneType' object has no attribute 'lower'
```
**解决方法**: 已在最新版本修复，请确保使用最新代码。

## 更新日志

- **2026-01-29**:
  - 添加多提供商支持，支持 LB One API
  - 添加 python-dotenv 自动加载环境变量
  - 修复 URL 配置问题
  - 修复 fallback 逻辑中的 None 处理
- 之前版本: 仅支持智谱 AI
