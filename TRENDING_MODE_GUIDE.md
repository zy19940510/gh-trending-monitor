# GitHub Trending 模式使用指南

本项目现在支持两种数据获取模式：**Topic 模式**和 **Trending 模式**。

## 模式对比

| 特性 | Topic 模式（默认） | Trending 模式 |
|-----|-----------------|--------------|
| **数据源** | 指定话题（如 `claude-code`） | 全站项目 |
| **排序依据** | 总星标数 | 总星标数（可配置） |
| **时间范围** | 全部历史 | 最近 N 天创建 |
| **适用场景** | 追踪特定话题热门项目 | 发现全站新兴项目 |
| **类似网站** | GitHub Topics 页面 | GitHub Trending 页面 |

## 快速切换

### 切换到 Trending 模式

编辑 `.env` 文件：

```bash
# 修改这一行
TRENDING_MODE=trending

# 可选配置
TRENDING_DAYS=7                # 获取最近 7 天创建的项目
TRENDING_MIN_STARS=50          # 最低星标数过滤
TRENDING_LANGUAGE=             # 语言过滤（空=全部）
```

### 切换回 Topic 模式

```bash
# 修改这一行
TRENDING_MODE=topic
TOPIC=claude-code              # 指定要追踪的话题
```

## 配置详解

### TRENDING_MODE
- **类型**: 字符串
- **可选值**: `topic` 或 `trending`
- **默认值**: `topic`
- **说明**: 数据获取模式

### TRENDING_DAYS
- **类型**: 整数
- **默认值**: `7`
- **说明**: trending 模式下，获取最近多少天**创建**的项目
- **示例**:
  - `TRENDING_DAYS=1` - 获取今天创建的项目
  - `TRENDING_DAYS=7` - 获取最近一周创建的项目
  - `TRENDING_DAYS=30` - 获取最近一个月创建的项目

### TRENDING_MIN_STARS
- **类型**: 整数
- **默认值**: `50`
- **说明**: trending 模式下，项目最低星标数
- **建议值**:
  - `10-50` - 包含较新的项目
  - `100-500` - 中等热度项目
  - `1000+` - 只看非常热门的项目

### TRENDING_LANGUAGE
- **类型**: 字符串
- **默认值**: `""` (空字符串，表示不过滤)
- **说明**: trending 模式下，按编程语言过滤
- **常用值**:
  - `Python`
  - `JavaScript`
  - `TypeScript`
  - `Go`
  - `Rust`
  - `Java`
  - 留空表示获取所有语言的项目

## 使用示例

### 示例 1: 获取今日热门 Python 项目

```bash
# .env 配置
TRENDING_MODE=trending
TRENDING_DAYS=1
TRENDING_MIN_STARS=100
TRENDING_LANGUAGE=Python
```

**效果**: 获取今天创建、至少 100 星标的 Python 项目

### 示例 2: 获取本周全站新秀

```bash
# .env 配置
TRENDING_MODE=trending
TRENDING_DAYS=7
TRENDING_MIN_STARS=50
TRENDING_LANGUAGE=
```

**效果**: 获取最近 7 天创建、至少 50 星标的所有项目

### 示例 3: 继续追踪特定话题

```bash
# .env 配置
TRENDING_MODE=topic
TOPIC=ai
```

**效果**: 获取 `ai` 话题下按星标排序的项目

## 命令行测试

### 测试 Topic 模式

```bash
python -c "
from src.github_fetcher import GitHubFetcher
fetcher = GitHubFetcher()
repos = fetcher.fetch(limit=5, mode='topic')
for r in repos[:5]:
    print(f'{r[\"repo_name\"]} - ⭐ {r[\"stars\"]}')
"
```

### 测试 Trending 模式

```bash
python -c "
from src.github_fetcher import GitHubFetcher
fetcher = GitHubFetcher()
repos = fetcher.fetch(limit=5, mode='trending')
for r in repos[:5]:
    print(f'{r[\"repo_name\"]} - ⭐ {r[\"stars\"]}')
"
```

## 运行完整流程

```bash
# 确保配置正确
cat .env | grep TRENDING

# 运行主程序
python -m src.main
```

## GitHub Actions 配置

在 `.github/workflows/github-trending.yml` 中设置环境变量：

```yaml
env:
  # Topic 模式
  TRENDING_MODE: topic
  TOPIC: claude-code

  # 或 Trending 模式
  TRENDING_MODE: trending
  TRENDING_DAYS: 7
  TRENDING_MIN_STARS: 50
  TRENDING_LANGUAGE: ""
```

## 技术实现

### Topic 模式查询

```
GET /search/repositories?q=topic:claude-code&sort=stars&order=desc
```

### Trending 模式查询

```
GET /search/repositories?q=created:>2026-01-22 stars:>=50&sort=stars&order=desc
```

如果设置了语言过滤：

```
GET /search/repositories?q=created:>2026-01-22 stars:>=50 language:Python&sort=stars&order=desc
```

## 注意事项

1. **GitHub API 限制**: 认证用户 5000 requests/hour，已通过 `GH_TOKEN` 认证
2. **Search API 限制**: 每个查询最多返回 1000 个结果
3. **时间计算**: `TRENDING_DAYS` 是基于项目**创建时间**，不是最近活跃时间
4. **星标数**: Trending 模式的星标数是**总星标数**，不是日增长量

## 常见问题

### Q: Trending 模式和 GitHub Trending 页面的结果一样吗？
A: 不完全一样。GitHub Trending 官方算法未公开，本实现是基于：
- 项目创建时间（最近 N 天）
- 总星标数排序
- 可选的语言过滤

官方 Trending 可能还考虑了增长速度、fork 数等其他因素。

### Q: 如何获取真正的"日增长"数据？
A: 需要每日运行并保存历史数据，然后计算差值。项目的数据库模块（`trending_db.py`）已经支持这个功能。

### Q: 可以同时获取多个语言的项目吗？
A: 目前不支持，`TRENDING_LANGUAGE` 只能设置单个语言或留空（全部语言）。

### Q: 为什么有些新项目没有出现？
A: 可能是因为：
1. 星标数未达到 `TRENDING_MIN_STARS` 阈值
2. 创建时间超过 `TRENDING_DAYS` 天数
3. GitHub API 缓存延迟

### Q: Trending 模式下 TOPIC 配置还有用吗？
A: 没有。Trending 模式会忽略 `TOPIC` 配置，直接搜索全站项目。

## 更新日志

- **2026-01-29**: 添加 Trending 模式支持
  - 支持按创建时间过滤
  - 支持最低星标数过滤
  - 支持编程语言过滤
  - 保持与 Topic 模式的兼容性
