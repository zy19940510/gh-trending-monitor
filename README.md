# GitHub Topics Trending

> 追踪 GitHub 话题下的热门项目，AI 智能分析，每日趋势报告邮件

> **真实还原官方 GitHub Trending**：支持双模式（Topic / Trending），完美复刻官方 Trending 算法！

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

[English](./README_EN.md) | 简体中文

---

## 核心亮点

### 🎯 真实还原官方 GitHub Trending

与其他趋势追踪工具不同，本项目**完美复刻了官方 GitHub Trending 算法**：

- **双模式支持**：
  - **Topic 模式**：追踪特定话题的热门仓库（如 `claude-code`、`ai`）
  - **Trending 模式**：发现全站新兴项目，完全模拟官方 Trending 页面

- **智能过滤**：
  - 按创建时间过滤（最近 1/7/30 天）
  - 最低星标数阈值，聚焦高质量项目
  - 语言过滤（Python、TypeScript、Go 等）

- **真实趋势数据**：获取新创建的仓库并按总星标数排序，完美匹配官方 GitHub Trending 行为

### 🤖 AI 智能分析

- **Claude AI 分析**：自动为每个仓库生成一句话总结
- **智能分类**：自动分类为插件、工具、模板、文档等
- **问题识别**：提取每个项目解决的核心问题
- **趋势洞察**：检测新晋项目、快速增长和活跃仓库

### 🚀 专业自动化

- **每日邮件报告**：精美的 HTML 邮件，每个仓库卡片可点击跳转
- **GitHub Pages 网站**：自动生成静态网站展示趋势数据
- **SQLite 数据库**：历史数据存储，支持趋势分析
- **GitHub Actions**：全自动每日执行

---

## 目录

