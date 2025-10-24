import torch
import torch.nn as nn
import pandas as pd
import numpy as np

class EMG_NN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.net(x)

data = pd.read_csv("emg_test_data.csv")
X = data[["ref_voltage","ch1","ch2","ch3","contact_quality","noise_level","typing","key_count"]]
y = data[["mouse_dx","mouse_dy","mouse_speed","button1","button2","scroll_press","scroll_up","scroll_down","window_focus"]]

X = torch.tensor(X.values, dtype=torch.float32)
y = torch.tensor(y.values, dtype=torch.float32)

emg_model = EMG_NN(input_size=X.shape[1], hidden_size=64, output_size=y.shape[1])
criterion = nn.MSELoss()
optimizer = torch.optim.Adam(emg_model.parameters(), lr=0.001)

epoch_losses = []
epoch_grad_norms = []
EPOCHS = 300000
for epoch in range(EPOCHS):
    outputs = emg_model(X)
    loss = criterion(outputs, y)
    optimizer.zero_grad()
    loss.backward()
    grad_norm = 0.0
    for p in emg_model.parameters():
        if p.grad is not None:
            grad_norm += p.grad.data.norm(2).item() ** 2
    grad_norm = grad_norm ** 0.5
    optimizer.step()

    epoch_losses.append(loss.item())
    epoch_grad_norms.append(grad_norm)

    # --- Epoch analytics ---
    if (epoch + 1) % 10 == 0 or epoch == 0:
        change = 0 if len(epoch_losses) < 2 else epoch_losses[-2] - epoch_losses[-1]
        print(f"Epoch {epoch+1:03d}/{EPOCHS} | "
              f"Loss: {loss.item():.6f} | "
              f"ΔLoss: {change:+.6f} | "
              f"GradNorm: {grad_norm:.3f}")

# ---- Final analysis ----
final_loss = epoch_losses[-1]
best_loss = min(epoch_losses)
best_epoch = np.argmin(epoch_losses) + 1
avg_grad = np.mean(epoch_grad_norms)
grad_stability = np.std(epoch_grad_norms)

print("\n=== FINAL TRAINING ANALYSIS ===")
print(f"Total Epochs:       {EPOCHS}")
print(f"Final Loss:         {final_loss:.6f}")
print(f"Best Loss:          {best_loss:.6f} (Epoch {best_epoch})")
print(f"Average Grad Norm:  {avg_grad:.4f}")
print(f"Grad Stability (SD):{grad_stability:.4f}")

# Quick trend check
if final_loss < epoch_losses[0] * 0.1:
    print("✅ Model converged strongly — large loss reduction.")
elif final_loss < epoch_losses[0] * 0.5:
    print("⚙️  Model improved moderately — may benefit from more epochs or LR tuning.")
else:
    print("⚠️  Minimal improvement — check learning rate, data scaling, or model capacity.")

# Evaluate final performance
emg_model.eval()
with torch.no_grad():
    preds = emg_model(X)

# Error metrics
mse_per_output = torch.mean((preds - y) ** 2, dim=0)
mae_per_output = torch.mean(torch.abs(preds - y), dim=0)

print("\n=== PER-OUTPUT METRICS ===")
for i, col in enumerate(y.shape[1] if hasattr(y, 'columns') else range(y.shape[1])):
    print(f"Output {i:02d}: MSE={mse_per_output[i]:.6f} | MAE={mae_per_output[i]:.6f}")

# Aggregate stats
overall_mse = torch.mean(mse_per_output).item()
overall_mae = torch.mean(mae_per_output).item()
print(f"\nOverall MSE: {overall_mse:.6f} | Overall MAE: {overall_mae:.6f}")

# Random sample check
idx = np.random.randint(0, len(X))
print("\nSample prediction vs target:")
print(f"Pred: {preds[idx].numpy().round(3)}")
print(f"True: {y[idx].numpy().round(3)}")
