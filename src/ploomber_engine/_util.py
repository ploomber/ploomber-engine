from pathlib import Path
import re

import nbformat

from ploomber_engine._translator import translate_parameters


# taken from jupytext
def recursive_update(target, update):
    for key in update:
        value = update[key]
        if value is None:
            del target[key]
        elif isinstance(value, dict):
            target[key] = recursive_update(target.get(key, {}), value)
        else:
            target[key] = value

    return target


def find_cell_with_tags(nb, tags):
    """
    Find the first cell with any of the given tags, returns a dictionary
    with 'cell' (cell object) and 'index', the cell index.
    """
    tags_to_find = list(tags)
    tags_found = {}

    for index, cell in enumerate(nb["cells"]):
        for tag in cell["metadata"].get("tags", []):
            if tag in tags_to_find:
                tags_found[tag] = dict(cell=cell, index=index)
                tags_to_find.remove(tag)

                if not tags_to_find:
                    break

    return tags_found


def find_cell_with_tag(nb, tag):
    """
    Find a cell with a given tag, returns a cell, index tuple. Otherwise
    (None, None)
    """
    out = find_cell_with_tags(nb, [tag])

    if out:
        located = out[tag]
        return located["cell"], located["index"]
    else:
        return None, None


def find_cell_with_parameters_comment(nb):
    """
    Find cell with a "# parameters" comment (case independent). If it finds a cell
    matchinf the criteria, it returns a (cell, index) tuple, otherwise, it returns
    (None, None)
    """
    for idx, cell in enumerate(nb["cells"]):
        if re.match(r"\s*#\s*PARAMETERS?\s*", cell["source"]) or re.match(
            r"\s*#\s*parameters?\s*", cell["source"]
        ):
            return cell, idx

    return None, None


def parametrize_notebook(nb, parameters):
    """Add parameters to a notebook object"""
    _, idx_injected = find_cell_with_tag(nb, "injected-parameters")
    _, idx_params = find_cell_with_tag(nb, "parameters")
    _, idx_comment = find_cell_with_parameters_comment(nb)

    insert = True

    if idx_injected is not None:
        insert = False
        idx_to_inject = idx_injected
    elif idx_params is not None and idx_comment is None:
        idx_to_inject = idx_params + 1
    elif idx_params is None and idx_comment is not None:
        idx_to_inject = idx_comment + 1
    elif idx_params is not None and idx_comment is not None:
        idx_to_inject = max(idx_params, idx_comment) + 1
    else:
        idx_to_inject = 0

    params_translated = translate_parameters(
        parameters=parameters, comment="Injected parameters"
    )
    nbformat_ = nbformat.versions[nb.nbformat]
    params_cell = nbformat_.new_code_cell(
        params_translated, metadata=dict(tags=["injected-parameters"])
    )

    if insert:
        nb.cells.insert(idx_to_inject, params_cell)
    else:
        nb.cells[idx_to_inject] = params_cell

    return nb


def add_debuglater_cells(nb, path_to_dump=None):
    """Injects a cell at the top with to enable debuglater"""
    _, idx = find_cell_with_tag(nb, "injected-debuglater")

    if path_to_dump is None:
        source = """
from debuglater import patch_ipython
patch_ipython()
"""
    else:
        source = f"""
from debuglater import patch_ipython
patch_ipython({str(path_to_dump)!r})
"""
    nbformat_ = nbformat.versions[nb["nbformat"]]

    cell_debuglater = nbformat_.new_code_cell(
        source=source, metadata=dict(tags=["injected-debuglater"])
    )

    if idx is not None:
        nb.cells[idx] = cell_debuglater
    else:
        nb.cells.insert(0, cell_debuglater)


def sibling_with_suffix(path, suffix):
    """
    Returns a path to a file in the same directory with the same
    filename (but no extension) and with the added suffix
    """
    path = Path(path)
    return path.with_name(path.stem + suffix)
