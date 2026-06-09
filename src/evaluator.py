from typing import List
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, confusion_matrix
from seqeval.metrics import classification_report, f1_score, precision_score, recall_score


ALL_LABELS = ["B-NP", "I-NP", "B-VP", "I-VP", "B-ADVP", "I-ADVP", "B-ADJP", "I-ADJP", "O"]


def evaluate(y_true: List[List[str]], y_pred: List[List[str]], report_path: str) -> dict:
    # seqeval chunk-level metrikleri
    report = classification_report(y_true, y_pred, digits=4)
    f1 = f1_score(y_true, y_pred)
    precision = precision_score(y_true, y_pred)
    recall = recall_score(y_true, y_pred)

    # token-level accuracy
    flat_true = [t for seq in y_true for t in seq]
    flat_pred = [t for seq in y_pred for t in seq]
    accuracy = accuracy_score(flat_true, flat_pred)

    summary = (
        f"=== Chunk-Level Metrics (seqeval) ===\n"
        f"{report}\n"
        f"Micro F1:     {f1:.4f}\n"
        f"Precision:    {precision:.4f}\n"
        f"Recall:       {recall:.4f}\n"
        f"Token Acc.:   {accuracy:.4f}\n"
    )
    print(summary)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(summary)

    return {"f1": f1, "precision": precision, "recall": recall, "accuracy": accuracy}


def plot_confusion_matrix(y_true: List[List[str]], y_pred: List[List[str]], save_path: str) -> None:
    flat_true = [t for seq in y_true for t in seq]
    flat_pred = [t for seq in y_pred for t in seq]

    present = sorted(set(flat_true) | set(flat_pred))
    labels = [l for l in ALL_LABELS if l in present]

    cm = confusion_matrix(flat_true, flat_pred, labels=labels)
    cm_norm = cm.astype(float) / cm.sum(axis=1, keepdims=True).clip(min=1)

    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(cm_norm, interpolation="nearest", cmap=plt.cm.Blues)
    plt.colorbar(im, ax=ax)

    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=9)
    ax.set_yticklabels(labels, fontsize=9)
    ax.set_xlabel("Tahmin Edilen", fontsize=11)
    ax.set_ylabel("Gerçek", fontsize=11)
    ax.set_title("Confusion Matrix (normalize edilmiş)", fontsize=12)

    thresh = cm_norm.max() / 2.0
    for i in range(len(labels)):
        for j in range(len(labels)):
            ax.text(j, i, f"{cm[i, j]}", ha="center", va="center",
                    color="white" if cm_norm[i, j] > thresh else "black", fontsize=7)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Confusion matrix kaydedildi: {save_path}")


def write_predictions_conll(
    sentences: List[List[tuple]],
    y_pred: List[List[str]],
    filepath: str,
) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("# columns = ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE\n")
        for sent, preds in zip(sentences, y_pred):
            for i, (row, pred) in enumerate(zip(sent, preds), 1):
                form = row[0]
                inner = row[4]
                clause = row[5]
                f.write(f"{i}\t{form}\t{pred}\t{inner}\t{clause}\n")
            f.write("\n")
    print(f"Tahminler CoNLL formatında kaydedildi: {filepath}")
