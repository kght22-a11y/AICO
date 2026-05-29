import json
import os
import time
import re

class BioLogManager:
    """
    Handles 'Rolling Context' and 'Long-Term Bio-Log' archiving.
    Focus: Cut-and-paste persistence (Phase 1).
    """
    def __init__(self, context_file="active_context.json", archive_file="biolog.ndjson", stash_file="last_stash.json"):
        self.context_file = context_file
        self.archive_file = archive_file
        self.stash_file = stash_file
        self.max_chars = 4000
        self.context = self.load_context()

    def load_context(self):
        if os.path.exists(self.context_file):
            try:
                with open(self.context_file, "r") as f:
                    return json.load(f)
            except: pass
        return {"history": []}

    def save_context(self):
        with open(self.context_file, "w") as f:
            json.dump(self.context, f, indent=2)

    def add_entry(self, user_input, ai_output):
        entry = {"timestamp": time.time(), "user": user_input, "ai": ai_output}
        self.context["history"].append(entry)
        
        # Check for overflow
        full_text = self.get_full_text()
        if len(full_text) > self.max_chars:
            self.archive_oldest()
        
        self.save_context()

    def get_full_text(self):
        return "\n".join([f"USER: {e['user']}\nAI: {e['ai']}" for e in self.context["history"]])

    def archive_oldest(self):
        """Cut-and-paste the oldest entry to the Bio-Log."""
        if not self.context["history"]: return
        
        oldest = self.context["history"].pop(0)
        print(f"[BioLog] Archiving entry from {oldest['timestamp']}")
        
        with open(self.archive_file, "a") as f:
            f.write(json.dumps(oldest) + "\n")

    def get_context_for_llm(self):
        return self.get_full_text()

    def clear_context(self):
        """Stashes current context and clears active memory."""
        if self.context["history"]:
            with open(self.stash_file, "w") as f:
                json.dump(self.context, f, indent=2)
        self.context = {"history": []}
        self.save_context()

    def restore_context(self):
        """Restores the last stashed context."""
        if os.path.exists(self.stash_file):
            try:
                with open(self.stash_file, "r") as f:
                    self.context = json.load(f)
                self.save_context()
                return True
            except: pass
        return False

    def get_ghost_memories(self, query, limit=3):
        """
        Phase 4: Ghost Memories (Keyword-based RAG).
        Scans biolog.ndjson for relevant past interactions.
        """
        if not os.path.exists(self.archive_file):
            return []
        
        # Simple keyword extraction (words > 4 chars)
        keywords = [w.lower() for w in re.findall(r'\w+', query) if len(w) > 4]
        if not keywords:
            return []
            
        matches = []
        try:
            with open(self.archive_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    text = (entry.get("prompt", "") + " " + entry.get("response", "")).lower()
                    
                    score = sum(1 for k in keywords if k in text)
                    if score > 0:
                        matches.append((score, entry))
            
            # Sort by keyword density and take top N
            matches.sort(key=lambda x: x[0], reverse=True)
            return [m[1] for m in matches[:limit]]
        except:
            return []

if __name__ == "__main__":
    bl = BioLogManager(context_file="test_context.json", archive_file="test_biolog.ndjson")
    bl.add_entry("Hello", "Hi there!")
    print("Context:", bl.get_context_for_llm())
