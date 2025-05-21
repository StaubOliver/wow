import json
import random

source_path = "data.jsonl"
target_path = "index.json"

# Read all items from source.jsonl
with open(source_path, "r", encoding="utf-8") as f:
    lines = f.readlines()

if not lines:
    print("No items left in source.jsonl")
    exit(0)

# ---- Modify this selection logic as needed ----
# For example: pick the first, random, or based on some field
idx = random.randint(0, len(lines) - 1)
item = json.loads(lines[idx])
# ------------------------------------------------

# Append the selected item to target.jsonl
with open(target_path, "w", encoding="utf-8") as f:
    f.write(json.dumps(item))


print(f"Moved item: {item}")
