# Turkish Chunk Parser

Türkçe cümleler için BIO etiketleme ile sözdizimsel öbek saptanması (Chunking). CRF (Conditional Random Fields) algoritması kullanılarak eğitilmiş bir makine öğrenmesi pipeline'ı.

## Proje Hakkında

Bu proje, verilen bir Türkçe cümledeki isim öbeklerini (NP), eylem öbeklerini (VP), zarf öbeklerini (ADVP) ve sıfat öbeklerini (ADJP) otomatik olarak saptamaktadır. Çıktılar CoNLL formatında üretilmektedir.

### Tanınan Öbek Tipleri

| Etiket | Açıklama | Örnek |
|--------|----------|-------|
| NP | İsim öbeği | "toplantıdan erken çıkan öğrenci" |
| VP | Eylem öbeği | "fark ettim", "geldi" |
| ADVP | Zarf öbeği | "dün akşam", "dikkatlice" |
| ADJP | Sıfat öbeği | "çok güzel" |

### Örnek Çıktı

```
# columns = ID FORM CHUNK-OUTER CHUNK-INNER CLAUSE
1   Dün           B-ADVP   _         O
2   akşam         I-ADVP   _         O
3   toplantıdan   B-NP     B-RELCL   B-RELCL
4   erken         I-NP     I-RELCL   I-RELCL
5   çıkan         I-NP     I-RELCL   I-RELCL
6   öğrencinin    I-NP     _         O
7   ,             O        _         O
8   geldi         B-VP     _         O
```

## Kurulum

```bash
pip install -r requirements.txt
```

Veri setleri:
```bash
# Eğitim verisi (IMST)
git clone https://github.com/UniversalDependencies/UD_Turkish-IMST.git data/raw/

# Test verisi (BOUN — bağımsız kaynak)
git clone https://github.com/UniversalDependencies/UD_Turkish-BOUN.git data/boun/
```

## Kullanım

```bash
python3 main.py
```

Tek komut ile tüm pipeline çalışır:
1. Veri yüklenir
2. Dependency ilişkilerinden BIO chunk etiketleri türetilir
3. CRF modeli eğitilir
4. Test seti üzerinde değerlendirme yapılır
5. Sonuçlar `outputs/` klasörüne kaydedilir

## Proje Yapısı

```
turkish-chunk-parser/
├── src/
│   ├── data_loader.py        # CoNLL-U dosya okuyucu
│   ├── chunk_converter.py    # Dependency → BIO chunk etiketleri
│   ├── feature_extractor.py  # CRF özellik mühendisliği
│   ├── crf_model.py          # Model eğitimi ve tahmini
│   └── evaluator.py          # Metrikler ve confusion matrix
├── data/
│   ├── raw/                  # UD IMST ham veri (git clone ile indirilir)
│   └── processed/            # Chunk etiketleri eklenmiş CoNLL dosyaları
├── outputs/
│   ├── predictions.conll     # Test seti tahminleri (CoNLL formatı)
│   ├── metrics_report.txt    # Sınıf bazında F1/Precision/Recall
│   └── confusion_matrix.png  # Confusion matrix grafiği
├── main.py
└── requirements.txt
```

## Veri Seti

[UD Turkish IMST Treebank](https://github.com/UniversalDependencies/UD_Turkish-IMST)

- Eğitim: ~4535 cümle (train + dev)
- Test: ~1100 cümle
- Format: CoNLL-U

## Sonuçlar

Eğitim: IMST Treebank | Test: BOUN Treebank (bağımsız kaynak)

| Sınıf | Precision | Recall | F1 |
|-------|-----------|--------|----|
| ADJP | 0.88 | 0.90 | 0.89 |
| ADVP | 0.91 | 0.87 | 0.89 |
| NP | 0.82 | 0.83 | 0.82 |
| VP | 0.84 | 0.83 | 0.83 |
| **Micro Avg** | **0.84** | **0.84** | **0.84** |
| Token Accuracy | | | **0.91** |

Detaylı metrikler ve grafikler: `outputs/` klasörü

## Gereksinimler

- Python 3.8+
- sklearn-crfsuite
- seqeval
- scikit-learn
- numpy
- matplotlib
