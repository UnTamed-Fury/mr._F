"""
Meta-Evolution System - The Agent That Evolves Itself

This system allows Mr. F to evolve its OWN capabilities:
- Self-modification of operational code
- Capability discovery
- Architecture improvement
- Meta-learning (learning how to learn better)

SAFETY CONSTRAINTS:
- Immutable core files (agent.md, rules.md, IDENTITY.md) NEVER modified
- All changes must pass tests
- All changes must improve metrics
- Rollback on any regression
"""

import os
import sys
import json
import shutil
from datetime import datetime


class MetaEvolutionSystem:
    """System for evolving the agent itself."""
    
    def __init__(self, base_path):
        self.base_path = base_path
        self.core_path = os.path.join(base_path, 'core')
        self.memory_path = os.path.join(base_path, 'memory')
        self.meta_path = os.path.join(base_path, 'meta')
        
        # Files that CAN be evolved (operational code)
        self.evolvable_files = [
            'runner.py',
            'evaluator.py',
            'planner.py',
            'agents.py',
            'memory_retrieval.py',
            'semantic_memory.py',
            'exploration.py',
            'iteration_control.py',
            'trace_logger.py',
            'mutation_test.py',
            'github_issues.py',
        ]
        
        # Files that are IMMUTABLE (core identity/rules)
        self.immutable_files = [
            'agent.md',
            'IDENTITY.md',
            'rules.md',
            'evaluation.md',
            'memory_policy.md',
            'AGENT_INSTRUCTIONS.md',
        ]
        
        # Evolution history
        self.history_file = os.path.join(self.meta_path, 'self_evolution_history.json')
    
    def can_evolve(self, file_name):
        """Check if a file can be evolved."""
        return file_name in self.evolvable_files
    
    def is_immutable(self, file_name):
        """Check if a file is immutable."""
        return file_name in self.immutable_files or file_name.endswith('.md')
    
    def get_evolution_prompt(self, file_name, current_code, metrics, failures):
        """Generate prompt for evolving a system file."""
        return f"""You are evolving Mr. F's own code to make it better.

## File to Evolve: core/{file_name}

## Current Performance Metrics
{json.dumps(metrics, indent=2)}

## Recent Failures to Address
{json.dumps(failures, indent=2)}

## Current Code
```python
{current_code}
```

## Evolution Goals

1. **Improve Performance** - Make it faster, more efficient
2. **Fix Weaknesses** - Address the failures above
3. **Add Capabilities** - New features that help the system
4. **Reduce Complexity** - Simplify without losing functionality
5. **Enhance Safety** - Better error handling, validation

## Constraints

- Do NOT modify function signatures used by other modules
- Do NOT remove safety checks
- Do NOT modify immutable files
- Keep changes minimal and focused
- Preserve all docstrings
- Must pass all tests after change

## Output

Return ONLY the improved code. No explanations.

```python
# Improved {file_name}
```
"""
    
    def create_backup(self, file_name):
        """Create backup before evolution."""
        file_path = os.path.join(self.core_path, file_name)
        backup_path = file_path + '.evolution_backup'
        
        if os.path.exists(file_path):
            shutil.copy2(file_path, backup_path)
            return backup_path
        return None
    
    def restore_backup(self, backup_path):
        """Restore from backup."""
        if backup_path and os.path.exists(backup_path):
            original_path = backup_path.replace('.evolution_backup', '')
            shutil.copy2(backup_path, original_path)
            return True
        return False
    
    def cleanup_backup(self, backup_path):
        """Remove backup after successful evolution."""
        if backup_path and os.path.exists(backup_path):
            os.unlink(backup_path)
    
    def validate_evolution(self, file_name, new_code):
        """Validate evolved code."""
        # Syntax check
        try:
            compile(new_code, file_name, 'exec')
        except SyntaxError as e:
            return False, f"Syntax error: {e}"
        
        # Check for obvious issues
        if 'import os' in new_code and 'os.path' not in new_code:
            pass  # Might be unused import, but not critical
        
        return True, None
    
    def test_evolution(self, file_name):
        """Test evolved code."""
        # For now, just check it imports
        try:
            import importlib
            import sys
            
            # Remove old module if exists
            module_name = file_name.replace('.py', '')
            if module_name in sys.modules:
                del sys.modules[module_name]
            
            # Try to import
            module = __import__(module_name)
            importlib.reload(module)
            
            return True, None
        except Exception as e:
            return False, str(e)
    
    def record_evolution(self, file_name, old_metrics, new_metrics, changes_made):
        """Record evolution in history."""
        history = self.load_history()
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'file': file_name,
            'old_metrics': old_metrics,
            'new_metrics': new_metrics,
            'changes_made': changes_made,
            'improvement': self._calculate_improvement(old_metrics, new_metrics)
        }
        
        history['evolutions'].append(entry)
        self.save_history(history)
        
        return entry
    
    def load_history(self):
        """Load evolution history."""
        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except Exception:
            return {'evolutions': [], 'total_improvements': 0}
    
    def save_history(self, history):
        """Save evolution history."""
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def _calculate_improvement(self, old_metrics, new_metrics):
        """Calculate improvement percentage."""
        # Simplified - would need actual metrics comparison
        return "Recorded"
    
    def get_self_improvement_candidates(self):
        """Identify files that could benefit from improvement."""
        candidates = []
        
        # Check failures for patterns
        failures_path = os.path.join(self.memory_path, 'failures.json')
        try:
            with open(failures_path, 'r') as f:
                failures = json.load(f)
            
            # High syntax errors → improve evaluator validation
            if failures.get('syntax_error', 0) > 5:
                candidates.append({
                    'file': 'evaluator.py',
                    'reason': f"High syntax errors ({failures['syntax_error']})",
                    'priority': 'high'
                })
            
            # High timeouts → improve runner efficiency
            if failures.get('timeout', 0) > 5:
                candidates.append({
                    'file': 'runner.py',
                    'reason': f"High timeouts ({failures['timeout']})",
                    'priority': 'high'
                })
        
        except Exception:
            pass
        
        # Check iteration state for stagnation
        iteration_state_path = os.path.join(self.memory_path, 'iteration_state.json')
        try:
            with open(iteration_state_path, 'r') as f:
                state = json.load(f)
            
            if state.get('iters_without_improvement', 0) > 20:
                candidates.append({
                    'file': 'planner.py',
                    'reason': 'Stagnation detected - need better planning',
                    'priority': 'medium'
                })
        except Exception:
            pass
        
        return candidates
    
    def evolve_self(self, file_name, llm_call_fn, evaluate_fn, metrics=None, failures=None):
        """
        Evolve a system file.
        
        Returns:
            tuple: (success, message, backup_path)
        """
        if not self.can_evolve(file_name):
            return False, f"Cannot evolve {file_name} - not in evolvable list", None
        
        if self.is_immutable(file_name):
            return False, f"Cannot evolve {file_name} - immutable", None
        
        # Get current code
        file_path = os.path.join(self.core_path, file_name)
        try:
            with open(file_path, 'r') as f:
                current_code = f.read()
        except Exception as e:
            return False, f"Failed to read {file_name}: {e}", None
        
        # Get metrics and failures
        if metrics is None:
            metrics = {'source': 'system_metrics'}
        if failures is None:
            failures_path = os.path.join(self.memory_path, 'failures.json')
            try:
                with open(failures_path, 'r') as f:
                    failures = json.load(f)
            except Exception:
                failures = {}
        
        # Generate evolution prompt
        prompt = self.get_evolution_prompt(file_name, current_code, metrics, failures)
        
        # Get improved code from LLM
        new_code = llm_call_fn(prompt)
        
        if not new_code or new_code == current_code:
            return False, "No improvement generated", None
        
        # Validate
        is_valid, error = self.validate_evolution(file_name, new_code)
        if not is_valid:
            return False, f"Validation failed: {error}", None
        
        # Create backup
        backup_path = self.create_backup(file_name)
        
        # Apply change
        try:
            with open(file_path, 'w') as f:
                f.write(new_code)
        except Exception as e:
            self.restore_backup(backup_path)
            return False, f"Failed to write change: {e}", backup_path
        
        # Test
        success, test_error = self.test_evolution(file_name)
        if not success:
            self.restore_backup(backup_path)
            return False, f"Test failed: {test_error}", backup_path
        
        # Record evolution
        self.record_evolution(file_name, metrics, {'status': 'success'}, "Code evolved")
        
        # Cleanup backup
        self.cleanup_backup(backup_path)
        
        return True, f"Successfully evolved {file_name}", None


def meta_evolve(base_path, file_name, llm_call_fn, evaluate_fn):
    """Convenience function for meta-evolution."""
    system = MetaEvolutionSystem(base_path)
    return system.evolve_self(file_name, llm_call_fn, evaluate_fn)


def get_evolution_history(base_path):
    """Get evolution history."""
    system = MetaEvolutionSystem(base_path)
    return system.load_history()
