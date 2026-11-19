
import torch
import os

file_path = "best.pt"

if not os.path.exists(file_path):
    print("best.pt not found!")
    exit()

checkpoint = torch.load(
    file_path,
    map_location="cpu",
    weights_only=False
)

print("\n========== MODEL CHECKPOINT ==========")

print("Checkpoint keys:", checkpoint.keys())

print("\n========== TRAINING ARGUMENTS ==========")

args = checkpoint.get("train_args", {})

if args:
    for key, value in args.items():
        print(f"{key}: {value}")
else:
    print("Training arguments not available.")

print("\n========== MODEL INFORMATION ==========")

print("Epoch:", checkpoint.get("epoch", "Unknown"))
print("Best fitness:", checkpoint.get("best_fitness", "Unknown"))

print("\n========== MODEL METADATA ==========")

print("Date:", checkpoint.get("date", "Unknown"))
print("Version:", checkpoint.get("version", "Unknown"))
print("License:", checkpoint.get("license", "Unknown"))
