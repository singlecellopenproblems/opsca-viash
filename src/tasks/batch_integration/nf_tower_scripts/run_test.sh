#!/bin/bash

DATASET_DIR=resources_test/batch_integration/pancreas

# try running on nf tower
cat > /tmp/params.yaml << HERE
id: batch_integration_test
input_dir: s3://openproblems-data/resources_test/batch_integration/pancreas/
rename_keys: 'input_dataset:output_dataset,input_solution:output_solution'
settings: '{"output": "scores.tsv"}'
publish_dir: s3://openproblems-nextflow/output_test/v2/batch_integration/
HERE

cat > /tmp/nextflow.config << HERE
process {
  executor = 'awsbatch'
}
HERE

tw launch https://github.com/openproblems-bio/openproblems-v2.git \
  --revision main_build \
  --pull-latest \
  --main-script target/nextflow/batch_integration/workflows/run_benchmark/main.nf \
  --workspace 53907369739130 \
  --compute-env 7IkB9ckC81O0dgNemcPJTD \
  --params-file /tmp/params.yaml \
  --entry-name auto \
  --config /tmp/nextflow.config