import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import joblib
from sklearn.preprocessing import OneHotEncoder

def create_engineered_features(X):
    """Create the same engineered features used in training"""
    X_eng = X.copy()
    
    # Interaction terms
    if 'BMI' in X.columns and 'PhysicalActivity' in X.columns:
        X_eng['BMI_Activity_Interaction'] = X['BMI'] * X['PhysicalActivity']
    
    if 'Age' in X.columns and 'MoCA' in X.columns:
        X_eng['Age_MoCA_Ratio'] = X['Age'] / (X['MoCA'] + 1)
    
    if 'SystolicBP' in X.columns and 'DiastolicBP' in X.columns:
        X_eng['Pulse_Pressure'] = X['SystolicBP'] - X['DiastolicBP']
        X_eng['BP_Ratio'] = X['SystolicBP'] / (X['DiastolicBP'] + 1)
    
    # Cholesterol ratios
    if 'CholesterolLDL' in X.columns and 'CholesterolHDL' in X.columns:
        X_eng['LDL_HDL_Ratio'] = X['CholesterolLDL'] / (X['CholesterolHDL'] + 1)
    
    if 'CholesterolTotal' in X.columns and 'CholesterolHDL' in X.columns:
        X_eng['Total_HDL_Ratio'] = X['CholesterolTotal'] / (X['CholesterolHDL'] + 1)
    
    # Motor symptom composite score
    motor_cols = ['Tremor', 'Rigidity', 'Bradykinesia', 'PosturalInstability']
    available_motor_cols = [col for col in motor_cols if col in X.columns]
    if available_motor_cols:
        X_eng['Motor_Score'] = X[available_motor_cols].sum(axis=1)
    
    return X_eng

try:
    preprocessor = joblib.load('preprocessor_balanced.pkl')
    rfe = joblib.load('feature_selector_balanced.pkl')
    ensemble_model = joblib.load('parkinson_severity_model_balanced.pkl')
    use_feature_selection = True
except FileNotFoundError:
    # Feature selector not found, try loading without it
    try:
        preprocessor = joblib.load('preprocessor_balanced.pkl')
        ensemble_model = joblib.load('parkinson_severity_model_balanced.pkl')
        rfe = None
        use_feature_selection = False
        print("Feature selector not found, using all features")
    except Exception as e:
        messagebox.showerror("Error", f"Model files not found or corrupted:\n\n{e}")
        raise SystemExit
except Exception as e:
    messagebox.showerror("Error", f"Model files not found or corrupted:\n\n{e}")
    raise SystemExit

for name, transformer, cols in preprocessor.transformers_:
    if isinstance(transformer, OneHotEncoder):
        transformer.handle_unknown = 'ignore'

try:
    dataset = pd.read_csv('parkinsons_severity_balanced.csv')
    gui_samples = pd.read_csv('gui_samples_original.csv')
except FileNotFoundError:
    dataset = pd.DataFrame()
    gui_samples = pd.DataFrame()

features = [
    'Age', 'Gender', 'Ethnicity', 'EducationLevel', 'BMI', 'Smoking', 'AlcoholConsumption', 
    'PhysicalActivity', 'DietQuality', 'SleepQuality', 'FamilyHistoryParkinsons', 
    'TraumaticBrainInjury', 'Hypertension', 'Diabetes', 'Depression', 'Stroke', 
    'SystolicBP', 'DiastolicBP', 'CholesterolTotal', 'CholesterolLDL', 'CholesterolHDL', 
    'CholesterolTriglycerides', 'MoCA', 'FunctionalAssessment', 'Tremor', 'Rigidity', 
    'Bradykinesia', 'PosturalInstability', 'SpeechProblems', 'SleepDisorders', 'Constipation'
]

root = tk.Tk()
root.title("Parkinson's Severity Predictor")
root.geometry("470x670")

canvas = tk.Canvas(root)
scrollbar = ttk.Scrollbar(root, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

entries = {}
for i, feature in enumerate(features):
    tk.Label(scrollable_frame, text=f"{feature}:").grid(row=i, column=0, sticky='w', padx=5, pady=2)
    entry = tk.Entry(scrollable_frame, width=18)
    entry.grid(row=i, column=1, padx=5, pady=2)
    entries[feature] = entry

def predict_severity():
    try:
        user_input = {}
        for feature in features:
            val = entries[feature].get().strip()
            if val == "":
                raise ValueError(f"Please enter a value for {feature}")
            try:
                user_input[feature] = float(val)
            except ValueError:
                user_input[feature] = val

        input_df = pd.DataFrame([user_input])
        
        # Create engineered features before preprocessing
        input_df_eng = create_engineered_features(input_df)
        
        X_processed = preprocessor.transform(input_df_eng)
        if use_feature_selection:
            X_selected = rfe.transform(X_processed)
        else:
            X_selected = X_processed
        prediction = ensemble_model.predict(X_selected)
        predicted_label = prediction[0]

        messagebox.showinfo("Prediction Result", f"Predicted Parkinson's Severity:\n\n{predicted_label}")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred:\n\n{e}")

def load_sample_by_severity(severity_label):
    if gui_samples.empty:
        messagebox.showerror("Error", "GUI samples dataset not found.")
        return
    subset = gui_samples[gui_samples['Severity'] == severity_label]
    if subset.empty:
        messagebox.showerror("Error", f"No sample record found for {severity_label}.")
        return
    row = subset.iloc[0]
    
    # Load the original feature values directly
    for feature in features:
        entries[feature].delete(0, tk.END)
        entries[feature].insert(0, str(row[feature]))
    messagebox.showinfo("Loaded", f"Sample record for {severity_label} loaded successfully.")

def load_from_file():
    file_path = filedialog.askopenfilename(
        title="Select Patient Record File",
        filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")]
    )
    if not file_path:
        return

    try:
        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)
        
        missing = [col for col in features if col not in df.columns]
        if missing:
            messagebox.showerror("Error", f"File missing required columns:\n{', '.join(missing)}")
            return

        # Create engineered features before preprocessing
        df_eng = create_engineered_features(df)
        
        X_processed = preprocessor.transform(df_eng)
        if use_feature_selection:
            X_selected = rfe.transform(X_processed)
        else:
            X_selected = X_processed
        predictions = ensemble_model.predict(X_selected)
        df['Predicted_Severity'] = predictions

        
        save_path = file_path.replace(".csv", "_predicted.csv")
        df.to_csv(save_path, index=False)

        messagebox.showinfo(
            "Prediction Complete",
            f"Prediction completed!\n\n predicted as: {predictions[0]}\n\nResults saved as:\n{save_path}"
        )

    except Exception as e:
        messagebox.showerror("Error", f"Could not process file:\n\n{e}")

button_frame = ttk.Frame(root)
button_frame.pack(fill='x', pady=8)

tk.Button(button_frame, text="Predict Severity", command=predict_severity, bg="#d1e7dd").pack(fill='x', pady=3)
tk.Button(button_frame, text="Upload Patient File", command=load_from_file, bg="#cff4fc").pack(fill='x', pady=3)
tk.Button(button_frame, text="Load Sample (Mild)", command=lambda: load_sample_by_severity("Mild")).pack(fill='x', pady=3)
tk.Button(button_frame, text="Load Sample (Moderate)", command=lambda: load_sample_by_severity("Moderate")).pack(fill='x', pady=3)
tk.Button(button_frame, text="Load Sample (Severe)", command=lambda: load_sample_by_severity("Severe")).pack(fill='x', pady=3)

root.mainloop()
