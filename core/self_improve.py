"""
Self-Improvement Module

Allows Mr. F to evolve its own code (runner.py, evaluator.py)
under strict constraints.
"""

import os
import sys
import json
import shutil

# Add core to path
sys.path.insert(0, os.path.dirname(__file__))
from evaluator import evaluate


class SelfImprover:
    """Handles self-improvement of the evolution system."""
    
    def __init__(self, base_path=None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.core_path = os.path.join(self.base_path, 'core')
        self.memory_path = os.path.join(self.base_path, 'memory')
        
        # Files that CAN be improved (NOT immutable core docs)
        self.improvable_files = [
            'runner.py',
            'evaluator.py'
        ]
        
        # Files that are IMMUTABLE (never change)
        self.immutable_files = [
            'agent.md',
            'rules.md',
            'evaluation.md',
            'memory_policy.md'
        ]
    
    def can_improve(self, file_name):
        """Check if a file can be improved."""
        return file_name in self.improvable_files
    
    def get_current_system_code(self, file_name):
        """Get current code for a system file."""
        file_path = os.path.join(self.core_path, file_name)
        try:
            with open(file_path, 'r') as f:
                return f.read()
        except Exception:
            return ""
    
    def save_improved_code(self, file_name, new_code):
        """Save improved system code with backup."""
        file_path = os.path.join(self.core_path, file_name)
        backup_path = file_path + '.backup'
        
        # Create backup
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
        
        # Save new code
        with open(file_path, 'w') as f:
            f.write(new_code)
        
        return backup_path
    
    def restore_backup(self, backup_path):
        """Restore from backup if improvement failed."""
        original_path = backup_path.replace('.backup', '')
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, original_path)
            os.unlink(backup_path)
            return True
        return False
    
    def cleanup_backup(self, backup_path):
        """Remove backup after successful improvement."""
        if os.path.exists(backup_path):
            os.unlink(backup_path)
    
    def validate_system_code(self, file_name, new_code):
        """Validate system code before applying."""
        import tempfile
        
        # Check syntax
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(new_code)
            temp_path = f.name
        
        try:
            compile(open(temp_path).read(), temp_path, 'exec')
            os.unlink(temp_path)
            return True, None
        except SyntaxError as e:
            os.unlink(temp_path)
            return False, str(e)
    
    def test_system_after_change(self, file_name):
        """Test the system after a change."""
        # For runner.py - just check it imports
        if file_name == 'runner.py':
            try:
                # Reload module
                import importlib
                import runner
                importlib.reload(runner)
                return True, None
            except Exception as e:
                return False, str(e)
        
        # For evaluator.py - run evaluation
        if file_name == 'evaluator.py':
            try:
                import importlib
                import evaluator
                importlib.reload(evaluator)
                
                # Test evaluation works
                from evaluator import evaluate
                result = evaluate(os.path.join(self.base_path, 'workspace'))
                return result.status == 'accepted', f"Eval status: {result.status}"
            except Exception as e:
                return False, str(e)
        
        return True, None
    
    def log_self_improvement(self, file_name, success, details):
        """Log self-improvement attempt."""
        journal_path = os.path.join(self.memory_path, 'journal.jsonl')
        
        entry = {
            'type': 'self_improvement',
            'file': file_name,
            'success': success,
            'details': details,
            'timestamp': __import__('datetime').datetime.now().isoformat()
        }
        
        with open(journal_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_improvement_prompt(self, file_name, current_code, metrics):
        """Generate prompt for improving system code."""
        return f"""You are improving Mr. F's own evolution system.

## File to Improve: core/{file_name}

## Current Metrics
{json.dumps(metrics, indent=2)}

## Current Code
```python
{current_code}
```

## Improvement Goals

1. **Performance** - Make it faster
2. **Reliability** - Reduce errors/rejections
3. **Efficiency** - Better LLM usage
4. **Safety** - Maintain all constraints

## Constraints

- Do NOT change function signatures used by other modules
- Do NOT remove safety checks
- Do NOT modify immutable files (agent.md, rules.md, etc.)
- Keep changes minimal and focused
- Preserve all docstrings

## Output

Return ONLY the improved code. No explanations.

```python
# Improved {file_name}
```
"""
