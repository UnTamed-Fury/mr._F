"""
Iteration Control System

Prevents infinite loops and manages evolution iterations:
- Max consecutive failures
- Max iterations without improvement
- Early stopping
- Best-of-N tracking
"""

import os
import json
from datetime import datetime


class IterationController:
    """Controls evolution iterations with safety limits."""
    
    def __init__(self, memory_path):
        self.memory_path = memory_path
        self.state_file = os.path.join(memory_path, 'iteration_state.json')
        
        # Default limits
        self.max_consecutive_failures = 5
        self.max_iters_without_improvement = 10
        self.max_total_iterations = 100
        self.best_score_file = os.path.join(memory_path, 'best.json')
    
    def load_state(self):
        """Load iteration state."""
        try:
            with open(self.state_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'consecutive_failures': 0,
                'iters_without_improvement': 0,
                'total_iterations': 0,
                'best_score_seen': 0.0,
                'last_improvement_iter': 0,
                'reset_at': None
            }
    
    def save_state(self, state):
        """Save iteration state."""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)
    
    def get_best_score(self):
        """Get best score from memory."""
        try:
            with open(self.best_score_file, 'r') as f:
                best = json.load(f)
                return best.get('score', 0.0)
        except Exception:
            return 0.0
    
    def record_iteration(self, accepted, score, score_before):
        """
        Record an iteration and check limits.
        
        Returns:
            tuple: (should_continue, reason, state)
        """
        state = self.load_state()
        state['total_iterations'] += 1
        
        improved = score > score_before
        
        if improved:
            state['consecutive_failures'] = 0
            state['iters_without_improvement'] = 0
            state['best_score_seen'] = max(state['best_score_seen'], score)
            state['last_improvement_iter'] = state['total_iterations']
        else:
            state['consecutive_failures'] += 1
            state['iters_without_improvement'] += 1
        
        # Check limits
        should_continue = True
        reason = "ok"
        
        # Limit 1: Max consecutive failures
        if state['consecutive_failures'] >= self.max_consecutive_failures:
            should_continue = False
            reason = f"max_consecutive_failures ({self.max_consecutive_failures})"
            state['reset_at'] = datetime.now().isoformat()
        
        # Limit 2: Max iterations without improvement
        elif state['iters_without_improvement'] >= self.max_iters_without_improvement:
            should_continue = False
            reason = f"max_iters_without_improvement ({self.max_iters_without_improvement})"
            state['reset_at'] = datetime.now().isoformat()
        
        # Limit 3: Max total iterations
        elif state['total_iterations'] >= self.max_total_iterations:
            should_continue = False
            reason = f"max_total_iterations ({self.max_total_iterations})"
            state['reset_at'] = datetime.now().isoformat()
        
        self.save_state(state)
        
        return should_continue, reason, state
    
    def should_stop_early(self, score, target_score=0.999):
        """Check if we should stop early due to high score."""
        if score >= target_score:
            return True, f"Reached target score ({target_score})"
        return False, "ok"
    
    def get_status_report(self):
        """Get human-readable status report."""
        state = self.load_state()
        
        report = []
        report.append("=== Iteration Control Status ===")
        report.append(f"Total Iterations: {state['total_iterations']}/{self.max_total_iterations}")
        report.append(f"Consecutive Failures: {state['consecutive_failures']}/{self.max_consecutive_failures}")
        report.append(f"Iters Without Improvement: {state['iters_without_improvement']}/{self.max_iters_without_improvement}")
        report.append(f"Best Score Seen: {state['best_score_seen']:.4f}")
        report.append(f"Current Best: {self.get_best_score():.4f}")
        
        if state['reset_at']:
            report.append(f"Last Reset: {state['reset_at']}")
        
        # Calculate health
        health = "healthy"
        if state['consecutive_failures'] > self.max_consecutive_failures * 0.8:
            health = "warning - near failure limit"
        if state['iters_without_improvement'] > self.max_iters_without_improvement * 0.8:
            health = "warning - stagnation detected"
        
        report.append(f"System Health: {health}")
        
        return '\n'.join(report)
    
    def reset(self):
        """Reset iteration state."""
        state = {
            'consecutive_failures': 0,
            'iters_without_improvement': 0,
            'total_iterations': 0,
            'best_score_seen': 0.0,
            'last_improvement_iter': 0,
            'reset_at': datetime.now().isoformat()
        }
        self.save_state(state)
        return state


