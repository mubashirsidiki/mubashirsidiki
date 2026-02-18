#!/usr/bin/env python3
"""
Script to fetch accurate GitHub stats and update README.md
Uses GitHub GraphQL API for precise data
"""
import os
import re
import requests
from datetime import datetime, timezone

# GitHub token from environment
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
USERNAME = 'mubashirsidiki'

def run_graphql_query(query):
    """Execute a GraphQL query against GitHub API"""
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Content-Type': 'application/json'
    }
    response = requests.post(
        'https://api.github.com/graphql',
        headers=headers,
        json={'query': query}
    )
    if response.status_code != 200:
        raise Exception(f"GraphQL query failed: {response.text}")
    return response.json()

def get_yearly_contributions():
    """Get contributions for each year"""
    current_year = datetime.now().year
    years = range(2021, current_year + 1)

    total_commits = 0
    total_private = 0

    for year in years:
        query = f'''
        query {{
          user(login: "{USERNAME}") {{
            contributionsCollection(from: "{year}-01-01T00:00:00Z", to: "{year}-12-31T23:59:59Z") {{
              totalCommitContributions
              restrictedContributionsCount
            }}
          }}
        }}
        '''
        result = run_graphql_query(query)
        data = result['data']['user']['contributionsCollection']
        total_commits += data['totalCommitContributions']
        total_private += data['restrictedContributionsCount']

    return total_commits, total_private

def get_user_stats():
    """Fetch comprehensive user statistics"""
    query = f'''
    query {{
      user(login: "{USERNAME}") {{
        createdAt
        followers {{ totalCount }}
        following {{ totalCount }}
        starredRepositories {{ totalCount }}
        repositories(first: 0, privacy: PUBLIC) {{ totalCount }}
        totalRepos: repositories {{ totalCount }}
      }}
    }}
    '''
    return run_graphql_query(query)['data']['user']

def get_pr_stats():
    """Fetch PR statistics using search API"""
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Total PRs
    total_resp = requests.get(
        f'https://api.github.com/search/issues?q=author:{USERNAME}+type:pr',
        headers=headers
    )
    total_prs = total_resp.json()['total_count']

    # Merged PRs
    merged_resp = requests.get(
        f'https://api.github.com/search/issues?q=author:{USERNAME}+type:pr+is:merged',
        headers=headers
    )
    merged_prs = merged_resp.json()['total_count']

    # Open PRs
    open_resp = requests.get(
        f'https://api.github.com/search/issues?q=author:{USERNAME}+type:pr+is:open',
        headers=headers
    )
    open_prs = open_resp.json()['total_count']

    return {
        'total': total_prs,
        'merged': merged_prs,
        'open': open_prs,
        'closed': total_prs - merged_prs - open_prs
    }

def get_issue_stats():
    """Fetch issue statistics using search API"""
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    # Total Issues
    total_resp = requests.get(
        f'https://api.github.com/search/issues?q=author:{USERNAME}+type:issue',
        headers=headers
    )
    total_issues = total_resp.json()['total_count']

    # Closed Issues
    closed_resp = requests.get(
        f'https://api.github.com/search/issues?q=author:{USERNAME}+type:issue+is:closed',
        headers=headers
    )
    closed_issues = closed_resp.json()['total_count']

    return {
        'total': total_issues,
        'closed': closed_issues,
        'open': total_issues - closed_issues
    }

