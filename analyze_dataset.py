import csv, sys
sys.stdout.reconfigure(encoding='utf-8')

with open("data/raw/dataset_oncologie_FINAL_v6.csv", "r", encoding="utf-8") as f:
    r = csv.reader(f)
    header = next(r)
    row1 = next(r)

print("CSV Header:")
print(header)
print("\nCSV Row 1:")
print(row1)
