#!/usr/bin/env python3
"""
NEXhome GitHub Issue Monitor

A script to help monitor and track issues in the nexhome-org/nexhome-homeassistant-component repository.
This script provides summaries, filtering, and basic analytics for issue management.

Usage:
    python3 issue_monitor.py [options]

Requirements:
    pip install requests

Note: For API rate limiting, consider setting GITHUB_TOKEN environment variable.
"""

import requests
import json
import sys
from datetime import datetime, timedelta
from collections import defaultdict
import argparse
import os

class GitHubIssueMonitor:
    def __init__(self, owner="nexhome-org", repo="nexhome-homeassistant-component"):
        self.owner = owner
        self.repo = repo
        self.base_url = "https://api.github.com/repos"
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Add authentication if token is available
        github_token = os.environ.get("GITHUB_TOKEN")
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def get_issues(self, state="all", per_page=100):
        """Fetch issues from GitHub API."""
        url = f"{self.base_url}/{self.owner}/{self.repo}/issues"
        params = {
            "state": state,
            "per_page": per_page,
            "sort": "updated",
            "direction": "desc"
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching issues: {e}")
            return []

    def categorize_issues(self, issues):
        """Categorize issues by type and priority."""
        categories = {
            "critical": [],
            "bugs": [],
            "features": [],
            "config": [],
            "documentation": []
        }
        
        critical_keywords = ["loading", "fail", "error", "crash", "sync", "not work"]
        bug_keywords = ["bug", "issue", "problem", "delay", "异常", "失败"]
        feature_keywords = ["feature", "request", "support", "add", "计划", "接入"]
        config_keywords = ["config", "setup", "install", "IOTID", "端口", "配置"]
        doc_keywords = ["document", "readme", "help", "怎么", "如何"]
        
        for issue in issues:
            title_lower = issue["title"].lower()
            body_lower = issue.get("body", "").lower()
            text = f"{title_lower} {body_lower}"
            
            # Skip pull requests
            if "pull_request" in issue:
                continue
                
            categorized = False
            
            # Critical issues first
            if any(keyword in text for keyword in critical_keywords):
                categories["critical"].append(issue)
                categorized = True
            elif any(keyword in text for keyword in bug_keywords):
                categories["bugs"].append(issue)
                categorized = True
            elif any(keyword in text for keyword in feature_keywords):
                categories["features"].append(issue)
                categorized = True
            elif any(keyword in text for keyword in config_keywords):
                categories["config"].append(issue)
                categorized = True
            elif any(keyword in text for keyword in doc_keywords):
                categories["documentation"].append(issue)
                categorized = True
                
            if not categorized:
                categories["bugs"].append(issue)  # Default to bugs
        
        return categories

    def get_issue_age(self, issue):
        """Calculate issue age in days."""
        created = datetime.strptime(issue["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        return (datetime.now() - created).days

    def format_issue_summary(self, issue, show_details=False):
        """Format a single issue for display."""
        age = self.get_issue_age(issue)
        state_icon = "🟢" if issue["state"] == "open" else "✅"
        
        summary = f"{state_icon} #{issue['number']} - {issue['title']}"
        summary += f" (👤 {issue['user']['login']}, 📅 {age}d ago"
        
        if issue["comments"] > 0:
            summary += f", 💬 {issue['comments']}"
        
        summary += ")"
        
        if show_details and issue.get("body"):
            body_preview = issue["body"][:200].replace("\n", " ").strip()
            if len(issue["body"]) > 200:
                body_preview += "..."
            summary += f"\n    📝 {body_preview}"
        
        return summary

    def print_report(self, categories, show_details=False):
        """Print formatted issue report."""
        print("=" * 80)
        print(f"NEXhome GitHub Issues Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)
        
        total_open = sum(len([i for i in cat if i["state"] == "open"]) for cat in categories.values())
        total_closed = sum(len([i for i in cat if i["state"] == "closed"]) for cat in categories.values())
        
        print(f"📊 Summary: {total_open} open, {total_closed} closed issues")
        print()
        
        category_names = {
            "critical": "🔴 Critical Issues",
            "bugs": "🐛 Bug Reports", 
            "features": "✨ Feature Requests",
            "config": "⚙️  Configuration Issues",
            "documentation": "📚 Documentation"
        }
        
        for category, issues in categories.items():
            if not issues:
                continue
                
            open_issues = [i for i in issues if i["state"] == "open"]
            closed_issues = [i for i in issues if i["state"] == "closed"]
            
            print(f"\n{category_names[category]} ({len(open_issues)} open, {len(closed_issues)} closed)")
            print("-" * 60)
            
            # Show open issues first
            for issue in sorted(open_issues, key=lambda x: x["number"], reverse=True):
                print(f"  {self.format_issue_summary(issue, show_details)}")
            
            # Then closed issues if requested
            if show_details and closed_issues:
                print("  Recently Closed:")
                for issue in sorted(closed_issues[:3], key=lambda x: x["updated_at"], reverse=True):
                    print(f"    {self.format_issue_summary(issue)}")

    def get_statistics(self, issues):
        """Generate issue statistics."""
        stats = {
            "total": len(issues),
            "open": len([i for i in issues if i["state"] == "open"]),
            "closed": len([i for i in issues if i["state"] == "closed"]),
            "avg_age_open": 0,
            "oldest_open": None,
            "most_comments": None,
            "recent_activity": 0
        }
        
        open_issues = [i for i in issues if i["state"] == "open"]
        if open_issues:
            ages = [self.get_issue_age(i) for i in open_issues]
            stats["avg_age_open"] = sum(ages) / len(ages)
            stats["oldest_open"] = max(open_issues, key=self.get_issue_age)
            
        if issues:
            stats["most_comments"] = max(issues, key=lambda x: x["comments"])
            
        # Count issues with activity in last 30 days
        cutoff = datetime.now() - timedelta(days=30)
        stats["recent_activity"] = len([
            i for i in issues 
            if datetime.strptime(i["updated_at"], "%Y-%m-%dT%H:%M:%SZ") > cutoff
        ])
        
        return stats

def main():
    parser = argparse.ArgumentParser(description="Monitor NEXhome GitHub issues")
    parser.add_argument("--details", "-d", action="store_true", 
                       help="Show detailed issue descriptions")
    parser.add_argument("--stats", "-s", action="store_true",
                       help="Show detailed statistics")
    parser.add_argument("--state", choices=["open", "closed", "all"], 
                       default="all", help="Filter by issue state")
    
    args = parser.parse_args()
    
    monitor = GitHubIssueMonitor()
    print("Fetching issues from GitHub...")
    
    issues = monitor.get_issues(state=args.state)
    if not issues:
        print("No issues found or API error occurred.")
        return 1
    
    categories = monitor.categorize_issues(issues)
    monitor.print_report(categories, show_details=args.details)
    
    if args.stats:
        print("\n" + "=" * 80)
        print("📈 Detailed Statistics")
        print("=" * 80)
        stats = monitor.get_statistics(issues)
        
        print(f"Total Issues: {stats['total']}")
        print(f"Open: {stats['open']}, Closed: {stats['closed']}")
        print(f"Average age of open issues: {stats['avg_age_open']:.1f} days")
        
        if stats['oldest_open']:
            age = monitor.get_issue_age(stats['oldest_open'])
            print(f"Oldest open issue: #{stats['oldest_open']['number']} ({age} days old)")
            
        if stats['most_comments']:
            print(f"Most discussed: #{stats['most_comments']['number']} "
                 f"({stats['most_comments']['comments']} comments)")
            
        print(f"Recent activity (30 days): {stats['recent_activity']} issues")
    
    print(f"\n💡 Tip: Set GITHUB_TOKEN environment variable to increase API rate limits.")
    return 0

if __name__ == "__main__":
    sys.exit(main())