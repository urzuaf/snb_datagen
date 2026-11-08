#!/usr/bin/env python3
import os
import sys
import time


def find_file(name):
    candidates = [
        name,
        os.path.join("pgdf_output", name),
        os.path.join("out", "pgdf_output", name),
    ]
    for c in candidates:
        if os.path.exists(c):
            return c
    return name


def validate():
    nodes_file = sys.argv[1] if len(sys.argv) > 1 else find_file("Nodes.pgdf")
    edges_file = sys.argv[2] if len(sys.argv) > 2 else find_file("Edges.pgdf")

    if not os.path.exists(nodes_file):
        print(f"Error: No se encontró '{nodes_file}'")
        sys.exit(1)
    if not os.path.exists(edges_file):
        print(f"Error: No se encontró '{edges_file}'")
        sys.exit(1)

    start_time = time.time()

    # Cargar IDs de nodos
    print(f"Cargando nodos desde '{nodes_file}'...")
    node_ids = set()
    total_nodes = 0

    with open(nodes_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line or line.startswith("@id"):
                continue
            pipe_idx = line.find("|")
            node_id = line[:pipe_idx].strip() if pipe_idx != -1 else line.strip()
            node_ids.add(node_id)
            total_nodes += 1
            if total_nodes % 5_000_000 == 0:
                print(f"  -> {total_nodes:,} nodos procesados...")

    print(
        f"✓ Total nodos únicos cargados: {len(node_ids):,} (en {time.time() - start_time:.1f}s)"
    )

    # Validar aristas
    print(f"\nValidando aristas en '{edges_file}'...")
    edges_start = time.time()
    total_edges = 0
    missing_src = 0
    missing_dst = 0
    examples = []

    with open(edges_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line or line.startswith("@id"):
                continue

            total_edges += 1
            parts = line.split("|", 5)
            if len(parts) < 5:
                continue

            src = parts[3].strip()
            dst = parts[4].strip()

            if src not in node_ids:
                missing_src += 1
                if len(examples) < 10:
                    examples.append(
                        f"Fila {total_edges}: SRC inexistente -> '{src}' (Arista: {parts[0]}, Label: {parts[1]})"
                    )

            if dst not in node_ids:
                missing_dst += 1
                if len(examples) < 10:
                    examples.append(
                        f"Fila {total_edges}: DST inexistente -> '{dst}' (Arista: {parts[0]}, Label: {parts[1]})"
                    )

            if total_edges % 20_000_000 == 0:
                print(f"  -> {total_edges:,} aristas revisadas...")

    print(f"\n================ RESUMEN DE VALIDACIÓN ================")
    print(f"Total aristas analizadas : {total_edges:,}")
    print(f"Aristas con SRC faltante : {missing_src:,}")
    print(f"Aristas con DST faltante : {missing_dst:,}")
    print(f"Tiempo de validación     : {time.time() - edges_start:.1f}s")

    if examples:
        print(f"\n  Primeros errores encontrados:")
        for ex in examples:
            print(f"  - {ex}")
    else:
        print("\n Todas las aristas apuntan a nodos válidos.")


if __name__ == "__main__":
    validate()
