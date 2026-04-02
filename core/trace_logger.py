"""
Comprehensive Logging and Traceability System

Tracks every evolution iteration with detailed metrics:
- Full iteration history
- Score progression
- Change tracking
- Performance metrics
- Comparison tools
"""

import os
import json
import csv
from datetime import datetime


class EvolutionLogger:
    """Comprehensive logging for evolution tracking."""
    
    def __init__(self, runs_path, memory_path):
        self.runs_path = runs_path
        self.memory_path = memory_path
        self.trace_path = os.path.join(runs_path, 'trace')
        self.metrics_file = os.path.join(self.trace_path, 'metrics.csv')
        self.history_file = os.path.join(self.trace_path, 'history.json')
    
    def ensure_dirs(self):
        """Ensure trace directories exist."""
        os.makedirs(self.trace_path, exist_ok=True)
    
    def log_iteration(self, iteration_data):
        """
        Log a complete iteration with all metrics.
        
        Args:
            iteration_data: dict with iteration details
        """
        self.ensure_dirs()
        
        # Add timestamp
        iteration_data['timestamp'] = datetime.now().isoformat()
        
        # Append to history
        history = self.load_history()
        history['iterations'].append(iteration_data)
        history['last_updated'] = iteration_data['timestamp']
        self.save_history(history)
        
        # Append to metrics CSV
        self.append_to_metrics(iteration_data)
    
    def load_history(self):
        """Load iteration history."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'iterations': [],
                'started_at': datetime.now().isoformat(),
                'last_updated': None
            }
    
    def save_history(self, history):
        """Save iteration history."""
        self.ensure_dirs()
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def append_to_metrics(self, data):
        """Append metrics to CSV."""
        file_exists = os.path.exists(self.metrics_file)
        
        with open(self.metrics_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'timestamp', 'run_number', 'score_before', 'score_after',
                'score_delta', 'status', 'lines_changed', 'execution_time',
                'test_pass_rate', 'code_quality', 'safety_score',
                'improvement_score', 'hallucination_penalty', 'error'
            ])
            
            if not file_exists:
                writer.writeheader()
            
            writer.writerow({
                'timestamp': data.get('timestamp', ''),
                'run_number': data.get('run_number', 0),
                'score_before': data.get('score_before', 0),
                'score_after': data.get('score_after', 0),
                'score_delta': data.get('score_delta', 0),
                'status': data.get('status', ''),
                'lines_changed': data.get('lines_changed', 0),
                'execution_time': data.get('execution_time', 0),
                'test_pass_rate': data.get('test_pass_rate', 0),
                'code_quality': data.get('code_quality_score', 0),
                'safety_score': data.get('safety_score', 0),
                'improvement_score': data.get('improvement_score', 0),
                'hallucination_penalty': data.get('hallucination_penalty', 0),
                'error': data.get('error', '') or ''
            })
    
    def get_score_progression(self):
        """Get score progression over time."""
        history = self.load_history()
        
        progression = []
        for entry in history['iterations']:
            progression.append({
                'run': entry.get('run_number', 0),
                'score_before': entry.get('score_before', 0),
                'score_after': entry.get('score_after', 0),
                'status': entry.get('status', '')
            })
        
        return progression
    
    def get_statistics(self):
        """Get aggregate statistics."""
        history = self.load_history()
        iterations = history['iterations']
        
        if not iterations:
            return {
                'total_runs': 0,
                'accepted': 0,
                'rejected': 0,
                'acceptance_rate': 0,
                'avg_score_delta': 0,
                'best_score': 0,
                'avg_lines_changed': 0,
                'avg_execution_time': 0
            }
        
        accepted = sum(1 for i in iterations if i.get('status') == 'accepted')
        score_deltas = [i.get('score_delta', 0) for i in iterations]
        scores_after = [i.get('score_after', 0) for i in iterations]
        lines_changed = [i.get('lines_changed', 0) for i in iterations]
        exec_times = [i.get('execution_time', 0) for i in iterations]
        
        return {
            'total_runs': len(iterations),
            'accepted': accepted,
            'rejected': len(iterations) - accepted,
            'acceptance_rate': accepted / len(iterations) if iterations else 0,
            'avg_score_delta': sum(score_deltas) / len(score_deltas) if score_deltas else 0,
            'best_score': max(scores_after) if scores_after else 0,
            'avg_lines_changed': sum(lines_changed) / len(lines_changed) if lines_changed else 0,
            'avg_execution_time': sum(exec_times) / len(exec_times) if exec_times else 0,
            'total_improvement': sum(d for d in score_deltas if d > 0),
            'total_regression': sum(d for d in score_deltas if d < 0)
        }
    
    def get_recent_changes(self, limit=10):
        """Get recent changes with details."""
        history = self.load_history()
        return history['iterations'][-limit:][::-1]  # Most recent first
    
    def compare_runs(self, run_a, run_b):
        """Compare two runs."""
        history = self.load_history()
        
        a_data = None
        b_data = None
        
        for entry in history['iterations']:
            if entry.get('run_number') == run_a:
                a_data = entry
            if entry.get('run_number') == run_b:
                b_data = entry
        
        if not a_data or not b_data:
            return None
        
        return {
            'run_a': {
                'number': run_a,
                'score': a_data.get('score_after', 0),
                'lines': a_data.get('lines_changed', 0),
                'status': a_data.get('status', '')
            },
            'run_b': {
                'number': run_b,
                'score': b_data.get('score_after', 0),
                'lines': b_data.get('lines_changed', 0),
                'status': b_data.get('status', '')
            },
            'score_diff': b_data.get('score_after', 0) - a_data.get('score_after', 0),
            'lines_diff': b_data.get('lines_changed', 0) - a_data.get('lines_changed', 0)
        }
    
    def export_report(self, output_path=None):
        """Export comprehensive report."""
        if output_path is None:
            output_path = os.path.join(self.trace_path, 'report.json')
        
        stats = self.get_statistics()
        progression = self.get_score_progression()
        recent = self.get_recent_changes(limit=20)
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'statistics': stats,
            'score_progression': progression,
            'recent_changes': recent,
            'milestones': self._identify_milestones()
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        return report
    
    def _identify_milestones(self):
        """Identify key milestones in evolution."""
        history = self.load_history()
        milestones = []
        
        best_score = 0
        for entry in history['iterations']:
            score = entry.get('score_after', 0)
            if score > best_score:
                best_score = score
                milestones.append({
                    'type': 'new_best_score',
                    'run': entry.get('run_number', 0),
                    'score': score,
                    'timestamp': entry.get('timestamp', '')
                })
        
        return milestones
    
    def get_trace_dashboard(self):
        """Get human-readable dashboard."""
        stats = self.get_statistics()
        
        lines = []
        lines.append("╔════════════════════════════════════════════╗")
        lines.append("║     EVOLUTION TRACE DASHBOARD              ║")
        lines.append("╠════════════════════════════════════════════╣")
        lines.append(f"║ Total Runs:       {stats['total_runs']:>10}                  ║")
        lines.append(f"║ Accepted:         {stats['accepted']:>10}                  ║")
        lines.append(f"║ Rejected:         {stats['rejected']:>10}                  ║")
        lines.append(f"║ Acceptance Rate:  {stats['acceptance_rate']*100:>9.1f}%                 ║")
        lines.append(f"║ Avg Score Delta:  {stats['avg_score_delta']:>10.4f}                  ║")
        lines.append(f"║ Best Score:       {stats['best_score']:>10.4f}                  ║")
        lines.append(f"║ Avg Lines:        {stats['avg_lines_changed']:>10.1f}                  ║")
        lines.append(f"║ Avg Exec Time:    {stats['avg_execution_time']:>10.4f}s                 ║")
        lines.append("╠════════════════════════════════════════════╣")
        
        # Health indicator
        health = "HEALTHY"
        if stats['acceptance_rate'] < 0.3:
            health = "WARNING - Low acceptance"
        if stats['avg_score_delta'] < 0:
            health = "WARNING - Negative progress"
        
        lines.append(f"║ System Health:    {health:>10}                  ║")
        lines.append("╚════════════════════════════════════════════╝")
        
        return '\n'.join(lines)


def log_evolution_iteration(runs_path, memory_path, data):
    """Log an evolution iteration."""
    logger = EvolutionLogger(runs_path, memory_path)
    logger.log_iteration(data)


def get_evolution_stats(runs_path, memory_path):
    """Get evolution statistics."""
    logger = EvolutionLogger(runs_path, memory_path)
    return logger.get_statistics()


def get_trace_dashboard(runs_path, memory_path):
    """Get trace dashboard."""
    logger = EvolutionLogger(runs_path, memory_path)
    return logger.get_trace_dashboard()
