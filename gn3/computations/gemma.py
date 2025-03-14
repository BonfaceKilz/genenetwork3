"""Procedures related gemma computations"""
import os

from base64 import b64encode
from hashlib import md5
from typing import Optional, Dict
from typing import List
from gn3.commands import compose_gemma_cmd
from gn3.fs_helpers import get_hash_of_files


def generate_hash_of_string(unhashed_str: str) -> str:
    """Given an UNHASHED_STRING, generate it's md5 hash while removing the '==' at
the end"""
    hashed_str = md5(unhashed_str.encode("utf-8")).digest()
    return b64encode(hashed_str).decode("utf-8").replace("==", "")


def generate_pheno_txt_file(trait_filename: str,
                            values: List,
                            tmpdir: str = "/tmp") -> str:
    """Given VALUES, and TMPDIR, generate a valid traits file"""

    if not os.path.isdir(f"{tmpdir}/gn3/"):
        os.mkdir(f"{tmpdir}/gn3/")
    ext = trait_filename.partition(".")[-1]
    if ext:
        trait_filename = trait_filename.replace(f".{ext}", "")
        ext = f".{ext}"
    trait_filename += f"_{generate_hash_of_string(''.join(values))}{ext}"
    # Early return if this already exists!
    if os.path.isfile(f"{tmpdir}/gn3/{trait_filename}"):
        return f"{tmpdir}/gn3/{trait_filename}"
    with open(f"{tmpdir}/gn3/{trait_filename}", "w", encoding="utf-8") as _file:
        for value in values:
            if value == "x":
                _file.write("NA\n")
            else:
                _file.write(f"{value}\n")
    return f"{tmpdir}/gn3/{trait_filename}"


# pylint: disable=R0913
def generate_gemma_cmd(# pylint: disable=[too-many-positional-arguments]
        gemma_cmd: str,
        output_dir: str,
        token: str,
        gemma_kwargs: Dict,
        gemma_wrapper_kwargs: Optional[Dict] = None,
        chromosomes: Optional[str] = None) -> Dict:
    """Compute k values"""
    _hash = get_hash_of_files(
        [v for k, v in gemma_kwargs.items() if k in ["g", "p", "a", "c"]])
    if chromosomes:  # Only reached when calculating k-values
        gemma_wrapper_kwargs = {"loco": f"{chromosomes}"}
        _hash += f"-{generate_hash_of_string(chromosomes)[:6]}"
    _output_filename = f"{_hash}-output.json"
    return {
        "output_file":
        _output_filename,
        "gemma_cmd":
        compose_gemma_cmd(gemma_wrapper_cmd=gemma_cmd,
                          gemma_wrapper_kwargs=gemma_wrapper_kwargs,
                          gemma_kwargs=gemma_kwargs,
                          gemma_args=[
                              "-gk", ">",
                              (f"{output_dir}/"
                               f"{token}/{_output_filename}")
                          ])
    }
