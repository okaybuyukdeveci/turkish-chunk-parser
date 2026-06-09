import os
import sys
from collections import Counter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from data_loader import load_conllu
from chunk_converter import convert_to_bio, write_conll
from feature_extractor import sent2features, sent2labels
from crf_model import train, predict, save
from evaluator import evaluate, plot_confusion_matrix, plot_metrics_per_class, plot_accuracy_bar, write_predictions_conll

RAW_DIR      = os.path.join(os.path.dirname(__file__), "data", "raw")
BOUN_DIR     = os.path.join(os.path.dirname(__file__), "data", "boun")
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "data", "processed")
OUTPUTS_DIR  = os.path.join(os.path.dirname(__file__), "outputs")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)


def main():
    print("=== 1/5 Veri Yükleniyor ===")
    # Eğitim: IMST train + dev
    train_sents = load_conllu(os.path.join(RAW_DIR, "tr_imst-ud-train.conllu"))
    dev_sents   = load_conllu(os.path.join(RAW_DIR, "tr_imst-ud-dev.conllu"))
    all_train_sents = train_sents + dev_sents

    # Test: BOUN test (tamamen farklı kaynak → gerçekçi değerlendirme)
    test_sents = load_conllu(os.path.join(BOUN_DIR, "tr_boun-ud-test.conllu"))

    print(f"  Eğitim : IMST train+dev → {len(all_train_sents)} cümle")
    print(f"  Test   : BOUN test      → {len(test_sents)} cümle")

    print("\n=== 2/5 Chunk Etiketleri Türetiliyor (deprel → BIO) ===")
    train_labeled = convert_to_bio(all_train_sents)
    test_labeled  = convert_to_bio(test_sents)

    write_conll(train_labeled, os.path.join(PROCESSED_DIR, "train_chunked.conll"))
    write_conll(test_labeled,  os.path.join(PROCESSED_DIR, "test_chunked.conll"))
    print("  İşaretlenmiş veri data/processed/ klasörüne kaydedildi.")

    label_dist = Counter(row[3] for sent in train_labeled for row in sent)
    print("  Eğitim etiket dağılımı:", dict(sorted(label_dist.items())))

    print("\n=== 3/5 Özellikler Çıkarılıyor ===")
    X_train = [sent2features(s) for s in train_labeled]
    y_train = [sent2labels(s)   for s in train_labeled]
    X_test  = [sent2features(s) for s in test_labeled]
    y_test  = [sent2labels(s)   for s in test_labeled]
    print(f"  Eğitim token sayısı: {sum(len(s) for s in X_train)}")
    print(f"  Test token sayısı:   {sum(len(s) for s in X_test)}")

    print("\n=== 4/5 CRF Modeli Eğitiliyor ===")
    crf = train(X_train, y_train)
    save(crf, os.path.join(OUTPUTS_DIR, "crf_model.pkl"))
    print("  Model outputs/crf_model.pkl olarak kaydedildi.")

    print("\n=== 5/5 Değerlendirme ===")
    y_pred = predict(crf, X_test)

    metrics = evaluate(
        y_test,
        y_pred,
        report_path=os.path.join(OUTPUTS_DIR, "metrics_report.txt"),
    )
    plot_confusion_matrix(
        y_test,
        y_pred,
        save_path=os.path.join(OUTPUTS_DIR, "confusion_matrix.png"),
    )
    plot_metrics_per_class(
        y_test,
        y_pred,
        save_path=os.path.join(OUTPUTS_DIR, "metrics_per_class.png"),
    )
    plot_accuracy_bar(
        metrics["accuracy"],
        save_path=os.path.join(OUTPUTS_DIR, "accuracy.png"),
    )
    write_predictions_conll(
        test_labeled,
        y_pred,
        filepath=os.path.join(OUTPUTS_DIR, "predictions.conll"),
    )

    print("\nTamamlandi. Ciktilar: outputs/ klasorunde.")


if __name__ == "__main__":
    main()
