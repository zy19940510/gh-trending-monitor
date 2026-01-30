# GitHub Topics Trending

> Track trending GitHub repositories by topic or discover emerging projects across the platform, with AI-powered analysis and daily email reports.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

## Highlights

### Authentic GitHub Trending Experience

Unlike other trending trackers, this project **accurately replicates the official GitHub Trending algorithm**:

- **Dual Mode Support**:
  - **Topic Mode**: Track top repositories by specific topics (e.g., `claude-code`, `ai`)
  - **Trending Mode**: Discover emerging projects across all of GitHub, just like the official Trending page

- **Smart Filtering**:
  - Filter by creation date (last 1/7/30 days)
  - Minimum star threshold to focus on quality
  - Language-specific tracking (Python, TypeScript, Go, etc.)

- **Real Trending Data**: Fetch newly created repositories sorted by total stars, matching the official GitHub Trending behavior

### AI-Powered Intelligence

- **Claude AI Analysis**: Automatically summarizes each repository in one sentence
- **Smart Categorization**: Classifies repos as plugins, tools, templates, docs, etc.
- **Problem Detection**: Identifies what problems each project solves
- **Trend Insights**: Detects newcomers, fast-growing projects, and active repos

### Professional Automation

- **Daily Email Reports**: Beautiful HTML emails with clickable repository cards
- **GitHub Pages Website**: Auto-generated static site with all trending data
- **SQLite Database**: Historical data storage for trend analysis
- **GitHub Actions**: Fully automated daily execution

---

## Quick Start

### Prerequisites

