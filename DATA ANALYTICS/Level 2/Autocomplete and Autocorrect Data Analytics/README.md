# Autocomplete and Autocorrect

This notebook demonstrates next-word prediction and spelling correction using a public-domain English text corpus.

## Files

- `Autocomplete_Autocorrect_Analysis.ipynb` — preprocessing, corpus inspection, frequency chart, bigram/trigram autocomplete, held-out evaluation, typo correction comparisons, confusion matrices, and limitations.
- `data/sherlock_holmes_gutenberg.txt` — Project Gutenberg plain-text edition of *The Adventures of Sherlock Holmes* (eBook #1661) by Arthur Conan Doyle.
- `requirements.txt` — Python dependencies.

## Methods

The notebook lowercases, tokenizes alphabetic words, and removes punctuation. Sentences stay separate so n-grams do not cross sentence boundaries. Stopwords are excluded from the top-20 frequency visualization; they are intentionally preserved in n-gram sequences because words such as “the”, “is”, and “to” are essential for natural next-word prediction. A sequential 90/10 sentence-level train/test split avoids training on future text during autocomplete scoring. A bigram frequency model and a trigram model with bigram backoff return up to three suggestions; Precision@3 and Recall@3 are evaluated against the next word in held-out sentences.

Two custom spelling algorithms are compared: Levenshtein edit distance and Damerau-Levenshtein distance (which handles adjacent transpositions). Candidates are drawn only from the training corpus vocabulary, ranked by distance and then corpus frequency. Twenty misspellings have known intended words present in the corpus; twenty common correctly spelled words serve as controls. Correction accuracy measures exact restoration of the intended word. Detection precision/recall and confusion matrices measure whether the algorithm edits known misspellings while leaving valid controls unchanged.

This is a small, single-author literary corpus. Its vocabulary and frequency distribution do not represent modern messaging, names, slang, multiple languages, or user-specific writing. Real keyboards also use context-aware neural models, personal dictionaries, latency optimization, privacy safeguards, and carefully calibrated suggestions.

## Run

From this folder, install dependencies and open the notebook:

```powershell
python -m pip install -r requirements.txt
jupyter notebook
```
