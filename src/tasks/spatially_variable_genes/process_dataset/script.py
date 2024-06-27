import anndata as ad
import sys 

## VIASH START
par = {
    "input": "resources_test/common/10x_visium_mouse_brain/dataset.h5ad",
    "output_dataset": "dataset.h5ad",
    "output_solution": "solution.h5ad",
}
meta = {
    "functionality_name": "process_dataset",
    "resources_dir": "src/tasks/spatially_variable_genes/process_dataset",
    "config": "target/nextflow/spatially_variable_genes/process_dataset/.config.vsh.yaml"
}
## VIASH END

sys.path.append(meta['resources_dir'])
from subset_anndata import read_config_slots_info, subset_anndata

print(">> Load dataset", flush=True)
adata = ad.read_h5ad(par["input"])

print(">> Figuring out which data needs to be copied to which output file", flush=True)
slot_info = read_config_slots_info(meta["config"])

print(">> Create dataset for methods", flush=True)
output_dataset = subset_anndata(adata, slot_info['output_dataset'])
# TODO: remove gene names to prevent data leakage!

print(">> Create solution object for metrics", flush=True)
output_solution = subset_anndata(adata, slot_info['output_solution'])

print(">> Write to disk", flush=True)
output_dataset.write_h5ad(par["output_dataset"])
output_solution.write_h5ad(par["output_solution"])
