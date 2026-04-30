import json
import os


class Database:
    def __init__(self, filename="algorithms.json"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, 'w') as f:
                json.dump([], f)

    def get_all(self):
        with open(self.filename, 'r') as f:
            return json.load(f)

    def save(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def search(self, criteria, contest_mode, settings):
        all_algos = self.get_all()
        results = []
        
        # New: Favorite filter
        if criteria.get("fav_only"):
            all_algos = [a for a in all_algos if a.get("is_favorite")]
        
        name_q = criteria.get("name", "").lower()
        tag_q = criteria.get("tag", "").lower()
        comp_q = criteria.get("complexity", "").lower()

        for algo in all_algos:
            # 1. Name Filter (Always active)
            # Handles "Exact Name" logic from settings if contest_mode is active
            if contest_mode and settings.get("exact_name_only", True):
                if name_q and name_q != algo['name'].lower(): continue
            else:
                if name_q and name_q not in algo['name'].lower(): continue

            # 2. Skip other filters if in Contest Mode
            if not contest_mode:
                # Tag Filter
                if tag_q:
                    tags_str = " ".join(algo.get('tags', [])).lower()
                    if tag_q not in tags_str: continue

                # Complexity Filter
                if comp_q and comp_q not in algo.get('complexity', '').lower(): continue
            
            results.append(algo)
        return results