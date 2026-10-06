# Three-Class Sentiment Analysis

This project trains and compares Multinomial Naive Bayes and Logistic Regression models for negative, neutral, and positive sentiment using TF-IDF features.

## Contents

- `Sentiment_Analysis.ipynb` — data inspection, preprocessing, EDA, word clouds, stratified 80/20 train/test split, model evaluation, confusion matrices, and error analysis.
- `data/tweet_eval_sentiment_train.parquet` — the TweetEval sentiment training split used as the notebook dataset.
- `requirements.txt` — notebook and Parquet dependencies.

## Dataset and labels

The source is the `sentiment` configuration of [TweetEval by Cardiff NLP](https://huggingface.co/datasets/cardiffnlp/tweet_eval), distributed through the Hugging Face Hub. Its dataset card documents three class names and defines label IDs as `0 = negative`, `1 = neutral`, and `2 = positive`. Dataset-card metadata currently reports the license as unknown; review the source terms and usage restrictions before redistributing dataset content or deploying a model commercially. The notebook uses the source training split and creates a reproducible stratified 80/20 split with seed 42; the source's separate validation and test splits are not combined with this split.

## Preprocessing and modeling

Text is lowercased, URLs and `@user` mentions are removed, punctuation/numbers are removed, text is tokenized with a regular expression, and English stopwords are removed while negators (`no`, `nor`, `not`, `never`) are retained. No stemming or lemmatization is applied. TF-IDF is fit on training text only, then the same learned vocabulary/weights are applied to held-out text. TF-IDF emphasizes terms informative within a document while down-weighting terms common across the corpus.

The source training split contains 45,615 records (7,093 negative; 20,673 neutral; 17,849 positive). It includes a small number of repeated texts, some with conflicting labels; these records are preserved, but a stratified five-fold group split holds identical cleaned text in only one side of the 80/20 holdout. The notebook reports accuracy and macro/weighted precision, recall, and F1, per-class reports, confusion matrices, a sentiment-distribution chart, a WordCloud for each class, and five held-out misclassifications. Model scores are dataset- and split-specific and should not be treated as a guarantee of production performance.

## Run

From this folder in PowerShell:

```powershell
python -m pip install -r requirements.txt
jupyter notebook
```

Open `Sentiment_Analysis.ipynb` and run all cells. Python 3.10+ is recommended.