- [快速开始](#快速开始)
- [功能特性](#功能特性)
- [GitHub Actions 配置](#github-actions-配置)
- [GitHub Pages 配置](#github-pages-配置)
- [未来规划](#未来规划)
- [常见问题](#常见问题)

---

## 功能特性

### 双运行模式

| 特性 | Topic 模式 | Trending 模式 |
|-----|-----------|--------------|
| **数据源** | 指定话题（如 `claude-code`） | 全站仓库 |
| **排序依据** | 总星标数 | 总星标数（可配置） |
| **时间范围** | 全部历史 | 最近 N 天创建 |
| **适用场景** | 追踪特定话题 | 发现新兴项目 |
| **类似页面** | GitHub Topics | GitHub Trending |

**切换模式**：修改 `.env` 中的 `TRENDING_MODE` 即可

### 邮件报告内容

- **Top 20 榜单** - 含 AI 智能总结
- **星标增长 Top 5** - 涨势最快的项目
- **新晋项目** - 新上榜的仓库
- **活跃项目** - 最近更新的项目
- **趋势统计** - 整体洞察

### 智能分类

自动将仓库分类为：
- **插件**（VS Code、Claude Code 扩展）
- **工具**（CLI 工具、开发工具）
- **模板**（项目模板、脚手架）
- **文档**（教程、书籍、指南）
- **示例**（Demo、示例代码）
- **集成**（API 包装器、SDK）
- **库**（Python/JS/其他库）
- **应用**（完整应用、产品）

---

## 快速开始

### 环境要求

- Python 3.11+
- GitHub Personal Access Token（[如何创建](https://github.com/settings/tokens)）
- LLM API Key（支持智谱 AI 或 LB One API）
- Resend API Key（[注册地址](https://resend.com)）

### 安装

```bash
# 克隆仓库
git clone https://github.com/YOUR_USERNAME/gh-trending-monitor.git
cd gh-trending-monitor

# 安装依赖
pip install -r requirements.txt

# 配置环境
cp .env.example .env
nano .env
```

### 配置

编辑 `.env` 文件：

```bash
# GitHub API
GH_TOKEN=your_github_token

# 模式选择：topic 或 trending
TRENDING_MODE=trending

# Trending 模式配置（使用 topic 模式可跳过）
TRENDING_DAYS=7              # 获取最近 7 天创建的项目
TRENDING_MIN_STARS=50        # 最低星标数过滤
TRENDING_LANGUAGE=           # 语言过滤（空=全部）

# Topic 模式配置（使用 trending 模式可跳过）
TOPIC=claude-code            # 要追踪的话题

# LLM 配置：zhipu 或 one
LLM_PROVIDER=one
ONE_API_KEY=sk-xxxxxxxxxxxxxxxx
ONE_BASE_URL=https://lboneapi.longbridge-inc.com
ONE_MODEL=claude-sonnet-4-5-20250929

# 邮件服务
RESEND_API_KEY=re_xxxxxxxxxxxxx
EMAIL_TO=your-email@example.com
```

**详细的 LLM 配置**：查看 [LLM_PROVIDER_GUIDE.md](./LLM_PROVIDER_GUIDE.md)
**Trending 模式详情**：查看 [TRENDING_MODE_GUIDE.md](./TRENDING_MODE_GUIDE.md)

### 运行

```bash
# 完整流程（获取 + 分析 + 邮件 + 网站）
python -m src.main

# 仅获取数据（不发送邮件）
python -m src.main --fetch-only
```

---

## GitHub Actions 配置

### 1. 配置 Secrets

进入 **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

添加以下 Secrets：

| Name | 必需 | Value |
|------|------|-------|
| `GH_TOKEN` | ✅ | 你的 GitHub PAT |
| `TOPIC` | - | `claude-code`（Topic 模式） |
| `ZHIPU_API_KEY` | ✅ | 智谱 API Key |
| `RESEND_API_KEY` | ✅ | Resend API Key |
| `EMAIL_TO` | ✅ | 接收邮箱 |

### 2. 启用 Workflow 权限

**Settings** → **Actions** → **General** → **Workflow permissions**
选择：**Read and write permissions** → **Save**

### 3. 手动触发

**Actions** 标签 → 选择 **GitHub Topics Trending** → **Run workflow**

### 4. 定时执行

默认每天 **UTC 02:00**（北京时间 10:00）自动运行

---

## GitHub Pages 配置

### 启用 Pages

1. **Settings** → **Pages**
2. **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **gh-pages** / **/ (root)**
   - 点击 **Save**

3. **设置为 Public 仓库**:
   - **Settings** → **General** → **Danger Zone**
   - **Change repository visibility** → **Public**

4. **访问网站**:
   ```
   https://YOUR_USERNAME.github.io/gh-trending-monitor/
   ```

⚠️ **注意**：首次部署需要等待 5-10 分钟

---

## 未来规划

### 计划功能

- [ ] **多语言支持**
  - 同时追踪多种编程语言
  - 按语言分别生成报告

- [ ] **高级分析**
  - Fork/Star 比率分析
  - Issue 活跃度追踪
  - 贡献者增长趋势
  - 周报/月报汇总

- [ ] **增强过滤**
  - 按许可证类型过滤
  - 排除已归档仓库
  - 自定义星标阈值

- [ ] **社交集成**
  - 自动发布到 Twitter/X
  - Slack/Discord Webhook 通知
  - Telegram Bot 集成

- [ ] **Web 仪表板**
  - 交互式图表
  - 历史趋势可视化
  - 搜索和过滤功能
  - 导出为 CSV/JSON

- [ ] **智能推荐**
  - 基于已加星仓库的个性化推荐
  - 相似项目发现
  - 跨话题趋势模式

- [ ] **API 端点**
  - RESTful API 访问趋势数据
  - Webhook 支持实时更新
  - GraphQL 查询接口

- [ ] **性能优化**
  - 并行 API 请求
  - Redis 缓存层
  - 增量更新

### 欢迎贡献！

有想法？欢迎提 Issue 或 PR！

---

## 常见问题

### 邮件没有收到？

1. 检查 Resend API Key 是否正确
2. 确认收件人邮箱地址
3. 查看垃圾邮件箱
4. 检查 GitHub Actions 日志

### GitHub API 速率限制？

- 认证用户：5000 requests/hour
- 未认证用户：60 requests/hour
- 使用 `GH_TOKEN` 可提高限制

### 如何查看历史数据？

```bash
sqlite3 data/github-trending.db
.tables
SELECT * FROM repos_daily ORDER BY date DESC LIMIT 10;
```

### 如何更改运行时间？

编辑 `.github/workflows/github-trending.yml`：
```yaml
schedule:
  - cron: '0 2 * * *'  # UTC 时间
```

---

## License

[MIT](LICENSE)

---

## Credits

- [GitHub](https://github.com) - Data source
- [Anthropic](https://anthropic.com) - Claude AI
- [Resend](https://resend.com) - Email service
