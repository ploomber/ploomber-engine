"""
Testing notebooks against their recorded outputs
"""
import warnings

import nbformat

from ploomber_engine.ipython import PloomberClient


class NotebookTestException(Exception):
    pass


def _process_output(output):
    if output["output_type"] == "stream":
        return output["text"].strip()
    elif output["output_type"] == "execute_result":
        text_plain = output["data"].get("text/plain")

        if text_plain:
            if "[<matplotlib." in text_plain:
                return None
            else:
                return text_plain.strip()

        image_png = output["data"].get("image/png")

        if image_png:
            warnings.warn("Image found, it will be ignore...")
            return None


def _process_outputs(outputs):
    return [_process_output(output) for output in outputs]


def _process_notebook(nb):
    return [_process_outputs(c.outputs) for c in nb.cells]


def _compare_outputs(idx, out_ref, out_actual):
    for ref, actual in zip(out_ref, out_actual):
        if ref != actual:
            raise NotebookTestException(
                f"Error in cell {idx}: Expected output ({ref}), actual ({actual})"
            )


def test_notebook(path_to_nb):
    """Test a notebook by running it and comparing produced with existing outputs

    Notes
    -----
    .. versionadded:: 0.0.16
    """
    ref = nbformat.read(path_to_nb, as_version=nbformat.NO_CONVERT)
    ref_ = _process_notebook(ref)

    client = PloomberClient.from_path(path_to_nb)
    out = client.execute()
    out_ = _process_notebook(out)

    for idx, (expected, actual) in enumerate(zip(ref_, out_), start=1):
        len_expected = len(expected)
        len_actual = len(actual)

        if len_expected != len_actual:
            raise NotebookTestException(
                f"Error in cell {idx}: Expected number of "
                f"cell outputs ({len_expected}), actual ({len_actual})"
            )

        _compare_outputs(idx, expected, actual)
