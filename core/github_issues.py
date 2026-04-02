"""
GitHub Issues Integration

Fetches and prioritizes GitHub issues for evolution tasks.
Inspired by yoyo-evolve's community-driven approach.
"""

import os
import json
import urllib.request
import urllib.error


class GitHubIssuesFetcher:
    """Fetch and prioritize GitHub issues."""
    
    def __init__(self, repo_owner, repo_name, token=None):
        self.owner = repo_owner
        self.repo = repo_name
        self.token = token or os.environ.get('GITHUB_TOKEN', '')
        self.api_base = 'https://api.github.com'
    
    def fetch_issues(self, labels=None, state='open', limit=20):
        """Fetch issues with optional label filtering."""
        url = f'{self.api_base}/repos/{self.owner}/{self.repo}/issues'
        params = f'state={state}&per_page={limit}'
        
        if labels:
            params += f'&labels={",".join(labels)}'
        
        url += f'?{params}'
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        
        if self.token:
            headers['Authorization'] = f'token {self.token}'
        
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                issues = json.loads(response.read().decode('utf-8'))
                return self._prioritize_issues(issues)
        except Exception as e:
            print(f"[Mr. F] Failed to fetch issues: {e}")
            return []
    
    def _prioritize_issues(self, issues):
        """Prioritize issues by votes and labels."""
        prioritized = []
        
        for issue in issues:
            # Skip pull requests
            if 'pull_request' in issue:
                continue
            
            # Calculate priority score
            score = 0
            
            # Reactions scoring
            reactions = issue.get('reactions', {})
            score += reactions.get('+1', 0) * 2
            score += reactions.get('heart', 0) * 3
            score -= reactions.get('-1', 0) * 5  # Downvotes hurt
            
            # Label scoring
            labels = [l['name'] for l in issue.get('labels', [])]
            if 'bug' in labels:
                score += 10
            if 'agent-self' in labels:
                score += 8
            if 'agent-input' in labels:
                score += 6
            if 'help wanted' in labels:
                score += 5
            if 'enhancement' in labels:
                score += 3
            
            # Comments indicate interest
            score += issue.get('comments', 0)
            
            prioritized.append({
                'number': issue['number'],
                'title': issue['title'],
                'body': issue['body'] or '',
                'labels': labels,
                'score': score,
                'url': issue['html_url'],
                'created_at': issue['created_at'],
                'comments': issue.get('comments', 0)
            })
        
        # Sort by score descending
        prioritized.sort(key=lambda x: x['score'], reverse=True)
        return prioritized
    
    def fetch_pending_replies(self):
        """Fetch issues pending human reply."""
        # This would check for issues where bot replied but human hasn't
        # For now, return empty list
        return []
    
    def comment_on_issue(self, issue_number, comment):
        """Post comment to GitHub issue."""
        if not self.token:
            print("[Mr. F] No GitHub token, cannot comment")
            return False
        
        url = f'{self.api_base}/repos/{self.owner}/{self.repo}/issues/{issue_number}/comments'
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.token}',
            'Content-Type': 'application/json'
        }
        
        data = json.dumps({'body': comment}).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as response:
                print(f"[Mr. F] Commented on issue #{issue_number}")
                return True
        except Exception as e:
            print(f"[Mr. F] Failed to comment: {e}")
            return False
    
    def create_issue(self, title, body, labels=None):
        """Create new GitHub issue."""
        if not self.token:
            print("[Mr. F] No GitHub token, cannot create issue")
            return False
        
        url = f'{self.api_base}/repos/{self.owner}/{self.repo}/issues'
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'token {self.token}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'title': title,
            'body': body,
            'labels': labels or []
        }
        
        data = json.dumps(payload).encode('utf-8')
        
        try:
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"[Mr. F] Created issue #{result['number']}: {title}")
                return True
        except Exception as e:
            print(f"[Mr. F] Failed to create issue: {e}")
            return False


class IssueDrivenEvolution:
    """Evolution driven by GitHub issues."""
    
    def __init__(self, runner):
        self.runner = runner
        self.fetcher = GitHubIssuesFetcher(
            'UnTamed-Fury',
            'mr._F',
            os.environ.get('GITHUB_TOKEN', '')
        )
    
    def get_next_task(self):
        """Get next task from prioritized issues."""
        # Fetch issues with agent-related labels
        issues = self.fetcher.fetch_issues(
            labels=['agent-self', 'agent-input', 'bug', 'enhancement'],
            limit=10
        )
        
        if not issues:
            return None
        
        # Return highest priority issue
        return issues[0]
    
    def format_task_for_agent(self, issue):
        """Format issue as task for agent."""
        return f"""
## Task from GitHub Issue #{issue['number']}

**Title:** {issue['title']}
**Priority Score:** {issue['score']}
**Labels:** {', '.join(issue['labels'])}

**Description:**
{issue['body']}

**URL:** {issue['url']}

Please address this issue in your next evolution step.
"""
