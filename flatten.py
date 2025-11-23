import os
import shutil

SOURCE_DIR = "graphs/csv/bi/composite-projected-fk/initial_snapshot"
OUTPUT_DIR = "csv_files"

subfolders = ["dynamic", "static"]

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

print(f"processing files in {SOURCE_DIR}...")

for sub in subfolders:
    search_path = os.path.join(SOURCE_DIR, sub)
    if not os.path.exists(search_path):
        print(f"Not found: {search_path}")
        continue
        
    for entity_name in os.listdir(search_path):
        entity_path = os.path.join(search_path, entity_name)
        
        if os.path.isdir(entity_path):
            for filename in os.listdir(entity_path):
                if filename.startswith("part-") and filename.endswith(".csv"):

                    src_file = os.path.join(entity_path, filename)
                    dst_name = f"{entity_name}.csv"
                    dst_file = os.path.join(OUTPUT_DIR, dst_name)
                    
                    print(f"Copying: {entity_name} -> {dst_file}")
                    shutil.copy(src_file, dst_file)

print("\nDone.")
