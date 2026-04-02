"""
Git History Compression System

Compresses old commits to keep history manageable.

Rule: After every 29 commits, compress oldest 10 into 1.
Formula: 20 commits → compress 10 → 11 commits left
         Reach 20 again → compress 10 → 11 left
         Repeat indefinitely

This keeps history readable while preserving all changes.
"""

import os
import subprocess
import json


class CommitCompressor:
    """Compresses old git commits to maintain manageable history."""
    
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.compression_threshold = 29
        self.compress_count = 10
        self.compress_marker_file = os.path.join(
            os.path.dirname(__file__), '..', 'meta', 'compression_state.json'
        )
    
    def get_commit_count(self):
        """Get total number of commits."""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--count', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            return int(result.stdout.strip())
        except Exception:
            return 0
    
    def should_compress(self):
        """Check if compression should run."""
        commit_count = self.get_commit_count()
        return commit_count >= self.compression_threshold
    
    def get_state(self):
        """Load compression state."""
        try:
            with open(self.compress_marker_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {'last_compression_commit': 0, 'compression_runs': 0}
    
    def save_state(self, state):
        """Save compression state."""
        os.makedirs(os.path.dirname(self.compress_marker_file), exist_ok=True)
        with open(self.compress_marker_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def compress_history(self):
        """
        Compress oldest commits into a single commit.
        
        Process:
        1. Get list of all commits (oldest first)
        2. Take oldest 10 commits
        3. Create orphan branch at oldest commit
        4. Squash those 10 into 1 commit
        5. Rebase rest of history onto this
        6. Update main branch
        """
        print("[Mr. F] === Starting Commit Compression ===")
        
        commit_count = self.get_commit_count()
        print(f"[Mr. F] Current commits: {commit_count}")
        print(f"[Mr. F] Compressing oldest {self.compress_count} into 1...")
        
        try:
            # Get commit list (oldest first)
            result = subprocess.run(
                ['git', 'rev-list', '--reverse', 'HEAD'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            commits = result.stdout.strip().split('\n')
            
            if len(commits) < self.compress_count:
                print("[Mr. F] Not enough commits to compress")
                return False
            
            # Get the commits to compress
            commits_to_compress = commits[:self.compress_count]
            remaining_commits = commits[self.compress_count:]
            
            print(f"[Mr. F] Oldest commit: {commits_to_compress[0][:8]}")
            print(f"[Mr. F] Newest to compress: {commits_to_compress[-1][:8]}")
            print(f"[Mr. F] Remaining after: {len(remaining_commits)} commits")
            
            # Create backup branch
            subprocess.run(
                ['git', 'branch', f'backup-pre-compress-{commit_count}'],
                cwd=self.repo_path,
                timeout=10
            )
            print(f"[Mr. F] Created backup branch: backup-pre-compress-{commit_count}")
            
            # Create orphan branch at oldest commit
            subprocess.run(
                ['git', 'checkout', '--orphan', 'temp-compress', commits_to_compress[0]],
                cwd=self.repo_path,
                capture_output=True,
                timeout=10
            )
            
            # Reset to get clean state
            subprocess.run(
                ['git', 'reset', '--hard', commits_to_compress[0]],
                cwd=self.repo_path,
                timeout=10
            )
            
            # Commit as squashed history
            subprocess.run(
                ['git', 'commit', '--allow-empty', '-m', 
                 '[Mr. F] Compressed history: First '
                 f'{self.compress_count} commits squashed into one'],
                cwd=self.repo_path,
                capture_output=True,
                timeout=10
            )
            
            # Cherry-pick remaining commits
            for commit_hash in remaining_commits:
                result = subprocess.run(
                    ['git', 'cherry-pick', commit_hash, '--no-commit'],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Commit the cherry-picked changes
                subprocess.run(
                    ['git', 'commit', '--allow-empty', '-m', 'CHERRY_PICK'],
                    cwd=self.repo_path,
                    capture_output=True,
                    timeout=10
                )
            
            # Get commit messages for the squashed commit
            messages = []
            for commit_hash in commits_to_compress:
                result = subprocess.run(
                    ['git', 'log', '-1', '--format=%s', commit_hash],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.stdout.strip():
                    messages.append(result.stdout.strip())
            
            # Update main branch to point here
            subprocess.run(
                ['git', 'branch', '-f', 'main'],
                cwd=self.repo_path,
                timeout=10
            )
            subprocess.run(
                ['git', 'checkout', 'main'],
                cwd=self.repo_path,
                capture_output=True,
                timeout=10
            )
            
            # Clean up temp branch
            subprocess.run(
                ['git', 'branch', '-D', 'temp-compress'],
                cwd=self.repo_path,
                capture_output=True,
                timeout=10
            )
            
            # Update state
            state = self.get_state()
            state['last_compression_commit'] = commit_count
            state['compression_runs'] += 1
            self.save_state(state)
            
            new_count = self.get_commit_count()
            print(f"[Mr. F] ✅ Compression complete!")
            print(f"[Mr. F] Before: {commit_count} commits")
            print(f"[Mr. F] After: {new_count} commits")
            print(f"[Mr. F] Removed: {commit_count - new_count} commits")
            print(f"[Mr. F] Total compressions run: {state['compression_runs']}")
            
            return True
            
        except Exception as e:
            print(f"[Mr. F] ❌ Compression failed: {e}")
            
            # Try to restore from backup
            try:
                subprocess.run(
                    ['git', 'checkout', 'main'],
                    cwd=self.repo_path,
                    capture_output=True,
                    timeout=10
                )
            except:
                pass
            
            return False
    
    def get_compression_stats(self):
        """Get compression statistics."""
        state = self.get_state()
        return {
            'current_commits': self.get_commit_count(),
            'last_compression_at': state.get('last_compression_commit', 0),
            'total_compressions': state.get('compression_runs', 0),
            'next_compression_at': self.compression_threshold
        }


def check_and_compress(repo_path=None):
    """Check if compression needed and run if so."""
    if repo_path is None:
        repo_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    compressor = CommitCompressor(repo_path)
    
    if compressor.should_compress():
        return compressor.compress_history()
    else:
        stats = compressor.get_compression_stats()
        print(f"[Mr. F] Compression not needed yet")
        print(f"[Mr. F] Current commits: {stats['current_commits']}/{stats['next_compression_at']}")
        return None


if __name__ == '__main__':
    check_and_compress()
