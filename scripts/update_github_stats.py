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

    # Get language stats
    print("  - Fetching language stats...")
    language_stats = get_language_stats()

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
        'account_created': user_stats['createdAt'][:10],
        'languages': language_stats
    }

def get_language_stats():
    """Fetch accurate language statistics excluding forks and bloated files"""
    # Languages to exclude (not real code or bloated)
    EXCLUDED_LANGUAGES = {
        'Jupyter Notebook', 'HTML', 'CSS', 'SCSS', 'Dockerfile',
        'Shell', 'PowerShell', 'Batchfile', 'Makefile', 'Roff',
        'HCL', 'XSLT', 'MDX', 'Game Maker Language'
    }

    # Repos to exclude (forks with bloated data)
    EXCLUDED_REPOS = {
        'langchain', 'AgentPro', 'datasharing', 'jackettio',
        'lstm-siamese-text-similarity', 'datasciencecoursera',
        'certifications_work', 'clone-product-ai-platform',
        'prac_clone-product-ai-platform', '2_clone-product-ai-platform',
        'script_clone-product-ai-platform', 'avi_ai_platform'
    }

    query = f'''
    query {{
      user(login: "{USERNAME}") {{
        repositories(first: 100, ownerAffiliations: OWNER) {{
          nodes {{
            name
            isFork
            languages(first: 50) {{
              edges {{
                size
                node {{
                  name
                  color
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''
    result = run_graphql_query(query)

    # Custom colors for better distinction
    CUSTOM_COLORS = {
        'Python': '3776AB',       # Blue
        'TypeScript': '3178C6',   # Microsoft blue
        'JavaScript': 'F7DF1E',   # Yellow
        'C#': '512BD4',           # Purple
        'Bicep': '519ABA',        # Azure blue
        'R': '276DC3',            # Darker blue
    }

    lang_totals = {}

    for repo in result['data']['user']['repositories']['nodes']:
        # Skip excluded repos and forks
        if repo['name'] in EXCLUDED_REPOS or repo['isFork']:
            continue

        for edge in repo['languages']['edges']:
            lang_name = edge['node']['name']
            if lang_name in EXCLUDED_LANGUAGES:
                continue

            if lang_name not in lang_totals:
                color = edge['node']['color']
                # Use custom color if defined, otherwise use GitHub's color
                lang_totals[lang_name] = {
                    'bytes': 0,
                    'color': CUSTOM_COLORS.get(lang_name, color.lstrip('#') if color else '888888')
                }
            lang_totals[lang_name]['bytes'] += edge['size']

    # Calculate percentages
    total_bytes = sum(l['bytes'] for l in lang_totals.values())

    if total_bytes == 0:
        return []

    # Sort by bytes and get top languages
    sorted_langs = sorted(lang_totals.items(), key=lambda x: -x[1]['bytes'])[:6]

    languages = []
    for name, data in sorted_langs:
        percentage = round((data['bytes'] / total_bytes) * 100, 1)
        if percentage >= 1:  # Only include languages with >= 1%
            languages.append({
                'name': name,
                'percentage': percentage,
                'color': data['color']
            })

    return languages

def update_readme(stats):
    """Update the README.md with accurate stats"""
    readme_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'README.md')

    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Generate language badges
    lang_badges = ""
    if stats.get('languages'):
        lang_badges = '\n<p align="center">\n'
        for lang in stats['languages']:
            # Use URL encoding for special characters
            lang_name = lang['name'].replace('#', '%23').replace(' ', '%20')
            lang_badges += f'  <img src="https://img.shields.io/badge/{lang["name"]}-{lang["percentage"]}%25-{lang["color"]}?style=flat-square&labelColor=151515&logo={lang["name"].lower().replace("#", "-")}&logoColor=white" alt="{lang["name"]}" />\n'
        lang_badges += '</p>'

    # Create the dynamic stats badges section (no Vercel dependency for stats)
    new_stats_section = f'''<!-- START_GITHUB_STATS -->
<p align="center">
  <img src="https://img.shields.io/badge/🎯_Total_Contributions-{stats['total_contributions']:,}-8ac926?style=for-the-badge&labelColor=151515&color=151515" alt="Total Contributions" />
  <img src="https://img.shields.io/badge/⭐_Stars_Earned-{stats['total_stars']:,}-ffc857?style=for-the-badge&labelColor=151515&color=151515" alt="Stars" />
  <img src="https://img.shields.io/badge/📁_Public_Repos-{stats['public_repos']:,}-58a6ff?style=for-the-badge&labelColor=151515&color=151515" alt="Repos" />
</p>

<p align="center">
  <img src="https://img.shields.io/badge/🔄_Pull_Requests-{stats['total_prs']:,}-238636?style=for-the-badge&labelColor=151515&color=151515" alt="PRs" />
  <img src="https://img.shields.io/badge/✅_Merged-{stats['merged_prs']:,}_({stats['merge_rate']}%25)-238636?style=for-the-badge&labelColor=151515&color=151515" alt="Merged" />
  <img src="https://img.shields.io/badge/❗_Issues-{stats['total_issues']:,}-f0883e?style=for-the-badge&labelColor=151515&color=151515" alt="Issues" />
  <img src="https://img.shields.io/badge/👥_Followers-{stats['followers']:,}-a371f7?style=for-the-badge&labelColor=151515&color=151515" alt="Followers" />
</p>
{lang_badges}
<!-- END_GITHUB_STATS -->'''

    # Pattern to match the stats section
    stats_pattern = r'<!-- START_GITHUB_STATS -->.*?<!-- END_GITHUB_STATS -->'

    if re.search(stats_pattern, content, re.DOTALL):
        content = re.sub(stats_pattern, new_stats_section, content, flags=re.DOTALL)
        print("✅ Updated existing stats section")
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

        if stats.get('languages'):
            print("\n🔤 Top Languages:")
            for lang in stats['languages']:
                print(f"    {lang['name']}: {lang['percentage']}%")

        if update_readme(stats):
            print("\n✅ README updated successfully!")
        else:
            print("\n⚠️ README update had issues")

    except Exception as e:
        print(f"❌ Error: {e}")
        raise

if __name__ == "__main__":
    main()
