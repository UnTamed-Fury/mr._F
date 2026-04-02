"""
Mr. F - Evolution Runner

Main evolution loop with inspiration from yoyo-evolve:
- Checkpoint system for safe reverts
- Journal-based learning
- Identity-guided behavior
- Multi-stage validation

Advanced features:
- Multi-metric evaluation with hallucination detection
- Iteration control with early stopping
- Memory retrieval for context
- Comprehensive trace logging
"""

import os
import sys
import json
import difflib
import datetime
import tempfile
import shutil

# Add core to path
sys.path.insert(0, os.path.dirname(__file__))
from evaluator import evaluate, validate_syntax, count_lines_changed, get_file_size, detect_hallucination
from iteration_control import IterationController, check_iteration_limits, get_iteration_status
from memory_retrieval import MemoryRetriever, get_memory_context
from semantic_memory import SemanticMemoryRetriever, get_semantic_context
from trace_logger import EvolutionLogger, log_evolution_iteration, get_trace_dashboard
from meta_evolution import MetaEvolutionSystem, meta_evolve


class EvolutionRunner:
    """Main evolution loop runner with checkpoint/revert support."""
    
    def __init__(self, base_path=None):
        self.base_path = base_path or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.core_path = os.path.join(self.base_path, 'core')
        self.workspace_path = os.path.join(self.base_path, 'workspace')
        self.memory_path = os.path.join(self.base_path, 'memory')
        self.runs_path = os.path.join(self.base_path, 'runs')
        self.meta_path = os.path.join(self.base_path, 'meta')

        # Load configuration
        self.config = self._load_config()
        self.limits = self._load_limits()

        # API configuration
        self.api_key = os.environ.get('OPENROUTER_API_KEY', '')
        self.api_base = 'https://openrouter.ai/api/v1'
        self.model = self.config.get('model', 'openrouter/free')

        # Initialize new systems
        self.iteration_controller = IterationController(self.memory_path)
        self.memory_retriever = MemoryRetriever(self.memory_path)
        self.semantic_retriever = SemanticMemoryRetriever(self.memory_path)
        self.trace_logger = EvolutionLogger(self.runs_path, self.memory_path)
        self.meta_evolution = MetaEvolutionSystem(self.base_path)

        # Iteration tracking
        self.run_number = self._load_version().get('total_runs', 0) + 1
        
        # Self-evolution trigger (every 25 runs for deep evolution)
        self.self_evolve_interval = 25
    
    def _load_config(self):
        """Load workspace config."""
        config_path = os.path.join(self.workspace_path, 'config.json')
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _load_limits(self):
        """Load limits config."""
        limits_path = os.path.join(self.meta_path, 'limits.json')
        try:
            with open(limits_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _create_checkpoint(self):
        """Create a checkpoint for potential revert."""
        import hashlib
        
        checkpoint = {
            'timestamp': datetime.datetime.now().isoformat(),
            'workspace_hash': '',
            'runner_hash': '',
            'git_sha': self._get_git_sha()
        }
        
        # Hash workspace target
        target_path = os.path.join(self.workspace_path, 'target.py')
        if os.path.exists(target_path):
            with open(target_path, 'r') as f:
                checkpoint['workspace_hash'] = hashlib.sha256(f.read().encode()).hexdigest()
        
        # Hash runner
        runner_path = os.path.join(self.core_path, 'runner.py')
        if os.path.exists(runner_path):
            with open(runner_path, 'r') as f:
                checkpoint['runner_hash'] = hashlib.sha256(f.read().encode()).hexdigest()
        
        # Save checkpoint
        checkpoint_path = os.path.join(self.runs_path, 'latest', 'checkpoint.json')
        os.makedirs(os.path.dirname(checkpoint_path), exist_ok=True)
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint, f, indent=2)
        
        print(f"[Mr. F] Checkpoint created: {checkpoint['git_sha'][:8]}")
        return checkpoint
    
    def _get_git_sha(self):
        """Get current git SHA."""
        import subprocess
        try:
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.base_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.stdout.strip()
        except Exception:
            return 'no-git'
    
    def _revert_to_checkpoint(self, checkpoint):
        """Revert to checkpoint state."""
        print(f"[Mr. F] Reverting to checkpoint: {checkpoint.get('git_sha', 'unknown')[:8]}")
        
        # Reset git to checkpoint SHA
        import subprocess
        try:
            subprocess.run(
                ['git', 'reset', '--hard', checkpoint['git_sha']],
                cwd=self.base_path,
                check=True,
                timeout=30
            )
            subprocess.run(
                ['git', 'clean', '-fd'],
                cwd=self.base_path,
                check=True,
                timeout=30
            )
            print("[Mr. F] Revert successful")
            return True
        except Exception as e:
            print(f"[Mr. F] Revert failed: {e}")
            return False
    
    def _load_memory(self):
        """Load all memory files."""
        memory = {
            'best': {},
            'failures': {},
            'summaries': [],
            'reflections': [],
            'journal_count': 0
        }
        
        # Load best.json
        best_path = os.path.join(self.memory_path, 'best.json')
        try:
            with open(best_path, 'r') as f:
                memory['best'] = json.load(f)
        except Exception:
            memory['best'] = {'score': 0.0, 'version': 0}
        
        # Load failures.json
        failures_path = os.path.join(self.memory_path, 'failures.json')
        try:
            with open(failures_path, 'r') as f:
                memory['failures'] = json.load(f)
        except Exception:
            memory['failures'] = {}
        
        # Load summaries.json
        summaries_path = os.path.join(self.memory_path, 'summaries.json')
        try:
            with open(summaries_path, 'r') as f:
                memory['summaries'] = json.load(f)
        except Exception:
            memory['summaries'] = []
        
        # Load last few reflections
        reflections_path = os.path.join(self.memory_path, 'reflections.jsonl')
        try:
            with open(reflections_path, 'r') as f:
                lines = f.readlines()[-5:]
                memory['reflections'] = [json.loads(l) for l in lines if l.strip()]
        except Exception:
            memory['reflections'] = []
        
        # Count journal entries
        journal_path = os.path.join(self.memory_path, 'journal.jsonl')
        try:
            with open(journal_path, 'r') as f:
                memory['journal_count'] = sum(1 for _ in f)
        except Exception:
            memory['journal_count'] = 0
        
        return memory
    
    def _load_prompt(self, name):
        """Load a prompt template."""
        prompt_path = os.path.join(self.core_path, 'prompts', f'{name}.txt')
        try:
            with open(prompt_path, 'r') as f:
                return f.read()
        except Exception:
            return ""
    
    def _build_memory_context(self, memory):
        """Build comprehensive memory context for the agent."""
        context_parts = []
        
        # Add summaries
        if memory.get('summaries'):
            summaries = memory['summaries'][-3:]
            context_parts.append("### Learned Patterns")
            for s in summaries:
                if 'insights' in s:
                    for insight in s['insights']:
                        context_parts.append(f"- {insight}")
        
        # Add recent reflections
        if memory.get('reflections'):
            reflections = memory['reflections'][-3:]
            context_parts.append("\n### Recent Insights")
            for r in reflections:
                if 'next_strategy' in r:
                    context_parts.append(f"- {r.get('result', 'unknown')}: {r['next_strategy']}")
        
        # Add failure warnings
        if memory.get('failures'):
            failures = memory['failures']
            high_failures = {k: v for k, v in failures.items() if v > 2}
            if high_failures:
                context_parts.append("\n### Warnings")
                for failure_type, count in high_failures.items():
                    context_parts.append(f"- Avoid {failure_type} (failed {count} times)")
        
        return '\n'.join(context_parts) if context_parts else "No memory context available yet."
    
    def _build_reflection_context(self, memory):
        """Build reflection context for the agent."""
        if not memory.get('reflections'):
            return "No recent reflections."

        context = []
        for r in memory['reflections'][-5:]:
            result = r.get('result', 'unknown')
            reason = r.get('reason', '')[:100]
            context.append(f"- {result}: {reason}")

        return '\n'.join(context)

    def _run_critic(self, original_code, new_code):
        """Run critic analysis on proposed change."""
        try:
            # Generate diff
            diff_text = self._generate_diff(original_code, new_code)
            
            # Load critic prompt
            critic_prompt = self._load_prompt('critic')
            critic_prompt = critic_prompt.format(
                original_code=original_code[:2000],  # Truncate for context
                new_code=new_code[:2000],
                diff=diff_text[:1000]
            )
            
            # Call LLM for critic analysis
            critic_response = self._call_llm(critic_prompt)
            
            # Parse JSON response
            if critic_response:
                # Try to extract JSON from response
                import re
                json_match = re.search(r'\{[^}]+\}', critic_response, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
            
            # Default if parsing fails
            return {
                'risk_level': 'medium',
                'issues': ['Could not parse critic response'],
                'recommendation': 'accept',
                'reasoning': 'Default acceptance due to parsing failure'
            }
            
        except Exception as e:
            print(f"[Mr. F] Critic analysis failed: {e}")
            return {
                'risk_level': 'medium',
                'issues': [f'Critic error: {str(e)}'],
                'recommendation': 'accept',
                'reasoning': 'Default acceptance due to error'
            }

    def _get_current_code(self):
        """Get current target.py code."""
        target_path = os.path.join(self.workspace_path, 'target.py')
        try:
            with open(target_path, 'r') as f:
                return f.read()
        except Exception:
            return ""
    
    def _generate_diff(self, old_code, new_code):
        """Generate unified diff between old and new code."""
        old_lines = old_code.splitlines(keepends=True)
        new_lines = new_code.splitlines(keepends=True)
        
        diff = difflib.unified_diff(
            old_lines, new_lines,
            fromfile='old/target.py',
            tofile='new/target.py'
        )
        
        return ''.join(diff)
    
    def _call_llm(self, prompt, system_message=None):
        """Call LLM via OpenRouter API."""
        import urllib.request
        import urllib.error
        import re

        if not self.api_key:
            return self._get_current_code()

        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'HTTP-Referer': 'https://github.com/UnTamed-Fury/mr._F',
            'X-Title': 'Mr. F Evolution'
        }

        messages = []
        if system_message:
            messages.append({'role': 'system', 'content': system_message})
        messages.append({'role': 'user', 'content': prompt})

        payload = {
            'model': self.model,
            'messages': messages,
            'temperature': self.config.get('temperature', 0.7),
            'max_tokens': 2000
        }

        try:
            data = json.dumps(payload).encode('utf-8')
            req = urllib.request.Request(
                f'{self.api_base}/chat/completions',
                data=data,
                headers=headers,
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=90) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if not result or 'choices' not in result:
                    print(f"[Mr. F] LLM response format unexpected")
                    return None
                
                choices = result.get('choices', [])
                if not choices or len(choices) == 0:
                    print("[Mr. F] LLM returned no choices")
                    return None
                
                message = choices[0].get('message', {})
                if not message:
                    print("[Mr. F] LLM returned empty message")
                    return None
                    
                content = message.get('content', '')
                
                # Check for reasoning models
                if not content:
                    reasoning = message.get('reasoning', '')
                    if reasoning:
                        print("[Mr. F] Model returned reasoning, extracting code...")
                        code = self._extract_code_from_reasoning(reasoning)
                        if code:
                            content = code
                
                if not content:
                    print("[Mr. F] LLM returned empty content")
                    return None
                
                # Extract code from response
                if '```python' in content:
                    start = content.find('```python') + len('```python')
                    end = content.find('```', start)
                    code = content[start:end].strip()
                elif '```' in content:
                    start = content.find('```') + 3
                    end = content.find('```', start)
                    code = content[start:end].strip()
                else:
                    code = content.strip()
                
                # Merge with original to preserve structure
                merged = self._merge_changes(code)
                return merged
                
        except urllib.error.HTTPError as e:
            print(f"[Mr. F] HTTP Error: {e.code} - {e.reason}")
            return None
        except urllib.error.URLError as e:
            print(f"[Mr. F] URL Error: {e.reason}")
            return None
        except Exception as e:
            print(f"[Mr. F] LLM call failed: {e}")
            return None
    
    def _merge_changes(self, new_code):
        """Merge LLM changes with original code to preserve structure."""
        original = self._get_current_code()
        original_lines = len(original.split('\n'))
        new_lines = len(new_code.split('\n'))
        
        # If LLM deleted too much, keep original
        if new_lines < original_lines * 0.7:
            print(f"[Mr. F] LLM deleted too much, keeping original")
            return original
        
        # If new code is way bigger, keep original
        if new_lines > original_lines * 1.5:
            print(f"[Mr. F] LLM added too much, keeping original")
            return original
        
        # Validate syntax before using
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(new_code)
            temp_path = f.name
        
        is_valid, _ = validate_syntax(temp_path)
        os.unlink(temp_path)
        
        if is_valid:
            return new_code
        else:
            print("[Mr. F] New code has syntax errors, keeping original")
            return original
    
    def _extract_code_from_reasoning(self, reasoning):
        """Extract code snippets from model reasoning."""
        import re
        
        # Look for function definitions
        code_blocks = re.findall(r'def \w+\([^)]*\):.*?(?=\n\ndef |\nif __name__|$)', reasoning, re.DOTALL)
        
        if code_blocks:
            best = max(code_blocks, key=len)
            return best.strip()
        
        # Look for inline code
        inline = re.findall(r'`{1,3}([^`]+)`{1,3}', reasoning)
        if inline:
            return '\n'.join(inline)
        
        return None
    
    def _save_run_artifacts(self, input_text, output_text, diff_text, result_dict):
        """Save run artifacts to runs/latest/."""
        latest_path = os.path.join(self.runs_path, 'latest')
        os.makedirs(latest_path, exist_ok=True)
        
        with open(os.path.join(latest_path, 'input.txt'), 'w') as f:
            f.write(input_text[:1000])
        
        with open(os.path.join(latest_path, 'output.txt'), 'w') as f:
            f.write(output_text[:1000])
        
        with open(os.path.join(latest_path, 'diff.txt'), 'w') as f:
            f.write(diff_text)
        
        with open(os.path.join(latest_path, 'result.json'), 'w') as f:
            json.dump(result_dict, f, indent=2)
    
    def _append_to_journal(self, entry):
        """Append entry to journal.jsonl."""
        journal_path = os.path.join(self.memory_path, 'journal.jsonl')
        with open(journal_path, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _append_reflection(self, reflection):
        """Append reflection to reflections.jsonl."""
        reflections_path = os.path.join(self.memory_path, 'reflections.jsonl')
        with open(reflections_path, 'a') as f:
            f.write(json.dumps(reflection) + '\n')
    
    def _update_failures(self, error_type):
        """Update failures.json with error type."""
        failures_path = os.path.join(self.memory_path, 'failures.json')
        
        try:
            with open(failures_path, 'r') as f:
                failures = json.load(f)
        except Exception:
            failures = {}
        
        category = 'runtime_error'
        if error_type:
            if 'syntax' in error_type.lower():
                category = 'syntax_error'
            elif 'timeout' in error_type.lower():
                category = 'timeout'
            elif 'wrong' in error_type.lower() or 'assert' in error_type.lower():
                category = 'wrong_output'
            elif 'regression' in error_type.lower():
                category = 'regression'
        
        failures[category] = failures.get(category, 0) + 1
        
        with open(failures_path, 'w') as f:
            json.dump(failures, f, indent=2)
    
    def _update_best(self, score, version, notes):
        """Update best.json if score improved."""
        best_path = os.path.join(self.memory_path, 'best.json')
        
        try:
            with open(best_path, 'r') as f:
                best = json.load(f)
        except Exception:
            best = {'score': 0.0, 'version': 0}
        
        if score > best.get('score', 0):
            best['score'] = score
            best['version'] = version
            best['notes'] = notes
            best['last_updated'] = datetime.datetime.now().isoformat()
            
            with open(best_path, 'w') as f:
                json.dump(best, f, indent=2)
            
            return True
        return False
    
    def _append_changelog(self, change_summary, score_before, score_after):
        """Append entry to changelog.md."""
        changelog_path = os.path.join(self.memory_path, 'changelog.md')
        
        date_str = datetime.datetime.now().strftime('%Y-%m-%d')
        entry = f"\n## {date_str}\n\n- Change: {change_summary}\n- Reason: Score improvement\n- Score: {score_before:.4f} → {score_after:.4f}\n"
        
        with open(changelog_path, 'a') as f:
            f.write(entry)
    
    def _update_version(self, accepted=False):
        """Update version.json with run stats."""
        version_path = os.path.join(self.meta_path, 'version.json')
        
        try:
            with open(version_path, 'r') as f:
                version = json.load(f)
        except Exception:
            version = {}
        
        version['total_runs'] = version.get('total_runs', 0) + 1
        if accepted:
            version['accepted_changes'] = version.get('accepted_changes', 0) + 1
        else:
            version['rejected_changes'] = version.get('rejected_changes', 0) + 1
        version['last_modified'] = datetime.datetime.now().isoformat()
        
        with open(version_path, 'w') as f:
            json.dump(version, f, indent=2)
    
    def _calculate_max_lines(self):
        """
        Calculate max lines allowed based on codebase size.
        
        PROGRESSIVE SCALE (scales up to 1M+ lines):
        
        Codebase Size      | Max Lines
        -------------------|------------------
        < 1,000            | 50 lines (base)
        1,000 - 9,999      | codebase / 10
        10,000 - 99,999    | codebase / 5
        100,000 - 999,999  | codebase / 3
        ≥ 1,000,000        | codebase / 2 (500k lines!)
        
        This allows the agent to make meaningful changes at any scale.
        """
        # Count total lines in workspace
        total_lines = 0
        workspace_files = ['target.py', 'tests.py', 'utils.py']
        
        for filename in workspace_files:
            filepath = os.path.join(self.workspace_path, filename)
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    total_lines += len(f.readlines())
        
        # Progressive scale calculation
        if total_lines < 1000:
            max_lines = 50
        elif total_lines < 10000:
            max_lines = max(50, total_lines // 10)
        elif total_lines < 100000:
            max_lines = max(100, total_lines // 5)
        elif total_lines < 1000000:
            max_lines = max(2000, total_lines // 3)
        else:  # 1M+ lines
            max_lines = max(33000, total_lines // 2)
        
        return max_lines, total_lines
    
    def _load_version(self):
        """Load version info."""
        version_path = os.path.join(self.meta_path, 'version.json')
        try:
            with open(version_path, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def _validate_syntax_content(self, content):
        """Validate syntax of code content string."""
        try:
            compile(content, '<string>', 'exec')
            return True, None
        except SyntaxError as e:
            return False, str(e)
    
    def count_lines_changed(self, diff_text):
        """Count lines changed in a diff."""
        return count_lines_changed(diff_text)
    
    def run_evolution_step(self):
        """Execute one evolution step with checkpoint/revert support."""
        print("[Mr. F] Starting evolution step...")
        print(f"[Mr. F] Model: {self.model} | Mode: Normal")
        
        timestamp = datetime.datetime.now().isoformat()
        
        # Create checkpoint for potential revert
        checkpoint = self._create_checkpoint()
        
        # Load State & Memory
        print("[Mr. F] Loading state and memory...")
        memory = self._load_memory()
        current_code = self._get_current_code()
        baseline_score = memory['best'].get('score', 0.0)
        
        # Evaluate current state
        print("[Mr. F] Evaluating current state...")
        current_result = evaluate(self.workspace_path)
        score_before = current_result.total_score
        
        print(f"[Mr. F] Current score: {score_before:.4f}")
        
        # Generate Candidate (LLM)
        print("[Mr. F] Generating improvement candidate...")
        print("[Mr. F] Using master prompt with deep reasoning...")

        # Build rich context for the agent
        memory_context = self._build_memory_context(memory)
        reflection_context = self._build_reflection_context(memory)
        
        # Extract success and failure patterns
        success_patterns = []
        failure_patterns = []
        if memory.get('summaries'):
            for s in memory['summaries'][-3:]:
                if 'successful_patterns' in s:
                    success_patterns.extend(s['successful_patterns'][:3])
                if 'failures_to_avoid' in s:
                    failure_patterns.extend(s['failures_to_avoid'][:3])
        
        # Try master prompt first, fall back to improve prompt
        master_prompt = self._load_prompt('master')
        
        if master_prompt:
            improve_prompt = master_prompt.format(
                goal=self.config.get('goal', 'Optimize code'),
                score=f"{score_before:.4f}",
                best_score=f"{baseline_score:.4f}",
                memory_context=memory_context,
                reflection_context=reflection_context,
                success_patterns='\n'.join(f"- {p}" for p in success_patterns) if success_patterns else "No specific success patterns yet",
                failure_patterns='\n'.join(f"- {p}" for p in failure_patterns) if failure_patterns else "No specific failure patterns yet",
                current_code=current_code
            )
        else:
            # Fallback to original improve prompt
            improve_prompt = self._load_prompt('improve')
            improve_prompt = improve_prompt.format(
                goal=self.config.get('goal', 'Optimize code'),
                score=f"{score_before:.4f}",
                best_score=f"{baseline_score:.4f}",
                summaries=memory_context,
                failures=json.dumps(memory['failures']) if memory['failures'] else 'No failures recorded',
                reflections=reflection_context,
                current_code=current_code
            )

        new_code = self._call_llm(improve_prompt)

        if new_code is None:
            print("[Mr. F] LLM call failed, keeping current code")
            new_code = current_code

        # CRITIC STEP: Analyze proposed change
        print("[Mr. F] Running critic analysis...")
        critic_result = self._run_critic(current_code, new_code)
        
        if critic_result.get('recommendation') == 'reject':
            print(f"[Mr. F] REJECTED by critic: {critic_result.get('reasoning', 'Unknown')}")
            print(f"[Mr. F] Issues: {critic_result.get('issues', [])}")
            new_code = current_code  # Revert to original
        elif critic_result.get('risk_level') == 'high':
            print(f"[Mr. F] ⚠️ High risk change: {critic_result.get('reasoning', 'Unknown')}")
            # Continue but log the risk

        # Generate diff
        diff_text = self._generate_diff(current_code, new_code)
        lines_changed = count_lines_changed(diff_text)

        print(f"[Mr. F] Proposed changes: {lines_changed} lines")

        # Validate - Dynamic line limit based on codebase size
        print("[Mr. F] Validating changes...")
        print("[Mr. F] Calculating dynamic line limit...")
        
        max_lines, codebase_lines = self._calculate_max_lines()
        print(f"[Mr. F] Codebase: {codebase_lines} lines → Max changes: {max_lines} lines")
        
        if lines_changed > max_lines:
            print(f"[Mr. F] REJECTED: Changes exceed limit ({lines_changed} > {max_lines})")

            journal_entry = {
                'timestamp': timestamp,
                'score_before': score_before,
                'score_after': score_before,
                'accepted': False,
                'change_summary': f'Too many lines changed: {lines_changed}',
                'diff': diff_text,
                'error': 'line_limit_exceeded'
            }
            self._append_to_journal(journal_entry)
            self._update_failures('line_limit_exceeded')
            self._update_version(accepted=False)

            return {'status': 'rejected', 'reason': 'line_limit_exceeded'}
        
        # Validate syntax
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(new_code)
            temp_path = f.name
        
        is_valid, syntax_error = validate_syntax(temp_path)
        os.unlink(temp_path)
        
        if not is_valid:
            print(f"[Mr. F] REJECTED: Syntax error - {syntax_error}")
            
            # Revert to checkpoint
            self._revert_to_checkpoint(checkpoint)
            
            journal_entry = {
                'timestamp': timestamp,
                'score_before': score_before,
                'score_after': score_before,
                'accepted': False,
                'change_summary': 'Syntax validation failed',
                'diff': diff_text,
                'error': syntax_error
            }
            self._append_to_journal(journal_entry)
            self._update_failures('syntax_error')
            self._update_version(accepted=False)
            
            return {'status': 'rejected', 'reason': 'syntax_error', 'error': syntax_error}
        
        # Execute & Evaluate
        print("[Mr. F] Executing and evaluating...")
        
        target_path = os.path.join(self.workspace_path, 'target.py')
        backup_code = current_code
        
        try:
            with open(target_path, 'w') as f:
                f.write(new_code)

            # Use advanced evaluator with hallucination detection
            new_result = evaluate(
                self.workspace_path,
                timeout=self.limits.get('timeout_seconds', 5),
                previous_score=score_before,
                claimed_improvement=None  # Can be extracted from LLM response
            )
            score_after = new_result.total_score

            print(f"[Mr. F] New score: {score_after:.4f}")
            print(f"[Mr. F]   - Test pass: {new_result.test_pass_rate:.2%}")
            print(f"[Mr. F]   - Speed: {new_result.speed_score:.2f}")
            print(f"[Mr. F]   - Quality: {new_result.code_quality_score:.2f}")
            print(f"[Mr. F]   - Safety: {new_result.safety_score:.2f}")
            print(f"[Mr. F]   - Improvement: {new_result.improvement_score:.2f}")

            if new_result.hallucination_penalty > 0:
                print(f"[Mr. F]   ⚠️ Hallucination penalty: -{new_result.hallucination_penalty:.2f}")

        except Exception as e:
            print(f"[Mr. F] Execution error: {e}")
            score_after = score_before
            new_result = current_result
            
            # Restore original
            with open(target_path, 'w') as f:
                f.write(backup_code)
        
        # Select (Accept/Reject)
        accepted = score_after >= score_before
        
        if accepted:
            print(f"[Mr. F] ACCEPTED: Score {score_before:.4f} → {score_after:.4f}")
            
            improved = self._update_best(score_after, memory['best'].get('version', 0) + 1, diff_text[:100])
            
            if improved:
                self._append_changelog(f"Code improvement (diff: {lines_changed} lines)", score_before, score_after)
            
            status = 'accepted'
        else:
            print(f"[Mr. F] REJECTED: Score regression {score_before:.4f} → {score_after:.4f}")
            
            # Restore original
            with open(target_path, 'w') as f:
                f.write(backup_code)
            
            status = 'rejected'
        
        # Save Artifacts
        result_dict = {
            'status': status,
            'score': score_after,
            'score_before': score_before,
            'score_delta': score_after - score_before,
            'runtime': new_result.execution_time,
            'lines_changed': lines_changed,
            'errors': new_result.error
        }
        
        self._save_run_artifacts(
            improve_prompt[:500],
            new_code[:500],
            diff_text,
            result_dict
        )
        
        # Log to Journal
        journal_entry = {
            'timestamp': timestamp,
            'score_before': score_before,
            'score_after': score_after,
            'accepted': accepted,
            'change_summary': f"{'Improved' if accepted else 'Rejected'} - {lines_changed} lines changed",
            'diff': diff_text,
            'error': new_result.error
        }
        self._append_to_journal(journal_entry)
        
        # Reflect
        print("[Mr. F] Generating reflection...")
        
        reflect_prompt = self._load_prompt('reflect')
        reflect_prompt = reflect_prompt.format(
            before=f"{score_before:.4f}",
            after=f"{score_after:.4f}",
            outcome='accepted' if accepted else 'rejected',
            diff=diff_text[:500],
            error=new_result.error or 'None'
        )
        
        reflection_text = self._call_llm(reflect_prompt)
        
        if reflection_text:
            try:
                if reflection_text.startswith('```json'):
                    reflection_text = reflection_text[7:-3]
                reflection = json.loads(reflection_text.strip())
            except Exception:
                reflection = {
                    'result': 'success' if accepted else 'failure',
                    'reason': reflection_text[:200],
                    'next_strategy': 'Continue with similar improvements' if accepted else 'Try different approach'
                }
            
            reflection['timestamp'] = timestamp
            self._append_reflection(reflection)
        
        # Update failures if rejected
        if not accepted and new_result.error:
            self._update_failures(new_result.error)

        # Update version stats
        self._update_version(accepted=accepted)

        # Log to trace system (comprehensive logging)
        trace_data = {
            'run_number': self.run_number,
            'score_before': score_before,
            'score_after': score_after,
            'score_delta': score_after - score_before,
            'status': status,
            'lines_changed': lines_changed,
            'execution_time': new_result.execution_time,
            'test_pass_rate': new_result.test_pass_rate,
            'code_quality_score': new_result.code_quality_score,
            'safety_score': new_result.safety_score,
            'improvement_score': new_result.improvement_score,
            'hallucination_penalty': new_result.hallucination_penalty,
            'error': new_result.error
        }
        log_evolution_iteration(self.runs_path, self.memory_path, trace_data)

        # Check iteration limits (early stopping)
        should_continue, reason, iter_status = check_iteration_limits(
            self.memory_path, accepted, score_after, score_before
        )
        print(f"\n{iter_status}")

        if not should_continue:
            print(f"\n⚠️ [Mr. F] ITERATION STOP: {reason}")
            print("[Mr. F] Consider resetting or adjusting parameters")

        # Commit Compression Check (every run, triggers at 29 commits)
        self._check_commit_compression()

        # Self-Improvement Check (every 10 runs - legacy)
        version = self._load_version()
        if version.get('total_runs', 0) > 0 and version.get('total_runs', 0) % 10 == 0:
            print("\n[Mr. F] === Self-Improvement Check (Legacy) ===")
            self._try_self_improve()
        
        # META-EVOLUTION TRIGGER (every 25 runs - deep evolution)
        self._trigger_meta_evolution_if_due()

        # Summary with trace dashboard
        print("\n[Mr. F] === Evolution Step Complete ===")
        print(f"[Mr. F] Status: {status.upper()}")
        print(f"[Mr. F] Score: {score_before:.4f} → {score_after:.4f} (Δ: {score_after - score_before:+.4f})")
        print(f"[Mr. F] Lines changed: {lines_changed}")
        print(f"[Mr. F] Run: {self.run_number}")
        print(f"[Mr. F] Iteration Health: {self.iteration_controller.get_status_report().split('Health: ')[-1].split()[0] if 'Health:' in self.iteration_controller.get_status_report() else 'unknown'}")

        # Generate session journal entry
        try:
            from session_journal import generate_session_journal
            if generate_session_journal(self.memory_path, self.base_path):
                print("[Mr. F] 📝 Session journal entry generated")
        except Exception as e:
            print(f"[Mr. F] ⚠️ Journal generation failed: {e}")

        # Show trace dashboard every 5 runs
        if self.run_number % 5 == 0:
            print(f"\n{get_trace_dashboard(self.runs_path, self.memory_path)}")

        self.run_number += 1

        return result_dict
    
    def _try_self_improve(self):
        """Attempt to improve the evolution system itself (legacy - uses new meta-evolution)."""
        print("\n[Mr. F] === META-EVOLUTION TRIGGERED ===")
        print("[Mr. F] This is where the agent evolves ITS OWN capabilities")
        
        try:
            # Get evolution candidates
            candidates = self.meta_evolution.get_self_improvement_candidates()
            
            if candidates:
                print(f"[Mr. F] Identified {len(candidates)} improvement candidates:")
                for c in candidates:
                    print(f"  - {c['file']}: {c['reason']} (priority: {c['priority']})")
                
                # Try to evolve highest priority candidate
                top_candidate = candidates[0]
                print(f"\n[Mr. F] Attempting to evolve {top_candidate['file']}...")
                
                memory = self._load_memory()
                failures = memory.get('failures', {})
                
                success, message, _ = self.meta_evolution.evolve_self(
                    top_candidate['file'],
                    self._call_llm,
                    evaluate,
                    metrics={'run_number': self.run_number},
                    failures=failures
                )
                
                if success:
                    print(f"[Mr. F] ✅ META-EVOLUTION SUCCESSFUL: {message}")
                    print("[Mr. F] The agent has evolved its own capabilities!")
                else:
                    print(f"[Mr. F] ⚠️ Meta-evolution rejected: {message}")
            else:
                print("[Mr. F] No self-improvement candidates identified")
                print("[Mr. F] System is operating optimally")
        
        except Exception as e:
            print(f"[Mr. F] Meta-evolution error: {e}")
        
        # Also trigger legacy self-improvement as fallback
        try:
            from self_improve import SelfImprover
            improver = SelfImprover(self.base_path)

            memory = self._load_memory()
            failures = memory.get('failures', {})

            if failures.get('syntax_error', 0) > 3:
                print("[Mr. F] High syntax errors - improving validator...")
                self._improve_system_file('evaluator.py', 'syntax_validation')
            elif failures.get('timeout', 0) > 3:
                print("[Mr. F] High timeouts - improving efficiency...")
                self._improve_system_file('runner.py', 'timeout_handling')
            else:
                print("[Mr. F] Improving runner efficiency...")
                self._improve_system_file('runner.py', 'general')

        except Exception as e:
            print(f"[Mr. F] Legacy self-improvement error: {e}")

    def _improve_system_file(self, file_name, focus):
        """Improve a specific system file (legacy method)."""
        try:
            from self_improve import SelfImprover
            improver = SelfImprover(self.base_path)

            if not improver.can_improve(file_name):
                print(f"[Mr. F] Cannot improve {file_name} - immutable")
                return

            current_code = improver.get_current_system_code(file_name)

            metrics = {
                'focus': focus,
                'total_runs': self._load_version().get('total_runs', 0),
                'memory': self._load_memory()
            }

            prompt = improver.get_improvement_prompt(file_name, current_code, metrics)
            improved_code = self._call_llm(prompt)

            if not improved_code:
                print(f"[Mr. F] No improvement generated for {file_name}")
                return

            is_valid, error = improver.validate_system_code(file_name, improved_code)
            if not is_valid:
                print(f"[Mr. F] Improvement rejected - syntax error: {error}")
                improver.log_self_improvement(file_name, False, f'Syntax error: {error}')
                return

            backup_path = improver.save_improved_code(file_name, improved_code)

            success, test_error = improver.test_system_after_change(file_name)
            if not success:
                print(f"[Mr. F] Improvement failed tests - {test_error}")
                improver.restore_backup(backup_path)
                improver.log_self_improvement(file_name, False, f'Test failed: {test_error}')
                return

            improver.cleanup_backup(backup_path)
            improver.log_self_improvement(file_name, True, f'Improved {focus}')
            print(f"[Mr. F] ✅ Self-improvement successful: {file_name}")

        except Exception as e:
            print(f"[Mr. F] Self-improvement failed: {e}")

    def _check_commit_compression(self):
        """Check and run commit compression if needed."""
        try:
            from commit_compressor import check_and_compress
            check_and_compress(self.base_path)
        except Exception as e:
            print(f"[Mr. F] Compression check failed: {e}")
    
    def _trigger_meta_evolution_if_due(self):
        """Trigger meta-evolution if enough runs have passed."""
        if self.run_number > 0 and self.run_number % self.self_evolve_interval == 0:
            print(f"\n🧬 [Mr. F] === META-EVOLUTION TRIGGER (Run {self.run_number}) ===")
            print(f"[Mr. F] Every {self.self_evolve_interval} runs, the agent evolves itself")
            self._try_self_improve()


def main():
    """Main entry point."""
    runner = EvolutionRunner()
    result = runner.run_evolution_step()
    sys.exit(0 if result['status'] == 'accepted' else 1)


if __name__ == '__main__':
    main()
