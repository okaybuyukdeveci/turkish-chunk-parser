from typing import List, Dict


def load_conllu(filepath: str) -> List[List[Dict]]:
    sentences = []
    current = []
    with open(filepath, encoding="utf-8") as f:
        for line in f:
            line = line.rstrip("\n")
            if line.startswith("#"):
                continue
            if line == "":
                if current:
                    sentences.append(current)
                    current = []
                continue
            parts = line.split("\t")
            if len(parts) < 10:
                continue
            token_id = parts[0]
            # multiword token (örn. "1-2") veya boş node ("1.1") → atla
            if "-" in token_id or "." in token_id:
                continue
            try:
                head = int(parts[6]) if parts[6] != "_" else 0
            except ValueError:
                head = 0
            current.append({
                "id": int(token_id),
                "form": parts[1],
                "lemma": parts[2],
                "upos": parts[3],
                "xpos": parts[4],
                "feats": parts[5],
                "head": head,
                "deprel": parts[7],
            })
    if current:
        sentences.append(current)
    return sentences