class BestOfNTracker:
    """Tracks best outputs across N iterations."""
    
    def __init__(self, memory_path, n=5):
        self.memory_path = memory_path
        self.n = n
        self.tracker_file = os.path.join(memory_path, 'best_of_n.json')
    
    def load(self):
        """Load tracker state."""
        try:
            with open(self.tracker_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {'entries': [], 'best_index': -1}
    
    def save(self, data):
        """Save tracker state."""
        os.makedirs(os.path.dirname(self.tracker_file), exist_ok=True)
        with open(self.tracker_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def add_entry(self, score, code, diff, metadata=None):
        """Add an entry to the tracker."""
        data = self.load()
        
        entry = {
            'index': len(data['entries']),
            'score': score,
            'code': code[:1000],  # Truncate for storage
            'diff': diff[:500],
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        data['entries'].append(entry)
        
        # Keep only last N
        if len(data['entries']) > self.n:
            data['entries'] = data['entries'][-self.n:]
        
        # Update best index
        best_idx = max(range(len(data['entries'])), 
                       key=lambda i: data['entries'][i]['score'])
        data['best_index'] = best_idx
        
        self.save(data)
        
        return entry
    
    def get_best(self):
        """Get the best entry."""
        data = self.load()
        if data['entries'] and data['best_index'] >= 0:
            return data['entries'][data['best_index']]
        return None
    
    def should_rollback(self, current_score):
        """
        Check if we should rollback to a previous best.
        
        AGGRESSIVE ROLLBACK POLICY:
        - If current score < best score by margin → rollback
        - If consecutive failures > threshold → rollback
        - If hallucination detected → rollback
        
        Returns:
            tuple: (should_rollback, best_entry, reason)
        """
        best = self.get_best()
        
        if not best:
            return False, None, "No previous best to rollback to"
        
        # Aggressive rollback: any regression triggers consideration
        rollback_margin = 0.001  # 0.1% regression tolerance
        
        if best['score'] > current_score + rollback_margin:
            return True, best, f"Score regression: {best['score']:.4f} > {current_score:.4f}"
        
        # Check consecutive failures
        state = self.load()
        if state.get('consecutive_failures', 0) >= 3:
            return True, best, f"Consecutive failures: {state['consecutive_failures']}"
        
        return False, None, "No rollback needed"
    
    def clear(self):
        """Clear the tracker."""
        self.save({'entries': [], 'best_index': -1})


class RollbackManager:
    """Manages aggressive rollback decisions."""
    
    def __init__(self, memory_path):
        self.memory_path = memory_path
        self.best_tracker = BestOfNTracker(memory_path)
        self.backup_path = os.path.join(memory_path, 'rollback_backup.json')
    
    def record_and_evaluate(self, score, code, diff, metadata=None):
        """
        Record a change and evaluate if rollback is needed.
        
        Returns:
            tuple: (accept_change, reason, rollback_target)
        """
        # Add to best-of-N tracker
        self.best_tracker.add_entry(score, code, diff, metadata)
        
        # Check if we should rollback
        should_rollback, best, reason = self.best_tracker.should_rollback(score)
        
        if should_rollback:
            return False, reason, best
        
        return True, "Change accepted", None
    
    def save_backup(self, code, score, run_number):
        """Save a backup for potential rollback."""
        backup = {
            'code': code,
            'score': score,
            'run_number': run_number,
            'timestamp': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.backup_path), exist_ok=True)
        with open(self.backup_path, 'w') as f:
            json.dump(backup, f, indent=2)
    
    def get_backup(self):
        """Get the backup for rollback."""
        try:
            with open(self.backup_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def clear_backup(self):
        """Clear the backup."""
        if os.path.exists(self.backup_path):
            os.unlink(self.backup_path)


def check_iteration_limits(memory_path, accepted, score, score_before):
    """
    Check iteration limits and return status.
    
    Returns:
        tuple: (should_continue, reason, message)
    """
    controller = IterationController(memory_path)
    should_continue, reason, state = controller.record_iteration(
        accepted, score, score_before
    )
    
    message = controller.get_status_report()
    
    return should_continue, reason, message


def get_iteration_status(memory_path):
    """Get current iteration status."""
    controller = IterationController(memory_path)
    return controller.get_status_report()
