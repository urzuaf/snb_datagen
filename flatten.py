import os
import shutil
import glob

# Detectar automáticamente si se ejecuta desde la raíz o dentro de out/
if os.path.exists("graphs/csv/bi/composite-projected-fk"):
    SOURCE_DIR = "graphs/csv/bi/composite-projected-fk" 
else:
    SOURCE_DIR = "out/graphs/csv/bi/composite-projected-fk"

OUTPUT_DIR = "flat_csv"                                 
subfolders = ["initial_snapshot/dynamic", "initial_snapshot/static"]   
def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    for sub in subfolders:
        search_path = os.path.join(SOURCE_DIR, sub)
        if not os.path.exists(search_path):
            print(f"Not found: {search_path}")
            continue
            
        print(f"\n--- Procesando subcarpeta: {sub} ---")
        
        for entity_name in sorted(os.listdir(search_path)):
            entity_path = os.path.join(search_path, entity_name)
            
            if os.path.isdir(entity_path):
                # Buscar todas las particiones generadas por Spark (ordenadas)
                part_files = sorted(glob.glob(os.path.join(entity_path, "part-*.csv")))
                
                if not part_files:
                    continue

                dst_file = os.path.join(OUTPUT_DIR, f"{entity_name}.csv")
                print(f"Uniendo {len(part_files)} partes para: {entity_name} -> {dst_file}")

                # Unir particiones en un único archivo
                with open(dst_file, 'wb') as outfile:
                    for i, part in enumerate(part_files):
                        with open(part, 'rb') as infile:
                            if i > 0:
                                # Descartar la línea 1 (header) de las partes 1, 2, 3...
                                infile.readline()
                            
                            # Copiar el contenido directamente
                            shutil.copyfileobj(infile, outfile)

    print("\n¡Listo! Todos los archivos quedaron unificados.")

if __name__ == "__main__":
    main()
