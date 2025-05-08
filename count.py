# class.py# class.py
import json
import numpy as np
from openai import OpenAI
import os
import sys
import time
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MultiLabelBinarizer
from sklearn.multioutput import MultiOutputClassifier
from sklearn.linear_model import LogisticRegression 

# Import evaluation metrics
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, hamming_loss, jaccard_score
import warnings
client = OpenAI(api_key='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')


EMBED_MODEL = "text-embedding-3-small" 

# Paths to your data files
ANNOTATED_DATA_PATH = "claim_level_triz_output.json"
PRINCIPLES_PATH = "triz_principles.json" 

TEST_SIZE = 0.2 
RANDOM_STATE = 42
BASE_ESTIMATOR = LogisticRegression(max_iter=2000, class_weight='balanced')
CLASSIFIER = MultiOutputClassifier(BASE_ESTIMATOR, n_jobs=-1)

# ── Data Loading and Preparation ───────────────────────────────────────────
def load_annotated_data(filepath):
    """Loads the annotated claim data."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"Loaded {len(data)} annotated claim entries.")
        return data
    except FileNotFoundError:
        print(f"Error: Annotated data file not found at {filepath}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
         print(f"Error: Could not decode JSON from {filepath}", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
         print(f"An unexpected error occurred loading annotated data: {e}", file=sys.stderr)
         sys.exit(1)


def load_all_principle_numbers(principles_filepath):
    """Loads all possible TRIZ principle numbers to create the label space."""
    try:
        with open(principles_filepath, 'r', encoding='utf-8') as f:
            principles = json.load(f)
        all_numbers = sorted(list(set(int(p['number']) for p in principles if p.get('number') is not None and isinstance(p.get('number'), (int, str)) and str(p['number']).isdigit())))
        print(f"Loaded {len(all_numbers)} unique TRIZ principle numbers.")
        return all_numbers
    except FileNotFoundError:
        print(f"Error: Principles file not found at {principles_filepath}", file=sys.stderr)
        sys.exit(1)
    except (ValueError, TypeError) as e:
         print(f"Error extracting principle numbers: {e}", file=sys.stderr)
         try:
             with open(principles_filepath, 'r', encoding='utf-8') as f:
                 principles = json.load(f)
                 for p in principles:
                     if p.get('number') is not None and not (isinstance(p.get('number'), (int, str)) and str(p['number']).isdigit()):
                          print(f"Problematic principle data: {p}", file=sys.stderr)
         except Exception as inner_e:
             print(f"Could not read principles file again to find problematic data: {inner_e}", file=sys.stderr)

         sys.exit(1)
    except json.JSONDecodeError:
         print(f"Error: Could not decode JSON from {principles_filepath}", file=sys.stderr)
         sys.exit(1)
    except Exception as e:
         print(f"An unexpected error occurred loading principles: {e}", file=sys.stderr)
         sys.exit(1)

def prepare_data(annotated_data, all_principle_numbers):
    """Extracts features (texts) and prepares multi-label targets."""
    claim_texts = [entry["claim_text"] for entry in annotated_data]
    assigned_principles_list = []
    for entry in annotated_data:
        valid_principles = []
        for p_num in entry.get("principles", []):
            try:
                p_num_int = int(p_num)
                if p_num_int in all_principle_numbers:
                    valid_principles.append(p_num_int)
                else:
                    print(f"Warning: Assigned principle number {p_num} from annotation not found in the full list of principles. Skipping.", file=sys.stderr)
            except (ValueError, TypeError):
                print(f"Warning: Invalid assigned principle number found during data prep: '{p_num}'. Skipping.", file=sys.stderr)
        assigned_principles_list.append(valid_principles)

    mlb = MultiLabelBinarizer(classes=all_principle_numbers)
    y = mlb.fit_transform(assigned_principles_list)

    print(f"Prepared data for {len(claim_texts)} claims.")
    print(f"Label matrix shape: {y.shape} (Claims x Principles)")
    return claim_texts, y, mlb.classes_ 
def embed_texts(texts, model=EMBED_MODEL, max_retries=3, delay=5):
    """Generates embeddings for a list of texts with retry logic."""
    if not texts:
        return np.array([], dtype=np.float32)

    for attempt in range(max_retries):
        try:
            string_texts = [str(text) for text in texts]
            resp = client.embeddings.create(model=model, input=string_texts)
            if len(resp.data) != len(texts):
                 print(f"Warning: Embedding response data count mismatch. Expected {len(texts)}, got {len(resp.data)}", file=sys.stderr)
                 raise ValueError(f"Embedding response data count mismatch: {len(resp.data)} != {len(texts)}")
            return np.array([d.embedding for d in resp.data], dtype=np.float32)
        except Exception as e:
            print(f"Attempt {attempt + 1} failed to get embeddings: {e}", file=sys.stderr)
            if attempt < max_retries - 1:
                time.sleep(delay)
            else:
                print("Max retries reached for embedding texts.", file=sys.stderr)
                raise

def train_model(X_train, y_train, classifier, principle_numbers):
    print("Training model...")
    trainable_principle_indices = [
        i for i in range(y_train.shape[1])
        if np.unique(y_train[:, i]).size > 1
    ]

    if not trainable_principle_indices:
        print("Error: No principles have more than one class in the training data. Cannot train.", file=sys.stderr)
        return {
            'trainable_principle_numbers': [],
            'estimators': []
        }

    X_train_trainable = X_train
    y_train_trainable = y_train[:, trainable_principle_indices]
    trainable_principle_numbers = [principle_numbers[i] for i in trainable_principle_indices]

    print(f"Found {len(trainable_principle_indices)} principles with sufficient data for training.")
    print(f"Skipping training for {y_train.shape[1] - len(trainable_principle_indices)} principles due to single-class training data.")
    estimators = [type(classifier.estimator)(**classifier.estimator.get_params()) for _ in trainable_principle_indices]

    trained_estimators = []
    print("Training individual estimators for trainable principles...")
    from joblib import Parallel, delayed

    def train_single_estimator(estimator, X, y_col, principle_num): 
        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
            estimator.fit(X, y_col)
        return estimator
    trained_estimators = Parallel(n_jobs=classifier.n_jobs)(
        delayed(train_single_estimator)(estimators[i], X_train_trainable, y_train_trainable[:, i], trainable_principle_numbers[i])
        for i in range(len(trainable_principle_indices))
    )


    print("Individual estimator training complete.")

    trained_model_components = {
        'trainable_principle_numbers': trainable_principle_numbers,
        'estimators': trained_estimators
    }

    print("Training complete.")
    return trained_model_components 
def evaluate_model(trained_model_components, X_test, y_test, all_principle_numbers):
    """Evaluates the multi-label classifier using the trained components."""
    print("Evaluating model...")

    trainable_principle_numbers = trained_model_components['trainable_principle_numbers']
    trained_estimators = trained_model_components['estimators']

    if not trained_estimators:
        print("No trained estimators available for evaluation.", file=sys.stderr)
        print("\n--- Evaluation Results ---")
        print(f"Exact Match Accuracy (Subset Accuracy): 0.0000")
        print(f"Hamming Loss (lower is better):        1.0000") 
        print("-" * 25)
        print(f"Macro Avg. Precision: 0.0000")
        print(f"Macro Avg. Recall:    0.0000")
        print(f"Macro Avg. F1-Score:  0.0000")
        print(f"Macro Avg. Jaccard:   0.0000")
        print("-" * 25)
        print(f"Weighted Avg. Precision: 0.0000")
        print(f"Weighted Avg. Recall:    0.0000")
        print(f"Weighted Avg. F1-Score:  0.0000")
        print(f"Weighted Avg. Jaccard:   0.0000")
        print("-" * 25)
        return
    y_pred = np.zeros_like(y_test)
    principle_to_index = {num: i for i, num in enumerate(all_principle_numbers)}
    trainable_indices_in_all = [principle_to_index[p_num] for p_num in trainable_principle_numbers]


    print(f"Predicting for {len(trainable_principle_numbers)} trainable principles on the test set...")
    for i, est in enumerate(trained_estimators):
        col_pred = est.predict(X_test)
        y_pred[:, trainable_indices_in_all[i]] = col_pred


    print("Prediction complete.")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=UserWarning, module="sklearn.metrics")

        exact_match_accuracy = accuracy_score(y_test, y_pred)
        hamming = hamming_loss(y_test, y_pred)
        precision_macro = precision_score(y_test, y_pred, average='macro', zero_division=0)
        recall_macro = recall_score(y_test, y_pred, average='macro', zero_division=0)
        f1_macro = f1_score(y_test, y_pred, average='macro', zero_division=0)

        precision_weighted = precision_score(y_test, y_pred, average='weighted', zero_division=0)
        recall_weighted = recall_score(y_test, y_pred, average='weighted', zero_division=0)
        f1_weighted = f1_score(y_test, y_pred, average='weighted', zero_division=0)

        jaccard_macro = jaccard_score(y_test, y_pred, average='macro', zero_division=0)
        jaccard_weighted = jaccard_score(y_test, y_pred, average='weighted', zero_division=0)


    print("\n--- Evaluation Results ---")
    print(f"Exact Match Accuracy (Subset Accuracy): {exact_match_accuracy:.4f}")
    print(f"Hamming Loss (lower is better):        {hamming:.4f}")
    print("-" * 25)
    print(f"Macro Avg. Precision: {precision_macro:.4f}")
    print(f"Macro Avg. Recall:    {recall_macro:.4f}")
    print(f"Macro Avg. F1-Score:  {f1_macro:.4f}")
    print(f"Macro Avg. Jaccard:   {jaccard_macro:.4f}")
    print("-" * 25)
    print(f"Weighted Avg. Precision: {precision_weighted:.4f}")
    print(f"Weighted Avg. Recall:    {recall_weighted:.4f}")
    print(f"Weighted Avg. F1-Score:  {f1_weighted:.4f}")
    print(f"Weighted Avg. Jaccard:   {jaccard_weighted:.4f}")
    print("-" * 25)

# ── Main Execution ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    annotated_data = load_annotated_data(ANNOTATED_DATA_PATH)
    all_principle_numbers = load_all_principle_numbers(PRINCIPLES_PATH)

    if not annotated_data or not all_principle_numbers:
        print("Exiting due to insufficient data.", file=sys.stderr)
        sys.exit(1)

    claim_texts, y, principle_column_mapping = prepare_data(annotated_data, all_principle_numbers)

    if len(claim_texts) != y.shape[0] or len(claim_texts) == 0:
         print("Data preparation failed. Number of texts and labels mismatch or zero data points.", file=sys.stderr)
         sys.exit(1)

    print("Generating embeddings for claim texts...")
    try:
        X = embed_texts(claim_texts)
        print("Claim embeddings generated.")
        if X.shape[0] != len(claim_texts):
             print(f"Warning: Number of embeddings ({X.shape[0]}) does not match number of claims ({len(claim_texts)}).", file=sys.stderr)
             print("Exiting due to embedding count mismatch.", file=sys.stderr)
             sys.exit(1)

    except Exception as e:
        print(f"Fatal Error: Could not generate embeddings for claims: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"Splitting data into training and testing sets ({1 - TEST_SIZE:.0%} train, {TEST_SIZE:.0%} test)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    print(f"Train data shape: {X_train.shape}, {y_train.shape}")
    print(f"Test data shape:  {X_test.shape}, {y_test.shape}")

    if y_test.sum() == 0:
         print("Warning: Test set contains no positive labels. Evaluation metrics might be misleading.", file=sys.stderr)
    model_components = train_model(X_train, y_train, CLASSIFIER, principle_column_mapping)

    evaluate_model(model_components, X_test, y_test, all_principle_numbers)

    print("\nModel training and evaluation complete.")
