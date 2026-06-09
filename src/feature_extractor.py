from typing import List, Dict, Tuple


def word2features(sentence: List[Tuple], i: int) -> Dict:
    form, upos, deprel = sentence[i][0], sentence[i][1], sentence[i][2]
    word = form.lower()

    features = {
        "bias": 1.0,
        "word.lower": word,
        "word[-4:]": word[-4:],
        "word[-3:]": word[-3:],
        "word[-2:]": word[-2:],
        "word[:3]": word[:3],
        "word[:2]": word[:2],
        "word.isupper": word.isupper(),
        "word.istitle": form.istitle(),
        "word.isdigit": word.isdigit(),
        "postag": upos,
        "deprel": deprel,
    }

    # -2 komşu
    if i >= 2:
        w2, pos2, dep2 = sentence[i-2][0], sentence[i-2][1], sentence[i-2][2]
        features.update({
            "-2:word.lower": w2.lower(),
            "-2:postag": pos2,
            "-2:word[-3:]": w2.lower()[-3:],
        })
    else:
        features["BOS2"] = True

    # -1 komşu
    if i >= 1:
        w1, pos1, dep1 = sentence[i-1][0], sentence[i-1][1], sentence[i-1][2]
        features.update({
            "-1:word.lower": w1.lower(),
            "-1:postag": pos1,
            "-1:word[-3:]": w1.lower()[-3:],
            "-1:deprel": dep1,
        })
    else:
        features["BOS"] = True

    # +1 komşu
    if i < len(sentence) - 1:
        w1, pos1, dep1 = sentence[i+1][0], sentence[i+1][1], sentence[i+1][2]
        features.update({
            "+1:word.lower": w1.lower(),
            "+1:postag": pos1,
            "+1:word[-3:]": w1.lower()[-3:],
            "+1:deprel": dep1,
        })
    else:
        features["EOS"] = True

    # +2 komşu
    if i < len(sentence) - 2:
        w2, pos2, dep2 = sentence[i+2][0], sentence[i+2][1], sentence[i+2][2]
        features.update({
            "+2:word.lower": w2.lower(),
            "+2:postag": pos2,
            "+2:word[-3:]": w2.lower()[-3:],
        })
    else:
        features["EOS2"] = True

    return features


def sent2features(sentence: List[Tuple]) -> List[Dict]:
    return [word2features(sentence, i) for i in range(len(sentence))]


def sent2labels(sentence: List[Tuple]) -> List[str]:
    return [row[3] for row in sentence]
