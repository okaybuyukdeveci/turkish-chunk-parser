import joblib
from typing import List, Dict
import sklearn_crfsuite
from sklearn_crfsuite import metrics as crf_metrics


def train(X_train: List[List[Dict]], y_train: List[List[str]]) -> sklearn_crfsuite.CRF:
    crf = sklearn_crfsuite.CRF(
        algorithm="lbfgs",
        c1=0.1,
        c2=0.01,
        max_iterations=200,
        all_possible_transitions=True,
    )
    crf.fit(X_train, y_train)
    return crf


def predict(crf: sklearn_crfsuite.CRF, X_test: List[List[Dict]]) -> List[List[str]]:
    return crf.predict(X_test)


def save(crf: sklearn_crfsuite.CRF, path: str) -> None:
    joblib.dump(crf, path)


def load(path: str) -> sklearn_crfsuite.CRF:
    return joblib.load(path)
