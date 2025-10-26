import torch
import torch.nn as nn
import pandas as pd
import numpy as np
import ast
from sklearn.model_selection import train_test_split

# ------------------------
# Neural Net Definition
# ------------------------
class EMG_NN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Sigmoid()  # for binary-like output
        )

    def forward(self, x):
        return self.net(x)

# ------------------------
# Data Loading & Cleaning
# ------------------------
df = pd.read_csv("emg_test_data.csv")
data = df.copy().fillna(0)

for col in data.columns:
    if data[col].dropna().isin([True, False]).all():
        data[col] = data[col].astype(int)
        continue
    first_val = str(data[col].dropna().iloc[0]) if not data[col].dropna().empty else None
    if first_val:
        if first_val.startswith("[") or "," in first_val:
            try:
                data[col] = data[col].apply(
                    lambda x: len(ast.literal_eval(x)) if isinstance(x, str) and x.startswith("[") else (
                        len(x.split(",")) if isinstance(x, str) and "," in x else 0
                    )
                )
                continue
            except Exception:
                pass
    if data[col].dtype == object:
        data[col] = data[col].astype("category").cat.codes

data = data.apply(pd.to_numeric, errors="coerce").fillna(0)

# ------------------------
# Feature / Target split
# ------------------------
X = data[["timestamp","mouse_x","mouse_y","mouse_velocity","scroll_velocity","mouse1","mouse2","mouse3","pressed_keys"]]
y = data[["ref_voltage","ch1_voltage","ch2_voltage","ch3_voltage"]]

# Binarize outputs (since we want classification metrics)
y = (y > y.median()).astype(int)

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

X_train = torch.tensor(X_train.values, dtype=torch.float32)
y_train = torch.tensor(y_train.values, dtype=torch.float32)
X_test = torch.tensor(X_test.values, dtype=torch.float32)
y_test = torch.tensor(y_test.values, dtype=torch.float32)

# ------------------------
# Model Setup
# ------------------------
emg_model = EMG_NN(input_size=X.shape[1], hidden_size=64, output_size=y.shape[1])
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(emg_model.parameters(), lr=0.001)

# ------------------------
# Training Loop
# ------------------------
EPOCHS = 1000
for epoch in range(EPOCHS):
    outputs = emg_model(X_train)
    loss = criterion(outputs, y_train)

    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    if (epoch + 1) % 100 == 0:
        print(f"Epoch {epoch+1}/{EPOCHS} | Loss: {loss.item():.6f}")

# ------------------------
# Evaluation
# ------------------------
emg_model.eval()
with torch.no_grad():
    preds = emg_model(X_test)
    preds_binary = (preds > 0.5).float()

# Compute confusion matrix elements
TP = ((preds_binary == 1) & (y_test == 1)).sum().item()
TN = ((preds_binary == 0) & (y_test == 0)).sum().item()
FP = ((preds_binary == 1) & (y_test == 0)).sum().item()
FN = ((preds_binary == 0) & (y_test == 1)).sum().item()

# Derived metrics
accuracy = (TP + TN) / (TP + TN + FP + FN + 1e-8)
precision = TP / (TP + FP + 1e-8)
recall = TP / (TP + FN + 1e-8)
f1 = 2 * (precision * recall) / (precision + recall + 1e-8)

print("\n=== TEST SET PERFORMANCE ===")
print(f"True Positives:  {TP}")
print(f"True Negatives:  {TN}")
print(f"False Positives: {FP}")
print(f"False Negatives: {FN}")
print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")