"""
GitHub Fetcher - 从 GitHub API 获取仓库数据
使用 GitHub Search API 按话题获取仓库
"""
import time
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import re

from src.config import (
    GITHUB_TOKEN, TOPIC, GITHUB_API_BASE,
    GITHUB_PER_PAGE, GITHUB_MAX_PAGES, GITHUB_SEARCH_SORT,
    GITHUB_SEARCH_ORDER, FETCH_REQUEST_DELAY,
    TRENDING_MODE, TRENDING_API_MODE, TRENDING_DAYS, TRENDING_MIN_STARS,
    TRENDING_LANGUAGE, TRENDING_SINCE
)


class GitHubFetcher:
    """从 GitHub API 获取仓库数据"""

    def __init__(self, token: str = None, topic: str = None):
        """
        初始化

        Args:
            token: GitHub Personal Access Token
            topic: 要搜索的 GitHub Topic
        """
        self.token = token or GITHUB_TOKEN
        self.topic = topic or TOPIC
        self.api_base = GITHUB_API_BASE
        self.per_page = GITHUB_PER_PAGE
        self.max_pages = GITHUB_MAX_PAGES
        self.delay = FETCH_REQUEST_DELAY

        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "GitHub-Topics-Trending/1.0"
        })

        if self.token:
            self.session.headers.update({
                "Authorization": f"Bearer {self.token}"
            })

        self.rate_limit_remaining = 5000
        self.rate_limit_reset = None

    def fetch(self, sort_by: str = None, limit: int = None, mode: str = None) -> List[Dict]:
        """
        获取仓库列表

        Args:
            sort_by: 排序方式 (stars, forks, updated)
            limit: 最大返回数量
            mode: 模式 ("topic" 或 "trending")，默认从环境变量读取

        Returns:
            [
                {
                    "rank": 1,
                    "repo_name": "owner/repo",
                    "owner": "owner",
                    "stars": 1000,
                    "forks": 100,
                    "issues": 10,
                    "language": "Python",
                    "url": "https://github.com/owner/repo",
                    "description": "...",
                    "topics": ["topic1", "topic2"],
                    "created_at": "2024-01-01T00:00:00Z",
                    "updated_at": "2024-01-01T00:00:00Z"
                },
                ...
            ]
        """
        mode = mode or TRENDING_MODE
        sort_by = sort_by or GITHUB_SEARCH_SORT
        limit = limit or (self.per_page * self.max_pages)

        if mode == "trending":
            return self._fetch_trending(sort_by, limit)
        else:
            return self._fetch_topic(sort_by, limit)

    def _fetch_topic(self, sort_by: str, limit: int) -> List[Dict]:
        """
        获取指定话题下的仓库列表

        Args:
            sort_by: 排序方式
            limit: 最大返回数量

        Returns:
            仓库列表
        """
        print(f"📡 正在获取话题 '{self.topic}' 的仓库列表...")
        print(f"   排序方式: {sort_by}")

        repos = []
        page = 1

        while page <= self.max_pages and len(repos) < limit:
            # 检查速率限制
            if self.rate_limit_remaining < 10:
                self._wait_for_rate_limit()

            data = self._fetch_page(page, sort_by, mode="topic")

            if not data or "items" not in data:
                break

            items = data["items"]
            if not items:
                break

            for item in items:
                repo = self._parse_repo_item(item, len(repos) + 1)
                repos.append(repo)

                if len(repos) >= limit:
                    break

            # 更新速率限制信息
            self._update_rate_limit(data)

            print(f"   第 {page} 页: 获取 {len(items)} 个仓库 (累计 {len(repos)})")

            # 如果返回数量少于 per_page，说明已经到最后一页
            if len(items) < self.per_page:
                break

            page += 1

            # 请求间隔
            if page <= self.max_pages and len(repos) < limit:
                time.sleep(self.delay)

        print(f"✅ 成功获取 {len(repos)} 个仓库")
        return repos

    def _fetch_trending(self, sort_by: str, limit: int) -> List[Dict]:
        """
        获取 GitHub Trending 风格的仓库（近期高增长项目）

        Args:
            sort_by: 排序方式
            limit: 最大返回数量

        Returns:
            仓库列表
        """
        # 使用第三方官方 Trending API
        if TRENDING_API_MODE == "official":
            return self._fetch_trending_from_page(TRENDING_SINCE, limit)
        else:
            # 使用 Search API 模拟
            return self._fetch_trending_from_search(sort_by, limit)

    def fetch_all_trending_periods(self, limit: int = 25) -> Dict[str, List[Dict]]:
        """
        一次性获取 daily、weekly、monthly 三个时间范围的 Trending 数据

        Args:
            limit: 每个时间范围获取的最大数量

        Returns:
            {
                "daily": [...],
                "weekly": [...],
                "monthly": [...]
            }
        """
        print("=" * 70)
        print("🔥 开始获取多时间段 Trending 数据")
        print("=" * 70)
        print()

        results = {}

        for period in ["daily", "weekly", "monthly"]:
            print(f"\n📅 正在获取 {period.upper()} Trending...")
            print("-" * 70)

            # 临时修改配置
            original_since = TRENDING_SINCE

            try:
                # 直接传递 period 参数
                repos = self._fetch_trending_with_period(period, limit)
                results[period] = repos

                print(f"✅ {period.upper()}: 成功获取 {len(repos)} 个项目")

                # 请求间隔，避免过快
                if period != "monthly":
                    time.sleep(1)

            except Exception as e:
                print(f"❌ {period.upper()}: 获取失败 - {e}")
                results[period] = []

        print()
        print("=" * 70)
        print(f"🎉 完成！共获取:")
        print(f"   📊 Today:     {len(results.get('daily', []))} 个项目")
        print(f"   📊 This Week: {len(results.get('weekly', []))} 个项目")
        print(f"   📊 This Month:{len(results.get('monthly', []))} 个项目")
        print("=" * 70)

        return results

    def _fetch_trending_with_period(self, period: str, limit: int) -> List[Dict]:
        """
        获取指定时间范围的 Trending 数据

        Args:
            period: "daily", "weekly", or "monthly"
            limit: 最大返回数量

        Returns:
            仓库列表
        """
        if TRENDING_API_MODE == "official":
            return self._fetch_trending_from_page(period, limit)
        else:
            # Search API 模式下，时间范围映射
            days_map = {"daily": 1, "weekly": 7, "monthly": 30}
            days = days_map.get(period, 7)
            return self._fetch_trending_from_search("stars", limit, days)

    def _fetch_trending_from_page(self, period: str, limit: int) -> List[Dict]:
        """
        爬取 GitHub Trending 页面获取数据（和官方页面完全一致）

        Args:
            period: "daily", "weekly", or "monthly"
            limit: 最大返回数量

        Returns:
            仓库列表
        """
        # 构建 GitHub Trending URL
        trending_url = "https://github.com/trending"

        params = {}
        if TRENDING_LANGUAGE:
            trending_url = f"{trending_url}/{TRENDING_LANGUAGE.lower()}"

        # since 参数
        params["since"] = period

        print(f"🔥 正在爬取 GitHub Trending 页面...")
        print(f"   时间范围: {period}")
        if TRENDING_LANGUAGE:
            print(f"   语言过滤: {TRENDING_LANGUAGE}")

        try:
            # 爬取页面
            headers = {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
            response = requests.get(trending_url, params=params, headers=headers, timeout=30)
            response.raise_for_status()

            # 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.find_all('article', class_='Box-row')

            if not articles:
                print(f"   ⚠️ 未找到 trending 项目")
                return []

            repos = []
            for i, article in enumerate(articles[:limit], 1):
                repo = self._parse_trending_html(article, i)
                if repo:
                    repos.append(repo)

            print(f"✅ 成功爬取 {len(repos)} 个 Trending 仓库")
            return repos

        except Exception as e:
            print(f"   ⚠️ 爬取 Trending 页面失败: {e}")
            print(f"   ℹ️ 降级使用 Search API")
            return self._fetch_trending_from_search("stars", limit)

    def _parse_trending_html(self, article, rank: int) -> Optional[Dict]:
        """
        解析 GitHub Trending 页面的单个仓库

        Args:
            article: BeautifulSoup article 元素
            rank: 排名

        Returns:
            仓库信息字典，解析失败返回 None
        """
        try:
            # 获取仓库名称
            h2 = article.find('h2', class_='h3')
            if not h2:
                return None

            repo_link = h2.find('a')
            if not repo_link:
                return None

            repo_name = repo_link['href'].strip('/')
            owner, name = repo_name.split('/')

            # 获取描述
            description_elem = article.find('p', class_='col-9')
            description = description_elem.text.strip() if description_elem else ""

            # 获取语言
            language_elem = article.find('span', attrs={'itemprop': 'programmingLanguage'})
            language = language_elem.text.strip() if language_elem else ""

            # 获取星标数
            star_elem = article.find('span', class_='d-inline-block float-sm-right')
            stars_text = star_elem.text.strip() if star_elem else "0"
            stars = self._parse_number(stars_text)

            # 获取 fork 数
            fork_elem = article.find_all('a', class_='Link--muted')
            forks = 0
            for elem in fork_elem:
                if 'network/members' in elem.get('href', ''):
                    forks = self._parse_number(elem.text.strip())
                    break

            # 获取今日星标增长
            stars_today_elem = article.find('span', class_='d-inline-block float-sm-right')
            trending_stars = 0
            if stars_today_elem:
                today_text = stars_today_elem.find_next_sibling('span')
                if today_text:
                    trending_stars = self._parse_number(today_text.text.strip())

            return {
                "rank": rank,
                "repo_name": repo_name,
                "owner": owner,
                "name": name,
                "stars": stars,
                "forks": forks,
                "issues": 0,
                "language": language,
                "url": f"https://github.com/{repo_name}",
                "description": description,
                "topics": [],
                "created_at": "",
                "updated_at": "",
                "trending_stars": trending_stars,
            }

        except Exception as e:
            print(f"   ⚠️ 解析仓库失败: {e}")
            return None

    def _parse_number(self, text: str) -> int:
        """解析数字（支持 1k, 1.5k 等格式）"""
        text = text.replace(',', '').strip()
        match = re.search(r'([\d.]+)\s*([km])?', text.lower())
        if not match:
            return 0

        num = float(match.group(1))
        unit = match.group(2)

        if unit == 'k':
            return int(num * 1000)
        elif unit == 'm':
            return int(num * 1000000)
        return int(num)

    def _parse_trending_api_item(self, item: Dict, rank: int) -> Dict:
        """
        解析第三方 Trending API 返回的数据

        Args:
            item: API 返回的仓库项
            rank: 排名

        Returns:
            标准化的仓库信息
        """
        # 第三方 API 返回格式：
        # {
        #   "author": "owner",
        #   "name": "repo",
        #   "url": "https://github.com/owner/repo",
        #   "description": "...",
        #   "language": "Python",
        #   "stars": 1000,
        #   "forks": 100,
        #   "currentPeriodStars": 50,  # 本期增长
        #   ...
        # }

        owner = item.get("author", "")
        name = item.get("name", "")
        repo_name = f"{owner}/{name}"

        return {
            "rank": rank,
            "repo_name": repo_name,
            "owner": owner,
            "name": name,
            "stars": item.get("stars", 0),
            "forks": item.get("forks", 0),
            "issues": 0,  # API 不提供
            "language": item.get("language", ""),
            "url": item.get("url", f"https://github.com/{repo_name}"),
            "description": item.get("description", ""),
            "topics": [],  # API 不提供
            "created_at": "",  # API 不提供
            "updated_at": "",  # API 不提供
            "trending_stars": item.get("currentPeriodStars", 0),  # 额外信息：本期增长
        }

    def _fetch_trending_from_search(self, sort_by: str, limit: int, days: int = None) -> List[Dict]:
        """
        获取 GitHub Trending 风格的仓库（近期高增长项目）

        Args:
            sort_by: 排序方式
            limit: 最大返回数量
            days: 最近 N 天（如果不指定，使用 TRENDING_DAYS）

        Returns:
            仓库列表
        """
        cutoff_date = (datetime.now() - timedelta(days=days or TRENDING_DAYS)).strftime("%Y-%m-%d")

        print(f"🔥 正在获取 GitHub Trending 仓库...")
        print(f"   时间范围: 最近 {TRENDING_DAYS} 天活跃 (pushed>{cutoff_date})")
        print(f"   最低星标: {TRENDING_MIN_STARS}+")
        if TRENDING_LANGUAGE:
            print(f"   语言过滤: {TRENDING_LANGUAGE}")
        print(f"   排序方式: {sort_by}")

        repos = []
        page = 1

        while page <= self.max_pages and len(repos) < limit:
            # 检查速率限制
            if self.rate_limit_remaining < 10:
                self._wait_for_rate_limit()

            data = self._fetch_page(page, sort_by, mode="trending")

            if not data or "items" not in data:
                break

            items = data["items"]
            if not items:
                break

            for item in items:
                repo = self._parse_repo_item(item, len(repos) + 1)
                repos.append(repo)

                if len(repos) >= limit:
                    break

            # 更新速率限制信息
            self._update_rate_limit(data)

            print(f"   第 {page} 页: 获取 {len(items)} 个仓库 (累计 {len(repos)})")

            # 如果返回数量少于 per_page，说明已经到最后一页
            if len(items) < self.per_page:
                break

            page += 1

            # 请求间隔
            if page <= self.max_pages and len(repos) < limit:
                time.sleep(self.delay)

        print(f"✅ 成功获取 {len(repos)} 个 Trending 仓库")
        return repos

    def _fetch_page(self, page: int, sort_by: str, mode: str = "topic") -> Optional[Dict]:
        """
        获取单页数据

        Args:
            page: 页码
            sort_by: 排序方式
            mode: "topic" 或 "trending"

        Returns:
            API 响应数据
        """
        url = f"{self.api_base}/search/repositories"

        # 根据模式构建查询
        if mode == "trending":
            # Trending 模式：最近N天有推送（活跃） + 最低星标数 + 可选语言过滤
            cutoff_date = (datetime.now() - timedelta(days=TRENDING_DAYS)).strftime("%Y-%m-%d")
            query_parts = [
                f"pushed:>{cutoff_date}",  # 改用 pushed: 捕获活跃项目
                f"stars:>={TRENDING_MIN_STARS}"
            ]
            if TRENDING_LANGUAGE:
                query_parts.append(f"language:{TRENDING_LANGUAGE}")
            query = " ".join(query_parts)
        else:
            # Topic 模式：按话题搜索
            query = f"topic:{self.topic}"

        params = {
            "q": query,
            "sort": sort_by,
            "order": GITHUB_SEARCH_ORDER,
            "per_page": self.per_page,
            "page": page
        }

        try:
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"   ⚠️ 请求失败 (页 {page}): {e}")
            return None

    def _parse_repo_item(self, item: Dict, rank: int) -> Dict:
        """
        解析仓库数据

        Args:
            item: GitHub API 返回的仓库项
            rank: 排名

        Returns:
            仓库信息字典
        """
        owner_data = item.get("owner") or {}
        owner = owner_data.get("login", "")
        name = item.get("name", "")
        repo_name = f"{owner}/{name}"

        return {
            "rank": rank,
            "repo_name": repo_name,
            "owner": owner,
            "name": name,
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "issues": item.get("open_issues_count", 0),
            "language": item.get("language", ""),
            "url": item.get("html_url", ""),
            "description": item.get("description", ""),
            "topics": item.get("topics", []),
            "created_at": item.get("created_at", ""),
            "updated_at": item.get("updated_at", ""),
            "pushed_at": item.get("pushed_at", ""),
            "homepage": item.get("homepage", ""),
            "archived": item.get("archived", False),
        }

    def _update_rate_limit(self, response_data: Dict):
        """
        更新速率限制信息

        Args:
            response_data: API 响应数据
        """
        # 注意：这些信息在实际请求中从响应头获取
        # 这里只是一个简化版本
        pass

    def _wait_for_rate_limit(self):
        """等待速率限制重置"""
        if self.rate_limit_reset:
            now = int(time.time())
            wait_time = self.rate_limit_reset - now + 1

            if wait_time > 0:
                print(f"⏳ 速率限制已用尽，等待 {wait_time} 秒后重试...")
                time.sleep(wait_time)

    def fetch_new_repos(self, days: int = 7) -> List[Dict]:
        """
        获取最近创建的仓库

        Args:
            days: 最近多少天

        Returns:
            仓库列表
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        query = f"topic:{self.topic} created:>{cutoff_date}"

        print(f"📡 正在获取最近 {days} 天创建的仓库...")

        repos = []
        page = 1

        while page <= self.max_pages:
            url = f"{self.api_base}/search/repositories"
            params = {
                "q": query,
                "sort": "stars",
                "order": "desc",
                "per_page": self.per_page,
                "page": page
            }

            try:
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                data = response.json()

                if not data or "items" not in data:
                    break

                items = data["items"]
                if not items:
                    break

                for item in items:
                    repo = self._parse_repo_item(item, len(repos) + 1)
                    repos.append(repo)

                print(f"   第 {page} 页: 获取 {len(items)} 个仓库")

                if len(items) < self.per_page:
                    break

                page += 1
                time.sleep(self.delay)

            except requests.RequestException as e:
                print(f"   ⚠️ 请求失败: {e}")
                break

        print(f"✅ 获取到 {len(repos)} 个新仓库")
        return repos

    def fetch_repo_details(self, owner: str, repo: str) -> Optional[Dict]:
        """
        获取单个仓库的详细信息

        Args:
            owner: 仓库拥有者
            repo: 仓库名称

        Returns:
            仓库详细信息
        """
        url = f"{self.api_base}/repos/{owner}/{repo}"

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return response.json()

        except requests.RequestException as e:
            print(f"   ⚠️ 获取仓库详情失败 {owner}/{repo}: {e}")
            return None


def fetch_repos(sort_by: str = "stars", limit: int = 100) -> List[Dict]:
    """便捷函数：获取仓库列表"""
    fetcher = GitHubFetcher()
    return fetcher.fetch(sort_by=sort_by, limit=limit)
