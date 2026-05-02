import json
import os


class Database:
    def __init__(self, filename="app/algorithms.json"):
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
        
        if criteria.get("fav_only"):
            all_algos = [a for a in all_algos if a.get("is_favorite")]
        
        name_q = criteria.get("name", "").lower()
        cat_q = criteria.get("category", "").lower()
        tag_q = criteria.get("tag", "").lower()

        for algo in all_algos:
            # Name Filter
            if name_q and name_q not in algo['name'].lower(): continue

            # Category Filter (Exact string match)
            if cat_q and cat_q != algo.get('category', '').lower(): continue

            # Tags Filter (Check if keyword is in tag list)
            if tag_q and tag_q not in " ".join(algo.get('tags', [])).lower(): continue

            if not contest_mode:
                comp_q = criteria.get("complexity", "").lower()
                if comp_q and comp_q not in algo.get('complexity', '').lower(): continue
            
            results.append(algo)
        return results