# LDBC SNB Dataset Generator & Converter

This repository contains tools to generate LDBC Social Network Benchmark (SNB) datasets using Docker and convert them into PGDF (Property Graph Data Format).

Prerequisites

- Docker installed and running.

- Python 3.

## Usage Guide

### Generate data

Follow these steps to generate and convert the data.

1. Pull the Docker Image

Download the specific version of the LDBC Datagen image to ensure compatibility.

```bash
docker pull ldbc/datagen-standalone:0.5.1-19-829b7a04-2.12_spark3.2
```

2. Generate the Dataset

Create the output directory and run the generator.

You can adjust the `--scale-factor` parameter to change the size of the dataset.

Available Scale Factors: 
- 0.003
- 0.1
- 0.3
- 1
- 3
- 10
- 30
- 100
- 300
- 1000
- 3000
- 10000
- 30000

Run the following command (example uses SF 0.003):

```bash
mkdir out

docker run --interactive --tty --rm \
  --mount type=bind,source="$(pwd)/out",target=/out \
  ldbc/datagen-standalone:0.5.1-19-829b7a04-2.12_spark3.2 \
  --parallelism 1 \
  -- \
  --mode bi \
  --format csv \
  --scale-factor 0.003 \
  --epoch-millis \
  --explode-edges \
  --output-dir /out

```

3. Convert to PGDF

Once the generation finishes, use the provided Python scripts to flatten the Spark output and convert it to PGDF.

```bash
cd out
cp ../flatten.py ../convert.py .
python3 flatten.py && python3 convert.py
rm flatten.py convert.py
```

## Output

The final processed files will be located in:

```bash
out/pgdf_output/
├── Nodes.pgdf
└── Edges.pgdf
```