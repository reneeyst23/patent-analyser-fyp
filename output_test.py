import pandas as pd
from sklearn.metrics import multilabel_confusion_matrix
from sklearn.preprocessing import MultiLabelBinarizer
import pprint
import ast

# TRIZ principles dictionary with all 40 principles
TRIZ_PRINCIPLES = {
    '1': 'Segmentation',
    '2': 'Taking Out',
    '3': 'Local Quality',
    '4': 'Asymmetry',
    '5': 'Merging',
    '6': 'Universality',
    '7': 'Nested Doll',
    '8': 'Counterbalance',
    '9': 'Preliminary Anti-Action',
    '10': 'Prior Cushioning',
    '11': 'Spheroidality',
    '12': 'Equipotentiality',
    '13': 'Inversion',
    '14': 'Spherical Shape',
    '15': 'Dynamics',
    '16': 'Partial or Excessive Action',
    '17': 'Moving to a New Dimension',
    '18': 'Mechanical Vibration',
    '19': 'Periodic Action',
    '20': 'Continuity of Useful Action',
    '21': 'Skipping',
    '22': 'Blessing in Disguise',
    '23': 'Feedback',
    '24': 'Intermediary',
    '25': 'Self-Service',
    '26': 'Copying',
    '27': 'Cheap Short-Lived Objects',
    '28': 'Replacement of Mechanical System',
    '29': 'Pneumatics and Hydraulics',
    '30': 'Flexible Shells and Thin Films',
    '31': 'Porous Materials',
    '32': 'Color Changes',
    '33': 'Homogeneity',
    '34': 'Discarding and Recovering',
    '35': 'Parameter Changes',
    '36': 'Phase Transitions',
    '37': 'Thermal Expansion',
    '38': 'Strong Oxidants',
    '39': 'Inert Atmosphere',
    '40': 'Composite Materials'
}

def load_and_prepare_data(classified_json: str, bulk_json: str, test_json: str) -> pd.DataFrame:
    """Load and merge data from JSON files."""
    try:
        res = pd.read_json(classified_json)
        df = pd.read_json(bulk_json)
        test = pd.read_json(test_json)
        
        # Extract title from essential_data
        df['title_extracted'] = df['essential_data'].apply(
            lambda x: ast.literal_eval(x).get('title', 'No Title')
        )
        
        # Merge dataframes
        merged_df = test.merge(
            df[['title_extracted', 'SerialCode']], 
            how='left', 
            left_on='title', 
            right_on='title_extracted'
        )
        merged_df.drop(columns=['title_extracted'], inplace=True)
        
        final_df = merged_df.merge(res, on='SerialCode', how='inner')
        return final_df
    
    except Exception as e:
        print(f"Error loading or processing data: {e}")
        raise

def prepare_labels(df: pd.DataFrame) -> tuple:
    """Prepare actual and predicted labels for evaluation."""
    try:
        # Convert principles to list of strings
        df['actual'] = df['principles'].apply(
            lambda plist: [str(p['number']) for p in plist]
        )
        
        # Ensure predicted principles are in correct format
        df['predicted'] = df['Results.principles'].apply(
            lambda x: [str(i) for i in x] if isinstance(x, list) else []
        )
        
        return df['actual'], df['predicted']
    
    except Exception as e:
        print(f"Error preparing labels: {e}")
        raise

def evaluate_triz_predictions(actual: list, predicted: list) -> dict:
    """Evaluate TRIZ principle predictions using confusion matrices."""
    try:
        mlb = MultiLabelBinarizer()
        actual_bin = mlb.fit_transform(actual)
        predicted_bin = mlb.transform(predicted)
        
        conf_matrices = multilabel_confusion_matrix(actual_bin, predicted_bin)
        conf_dict = {
            label: matrix for label, matrix in zip(mlb.classes_, conf_matrices)
        }
        return conf_dict
    
    except Exception as e:
        print(f"Error evaluating predictions: {e}")
        raise

def print_confusion_matrix(matrix: list, label: str) -> None:
    """Print formatted confusion matrix for a TRIZ principle."""
    tn, fp = matrix[0]
    fn, tp = matrix[1]
    
    principle_name = TRIZ_PRINCIPLES.get(label, 'Unknown')
    
    print(f"\nConfusion Matrix for TRIZ Principle {principle_name} ({label}):\n")
    print("                Predicted")
    print("               0       1")
    print("Actual  0    {:<5}   {:<5}".format(tn, fp))
    print("        1    {:<5}   {:<5}".format(fn, tp))
    print("\nLegend:")
    print("TN: True Negative, FP: False Positive")
    print("FN: False Negative, TP: True Positive")
    print(f"\nCounts - TN: {tn}, FP: {fp}, FN: {fn}, TP: {tp}")
    
def compute_overall_metrics(conf_dict):
    """
    Computes overall classification metrics from a dictionary of confusion matrices.
    
    Parameters:
        conf_dict (dict): Dictionary where each value is a 2x2 confusion matrix 
                          in the format [[TN, FP], [FN, TP]]
    
    Returns:
        dict: A dictionary containing overall TP, TN, FP, FN, and all evaluation metrics.
    """
    TP = TN = FP = FN = 0

    for matrix in conf_dict.values():
        tn, fp = matrix[0]
        fn, tp = matrix[1]
        TP += tp
        TN += tn
        FP += fp
        FN += fn

    sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0
    precision = TP / (TP + FP) if (TP + FP) > 0 else 0
    accuracy = (TP + TN) / (TP + TN + FP + FN)
    f1_score = 2 * (precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0

    metrics = {
        'TP': TP,
        'TN': TN,
        'FP': FP,
        'FN': FN,
        'Sensitivity (Recall)': round(sensitivity, 4),
        'Specificity': round(specificity, 4),
        'Precision': round(precision, 4),
        'Accuracy': round(accuracy, 4),
        'F1 Score': round(f1_score, 4)
    }

    return metrics


def main():
    try:
        # Load and prepare data
        final_df = load_and_prepare_data(
            "classified_result1.json",
            "data_extraction/bulk_patent.json",
            "test_data.json"
        )
        
        # Prepare labels
        actual, predicted = prepare_labels(final_df)
        
        # Evaluate predictions
        conf_dict = evaluate_triz_predictions(actual, predicted)
        
        # Print confusion matrices for all principles
        for label in sorted(conf_dict.keys(), key=lambda x: int(x)):
            print_confusion_matrix(conf_dict[label], label)
        
        print(compute_overall_metrics(conf_dict))
    except Exception as e:
        print(f"Error in main execution: {e}")

if __name__ == "__main__":
    main()







