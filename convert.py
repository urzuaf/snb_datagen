import os
import csv

INPUT_DIR = "csv_files"
OUTPUT_DIR = "pgdf_output"

DELIMITER_IN = '|'
DELIMITER_OUT = '|'

FORCE_PLACE_TARGET = ["isLocatedIn", "isPartOf"] 

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_clean_id(type_label, raw_id):
    return f"{type_label.lower()}_{raw_id}"

def process_nodes(files):
    print("processing nodes...")
    output_path = os.path.join(OUTPUT_DIR, "Nodes.pgdf")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=DELIMITER_OUT, quoting=csv.QUOTE_MINIMAL)
        
        for filename in files:
            if '_' in filename:
                continue
                
            label = os.path.splitext(filename)[0] 
            label = label.upper()
            file_path = os.path.join(INPUT_DIR, filename)
            
            print(f"Processing node: {label}")
            
            with open(file_path, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile, delimiter=DELIMITER_IN)
                headers = next(reader)
                
                try:
                    id_idx = headers.index('id')
                except ValueError:
                    print(f"️ERROR: column 'id' not found in: {filename}. Skipping.")
                    continue
                
                props_indices = [i for i, h in enumerate(headers) if h != 'id']
                props_names = [headers[i] for i in props_indices]
                
                pgdf_header = ["@id", "@label"] + props_names
                writer.writerow(pgdf_header)
                
                count = 0
                for row in reader:
                    original_id = row[id_idx]
                    unique_id = get_clean_id(label, original_id)
                    
                    row_data = [unique_id, label] + [row[i] for i in props_indices]
                    writer.writerow(row_data)
                    count += 1
                print(f"  -> {count} nodes written.")

def get_edge_col_indices(headers, src_type, dst_type):
    src_idx = -1
    dst_idx = -1
    
    if src_type == dst_type:
        for i, h in enumerate(headers):
            if "1Id" in h: src_idx = i
            if "2Id" in h: dst_idx = i
    else:
        for i, h in enumerate(headers):
            if h == f"{src_type}Id": src_idx = i
            if h == f"{dst_type}Id": dst_idx = i
            
            if dst_idx == -1 and "Id" in h and dst_type in h:
                dst_idx = i

    return src_idx, dst_idx

def process_edges(files):
    print("\nProcessing edges")
    output_path = os.path.join(OUTPUT_DIR, "Edges.pgdf")
    
    with open(output_path, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile, delimiter=DELIMITER_OUT, quoting=csv.QUOTE_MINIMAL)
        
        for filename in files:
            if '_' not in filename:
                continue
                
            name_parts = os.path.splitext(filename)[0].split('_')
            if len(name_parts) != 3:
                print(f"skipping, unsupported name format: {filename}")
                continue
                
            src_type, rel_label, dst_type_raw = name_parts
            
            if rel_label in FORCE_PLACE_TARGET:
                dst_type_final = "Place"
            else:
                dst_type_final = dst_type_raw

            # Capitalize first letter but keep the rest intact, not lowercasing them
            cap_label = rel_label.capitalize()[0]
            rel_label = cap_label + rel_label[1:]

            file_path = os.path.join(INPUT_DIR, filename)
            print(f"Processing edge: {src_type} -[{rel_label}]-> {dst_type_raw}")
            
            with open(file_path, 'r', encoding='utf-8') as infile:
                reader = csv.reader(infile, delimiter=DELIMITER_IN)
                headers = next(reader)
                
                src_idx, dst_idx = get_edge_col_indices(headers, src_type, dst_type_raw)
                
                if src_idx == -1 or dst_idx == -1:
                    print(f"️ERROR: could not find ids in {filename} headers: {headers}")
                    continue
                
                props_indices = [i for i, h in enumerate(headers) if i != src_idx and i != dst_idx]
                props_names = [headers[i] for i in props_indices]
                
                pgdf_header = ["@id", "@label", "@dir", "@out", "@in"] + props_names
                writer.writerow(pgdf_header)
                
                count = 0
                for row in reader:
                    src_raw = row[src_idx]
                    dst_raw = row[dst_idx]
                    
                    src_pgdf_id = get_clean_id(src_type, src_raw)
                    
                    dst_pgdf_id = get_clean_id(dst_type_final, dst_raw)
                    
                    edge_unique_id = f"{rel_label.lower()}_{src_pgdf_id}_{dst_pgdf_id}"
                    
                    row_data = [edge_unique_id, rel_label, 'T', src_pgdf_id, dst_pgdf_id] + [row[i] for i in props_indices]
                    
                    writer.writerow(row_data)
                    count += 1
                print(f"  -> {count} edges written.")

def main():
    ensure_dir(OUTPUT_DIR)
    files = sorted([f for f in os.listdir(INPUT_DIR) if f.endswith('.csv')])
    
    if not files:
        print(f"Error: No CSV files in {INPUT_DIR}")
        return

    process_nodes(files)
    process_edges(files)
    print(f"\nDone. files in: '{OUTPUT_DIR}'")

if __name__ == "__main__":
    main()