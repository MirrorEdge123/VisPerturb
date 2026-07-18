# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import copy
import json

import sqlglot
from sqlglot.expressions import Table

from pathlib import Path
from typing import Literal, get_args


_DATA_TYPES = Literal[
    "VisEval",
    "NLQ_Keyword_synonym", "NLQ_Keyword_indirect",
    "NLQ_Chart_synonym", "NLQ_Chart_indirect",
    "NLQ_ColRef_synonym", "NLQ_ColRef_indirect", "NLQ_ColRef_attribute", "NLQ_ColRef_value", "NLQ_ColRef_typo",
    "NLQ_TblRef_synonym", "NLQ_TblRef_typo",
    "NLQ_Value_synonym", "NLQ_Random_typo", "NLQ_Multitype", "NLQ_Sentence_syntactic",
    "DB_ColName_synonym", "DB_ColName_abbreviation", "DB_TblName_synonym", "DB_TblName_abbreviation"
]

_TABLE_TYPES = Literal["all", "single", "multiple"]


class Dataset:
    def __init__(
        self,
        folder: Path,
        data_type: _DATA_TYPES,
        use_perturbed: bool = False,
        table_type: _TABLE_TYPES = "all",
        with_irrelevant_tables: bool = False,
    ):
        if data_type not in get_args(_DATA_TYPES):
            raise ValueError(
                f"Invalid data_type: {data_type}. "
                f"Must be one of {get_args(_DATA_TYPES)}.")
        if table_type not in get_args(_TABLE_TYPES):
            raise ValueError(
                f"Invalid table_type: {table_type}. "
                f"Must be one of {get_args(_TABLE_TYPES)}.")
        if data_type == "VisEval" and use_perturbed:
            raise ValueError("No perturbed data for VisEval.")

        self.folder = folder
        self.data_folder = folder / "visEval_dataset" if data_type == "VisEval" else folder / data_type

        dict_name = "visEval" if data_type == "VisEval" else "perturbed"
        if table_type != "all":
            dict_name += "_" + table_type
        dict_name += ".json"
        with open(self.data_folder / dict_name, "r", encoding="utf-8") as f:
            data_dict = json.load(f)

        if data_type == "VisEval":
            self.dict = copy.deepcopy(data_dict)
        else:
            if use_perturbed:
                self.dict = self.__process_perturbed(data_dict)
            else:
                self.dict = self.__get_original(data_dict)

        if data_type.startswith("DB") and use_perturbed:
            self.db_dir = self.data_folder / "databases"
        else:
            self.db_dir = self.folder / "visEval_dataset" / "databases"
        with open(self.db_dir / "db_tables.json", "r", encoding="utf-8") as f:
            self.db_tables = json.load(f)

        def benchmark():
            for key in list(self.dict.keys()):
                self.dict[key]["id"] = key
                self.dict[key]["tables"] = self.__get_tables(key, with_irrelevant_tables)
                yield self.dict[key]

        self.benchmark = benchmark()

    def __process_perturbed(self, perturbed_data: dict):
        processed_data = {}
        for instance_id, instance in perturbed_data.items():
            processed_instance = copy.deepcopy(instance)

            processed_instance.pop("original_id", None)
            processed_instance.pop("original_index", None)
            processed_instance.pop("k", None)

            processed_data[instance_id] = processed_instance

        return processed_data

    def __get_original(self, perturbed_data: dict):
        with open(self.folder / "visEval_dataset" / "visEval.json", "r", encoding="utf-8") as f:
            visEval_data = json.load(f)

        original_data = {}
        for instance_id, instance in perturbed_data.items():
            original_id = instance["original_id"]
            original_index = instance["original_index"]
            original_instance = copy.deepcopy(visEval_data[original_id])

            original_instance["nl_queries"] = [original_instance["nl_queries"][idx]
                                               for idx in original_index]
            original_instance["query_meta"] = [original_instance["query_meta"][idx]
                                               for idx in original_index]
            original_instance.pop("original_id", None)
            original_instance.pop("original_index", None)
            original_instance.pop("k", None)

            original_data[instance_id] = original_instance

        return original_data

    def __extract_tables(self, sql: str):
        try:
            parsed = sqlglot.parse_one(sql)
            tables = set()
            for table in parsed.find_all(Table):
                tables.add(table.name)
            return list(tables)
        except Exception as e:
            return None

    def __get_tables(self, spec_id: str, with_irrelevant_tables: bool = False):
        spec = self.dict[spec_id]
        db_id = spec["db_id"]
        # table name
        all_table_names = self.db_tables[db_id]

        vis_tables = self.__extract_tables(spec["vis_query"]["data_part"]["sql_part"].lower())

        if vis_tables is None:
            return []

        table_names = [
            x
            for x in all_table_names
            if x.lower() in vis_tables
        ]

        if with_irrelevant_tables:
            irrelevant_tables = [
                x
                for x in all_table_names
                if x.lower() in [table.lower() for table in spec["irrelevant_tables"]]
            ]
            table_names.extend(irrelevant_tables)

        tables = list(
            map(
                lambda table_name: str(self.db_dir / db_id / f"{table_name}.csv"),
                table_names,
            )
        )

        return tables