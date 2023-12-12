#!/bin/bash

# get the root of the directory
REPO_ROOT=$(git rev-parse --show-toplevel)

# ensure that the command below is run from the root of the repository
cd "$REPO_ROOT"

params_file="/tmp/datasets_openproblems_v1_multimodal_params.yaml"

cat > "$params_file" << 'HERE'
param_list:
  - id: citeseq_cbmc
    dataset_name: "CITE-Seq CBMC"
    dataset_summary: "CITE-seq profiles of 8k Cord Blood Mononuclear Cells"
    dataset_description: "8k cord blood mononuclear cells profiled by CITEsequsing a panel of 13 antibodies."
    dataset_reference: stoeckius2017simultaneous
    dataset_url: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE100866
    dataset_organism: homo_sapiens
    layer_counts: counts

  - id: scicar_cell_lines
    dataset_name: "sci-CAR Cell Lines"
    dataset_summary: "sci-CAR profiles of 5k cell line cells (HEK293T, NIH/3T3, A549) across three treatment conditions (DEX 0h, 1h and 3h)"
    dataset_description: "Single cell RNA-seq and ATAC-seq co-profiling for HEK293T cells, NIH/3T3 cells, A549 cells across three treatment conditions (DEX 0 hour, 1 hour and 3 hour treatment)."
    dataset_reference: cao2018joint
    dataset_url: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE117089
    dataset_organism: "[homo_sapiens, mus_musculus]"
    obs_cell_type: cell_name
    layer_counts: counts

  - id: scicar_mouse_kidney
    dataset_name: "sci-CAR Mouse Kidney"
    dataset_summary: "sci-CAR profiles of 11k mouse kidney cells"
    dataset_description: "Single cell RNA-seq and ATAC-seq co-profiling of 11k mouse kidney cells."
    dataset_reference: cao2018joint
    dataset_url: https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE117089
    dataset_organism: mus_musculus
    obs_cell_type: cell_name
    obs_batch: replicate
    layer_counts: counts

normalization_methods: [log_cp10k, sqrt_cp10k, l1_sqrt]
output_dataset_mod1: '$id/dataset_mod1.h5ad'
output_dataset_mod2: '$id/dataset_mod2.h5ad'
output_meta_mod1: '$id/dataset_metadata_mod1.yaml'
output_meta_mod2: '$id/dataset_metadata_mod2.yaml'
output_state: '$id/state.yaml'
publish_dir: s3://openproblems-nextflow/resources/datasets/openproblems_v1_multimodal
HERE

tw launch https://github.com/openproblems-bio/openproblems-v2.git \
  --revision main_build \
  --pull-latest \
  --main-script target/nextflow/datasets/workflows/process_openproblems_v1_multimodal/main.nf \
  --workspace 53907369739130 \
  --compute-env 7IkB9ckC81O0dgNemcPJTD \
  --params-file "$params_file" \