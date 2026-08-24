from typing import Dict, List, Set, Tuple

class EntityGraph:
    """Knowledge Graph store representing extracted facts as (subject, predicate, object) triples."""
    def __init__(self):
        self._triples: List[Tuple[str, str, str]] = []
        self._nodes: Set[str] = set()

    def add_triple(self, subject: str, predicate: str, obj: str):
        sub = subject.strip().lower()
        pred = predicate.strip().lower()
        target = obj.strip().lower()
        triple = (sub, pred, target)
        if triple not in self._triples:
            self._triples.append(triple)
            self._nodes.add(sub)
            self._nodes.add(target)

    def query_entity(self, entity: str) -> List[Dict[str, str]]:
        ent = entity.strip().lower()
        results = []
        for s, p, o in self._triples:
            if s == ent or o == ent:
                results.append({"subject": s, "predicate": p, "object": o})
        return results

    def extract_from_text(self, text: str) -> List[Tuple[str, str, str]]:
        """Heuristic rule-based entity triple extractor for user facts."""
        extracted = []
        t = text.lower().strip()
        if "prefer" in t:
            # e.g., "I prefer python over typescript" -> extract python
            parts = t.split("prefer")[-1].split("over")[0].strip()
            extracted.append(("user", "prefers", parts))
        elif "favorite" in t:
            parts = t.split("favorite")[-1].replace("is", "").strip(". ")
            extracted.append(("user", "favorite", parts))
            
        if "live in" in t or "located in" in t:
            loc = t.split("live in")[-1].split("located in")[-1].strip(". ")
            extracted.append(("user", "location", loc))
        if "works at" in t or "work at" in t:
            company = t.split("work at")[-1].split("works at")[-1].strip(". ")
            extracted.append(("user", "works_at", company))
            
        for s, p, o in extracted:
            self.add_triple(s, p, o)
        return extracted

    def all_triples(self) -> List[Dict[str, str]]:
        return [{"subject": s, "predicate": p, "object": o} for s, p, o in self._triples]
