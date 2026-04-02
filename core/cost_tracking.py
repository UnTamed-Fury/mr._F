"""
Cost Tracking and Budget Limits

Tracks API usage and enforces budget limits:
- Token counting per run
- Cost estimation
- Budget limits
- Auto-stop when budget exceeded
"""

import os
import json
from datetime import datetime


class CostTracker:
    """Tracks API costs and enforces budget limits."""
    
    def __init__(self, meta_path):
        self.meta_path = meta_path
        self.limits_file = os.path.join(meta_path, 'limits.json')
        self.cost_file = os.path.join(meta_path, 'cost_tracking.json')
        
        # Default cost estimates (per 1K tokens)
        self.cost_per_1k_tokens = {
            'input': 0.0001,  # $0.10 per 1M tokens
            'output': 0.0003  # $0.30 per 1M tokens
        }
    
    def load_limits(self):
        """Load budget limits."""
        try:
            with open(self.limits_file, 'r') as f:
                limits = json.load(f)
                return {
                    'daily_budget': limits.get('daily_budget', 5.0),
                    'monthly_budget': limits.get('monthly_budget', 100.0),
                    'max_tokens_per_run': limits.get('max_tokens_per_run', 50000),
                    'max_runs_per_day': limits.get('max_runs_per_day', 100)
                }
        except Exception:
            return {
                'daily_budget': 5.0,
                'monthly_budget': 100.0,
                'max_tokens_per_run': 50000,
                'max_runs_per_day': 100
            }
    
    def load_cost_tracking(self):
        """Load cost tracking data."""
        try:
            with open(self.cost_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {
                'today': {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'tokens_in': 0,
                    'tokens_out': 0,
                    'cost': 0.0,
                    'runs': 0
                },
                'month': {
                    'month': datetime.now().strftime('%Y-%m'),
                    'cost': 0.0
                },
                'total': {
                    'cost': 0.0,
                    'runs': 0
                }
            }
    
    def save_cost_tracking(self, data):
        """Save cost tracking data."""
        os.makedirs(os.path.dirname(self.cost_file), exist_ok=True)
        with open(self.cost_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def record_run(self, tokens_in, tokens_out):
        """Record a run's token usage."""
        data = self.load_cost_tracking()
        limits = self.load_limits()
        
        # Check if day changed
        today_str = datetime.now().strftime('%Y-%m-%d')
        if data['today']['date'] != today_str:
            data['today'] = {
                'date': today_str,
                'tokens_in': 0,
                'tokens_out': 0,
                'cost': 0.0,
                'runs': 0
            }
        
        # Check if month changed
        month_str = datetime.now().strftime('%Y-%m')
        if data['month']['month'] != month_str:
            data['month'] = {
                'month': month_str,
                'cost': 0.0
            }
        
        # Update counts
        data['today']['tokens_in'] += tokens_in
        data['today']['tokens_out'] += tokens_out
        data['today']['runs'] += 1
        
        # Calculate cost
        run_cost = (tokens_in * self.cost_per_1k_tokens['input'] + 
                   tokens_out * self.cost_per_1k_tokens['output']) / 1000
        
        data['today']['cost'] += run_cost
        data['month']['cost'] += run_cost
        data['total']['cost'] += run_cost
        data['total']['runs'] += 1
        
        # Check limits
        exceeded = []
        
        if data['today']['cost'] > limits['daily_budget']:
            exceeded.append(f"Daily budget (${limits['daily_budget']:.2f})")
        
        if data['month']['cost'] > limits['monthly_budget']:
            exceeded.append(f"Monthly budget (${limits['monthly_budget']:.2f})")
        
        if tokens_in + tokens_out > limits['max_tokens_per_run']:
            exceeded.append(f"Max tokens per run ({limits['max_tokens_per_run']})")
        
        if data['today']['runs'] > limits['max_runs_per_day']:
            exceeded.append(f"Max runs per day ({limits['max_runs_per_day']})")
        
        self.save_cost_tracking(data)
        
        return {
            'allowed': len(exceeded) == 0,
            'exceeded': exceeded,
            'today_cost': data['today']['cost'],
            'month_cost': data['month']['cost'],
            'total_cost': data['total']['cost']
        }
    
    def can_run(self):
        """Check if we can run without exceeding budget."""
        data = self.load_cost_tracking()
        limits = self.load_limits()
        
        # Check day reset
        today_str = datetime.now().strftime('%Y-%m-%d')
        if data['today']['date'] != today_str:
            return True, []
        
        # Check limits
        exceeded = []
        
        if data['today']['cost'] >= limits['daily_budget'] * 0.9:
            exceeded.append(f"Approaching daily budget ({data['today']['cost']:.2f}/{limits['daily_budget']:.2f})")
        
        if data['month']['cost'] >= limits['monthly_budget'] * 0.9:
            exceeded.append(f"Approaching monthly budget ({data['month']['cost']:.2f}/{limits['monthly_budget']:.2f})")
        
        if data['today']['runs'] >= limits['max_runs_per_day']:
            exceeded.append(f"Reached max runs per day ({data['today']['runs']})")
        
        return len(exceeded) == 0, exceeded
    
    def get_cost_report(self):
        """Get human-readable cost report."""
        data = self.load_cost_tracking()
        limits = self.load_limits()
        
        report = []
        report.append("╔════════════════════════════════════════════╗")
        report.append("║         COST TRACKING REPORT               ║")
        report.append("╠════════════════════════════════════════════╣")
        report.append(f"║ Today: ${data['today']['cost']:.4f} / ${limits['daily_budget']:.2f} ({data['today']['runs']} runs)")
        report.append(f"║   - Tokens In:  {data['today']['tokens_in']:,}")
        report.append(f"║   - Tokens Out: {data['today']['tokens_out']:,}")
        report.append(f"║ This Month: ${data['month']['cost']:.2f} / ${limits['monthly_budget']:.2f}")
        report.append(f"║ Total: ${data['total']['cost']:.2f} ({data['total']['runs']} runs)")
        report.append("╚════════════════════════════════════════════╝")
        
        return '\n'.join(report)


def check_budget(meta_path):
    """Check if we can run within budget."""
    tracker = CostTracker(meta_path)
    return tracker.can_run()


def record_api_usage(meta_path, tokens_in, tokens_out):
    """Record API usage for a run."""
    tracker = CostTracker(meta_path)
    return tracker.record_run(tokens_in, tokens_out)


def get_cost_report(meta_path):
    """Get cost tracking report."""
    tracker = CostTracker(meta_path)
    return tracker.get_cost_report()
