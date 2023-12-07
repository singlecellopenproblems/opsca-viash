#!/bin/bash

cat > /tmp/params.yaml << HERE
id: batch_integration_process_datasets
input_states: s3://openproblems-nextflow/resources/datasets/openproblems_v1/**/state.yaml
rename_keys: 'input:output_dataset'
settings: '{"output_dataset": "dataset.h5ad", "output_solution": "solution.h5ad"}'
publish_dir: s3://openproblems-nextflow/resources/
HERE

cat > /tmp/nextflow.config << HERE
process {
  executor = 'awsbatch'
}
HERE

tw launch https://github.com/openproblems-bio/openproblems-v2.git \
  --revision integration_build \
  --pull-latest \
  --main-script target/nextflow/batch_integration/workflows/process_datasets/main.nf \
  --workspace 53907369739130 \
  --compute-env 7IkB9ckC81O0dgNemcPJTD \
  --params-file /tmp/params.yaml \
  --entry-name auto \
  --config /tmp/nextflow.config