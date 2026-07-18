# VisPerturb: A Robustness Benchmark of Natural-Language to Visualization

## Introduction
Natural-Language to Visualization (NL2Vis) aims to automatically generate visual representations over tabular data from natural-language queries, enabling users to analyze vast amounts of data and derive insights.
However, existing NL2Vis benchmarks largely assume explicit queries and normalized schema names, overlooking the diverse query expressions and schema naming conventions encountered in real-world scenarios.

To address this challenge, we present VisPerturb, a robustness benchmark that supports precise localization of NL2Vis robustness weaknesses under semantics-preserving variations in natural-language queries and database schema naming. VisPerturb defines 19 perturbation types distinguished by perturbation target and method. It comprises 7,430 perturbed evaluation instances, each paired with its original counterpart, supporting precise localization of robustness weaknesses.

## Data Structure
```txt
VisPerturb/
├─ VisEval/                      # Original VisEval dataset
├─ NLQ_Chart_synonym/            # NLQ perturbation subset
|  ├─ perturbed.json
|  ├─ perturbed_single.json
|  └─ perturbed_multiple.json
├─ ......
├─ DB_TblName_synonym/           # DB perturbation subset
|  ├─ databases/                 # Perturbed databases
|  |  └─ ......
|  ├─ perturbed.json
|  ├─ perturbed_single.json
|  ├─ perturbed_multiple.json
|  └─ perturb_mapping.json       # Mappings between Original and Perturbed Database Schemas
└─ ......
```

## Data Usage
To facilitate the use of the dataset, we provide `dataset.py` for direct access to VisPerturb. You can instantiate different subsets of VisPerturb using the following code:
```python
from pathlib import Path
from dataset import Dataset

if __name__ == "__main__":
    data_path = Path("VisPerturb")
    data = Dataset(folder=data_path, data_type="NLQ_Chart_synonym", use_perturbed=True, table_type="all")
    for instance in data.benchmark:
        nl_queries = instance["nl_queries"]
        tables = instance["tables"]
        print(nl_queries)
        print(tables)
        break
```
When using `Dataset()`, the parameters are defined as follows:
| Parameter                | Type   | Description                          |
| ------------------------ | ------ | ------------------------------------ |
| `folder`                 | `Path` | Path to the VisPerturb data directory. |
| `data_type`              | `str`  | Specifies a perturbation-type subset. It can also be used to access the complete original VisEval dataset. |
| `use_perturbed`          | `bool` | Defaults to `False`, indicating the original data corresponding to the selected perturbation subset. When set to `True`, the perturbed data are returned. |
| `table_type`             | `str`  | Defaults to `all`, indicating that all instances are included. Set it to `single` or `multiple` to select single-table or multi-table queries. |
| `with_irrelevant_tables` | `bool` | Defaults to `False`, in which case only tables relevant to the query are returned. When set to `True`, irrelevant tables are also included. |

## Evaluate
VisPerturb is fully compatible with the VisEval evaluation framework and can be evaluated directly using its existing evaluation pipeline. Please refer to the [VisEval repository](https://github.com/microsoft/VisEval) for detailed instructions.