def get_repo_stats():
    """Fetch repository statistics (stars, forks)"""
    headers = {
        'Authorization': f'Bearer {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }

    total_stars = 0
    total_forks = 0
    page = 1

    while True:
        resp = requests.get(
            f'https://api.github.com/users/{USERNAME}/repos?page={page}&per_page=100',
            headers=headers
        )
        repos = resp.json()

        if not repos:
            break

        for repo in repos:
            total_stars += repo.get('stargazers_count', 0)
            total_forks += repo.get('forks_count', 0)

        page += 1

    return {'stars': total_stars, 'forks': total_forks}

def calculate_streak():
    """Calculate current and longest streak from contribution calendar"""
    query = f'''
    query {{
      user(login: "{USERNAME}") {{
        contributionsCollection {{
          contributionCalendar {{
            weeks {{
              contributionDays {{
                date
                contributionCount
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    result = run_graphql_query(query)
    days = []

    for week in result['data']['user']['contributionsCollection']['contributionCalendar']['weeks']:
        for day in week['contributionDays']:
            days.append({
                'date': day['date'],
                'count': day['contributionCount']
            })

    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0

    # Sort by date
    days.sort(key=lambda x: x['date'])

    for i, day in enumerate(days):
        if day['count'] > 0:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0

    # Calculate current streak (from today backwards)
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    for day in reversed(days):
        if day['count'] > 0:
            current_streak += 1
        elif day['date'] < today:
            break

    return current_streak, longest_streak

def get_all_stats():
    """Fetch all statistics"""
    print("Fetching GitHub stats...")

    # Get yearly contributions
    print("  - Fetching yearly contributions...")
    public_commits, private_contributions = get_yearly_contributions()

    # Get user stats
    print("  - Fetching user stats...")
    user_stats = get_user_stats()

    # Get PR stats
    print("  - Fetching PR stats...")
    pr_stats = get_pr_stats()

    # Get issue stats
    print("  - Fetching issue stats...")
    issue_stats = get_issue_stats()

    # Get repo stats
    print("  - Fetching repo stats...")
    repo_stats = get_repo_stats()

    return {
        'total_contributions': public_commits + private_contributions,
        'public_commits': public_commits,
        'private_contributions': private_contributions,
        'total_prs': pr_stats['total'],
        'merged_prs': pr_stats['merged'],
        'open_prs': pr_stats['open'],
        'closed_prs': pr_stats['closed'],
        'merge_rate': round((pr_stats['merged'] / pr_stats['total']) * 100, 1) if pr_stats['total'] > 0 else 0,
        'total_issues': issue_stats['total'],
        'closed_issues': issue_stats['closed'],
        'open_issues': issue_stats['open'],
        'total_stars': repo_stats['stars'],
        'total_forks': repo_stats['forks'],
        'public_repos': user_stats['repositories']['totalCount'],
        'followers': user_stats['followers']['totalCount'],
        'following': user_stats['following']['totalCount'],
        'account_created': user_stats['createdAt'][:10]
    }

def update_readme(stats):
    """Update the README.md with accurate stats"""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create the stats section
    new_stats_section = f'''### <img src='https://media1.giphy.com/media/du3J3cXyzhj75IOgvA/giphy.gif' width='25' /> My Github Stats:

<p align="center">
<img src="https://github-readme-stats-sigma-five.vercel.app/api?username={USERNAME}&show_icons=true&title_color=ffc857&icon_color=8ac926&text_color=daf7dc&bg_color=151515&hide=issues,prs&count_private=true&include_all_commits=true" />
</p>

<p align="center">
<img src="https://github-readme-stats-sigma-five.vercel.app/api/top-langs/?username={USERNAME}&layout=compact&text_color=daf7dc&bg_color=151515&title_color=ffc857&hide=css,html" />
</p>

<p align="center">
<a href="https://git.io/streak-stats"><img src="https://github-readme-streak-stats.herokuapp.com/?user={USERNAME}&theme=dark" /></a>
</p>

<!-- START_GITHUB_STATS -->
<div align="center">

| 📊 **Metric** | 📈 **Count** |
|:-------------:|:------------:|
| **Total Contributions** | {stats['total_contributions']:,} |
| **Pull Requests** | {stats['total_prs']:,} ({stats['merged_prs']:,} merged · {stats['merge_rate']}% rate) |
| **Issues Opened** | {stats['total_issues']:,} ({stats['closed_issues']:,} closed) |
| **Stars Earned** | {stats['total_stars']:,} |
| **Public Repos** | {stats['public_repos']:,} |
| **Followers** | {stats['followers']:,} |

</div>
<!-- END_GITHUB_STATS -->'''

    # Pattern to match the stats section
    pattern = r"### <img src='https://media1\.giphy\.com/media/du3J3cXyzhj75IOgvA/giphy\.gif' width='25' /> My Github Stats:.*?(?=\n---\n\n<div align=\"center\">\s*\n\s*\n### ⏳ Year Progress)"

    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, new_stats_section + '\n\n', content, flags=re.DOTALL)
        print("✅ Updated existing stats section")
    else:
        # Try to find and update just the dynamic stats table
        table_pattern = r'<!-- START_GITHUB_STATS -->.*?<!-- END_GITHUB_STATS -->'
        if re.search(table_pattern, content, re.DOTALL):
            # Extract just the table part
            table_section = f'''<!-- START_GITHUB_STATS -->
<div align="center">

| 📊 **Metric** | 📈 **Count** |
|:-------------:|:------------:|
| **Total Contributions** | {stats['total_contributions']:,} |
| **Pull Requests** | {stats['total_prs']:,} ({stats['merged_prs']:,} merged · {stats['merge_rate']}% rate) |
| **Issues Opened** | {stats['total_issues']:,} ({stats['closed_issues']:,} closed) |
| **Stars Earned** | {stats['total_stars']:,} |
| **Public Repos** | {stats['public_repos']:,} |
| **Followers** | {stats['followers']:,} |

</div>
<!-- END_GITHUB_STATS -->'''
            content = re.sub(table_pattern, table_section, content, flags=re.DOTALL)
            print("✅ Updated dynamic stats table")
        else:
            print("⚠️ Could not find stats section to update")
            return False

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

def main():
    """Main function"""
    print("=" * 50)
    print("🚀 GitHub Stats Updater")
    print("=" * 50)

    if not GITHUB_TOKEN:
        print("❌ Error: GITHUB_TOKEN environment variable not set")
        return

    try:
        stats = get_all_stats()

        print("\n📊 Fetched Stats:")
        print(f"  Total Contributions: {stats['total_contributions']:,}")
        print(f"  Public Commits: {stats['public_commits']:,}")
        print(f"  Private Contributions: {stats['private_contributions']:,}")
        print(f"  Total PRs: {stats['total_prs']:,}")
        print(f"  Merged PRs: {stats['merged_prs']:,} ({stats['merge_rate']}%)")
        print(f"  Total Issues: {stats['total_issues']:,}")
        print(f"  Stars Earned: {stats['total_stars']:,}")
        print(f"  Public Repos: {stats['public_repos']:,}")
        print(f"  Followers: {stats['followers']:,}")

        if update_readme(stats):
            print("\n✅ README updated successfully!")
        else:
            print("\n⚠️ README update had issues")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
