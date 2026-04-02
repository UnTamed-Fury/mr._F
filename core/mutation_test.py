"""
Mutation Testing for Test Suite

Tests the test suite itself by introducing small mutations
and verifying tests catch them.
Inspired by yoyo-evolve's cargo-mutants usage.
"""

import os
import sys
import copy
import random


class MutationTester:
    """Test the test suite by mutating code."""
    
    def __init__(self, workspace_path):
        self.workspace_path = workspace_path
        self.mutations_tried = 0
        self.mutations_caught = 0
        self.mutations_survived = 0
    
    def run_mutation_testing(self, test_module, target_module):
        """
        Run mutation testing on target module using test module.
        
        Args:
            test_module: Module containing tests
            target_module: Module to mutate and test
        
        Returns:
            dict: Mutation testing results
        """
        results = {
            'total_mutations': 0,
            'caught': 0,
            'survived': 0,
            'mutation_score': 0.0,
            'details': []
        }
        
        # Get original code
        target_path = os.path.join(self.workspace_path, target_module)
        test_path = os.path.join(self.workspace_path, test_module)
        
        if not os.path.exists(target_path) or not os.path.exists(test_path):
            results['error'] = 'Files not found'
            return results
        
        # Read original code
        with open(target_path, 'r') as f:
            original_code = f.read()
        
        # Generate mutations
        mutations = self._generate_mutations(original_code)
        
        # Test each mutation
        for mutation in mutations:
            self.mutations_tried += 1
            results['total_mutations'] += 1
            
            # Write mutated code
            with open(target_path, 'w') as f:
                f.write(mutation['mutated_code'])
            
            # Run tests
            test_passed = self._run_tests(test_path)
            
            if not test_passed:
                # Mutation was caught!
                self.mutations_caught += 1
                results['caught'] += 1
                results['details'].append({
                    'type': mutation['type'],
                    'caught': True,
                    'description': mutation['description']
                })
            else:
                # Mutation survived - test suite weakness
                self.mutations_survived += 1
                results['survived'] += 1
                results['details'].append({
                    'type': mutation['type'],
                    'caught': False,
                    'description': mutation['description'],
                    'warning': 'Test suite did not catch this mutation!'
                })
            
            # Restore original
            with open(target_path, 'w') as f:
                f.write(original_code)
        
        # Calculate mutation score
        if results['total_mutations'] > 0:
            results['mutation_score'] = results['caught'] / results['total_mutations']
        
        return results
    
    def _generate_mutations(self, code):
        """Generate code mutations."""
        mutations = []
        lines = code.split('\n')
        
        # Mutation 1: Change operators
        operator_mutations = [
            ('+', '-'),
            ('-', '+'),
            ('*', '/'),
            ('<', '>'),
            ('<=', '>='),
            ('==', '!='),
        ]
        
        for i, line in enumerate(lines):
            for old_op, new_op in operator_mutations:
                if old_op in line and not line.strip().startswith('#'):
                    mutated = line.replace(old_op, new_op, 1)
                    mutated_code = '\n'.join(
                        lines[:i] + [mutated] + lines[i+1:]
                    )
                    mutations.append({
                        'type': 'operator_replacement',
                        'line': i,
                        'mutated_code': mutated_code,
                        'description': f'Changed {old_op} to {new_op} on line {i+1}'
                    })
        
        # Mutation 2: Change return values
        for i, line in enumerate(lines):
            if 'return' in line and not line.strip().startswith('#'):
                # Change return True to return False, etc.
                if 'return True' in line:
                    mutated = line.replace('return True', 'return False')
                    mutated_code = '\n'.join(
                        lines[:i] + [mutated] + lines[i+1:]
                    )
                    mutations.append({
                        'type': 'boolean_flip',
                        'line': i,
                        'mutated_code': mutated_code,
                        'description': f'Flipped boolean return on line {i+1}'
                    })
                elif 'return False' in line:
                    mutated = line.replace('return False', 'return True')
                    mutated_code = '\n'.join(
                        lines[:i] + [mutated] + lines[i+1:]
                    )
                    mutations.append({
                        'type': 'boolean_flip',
                        'line': i,
                        'mutated_code': mutated_code,
                        'description': f'Flipped boolean return on line {i+1}'
                    })
                elif 'return 0' in line:
                    mutated = line.replace('return 0', 'return 1')
                    mutated_code = '\n'.join(
                        lines[:i] + [mutated] + lines[i+1:]
                    )
                    mutations.append({
                        'type': 'zero_flip',
                        'line': i,
                        'mutated_code': mutated_code,
                        'description': f'Changed return 0 to return 1 on line {i+1}'
                    })
        
        # Mutation 3: Remove condition
        for i, line in enumerate(lines):
            stripped = line.strip()
            if stripped.startswith('if ') and stripped.endswith(':'):
                # Comment out this line
                mutated = '# ' + line
                mutated_code = '\n'.join(
                    lines[:i] + [mutated] + lines[i+1:]
                )
                mutations.append({
                    'type': 'condition_removal',
                    'line': i,
                    'mutated_code': mutated_code,
                    'description': f'Commented out condition on line {i+1}'
                })
        
        # Limit mutations for performance
        return mutations[:20]
    
    def _run_tests(self, test_path):
        """Run tests and return True if all pass."""
        import subprocess
        
        try:
            result = subprocess.run(
                [sys.executable, test_path],
                cwd=self.workspace_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def get_mutation_report(self, results):
        """Generate human-readable mutation report."""
        report = []
        report.append("=== Mutation Testing Report ===\n")
        report.append(f"Total Mutations: {results['total_mutations']}")
        report.append(f"Caught: {results['caught']}")
        report.append(f"Survived: {results['survived']}")
        report.append(f"Mutation Score: {results['mutation_score']:.2%}")
        report.append("")
        
        if results['survived'] > 0:
            report.append("⚠️ SURVIVED MUTATIONS (Test Suite Weaknesses):")
            report.append("-" * 40)
            for detail in results['details']:
                if not detail['caught']:
                    report.append(f"- {detail['description']}")
                    report.append(f"  Type: {detail['type']}")
                    if 'warning' in detail:
                        report.append(f"  ⚠️ {detail['warning']}")
            report.append("")
        
        report.append("✅ CAUGHT MUTATIONS:")
        report.append("-" * 40)
        for detail in results['details']:
            if detail['caught']:
                report.append(f"- {detail['description']}")
        
        return '\n'.join(report)
