import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from sklearn.metrics import confusion_matrix
import matplotlib.patches as mpatches

# Set style for professional graphs
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

# Data from your results
# Original test set confusion matrix
original_cm = np.array([[8, 10, 132],
                        [5, 12, 139],
                        [10, 11, 305]])

# Balanced test set confusion matrix
balanced_cm = np.array([[8, 10, 132],
                        [5, 12, 133],
                        [5, 4, 141]])

# Performance metrics
metrics_data = {
    'Test Set': ['Original', 'Original', 'Original', 'Balanced', 'Balanced', 'Balanced'],
    'Class': ['Mild', 'Moderate', 'Severe', 'Mild', 'Moderate', 'Severe'],
    'Precision': [0.35, 0.36, 0.53, 0.44, 0.46, 0.35],
    'Recall': [0.05, 0.08, 0.94, 0.05, 0.08, 0.94],
    'F1-Score': [0.09, 0.13, 0.68, 0.10, 0.14, 0.51]
}

# Model comparison data
model_comparison = {
    'Model': ['Random Forest', 'Logistic Regression', 'Gradient Boosting', 'Ensemble (Our Method)'],
    'Accuracy': [48.5, 46.2, 47.8, 51.4],
    'F1-macro': [0.42, 0.39, 0.41, 0.46],
    'F1-weighted': [0.45, 0.42, 0.44, 0.45]
}

# Create figure with subplots
fig = plt.figure(figsize=(16, 12))

# 1. Confusion Matrix - Original Test Set
plt.subplot(2, 3, 1)
sns.heatmap(original_cm, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['Mild', 'Moderate', 'Severe'],
            yticklabels=['Mild', 'Moderate', 'Severe'])
plt.title('Confusion Matrix\nOriginal Test Set (51.4% Accuracy)', fontsize=12, fontweight='bold')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')

# 2. Confusion Matrix - Balanced Test Set
plt.subplot(2, 3, 2)
sns.heatmap(balanced_cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=['Mild', 'Moderate', 'Severe'],
            yticklabels=['Mild', 'Moderate', 'Severe'])
plt.title('Confusion Matrix\nBalanced Test Set (35.8% Accuracy)', fontsize=12, fontweight='bold')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')

# 3. Class Distribution Before and After Balancing
plt.subplot(2, 3, 3)
before_balancing = [499, 520, 1086]  # Mild, Moderate, Severe
after_balancing = [753, 748, 743]    # Mild, Moderate, Severe

x = np.arange(3)
width = 0.35

plt.bar(x - width/2, before_balancing, width, label='Before Balancing', color='lightcoral')
plt.bar(x + width/2, after_balancing, width, label='After SMOTE+Tomek', color='lightblue')

plt.xlabel('Severity Class')
plt.ylabel('Number of Samples')
plt.title('Dataset Balancing Effect', fontsize=12, fontweight='bold')
plt.xticks(x, ['Mild', 'Moderate', 'Severe'])
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 4. Performance Metrics Comparison
plt.subplot(2, 3, 4)
metrics_df = pd.DataFrame(metrics_data)

x = np.arange(3)
width = 0.25

original_metrics = metrics_df[metrics_df['Test Set'] == 'Original']
balanced_metrics = metrics_df[metrics_df['Test Set'] == 'Balanced']

plt.bar(x - width/2, original_metrics['Precision'], width, label='Original Precision', alpha=0.8)
plt.bar(x + width/2, original_metrics['Recall'], width, label='Original Recall', alpha=0.8)
plt.bar(x + 1.5*width, original_metrics['F1-Score'], width, label='Original F1-Score', alpha=0.8)

plt.xlabel('Severity Class')
plt.ylabel('Score')
plt.title('Performance Metrics by Class\n(Original Test Set)', fontsize=12, fontweight='bold')
plt.xticks(x, ['Mild', 'Moderate', 'Severe'])
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 5. Model Comparison
plt.subplot(2, 3, 5)
model_df = pd.DataFrame(model_comparison)

x = np.arange(len(model_df))
width = 0.25

plt.bar(x - width, model_df['Accuracy'], width, label='Accuracy', alpha=0.8)
plt.bar(x, model_df['F1-macro'], width, label='F1-macro', alpha=0.8)
plt.bar(x + width, model_df['F1-weighted'], width, label='F1-weighted', alpha=0.8)

plt.xlabel('Model')
plt.ylabel('Performance (%)')
plt.title('Model Comparison', fontsize=12, fontweight='bold')
plt.xticks(x, model_df['Model'], rotation=45, ha='right')
plt.legend()
plt.grid(axis='y', alpha=0.3)

# 6. Accuracy Comparison - Original vs Balanced
plt.subplot(2, 3, 6)
test_sets = ['Original Test Set', 'Balanced Test Set']
accuracies = [51.4, 35.8]

bars = plt.bar(test_sets, accuracies, color=['lightgreen', 'lightcoral'])
plt.ylabel('Accuracy (%)')
plt.title('Accuracy: Original vs Balanced Test Set', fontsize=12, fontweight='bold')
plt.ylim(0, 60)

# Add value labels on bars
for bar, acc in zip(bars, accuracies):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
             f'{acc}%', ha='center', va='bottom', fontweight='bold')

plt.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig('experiments_results_graphs.png', dpi=300, bbox_inches='tight')
plt.show()

# Create a separate feature importance graph
plt.figure(figsize=(12, 8))

# Feature importance data
feature_importance = {
    'Feature': ['Cholesterol Total', 'MoCA Score', 'BMI', 'Functional Assessment', 
                'Diet Quality', 'Physical Activity', 'Sleep Quality', 'Alcohol Consumption',
                'Cholesterol LDL', 'Cholesterol Triglycerides'],
    'Importance': [0.054, 0.053, 0.053, 0.052, 0.051, 0.051, 0.051, 0.050, 0.050, 0.049]
}

feature_df = pd.DataFrame(feature_importance)
feature_df = feature_df.sort_values('Importance', ascending=True)

plt.barh(feature_df['Feature'], feature_df['Importance'], color='skyblue')
plt.xlabel('Feature Importance')
plt.title('Top 10 Most Important Features', fontsize=14, fontweight='bold')
plt.grid(axis='x', alpha=0.3)

# Add value labels
for i, (feature, importance) in enumerate(zip(feature_df['Feature'], feature_df['Importance'])):
    plt.text(importance + 0.001, i, f'{importance:.3f}', va='center')

plt.tight_layout()
plt.savefig('feature_importance_graph.png', dpi=300, bbox_inches='tight')
plt.show()

print("Graphs saved successfully!")
print("1. experiments_results_graphs.png - Comprehensive results visualization")
print("2. feature_importance_graph.png - Feature importance analysis")
