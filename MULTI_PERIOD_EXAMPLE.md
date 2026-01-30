# 多时间段 Trending 数据获取示例

本示例展示如何一次性获取 daily、weekly、monthly 三个时间段的 GitHub Trending 数据。

## 使用方法

### 方法 1：使用 `fetch_all_trending_periods()` 一次性获取

```python
from src.github_fetcher import GitHubFetcher

fetcher = GitHubFetcher()

# 一次性获取三个时间段的数据
results = fetcher.fetch_all_trending_periods(limit=25)

# 结果格式：
# {
#     "daily": [...],    # 今日 Trending
#     "weekly": [...],   # 本周 Trending
#     "monthly": [...]   # 本月 Trending
# }

# 访问数据
daily_repos = results["daily"]
weekly_repos = results["weekly"]
monthly_repos = results["monthly"]

print(f"Today 第1名: {daily_repos[0]['repo_name']}")
print(f"This Week 第1名: {weekly_repos[0]['repo_name']}")
print(f"This Month 第1名: {monthly_repos[0]['repo_name']}")
```

### 方法 2：手动切换 `TRENDING_SINCE` 配置

```python
from src.github_fetcher import GitHubFetcher
import os

results = {}

for period in ["daily", "weekly", "monthly"]:
    # 临时修改环境变量
    os.environ["TRENDING_SINCE"] = period

    fetcher = GitHubFetcher()
    repos = fetcher.fetch(limit=25)

    results[period] = repos
```

## 完整示例代码

```python
#!/usr/bin/env python3
"""
获取多时间段 GitHub Trending 数据
"""
from src.github_fetcher import GitHubFetcher

def main():
    fetcher = GitHubFetcher()

    # 获取所有时间段数据
    print("正在获取 GitHub Trending 数据...")
    results = fetcher.fetch_all_trending_periods(limit=25)

    # 分析结果
    print("\n" + "=" * 70)
    print("📊 Trending 数据汇总")
    print("=" * 70)

    for period_key, period_name in [
        ("daily", "Today"),
        ("weekly", "This Week"),
        ("monthly", "This Month")
    ]:
        repos = results.get(period_key, [])
        print(f"\n{period_name} ({len(repos)} 个项目):")
        print("-" * 70)

        # 显示 Top 5
        for i, repo in enumerate(repos[:5], 1):
            trending_stars = repo.get('trending_stars', 0)
            print(f"{i}. {repo['repo_name']:<40}")
            print(f"   ⭐ {repo['stars']:>6,} (+{trending_stars:>4,}) | 🔤 {repo['language'] or 'N/A'}")

    # 找出在所有榜单都出现的项目
    print("\n" + "=" * 70)
    print("🔥 霸榜项目（出现在所有榜单 Top 10）")
    print("=" * 70)

    daily_names = {r['repo_name'] for r in results.get('daily', [])[:10]}
    weekly_names = {r['repo_name'] for r in results.get('weekly', [])[:10]}
    monthly_names = {r['repo_name'] for r in results.get('monthly', [])[:10]}

    hot_projects = daily_names & weekly_names & monthly_names

    if hot_projects:
        for repo_name in hot_projects:
            print(f"🏆 {repo_name}")

            # 显示在各榜单的排名
            for period, period_name in [("daily", "Today"), ("weekly", "Week"), ("monthly", "Month")]:
                repos = results.get(period, [])
                for i, r in enumerate(repos, 1):
                    if r['repo_name'] == repo_name:
                        stars = r.get('stars', 0)
                        print(f"   {period_name:<6}: 第 {i:2d} 名 (⭐ {stars:>6,})")
                        break
            print()
    else:
        print("没有项目同时出现在所有榜单 Top 10")

if __name__ == "__main__":
    main()
```

## 输出示例

