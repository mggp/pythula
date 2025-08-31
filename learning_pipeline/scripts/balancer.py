import pandas as pd
import sqlite3 as sqlite
import json

DB_PATH = "../schemas/code_snippets.db"
OUTPUT_FILE = "../data/balanced_data.jsonl"
SEED = 42

conn = sqlite.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM snippets ORDER BY hash", conn)

counts = df["label"].value_counts()
min_count = counts.min()

balanced = (
    df.groupby("label", group_keys=False)
    .apply(lambda x: x.sample(n=min_count, random_state=SEED))
    .reset_index(drop=True)
)

print(f"Each label now has {min_count} samples")

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for _, row in balanced.iterrows():
        record = {
            "code": row["code"],
            "label": row["label"]
        }
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
