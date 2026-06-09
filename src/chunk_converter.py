from typing import List, Dict, Tuple

NP_UPOS = {"NOUN", "PROPN", "PRON", "NUM"}
NP_DEPREL = {"nsubj", "obj", "iobj", "obl", "nmod", "nsubj:pass",
             "obl:tmod", "obl:agent", "appos", "flat", "flat:name",
             "compound", "det", "nummod", "case"}
VP_UPOS = {"VERB", "AUX"}
VP_DEPREL = {"root", "aux", "aux:pass", "cop", "compound:redup", "xcomp", "ccomp", "parataxis"}
ADVP_UPOS = {"ADV"}
ADVP_DEPREL = {"advmod", "discourse"}
ADJP_UPOS = {"ADJ"}
ADJP_DEPREL = {"amod"}

# acl / acl:relcl → INNER=RELCL, CLAUSE=RELCL
RELCL_DEPREL = {"acl", "acl:relcl"}
# advcl, csubj → CLAUSE=COMPCL
COMPCL_DEPREL = {"advcl", "csubj", "csubj:pass"}


def _get_chunk_type(token: Dict) -> str:
    upos = token["upos"]
    deprel = token["deprel"]

    if upos in VP_UPOS or deprel in VP_DEPREL:
        return "VP"
    if upos in NP_UPOS or deprel in NP_DEPREL:
        return "NP"
    if upos in ADVP_UPOS or deprel in ADVP_DEPREL:
        return "ADVP"
    if upos in ADJP_UPOS or deprel in ADJP_DEPREL:
        return "ADJP"
    if deprel in RELCL_DEPREL:
        return "NP"
    return "O"


def _get_inner_clause(token: Dict, sentence: List[Dict]) -> Tuple[str, str]:
    """
    CHUNK-INNER ve CLAUSE sütunlarını döndürür.

    RELCL: token veya head'i acl:relcl olan gruba ait → B-RELCL / I-RELCL
    COMPCL: token veya head'i advcl/csubj olan gruba ait → B-COMPCL / I-COMPCL
    """
    deprel = token["deprel"]
    head_id = token["head"]

    head_deprel = ""
    if head_id > 0:
        # head_id 1-tabanlı, liste 0-tabanlı
        head_token = sentence[head_id - 1] if head_id <= len(sentence) else None
        if head_token:
            head_deprel = head_token["deprel"]

    # Token kendisi RELCL bağımlısı
    if deprel in RELCL_DEPREL:
        return "B-RELCL", "B-RELCL"
    # Token'ın head'i RELCL bağımlısı → bu token RELCL içinde
    if head_deprel in RELCL_DEPREL:
        return "I-RELCL", "I-RELCL"

    # Token kendisi COMPCL bağımlısı
    if deprel in COMPCL_DEPREL:
        return "_", "B-COMPCL"
    # Token'ın head'i COMPCL bağımlısı → bu token COMPCL içinde
    if head_deprel in COMPCL_DEPREL:
        return "_", "I-COMPCL"

    return "_", "O"


def convert_to_bio(sentences: List[List[Dict]]) -> List[List[Tuple]]:
    """
    Her cümle için (form, upos, deprel, outer, inner, clause) tuple listesi döndürür.
    outer:  B-NP, I-NP, B-VP, I-VP, B-ADVP, I-ADVP, B-ADJP, I-ADJP, O
    inner:  B-RELCL, I-RELCL, _ (iç içe öbek yoksa)
    clause: B-RELCL, I-RELCL, B-COMPCL, I-COMPCL, O
    """
    result = []
    for sentence in sentences:
        labeled = []
        prev_type = "O"
        for token in sentence:
            chunk_type = _get_chunk_type(token)
            if chunk_type == "O":
                outer = "O"
                prev_type = "O"
            elif chunk_type == prev_type:
                outer = f"I-{chunk_type}"
            else:
                outer = f"B-{chunk_type}"
                prev_type = chunk_type

            inner, clause = _get_inner_clause(token, sentence)
            labeled.append((token["form"], token["upos"], token["deprel"], outer, inner, clause))
        result.append(labeled)
    return result


def write_conll(sentences_with_labels: List[List[Tuple]], filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# columns = ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE\n")
        for sent in sentences_with_labels:
            for i, row in enumerate(sent, 1):
                form = row[0]
                outer = row[3]
                inner = row[4]
                clause = row[5]
                f.write(f"{i}\t{form}\t{outer}\t{inner}\t{clause}\n")
            f.write("\n")
