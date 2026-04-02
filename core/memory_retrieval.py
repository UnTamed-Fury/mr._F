"""
Operational Memory Retrieval System

Provides keyword-based retrieval from memory:
- Journal retrieval
- Failure pattern matching
- Summary relevance scoring
- Reflection search

Simple implementation first - upgrade to embeddings if needed.
"""

import os
import json
import re
from collections import Counter


class MemoryRetriever:
    """Retrieves relevant memories based on context."""
    
    def __init__(self, memory_path):
        self.memory_path = memory_path
        self.journal_path = os.path.join(memory_path, 'journal.jsonl')
        self.failures_path = os.path.join(memory_path, 'failures.json')
        self.summaries_path = os.path.join(memory_path, 'summaries.json')
        self.reflections_path = os.path.join(memory_path, 'reflections.jsonl')
    
    def get_relevant_memory(self, current_context=None, code=None, limit=5):
        """
        Get relevant memory for current context.
        
        Args:
            current_context: Optional context string
            code: Current code being evaluated
            limit: Max entries to return
        
        Returns:
            dict: Relevant memories organized by type
        """
        relevant = {
            'recent_failures': self.get_recent_failures(limit=3),
            'success_patterns': self.get_success_patterns(limit=3),
            'recent_reflections': self.get_recent_reflections(limit=3),
            'keyword_matches': []
        }
        
        # Add keyword-based retrieval if context provided
        if current_context:
            relevant['keyword_matches'] = self.search_by_keywords(
                current_context, limit=limit
            )
        
        # Add code-based retrieval if code provided
        if code:
            relevant['code_similar'] = self.find_similar_code_changes(
                code, limit=2
            )
        
        return relevant
    
    def get_recent_failures(self, limit=5):
        """Get recent failure patterns."""
        try:
            with open(self.failures_path, 'r') as f:
                failures = json.load(f)
            
            # Return failures that occurred more than once
            significant = {k: v for k, v in failures.items() if v >= 1}
            
            # Sort by count
            sorted_failures = sorted(
                significant.items(),
                key=lambda x: x[1],
                reverse=True
            )[:limit]
            
            return [
                {'type': k, 'count': v, 'warning': f"Avoid {k} (failed {v} times)"}
                for k, v in sorted_failures
            ]
        except Exception:
            return []
    
    def get_success_patterns(self, limit=5):
        """Get success patterns from summaries."""
        try:
            with open(self.summaries_path, 'r') as f:
                summaries = json.load(f)
            
            patterns = []
            for summary in summaries[-limit:]:
                if 'successful_patterns' in summary:
                    patterns.extend(summary['successful_patterns'])
            
            return patterns[:limit]
        except Exception:
            return []
    
    def get_recent_reflections(self, limit=5):
        """Get recent reflections."""
        try:
            reflections = []
            with open(self.reflections_path, 'r') as f:
                for line in f:
                    if line.strip():
                        reflections.append(json.loads(line))
            
            # Return most recent
            recent = reflections[-limit:]
            
            return [
                {
                    'result': r.get('result', 'unknown'),
                    'reason': r.get('reason', '')[:100],
                    'next_strategy': r.get('next_strategy', '')
                }
                for r in recent
            ][::-1]  # Most recent first
        except Exception:
            return []
    
    def search_by_keywords(self, query, limit=5):
        """Search memory by keywords."""
        matches = []
        
        # Extract keywords from query
        keywords = self._extract_keywords(query)
        
        if not keywords:
            return []
        
        # Search journal
        try:
            with open(self.journal_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        score = self._score_entry(entry, keywords)
                        if score > 0:
                            matches.append({
                                'source': 'journal',
                                'content': entry.get('change_summary', ''),
                                'score': score,
                                'accepted': entry.get('accepted', False)
                            })
        except Exception:
            pass
        
        # Sort by score and return top matches
        matches.sort(key=lambda x: x['score'], reverse=True)
        return matches[:limit]
    
    def find_similar_code_changes(self, code, limit=3):
        """Find similar code changes from history."""
        # Extract function names from current code
        current_funcs = self._extract_function_names(code)
        
        similar = []
        
        try:
            with open(self.journal_path, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        diff = entry.get('diff', '')
                        
                        # Check if diff mentions similar functions
                        for func in current_funcs:
                            if func in diff.lower():
                                similar.append({
                                    'source': 'journal',
                                    'summary': entry.get('change_summary', ''),
                                    'accepted': entry.get('accepted', False),
                                    'score': entry.get('score_after', 0)
                                })
                                break
        except Exception:
            pass
        
        return similar[:limit]
    
    def _extract_keywords(self, text):
        """Extract meaningful keywords from text."""
        # Remove common words
        stop_words = {
            'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'shall',
            'can', 'need', 'to', 'of', 'in', 'for', 'on', 'with', 'at',
            'by', 'from', 'as', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'between', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where',
            'why', 'how', 'all', 'each', 'few', 'more', 'most', 'other',
            'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same',
            'so', 'than', 'too', 'very', 'just', 'and', 'but', 'if', 'or'
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Filter stop words
        keywords = [w for w in words if w not in stop_words]
        
        # Count frequency
        return list(set(keywords))  # Unique keywords
    
    def _score_entry(self, entry, keywords):
        """Score an entry based on keyword matches."""
        text = ' '.join([
            entry.get('change_summary', ''),
            entry.get('error', '') or '',
        ]).lower()
        
        score = 0
        for keyword in keywords:
            if keyword in text:
                score += 1
        
        return score
    
    def _extract_function_names(self, code):
        """Extract function names from code."""
        pattern = r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\('
        return re.findall(pattern, code)
    
    def get_context_for_prompt(self, limit=5):
        """
        Build memory context for LLM prompt.
        
        Returns formatted string ready for injection.
        """
        relevant = self.get_relevant_memory(limit=limit)
        
        parts = []
        
        # Add recent failures
        if relevant['recent_failures']:
            parts.append("### ⚠️ Recent Failures to Avoid")
            for f in relevant['recent_failures']:
                parts.append(f"- {f['warning']}")
        
        # Add success patterns
        if relevant['success_patterns']:
            parts.append("\n### ✅ Patterns That Work")
            for p in relevant['success_patterns']:
                parts.append(f"- {p}")
        
        # Add recent reflections
        if relevant['recent_reflections']:
            parts.append("\n### 💡 Recent Insights")
            for r in relevant['recent_reflections']:
                parts.append(f"- [{r['result']}] {r['next_strategy']}")
        
        # Add keyword matches
        if relevant.get('keyword_matches'):
            parts.append("\n### 🔍 Relevant History")
            for m in relevant['keyword_matches'][:3]:
                status = "✅" if m['accepted'] else "❌"
                parts.append(f"- {status} {m['content']}")
        
        return '\n'.join(parts) if parts else "No relevant memory context available."


def get_memory_context(memory_path, code=None):
    """Get formatted memory context for prompt injection."""
    retriever = MemoryRetriever(memory_path)
    return retriever.get_context_for_prompt()


def search_memory(memory_path, query, limit=5):
    """Search memory by query."""
    retriever = MemoryRetriever(memory_path)
    return retriever.search_by_keywords(query, limit)
