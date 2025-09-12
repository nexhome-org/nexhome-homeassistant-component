# NEXhome Tools

This directory contains utility tools for managing and monitoring the NEXhome Home Assistant component project.

## issue_monitor.py

A Python script for monitoring GitHub issues in the repository.

### Features

- **Categorized Issue Reporting**: Automatically categorizes issues into:
  - 🔴 Critical Issues (loading failures, crashes, sync problems)
  - 🐛 Bug Reports (general bugs and problems)
  - ✨ Feature Requests (new functionality requests)
  - ⚙️ Configuration Issues (setup and configuration problems)
  - 📚 Documentation (documentation related issues)

- **Statistics**: Provides detailed statistics including:
  - Total/open/closed issue counts
  - Average age of open issues
  - Most discussed issues
  - Recent activity tracking

- **Flexible Display**: Options for detailed or summary views

### Requirements

```bash
pip install requests
```

### Usage

```bash
# Basic usage - show all issues
python3 tools/issue_monitor.py

# Show detailed descriptions
python3 tools/issue_monitor.py --details

# Show statistics
python3 tools/issue_monitor.py --stats

# Filter by state
python3 tools/issue_monitor.py --state open
python3 tools/issue_monitor.py --state closed

# Combined options
python3 tools/issue_monitor.py --details --stats --state open
```

### GitHub API Authentication

To avoid rate limiting, set a GitHub personal access token:

```bash
export GITHUB_TOKEN=your_github_token_here
python3 tools/issue_monitor.py
```

### Example Output

```
================================================================================
NEXhome GitHub Issues Report - 2025-09-12 06:27:45
================================================================================
📊 Summary: 6 open, 7 closed issues

🔴 Critical Issues (3 open, 0 closed)
------------------------------------------------------------
  🟢 #11 - 没有更新，没有任何操作，突然某一天就变成加载失败是怎么回事 (👤 arnold3115, 📅 82d ago, 💬 1)
  🟢 #8 - v1.1.10版本，接入HA后，会导致中控4寸屏主机和开关面板状态同步异常 (👤 vanscer, 📅 167d ago, 💬 8)
  🟢 #6 - 开关状态不能正常更新 (👤 wujieJaden, 📅 257d ago, 💬 1)
```

### Automation Ideas

- Set up as a cron job for regular monitoring
- Integrate with notification systems for critical issue alerts
- Generate weekly/monthly reports for project management
- Track issue resolution times and trends

### Contributing

Feel free to extend the script with additional features like:
- Issue prioritization algorithms
- Integration with project management tools
- Automated issue labeling suggestions
- Performance tracking metrics