```
======================================================================
🔥 开始获取多时间段 Trending 数据
======================================================================

📅 正在获取 DAILY Trending...
----------------------------------------------------------------------
🔥 正在爬取 GitHub Trending 页面...
   时间范围: daily
✅ 成功爬取 25 个 Trending 仓库
✅ DAILY: 成功获取 25 个项目

📅 正在获取 WEEKLY Trending...
----------------------------------------------------------------------
🔥 正在爬取 GitHub Trending 页面...
   时间范围: weekly
✅ 成功爬取 25 个 Trending 仓库
✅ WEEKLY: 成功获取 25 个项目

📅 正在获取 MONTHLY Trending...
----------------------------------------------------------------------
🔥 正在爬取 GitHub Trending 页面...
   时间范围: monthly
✅ 成功爬取 25 个 Trending 仓库
✅ MONTHLY: 成功获取 25 个项目

======================================================================
🎉 完成！共获取:
   📊 Today:     25 个项目
   📊 This Week: 25 个项目
   📊 This Month:25 个项目
======================================================================

📊 Trending 数据汇总
======================================================================

Today (25 个项目):
----------------------------------------------------------------------
1. moltbot/moltbot
   ⭐ 17,830 (+   0) | 🔤 TypeScript
2. badlogic/pi-mono
   ⭐    396 (+   0) | 🔤 TypeScript
...

This Week (25 个项目):
----------------------------------------------------------------------
1. moltbot/moltbot
   ⭐ 83,158 (+   0) | 🔤 TypeScript
2. VoltAgent/awesome-moltbot-skills
   ⭐  3,206 (+   0) | 🔤 N/A
...

This Month (25 个项目):
----------------------------------------------------------------------
1. moltbot/moltbot
   ⭐ 88,133 (+   0) | 🔤 TypeScript
2. antfu/skills
   ⭐  2,024 (+   0) | 🔤 TypeScript
...

======================================================================
🔥 霸榜项目（出现在所有榜单 Top 10）
======================================================================
🏆 moltbot/moltbot
   Today : 第  1 名 (⭐ 17,830)
   Week  : 第  1 名 (⭐ 83,158)
   Month : 第  1 名 (⭐ 88,133)
```

## 配置说明

在 `.env` 文件中：

```bash
# Trending 模式配置
TRENDING_MODE=trending
TRENDING_API_MODE=official  # 使用页面爬取
TRENDING_LANGUAGE=          # 空=全部语言，或指定如 Python
```

**注意**: 使用 `fetch_all_trending_periods()` 时，会忽略 `TRENDING_SINCE` 配置，自动获取所有三个时间段。

## API 参考

### `fetch_all_trending_periods(limit: int = 25) -> Dict[str, List[Dict]]`

一次性获取三个时间段的 Trending 数据。

**参数:**
- `limit`: 每个时间段获取的最大项目数量，默认 25

**返回:**
```python
{
    "daily": [
        {
            "rank": 1,
            "repo_name": "owner/repo",
            "owner": "owner",
            "name": "repo",
            "stars": 1000,
            "forks": 100,
            "language": "Python",
            "url": "https://github.com/owner/repo",
            "description": "...",
            "trending_stars": 50,  # 本期增长星标数
            ...
        },
        ...
    ],
    "weekly": [...],
    "monthly": [...]
}
```

## 使用场景

1. **对比分析** - 比较不同时间段的热门项目
2. **趋势追踪** - 发现持续热门的项目（霸榜项目）
3. **新项目发现** - 找出只在 daily 榜单的新兴项目
4. **报表生成** - 生成多维度的 Trending 报告

## 性能说明

- 每次调用会发起 3 次 HTTP 请求（每个时间段一次）
- 总耗时约 3-5 秒（包含请求间隔）
- 建议不要频繁调用，可以缓存结果

## 注意事项

1. GitHub 可能会对频繁请求进行限制
2. 页面结构变化可能导致爬取失败（有降级机制）
3. 建议在正式使用前测试爬取结果
