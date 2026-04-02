"""
Semantic Memory Retrieval with Embeddings

Upgrades keyword-based retrieval with semantic similarity:
- Lightweight sentence embeddings
- Cosine similarity search
- Relevance scoring
- Memory decay (old memories fade)

Uses sentence-transformers if available, falls back to hash-based similarity.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta


class SemanticMemoryRetriever:
    """Semantic memory retrieval with embeddings."""
    
    def __init__(self, memory_path, use_embeddings=True):
        self.memory_path = memory_path
        self.use_embeddings = use_embeddings
        self.embedding_model = None
        self.memory_index = []
        self.embeddings_cache = {}
        
        # Try to load sentence-transformers
        if use_embeddings:
            try:
                from sentence_transformers import SentenceTransformer
                self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
                print("[Mr. F] Semantic memory: Using sentence-transformers")
            except ImportError:
                print("[Mr. F] Semantic memory: Falling back to hash-based similarity")
                self.use_embeddings = False
        
        # Load memory index
        self._build_memory_index()
    
    def _build_memory_index(self):
        """Build index of all memories."""
        self.memory_index = []
        
        # Index journal entries
        journal_path = os.path.join(self.memory_path, 'journal.jsonl')
        try:
            with open(journal_path, 'r') as f:
                for i, line in enumerate(f):
                    if line.strip():
                        entry = json.loads(line)
                        text = entry.get('change_summary', '')
                        if text:
                            self.memory_index.append({
                                'id': f'journal_{i}',
                                'text': text,
                                'source': 'journal',
                                'timestamp': entry.get('timestamp', ''),
                                'accepted': entry.get('accepted', False),
                                'score_after': entry.get('score_after', 0)
                            })
        except Exception:
            pass
        
        # Index reflections
        reflections_path = os.path.join(self.memory_path, 'reflections.jsonl')
        try:
            with open(reflections_path, 'r') as f:
                for i, line in enumerate(f):
                    if line.strip():
                        entry = json.loads(line)
                        text = entry.get('reason', '') + ' ' + entry.get('next_strategy', '')
                        if text.strip():
                            self.memory_index.append({
                                'id': f'reflection_{i}',
                                'text': text.strip(),
                                'source': 'reflection',
                                'timestamp': entry.get('timestamp', ''),
                                'result': entry.get('result', '')
                            })
        except Exception:
            pass
        
        # Compute embeddings for all memories
        self._compute_all_embeddings()
    
    def _compute_all_embeddings(self):
        """Compute embeddings for all indexed memories."""
        if not self.use_embeddings or not self.embedding_model:
            return
        
        texts = [m['text'] for m in self.memory_index]
        if texts:
            embeddings = self.embedding_model.encode(texts, convert_to_numpy=True)
            for i, memory in enumerate(self.memory_index):
                memory['embedding'] = embeddings[i].tolist()
    
    def _compute_embedding(self, text):
        """Compute embedding for a single text."""
        if not self.use_embeddings or not self.embedding_model:
            return None
        
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        embedding = self.embedding_model.encode([text], convert_to_numpy=True)[0]
        self.embeddings_cache[text] = embedding.tolist()
        return embedding
    
    def _cosine_similarity(self, emb1, emb2):
        """Compute cosine similarity between two embeddings."""
        import numpy as np
        emb1 = np.array(emb1)
        emb2 = np.array(emb2)
        
        norm1 = np.linalg.norm(emb1)
        norm2 = np.linalg.norm(emb2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return np.dot(emb1, emb2) / (norm1 * norm2)
    
    def retrieve(self, query, top_k=5, min_relevance=0.3):
        """
        Retrieve relevant memories for query.
        
        Args:
            query: Query text
            top_k: Number of results to return
            min_relevance: Minimum relevance threshold
        
        Returns:
            list: Relevant memories with scores
        """
        if not self.memory_index:
            return []
        
        if self.use_embeddings and self.embedding_model:
            # Semantic retrieval
            query_embedding = self._compute_embedding(query)
            if query_embedding is None:
                return self._keyword_retrieve(query, top_k)
            
            results = []
            for memory in self.memory_index:
                if 'embedding' not in memory:
                    continue
                
                similarity = self._cosine_similarity(query_embedding, memory['embedding'])
                
                # Apply time decay (recent memories weighted higher)
                time_weight = self._get_time_weight(memory.get('timestamp', ''))
                weighted_score = similarity * time_weight
                
                if weighted_score >= min_relevance:
                    results.append({
                        **memory,
                        'relevance_score': weighted_score,
                        'similarity': similarity,
                        'time_weight': time_weight
                    })
            
            # Sort by relevance and return top_k
            results.sort(key=lambda x: x['relevance_score'], reverse=True)
            return results[:top_k]
        
        else:
            # Fallback to keyword retrieval
            return self._keyword_retrieve(query, top_k)
    
    def _get_time_weight(self, timestamp_str):
        """Calculate time-based weight (recent = higher weight)."""
        if not timestamp_str:
            return 0.5
        
        try:
            timestamp = datetime.fromisoformat(timestamp_str)
            age = datetime.now() - timestamp
            days_old = age.days
            
            # Decay: 1.0 for today, 0.5 for 7 days old, 0.25 for 14 days
            return max(0.1, 1.0 / (1 + days_old / 7))
        except Exception:
            return 0.5
    
    def _keyword_retrieve(self, query, top_k):
        """Fallback keyword-based retrieval."""
        query_words = set(query.lower().split())
        
        results = []
        for memory in self.memory_index:
            text_words = set(memory['text'].lower().split())
            overlap = len(query_words & text_words)
            
            if overlap > 0:
                results.append({
                    **memory,
                    'relevance_score': overlap / max(len(query_words), 1),
                    'similarity': overlap / max(len(query_words), 1),
                    'time_weight': self._get_time_weight(memory.get('timestamp', ''))
                })
        
        results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return results[:top_k]
    
    def get_context_for_prompt(self, query, top_k=5):
        """Get formatted memory context for LLM prompt."""
        memories = self.retrieve(query, top_k=top_k)
        
        if not memories:
            return "No relevant memories found."
        
        parts = []
        
        # Group by type
        successes = [m for m in memories if m.get('accepted', False) or m.get('result') == 'success']
        failures = [m for m in memories if not m.get('accepted', False) or m.get('result') == 'failure']
        
        if successes:
            parts.append("### ✅ Relevant Successes")
            for m in successes[:3]:
                parts.append(f"- {m['text']} (relevance: {m['relevance_score']:.2f})")
        
        if failures:
            parts.append("\n### ⚠️ Relevant Failures to Avoid")
            for m in failures[:3]:
                parts.append(f"- {m['text']} (relevance: {m['relevance_score']:.2f})")
        
        return '\n'.join(parts)
    
    def add_memory(self, text, metadata=None):
        """Add a new memory to the index."""
        memory = {
            'id': f'new_{len(self.memory_index)}',
            'text': text,
            'source': 'runtime',
            'timestamp': datetime.now().isoformat(),
        }
        
        # Add metadata
        if metadata:
            memory.update(metadata)
        
        if self.use_embeddings and self.embedding_model:
            embedding = self._compute_embedding(text)
            if embedding:
                memory['embedding'] = embedding
        
        self.memory_index.append(memory)
        return memory
    
    def clear_cache(self):
        """Clear embeddings cache."""
        self.embeddings_cache = {}


def get_semantic_context(memory_path, query, top_k=5):
    """Get semantic memory context for prompt."""
    retriever = SemanticMemoryRetriever(memory_path)
    return retriever.get_context_for_prompt(query, top_k)


def retrieve_memories(memory_path, query, top_k=5):
    """Retrieve relevant memories."""
    retriever = SemanticMemoryRetriever(memory_path)
    return retriever.retrieve(query, top_k)
