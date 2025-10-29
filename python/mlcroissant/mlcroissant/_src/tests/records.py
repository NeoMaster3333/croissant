"""Test utils to handle records."""

import hashlib
import math
import re
from typing import Any

import numpy as np
import pandas as pd


def record_to_python(record: Any):
    """Converts a record to a fully Python-native object.

    Warning: this function must be used for testing-purposes only!

    Records may contain non-serializable values (like `nan` or `pd.Timestamp` for
    example). This util converts records to Python-native objects:
    - bytes -> UTF-8 string (fallback to compact binary summary if not valid UTF-8)
    - nan -> None
    - pd.Timestamp -> pd.Timestamp.strftime
    """
    if isinstance(record, bytes):
        try:
            return record.decode()
        except UnicodeDecodeError:
            # Return a compact, deterministic summary for binary payloads
            md5 = hashlib.md5(record).hexdigest()
            size = len(record)
            return f"<BINARY md5={md5} size={size}B>"
    elif isinstance(record, pd.Timestamp):
        return record.strftime("%Y-%m-%d %X")
    elif isinstance(record, float) and math.isnan(record):
        return None
    elif isinstance(record, tuple) and record and isinstance(record[0], np.ndarray):
        array = record[0]
        rest = record[1:]
        array_repr = np.array2string(
            array, separator=", ", max_line_width=10**9
        )
        array_repr = array_repr.replace("..., ", "...,\n       ", 1)
        shape_repr = f"shape={array.shape}"
        dtype_repr = f"dtype={array.dtype}"
        array_summary = f"(array({array_repr},\n      {shape_repr}, {dtype_repr})"
        if rest:
            rest_repr = ", ".join(str(item) for item in rest)
            array_summary = f"{array_summary}, {rest_repr})"
        else:
            array_summary = f"{array_summary})"
        return array_summary
    elif isinstance(record, (bool, float, int)):
        return record
    elif not isinstance(record, dict):
        str_repr = str(record)
        # Remove memory addresses from string representation.
        memory_addresses = re.compile(r"0x[0-9a-fA-F]+")
        return memory_addresses.sub("<MEMORY_ADDRESS>", str_repr)
    else:
        # Record is a dict
        for key, value in record.items():
            record[key] = record_to_python(value)
        return record
