"""
Mr. F - Multi-Agent System

Inspired by yoyo-evolve's multi-agent approach:
- Assessment Agent: Analyzes current state
- Planning Agent: Creates improvement plan
- Evaluator Agent: Reviews changes
- Fix Agent: Attempts to fix issues
"""

import os
import sys
import json

sys.path.insert(0, os.path.dirname(__file__))


class AssessmentAgent:
    """Analyzes current codebase state and creates assessment."""
    
    def __init__(self, runner):
        self.runner = runner
    
    def assess(self):
        """Create assessment of current state."""
        current_code = self.runner._get_current_code()
        memory = self.runner._load_memory()
        
        assessment = {
            'code_lines': len(current_code.split('\n')),
            'functions': self._count_functions(current_code),
            'current_score': self._get_current_score(),
            'recent_failures': memory.get('failures', {}),
            'recent_successes': memory.get('summaries', [])[-3:],
            'recommendations': []
        }
        
        # Generate recommendations
        if assessment['recent_failures'].get('syntax_error', 0) > 2:
            assessment['recommendations'].append(
                'Focus on syntax-safe changes, avoid complex rewrites'
            )
        
        if assessment['recent_failures'].get('timeout', 0) > 2:
            assessment['recommendations'].append(
                'Optimize for performance, reduce complexity'
            )
        
        if assessment['current_score'] > 0.99:
            assessment['recommendations'].append(
                'Code is highly optimized, consider edge case improvements'
            )
        
        return assessment
    
    def _count_functions(self, code):
        """Count function definitions."""
        import re
        return len(re.findall(r'def \w+\(', code))
    
    def _get_current_score(self):
        """Get current evaluation score."""
        from evaluator import evaluate
        result = evaluate(self.runner.workspace_path)
        return result.total_score


class PlanningAgent:
    """Creates improvement plan based on assessment."""
    
    def __init__(self, runner):
        self.runner = runner
    
    def create_plan(self, assessment):
        """Generate improvement plan."""
        plan = {
            'priority': 'low',
            'focus_area': '',
            'suggested_changes': [],
            'risk_level': 'low',
            'expected_impact': ''
        }
        
        recommendations = assessment.get('recommendations', [])
        failures = assessment.get('recent_failures', {})
        
        # Determine priority
        if failures.get('syntax_error', 0) > 3:
            plan['priority'] = 'high'
            plan['focus_area'] = 'syntax_safety'
            plan['suggested_changes'].append(
                'Use more conservative code changes'
            )
        elif failures.get('timeout', 0) > 3:
            plan['priority'] = 'high'
            plan['focus_area'] = 'performance'
            plan['suggested_changes'].append(
                'Optimize loops and recursive calls'
            )
        elif assessment['current_score'] < 0.9:
            plan['priority'] = 'medium'
            plan['focus_area'] = 'correctness'
            plan['suggested_changes'].append(
                'Add input validation and edge case handling'
            )
        else:
            plan['priority'] = 'low'
            plan['focus_area'] = 'optimization'
            plan['suggested_changes'].append(
                'Minor optimizations where possible'
            )
        
        # Set risk level
        if plan['priority'] == 'high':
            plan['risk_level'] = 'medium'
        else:
            plan['risk_level'] = 'low'
        
        # Expected impact
        if plan['focus_area'] == 'performance':
            plan['expected_impact'] = 'Faster execution, better speed score'
        elif plan['focus_area'] == 'correctness':
            plan['expected_impact'] = 'Higher test pass rate'
        else:
            plan['expected_impact'] = 'Incremental improvement'
        
        return plan


