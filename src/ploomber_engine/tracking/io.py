"""
NOTE: this was copied from
https://github.com/ploomber/jupyblog/blob/master/src/jupyblog/execute.py
"""
from pathlib import Path
import base64
import re

PLAIN = "text/plain"
HTML = "text/html"
PNG = "image/png"
ANSI_ESCAPE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _process_content_data(
    content, counter, idx, serialize_images=False, img_dir=None, canonical_name=None
):
    """
    Parameters
    ----------
    content : list
        "outputs" key in a notebook's cell
    counter : str
        Prefix to apply to image paths. Only used if
        serialize_images=True
    idx : str
        Suffix to apply to the image path. Only used if
        serialize_images=True
    serialize_images : bool, default=False
        Serialize images as .png files. Otherwise, embed them as base64 strings
    img_dir : str, default=None
        Folder to serialize images. Only used if serialize_images=True
    canonical_name : str, default=None
        Used to construct the path to the images for this post:
        {img_dir}/{canonical_name}/serialized. Only used if
        serialize_images=True
    """

    if "data" in content:
        data = content["data"]

        if data.get("image/png"):
            image_base64 = data.get("image/png")

            if serialize_images:
                serialized = Path(img_dir, canonical_name, "serialized")
                serialized.mkdir(exist_ok=True, parents=True)

                id_ = f"{counter}-{idx}"
                filename = f"{id_}.png"
                path_to_image = serialized / filename
                base64_2_image(image_base64, path_to_image)

                return (HTML, f"![{id_}](serialized/{filename})")
            else:
                return PNG, base64_html_tag(image_base64)
        if data.get("text/html"):
            return HTML, data.get("text/html")
        else:
            return PLAIN, data["text/plain"]
    elif "text" in content:
        out = content["text"].rstrip()

        if out[-1] != "\n":
            out = out + "\n"

        return PLAIN, out
    elif "traceback" in content:
        return PLAIN, remove_ansi_escape("\n".join(content["traceback"]))


def remove_ansi_escape(s):
    """
    https://stackoverflow.com/a/14693789/709975
    """
    return ANSI_ESCAPE.sub("", s)


def base64_2_image(message, path_to_image):
    bytes = message.encode().strip()
    message_bytes = base64.b64decode(bytes)
    Path(path_to_image).write_bytes(message_bytes)


def base64_html_tag(base64):
    return f'<img src="data:image/png;base64, {base64.strip()}"/>'
