"""
Session Journal Generator

Auto-generates session summaries for JOURNAL.md after each run.
Inspired by yoyo-evolve's journaling system.
"""

import os
import json
from datetime import datetime


class SessionJournal:
    """Generate session journal entries."""
    
    def __init__(self, memory_path, core_path):
        self.memory_path = memory_path
        self.core_path = core_path
        self.journal_path = os.path.join(core_path, 'JOURNAL.md')
        self.day_count_path = os.path.join(core_path, 'DAY_COUNT')
    
    def get_day_count(self):
        """Get current day count."""
        try:
            with open(self.day_count_path, 'r') as f:
                return int(f.read().strip())
        except Exception:
            return 1
    
    def increment_day(self):
        """Increment day count."""
        day = self.get_day_count()
        day += 1
        with open(self.day_count_path, 'w') as f:
            f.write(str(day))
        return day
    
    def get_latest_run(self):
        """Get latest run result."""
        result_path = os.path.join(self.memory_path, '..', 'runs', 'latest', 'result.json')
        try:
            with open(result_path, 'r') as f:
                return json.load(f)
        except Exception:
            return None
    
    def get_latest_diff(self):
        """Get latest diff."""
        diff_path = os.path.join(self.memory_path, '..', 'runs', 'latest', 'diff.txt')
        try:
            with open(diff_path, 'r') as f:
                return f.read()
        except Exception:
            return ""
    
    def generate_entry(self, result, diff):
        """Generate a journal entry."""
        day = self.get_day_count()
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        status = result.get('status', 'unknown') if result else 'unknown'
        score_before = result.get('score_before', 0) if result else 0
        score_after = result.get('score_after', 0) if result else 0
        lines_changed = result.get('lines_changed', 0) if result else 0
        
        # Generate headline
        if status == 'accepted':
            if score_after > score_before:
                headline = f"Score improved ({score_before:.4f} → {score_after:.4f})"
            else:
                headline = "Accepted (no regression)"
        else:
            headline = f"Rejected (score regression or constraint violation)"
        
        # Generate entry
        entry = f"""## Day {day} — {timestamp} — {headline}

"""
        
        if status == 'accepted':
            entry += f"""Session result: **accepted** with score {score_after:.4f}.

"""
            if lines_changed > 0:
                entry += f"""**Changes:** {lines_changed} lines modified.

"""
            else:
                entry += """**Changes:** No code changes (LLM failed or no improvement found).

"""
        else:
            entry += f"""Session result: **rejected**. Score would have decreased from {score_before:.4f} to {score_after:.4f}.

**Safety system worked correctly** — bad change was caught and reverted.

"""
        
        entry += """---

"""
        
        return entry
    
    def append_entry(self, entry):
        """Append entry to journal."""
        # Ensure journal exists
        if not os.path.exists(self.journal_path):
            with open(self.journal_path, 'w') as f:
                f.write("# Journal\n\n")

        # Read existing journal
        with open(self.journal_path, 'r') as f:
            content = f.read()

        # Find position after "---" (after header)
        separator = content.find("\n---\n")
        if separator == -1:
            # No separator found, append at end
            new_content = content + "\n" + entry
        else:
            # Insert new entry after the separator (add newline after ---)
            insert_pos = separator + 5  # After "\n---\n"
            new_content = content[:insert_pos] + "\n" + entry

        # Write back
        with open(self.journal_path, 'w') as f:
            f.write(new_content)
    
    def generate_and_append(self):
        """Generate entry and append to journal."""
        result = self.get_latest_run()
        diff = self.get_latest_diff()
        
        if not result:
            return False
        
        entry = self.generate_entry(result, diff)
        self.append_entry(entry)
        self.increment_day()
        
        return True


def generate_session_journal(memory_path, core_path):
    """Generate session journal entry."""
    journal = SessionJournal(memory_path, core_path)
    return journal.generate_and_append()


if __name__ == '__main__':
    # Test
    memory_path = os.path.join(os.path.dirname(__file__), '..', 'memory')
    core_path = os.path.join(os.path.dirname(__file__), '..')
    
    success = generate_session_journal(memory_path, core_path)
    if success:
        print("✅ Session journal entry generated")
    else:
        print("⚠️ No result found to journal")