class EvaluatorAgent:
    """Reviews proposed changes before acceptance."""
    
    def __init__(self, runner):
        self.runner = runner
    
    def evaluate(self, old_code, new_code, diff_text):
        """Evaluate proposed change quality."""
        evaluation = {
            'passed': True,
            'issues': [],
            'risk_level': 'low',
            'recommendation': 'accept'
        }
        
        # Check diff size
        lines_changed = self.runner.count_lines_changed(diff_text)
        max_lines = self.runner.limits.get('max_lines_changed', 50)
        
        if lines_changed > max_lines:
            evaluation['passed'] = False
            evaluation['issues'].append(f'Too many lines changed: {lines_changed} > {max_lines}')
            evaluation['recommendation'] = 'reject'
        
        # Check if docstrings preserved
        old_docstrings = old_code.count('"""')
        new_docstrings = new_code.count('"""')
        
        if new_docstrings < old_docstrings * 0.8:
            evaluation['issues'].append('Docstrings removed')
            evaluation['risk_level'] = 'medium'
        
        # Check if function signatures changed
        import re
        old_funcs = set(re.findall(r'def (\w+)\([^)]*\):', old_code))
        new_funcs = set(re.findall(r'def (\w+)\([^)]*\):', new_code))
        
        if old_funcs != new_funcs:
            evaluation['issues'].append('Function signatures modified')
            evaluation['risk_level'] = 'high'
            evaluation['recommendation'] = 'reject'
        
        # Syntax check
        is_valid, error = self.runner.validate_syntax_content(new_code)
        if not is_valid:
            evaluation['passed'] = False
            evaluation['issues'].append(f'Syntax error: {error}')
            evaluation['recommendation'] = 'reject'
        
        return evaluation


class FixAgent:
    """Attempts to fix rejected changes."""
    
    def __init__(self, runner):
        self.runner = runner
        self.max_attempts = 2
    
    def fix(self, code, issues):
        """Attempt to fix issues in code."""
        fixed_code = code
        attempts = 0
        
        for issue in issues:
            if attempts >= self.max_attempts:
                break
            
            if 'syntax' in issue.lower():
                fixed_code = self._fix_syntax(fixed_code)
                attempts += 1
            elif 'docstring' in issue.lower():
                fixed_code = self._restore_docstrings(fixed_code)
                attempts += 1
        
        return fixed_code, attempts
    
    def _fix_syntax(self, code):
        """Attempt basic syntax fixes."""
        # For now, just return original
        # Could add more sophisticated fixing logic
        return code
    
    def _restore_docstrings(self, code):
        """Attempt to restore docstrings."""
        # For now, just return original
        return code


class SessionPlanner:
    """Creates and manages session plans."""
    
    def __init__(self, runner):
        self.runner = runner
        self.plan_dir = os.path.join(runner.runs_path, 'session_plans')
    
    def create_session_plan(self, assessment, plan):
        """Create session plan files."""
        os.makedirs(self.plan_dir, exist_ok=True)
        
        # Create assessment file
        assessment_file = os.path.join(self.plan_dir, 'assessment.md')
        with open(assessment_file, 'w') as f:
            f.write('# Session Assessment\n\n')
            f.write(f"- Code Lines: {assessment.get('code_lines', 0)}\n")
            f.write(f"- Functions: {assessment.get('functions', 0)}\n")
            f.write(f"- Current Score: {assessment.get('current_score', 0):.4f}\n")
            f.write(f"- Priority: {plan.get('priority', 'low')}\n")
            f.write(f"- Focus Area: {plan.get('focus_area', 'unknown')}\n")
            f.write('\n## Recommendations\n\n')
            for rec in assessment.get('recommendations', []):
                f.write(f"- {rec}\n")
        
        # Create task file
        task_file = os.path.join(self.plan_dir, 'task_001.md')
        with open(task_file, 'w') as f:
            f.write('# Task 001\n\n')
            f.write(f"**Priority:** {plan.get('priority')}\n")
            f.write(f"**Focus:** {plan.get('focus_area')}\n")
            f.write(f"**Risk Level:** {plan.get('risk_level')}\n\n")
            f.write('## Suggested Changes\n\n')
            for change in plan.get('suggested_changes', []):
                f.write(f"- {change}\n")
            f.write(f"\n**Expected Impact:** {plan.get('expected_impact')}\n")
        
        return {'assessment': assessment_file, 'tasks': [task_file]}
    
    def get_latest_plan(self):
        """Get latest session plan."""
        if not os.path.exists(self.plan_dir):
            return None
        
        plans = sorted(os.listdir(self.plan_dir), reverse=True)
        if plans:
            return os.path.join(self.plan_dir, plans[0])
        return None
