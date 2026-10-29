"""JSON Lines (JSONL) file reading and writing utilities."""
import json
from typing import Generator, List, Dict, Any, Tuple
from pathlib import Path


def read_jsonl(file_path: Path | str) -> Generator[Tuple[int, Dict[str, Any]], None, None]:
    """Stream lines from a JSONL file yielding (line_number, parsed_dict).
    
    If a line is malformed JSON, yields a dict containing `_raw_error`.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                data = json.loads(line_str)
                yield idx, data
            except json.JSONDecodeError as err:
                yield idx, {"_raw_error": str(err), "_raw_line": line_str}


def write_jsonl(file_path: Path | str, records: List[Dict[str, Any]]) -> int:
    """Write records to a JSONL file, one JSON object per line. Returns count written."""
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return len(records)
