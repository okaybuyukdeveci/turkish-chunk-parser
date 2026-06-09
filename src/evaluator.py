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


def plot_metrics_per_class(y_true: List[List[str]], y_pred: List[List[str]], save_path: str) -> None:
    from seqeval.metrics import classification_report as seqeval_report

    report = seqeval_report(y_true, y_pred, digits=4, output_dict=True)

    # Sadece sınıf satırlarını al (micro/macro/weighted avg hariç)
    classes = [k for k in report if k not in ("micro avg", "macro avg", "weighted avg")]
    classes = sorted(classes)

    precision_vals = [report[c]["precision"] for c in classes]
    recall_vals    = [report[c]["recall"]    for c in classes]
    f1_vals        = [report[c]["f1-score"]  for c in classes]

    x = np.arange(len(classes))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))
    bars1 = ax.bar(x - width, precision_vals, width, label="Precision", color="#4C72B0")
    bars2 = ax.bar(x,         recall_vals,    width, label="Recall",    color="#55A868")
    bars3 = ax.bar(x + width, f1_vals,        width, label="F1-Score",  color="#C44E52")

    ax.set_xlabel("Sınıf", fontsize=12)
    ax.set_ylabel("Değer", fontsize=12)
    ax.set_title("Sınıf Bazında Precision / Recall / F1-Score", fontsize=13)
    ax.set_xticks(x)
    ax.set_xticklabels(classes, fontsize=10)
    ax.set_ylim(0, 1.12)
    ax.legend(fontsize=10)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)

    for bar in [*bars1, *bars2, *bars3]:
        h = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, h + 0.01,
                f"{h:.2f}", ha="center", va="bottom", fontsize=7)

    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Metrik grafiği kaydedildi: {save_path}")


def plot_accuracy_bar(accuracy: float, save_path: str) -> None:
    fig, ax = plt.subplots(figsize=(4, 5))
    bar = ax.bar(["Token Accuracy"], [accuracy], color="#8172B2", width=0.4)
    ax.set_ylim(0, 1.15)
    ax.set_ylabel("Değer", fontsize=12)
    ax.set_title("Token-Level Accuracy", fontsize=13)
    ax.yaxis.grid(True, linestyle="--", alpha=0.7)
    ax.set_axisbelow(True)
    ax.text(bar[0].get_x() + bar[0].get_width() / 2, accuracy + 0.02,
            f"{accuracy:.4f}", ha="center", va="bottom", fontsize=12, fontweight="bold")
    plt.tight_layout()
    plt.savefig(save_path, dpi=150)
    plt.close()
    print(f"Accuracy grafiği kaydedildi: {save_path}")


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