- Python 3.11+
- GitHub Personal Access Token ([How to create](https://github.com/settings/tokens))
- LLM API Key (Zhipu AI or LB One API)
- Resend API Key ([Sign up here](https://resend.com))

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/gh-trending-monitor.git
cd gh-trending-monitor

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env
```

### Configuration

Edit `.env` file:

```bash
# GitHub API
GH_TOKEN=your_github_token

# Mode Selection: "topic" or "trending"
TRENDING_MODE=trending

# Trending Mode Settings (skip if using topic mode)
TRENDING_DAYS=7              # Get repos created in last 7 days
TRENDING_MIN_STARS=50        # Minimum stars filter
TRENDING_LANGUAGE=           # Language filter (empty = all)

# Topic Mode Settings (skip if using trending mode)
TOPIC=claude-code            # Topic to track

# LLM Provider: "zhipu" or "one"
LLM_PROVIDER=one
ONE_API_KEY=sk-xxxxxxxxxxxxxxxx
ONE_BASE_URL=https://lboneapi.longbridge-inc.com
ONE_MODEL=claude-sonnet-4-5-20250929

# Email Service
RESEND_API_KEY=re_xxxxxxxxxxxxx
EMAIL_TO=your-email@example.com
```

**Detailed LLM setup**: See [LLM_PROVIDER_GUIDE.md](./LLM_PROVIDER_GUIDE.md)
**Trending mode details**: See [TRENDING_MODE_GUIDE.md](./TRENDING_MODE_GUIDE.md)

### Run

```bash
# Full pipeline (fetch + analyze + email + web)
python -m src.main

# Fetch data only (no email)
python -m src.main --fetch-only
```

---

## Features

### Two Operation Modes

| Feature | Topic Mode | Trending Mode |
|---------|-----------|---------------|
| **Data Source** | Specific topic (e.g., `claude-code`) | Platform-wide repositories |
| **Sorting** | Total stars | Total stars (configurable) |
| **Time Range** | All-time | Recently created (1/7/30 days) |
| **Use Case** | Track niche topics | Discover emerging projects |
| **Similar To** | GitHub Topics page | GitHub Trending page |

**Switch modes** by changing `TRENDING_MODE` in `.env`

### Email Report Contents

- **Top 20 Repositories** with AI summaries
- **Star Growth Top 5** - Fastest rising stars
- **Newcomers** - New entries to the list
- **Active Projects** - Recently updated repos
- **Trend Statistics** - Overall insights

### Smart Categorization

Repos are automatically classified as:
- **Plugins** (VS Code, Claude Code extensions)
- **Tools** (CLI tools, dev utilities)
- **Templates** (Project starters, boilerplates)
- **Docs** (Tutorials, books, guides)
- **Examples** (Demo projects, samples)
- **Integrations** (API wrappers, SDKs)
- **Libraries** (Python/JS/Other packages)
- **Applications** (Full apps, products)

---

## GitHub Actions Setup

### 1. Configure Secrets

Go to **Settings** → **Secrets and variables** → **Actions** → **New repository secret**

Add these secrets:

| Name | Required | Value |
|------|----------|-------|
| `GH_TOKEN` | ✅ | Your GitHub PAT |
| `TOPIC` | - | `claude-code` (for topic mode) |
| `ZHIPU_API_KEY` | ✅ | Zhipu API Key |
| `RESEND_API_KEY` | ✅ | Resend API Key |
| `EMAIL_TO` | ✅ | Your email address |

### 2. Enable Workflow Permissions

**Settings** → **Actions** → **General** → **Workflow permissions**
Select: **Read and write permissions** → **Save**

### 3. Manual Trigger

**Actions** tab → Select **GitHub Topics Trending** → **Run workflow**

### 4. Scheduled Execution

Runs daily at **UTC 02:00** (Beijing 10:00 AM)

---

## GitHub Pages Setup

### Enable Pages

1. **Settings** → **Pages**
2. **Build and deployment**:
   - Source: **Deploy from a branch**
   - Branch: **gh-pages** / **/ (root)**
   - Click **Save**

3. **Make repository public**:
   - **Settings** → **General** → Scroll to **Danger Zone**
   - **Change repository visibility** → **Public**

4. **Access your site**:
   ```
   https://YOUR_USERNAME.github.io/github-topics-trending/
   ```

⚠️ **Note**: First deployment takes 5-10 minutes to become available

---

## Project Structure

```
github-topics-trending/
├── .github/workflows/
│   └── github-trending.yml     # GitHub Actions workflow
├── src/
│   ├── config.py               # Configuration management
│   ├── database.py             # SQLite operations
│   ├── github_fetcher.py       # GitHub API client
│   ├── readme_fetcher.py       # README retrieval
│   ├── claude_summarizer.py    # AI analysis
│   ├── trend_analyzer.py       # Trend calculation
│   ├── email_reporter.py       # Email generation
│   ├── web_generator.py        # Website generation
│   ├── resend_sender.py        # Email delivery
│   └── main.py                 # Entry point
├── docs/                       # GitHub Pages output
├── data/
│   └── github-trending.db      # SQLite database
├── requirements.txt
├── .env.example
└── README.md
```

---

## Future Roadmap

### Planned Features

- [ ] **Multi-Language Support**
  - Support tracking multiple programming languages simultaneously
  - Generate separate reports per language

- [ ] **Advanced Analytics**
  - Fork/Star ratio analysis
  - Issue activity tracking
  - Contributor growth trends
  - Weekly/Monthly summary reports

- [ ] **Enhanced Filtering**
  - Filter by license type
  - Exclude archived repositories
  - Custom star threshold per topic

- [ ] **Social Integration**
  - Auto-post to Twitter/X
  - Slack/Discord webhook notifications
  - Telegram bot integration

- [ ] **Web Dashboard**
  - Interactive charts and graphs
  - Historical trend visualization
  - Search and filter functionality
  - Export to CSV/JSON

- [ ] **Smart Recommendations**
  - Personalized project suggestions based on starred repos
  - Similar project discovery
  - Cross-topic trending patterns

- [ ] **API Endpoints**
  - RESTful API for accessing trending data
  - Webhook support for real-time updates
  - GraphQL query interface

- [ ] **Performance Optimization**
  - Parallel API requests
  - Redis caching layer
  - Incremental updates

### Community Contributions Welcome!

Have ideas? Open an issue or submit a PR!

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No email received | Check Resend API key, verify email address, check spam folder |
| GitHub API rate limit | Ensure `GH_TOKEN` is configured (5000 req/hour) |
| 404 on Pages | Ensure repo is public, wait 5-10 minutes for Pages to deploy |
| Actions permission denied | Set Workflow permissions to "Read and write" |

---

## Development

### Run Locally

```bash
# Set environment variables
export GH_TOKEN="your_token"
export TRENDING_MODE="trending"
export TRENDING_DAYS="7"

# Run the pipeline
python -m src.main
```

### Query Database

```bash
# View latest data date
sqlite3 data/github-trending.db "SELECT date FROM repos_daily ORDER BY date DESC LIMIT 1;"

# View today's top 10
sqlite3 data/github-trending.db "SELECT rank, repo_name, stars FROM repos_daily WHERE date = '2026-01-30' ORDER BY rank LIMIT 10;"

# View repo details
sqlite3 data/github-trending.db "SELECT repo_name, summary, category FROM repos_details WHERE repo_name = 'anthropics/claude-code';"
```

---

## Credits

- [GitHub](https://github.com) - Data source
- [Anthropic](https://anthropic.com) - Claude AI
- [Resend](https://resend.com) - Email service

---

## License

[MIT](LICENSE)
