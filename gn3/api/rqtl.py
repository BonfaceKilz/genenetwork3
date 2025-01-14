"""Endpoints for running the rqtl cmd"""

import os
import uuid
import subprocess
from pathlib import Path

from flask import Blueprint
from flask import current_app
from flask import jsonify
from flask import request

from gn3.computations.rqtl import (
    generate_rqtl_cmd,
    process_rqtl_mapping,
    process_rqtl_pairscan,
    process_perm_output,
)
from gn3.fs_helpers import assert_path_exists, get_tmpdir

rqtl = Blueprint("rqtl", __name__)


@rqtl.route("/compute", methods=["POST"])
def compute():
    """Given at least a geno_file and pheno_file, generate and
    run the rqtl_wrapper script and return the results as JSON

    """
    genofile = request.form["geno_file"]
    phenofile = request.form["pheno_file"]
    assert_path_exists(genofile)
    assert_path_exists(phenofile)

    run_id = request.args.get("id")
    with open(
        os.path.join(current_app.config.get("TMPDIR"), f"{run_id}.txt"),
        "w+",
        encoding="utf-8",
    ):
        # TODO thos should  be refactored
        pass
    # Split kwargs by those with values and boolean ones
    # that just convert to True/False
    kwargs = ["covarstruct", "model", "method", "nperm", "scale", "control"]
    boolean_kwargs = ["addcovar", "interval", "pstrata", "pairscan"]
    all_kwargs = kwargs + boolean_kwargs

    rqtl_kwargs = {
        "geno": genofile,
        "pheno": phenofile,
        "outdir": current_app.config.get("TMPDIR"),
    }
    rqtl_bool_kwargs = []

    for kwarg in all_kwargs:
        if kwarg in request.form:
            if kwarg in kwargs:
                rqtl_kwargs[kwarg] = request.form[kwarg]
            if kwarg in boolean_kwargs:
                rqtl_bool_kwargs.append(kwarg)

    outdir = os.path.join(get_tmpdir(), "gn3")
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    rqtl_cmd = generate_rqtl_cmd(
        rqtl_wrapper_cmd=str(
            Path(__file__)
            .absolute()
            .parent.parent.parent.joinpath("scripts/rqtl_wrapper.R")
        ),
        rqtl_wrapper_kwargs=rqtl_kwargs,
        rqtl_wrapper_bool_kwargs=rqtl_bool_kwargs,
    )

    rqtl_output = {}
    #  get the stdout file
    run_id = request.args.get("id", str(uuid.uuid4()))
    if not os.path.isfile(
        os.path.join(
            current_app.config.get("TMPDIR"), "gn3", rqtl_cmd.get("output_file")
        )
    ):
        pass
    stream_ouput_file = os.path.join(current_app.config.get("TMPDIR"), f"{run_id}.txt")

    with open("/tmp/cmd.txt", "w") as cmd:
        cmd.write(rqtl_cmd.get("rqtl_cmd"))
    run_process(rqtl_cmd.get("rqtl_cmd").split(), stream_ouput_file, run_id)

    if "pairscan" in rqtl_bool_kwargs:
        rqtl_output["results"] = process_rqtl_pairscan(
            rqtl_cmd.get("output_file"), genofile
        )
    else:
        rqtl_output["results"] = process_rqtl_mapping(rqtl_cmd.get("output_file"))

    if int(rqtl_kwargs["nperm"]) > 0:
        # pylint: disable=C0301
        (
            rqtl_output["perm_results"],
            rqtl_output["suggestive"],
            rqtl_output["significant"],
        ) = process_perm_output(rqtl_cmd.get("output_file"))
    return jsonify(rqtl_output)


def run_process(cmd, output_file, run_id):
    """Function to execute an external process and
       capture the stdout in a file
      input:
           cmd: the command to execute as a list of args.
           output_file: abs file path to write the stdout.
           run_id: unique id to identify the process

      output:
          Dict with the results o either success or failure.
    """
    try:
        # phase: execute the  rscript cmd
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        ) as process:
            for line in iter(process.stdout.readline, b""):
                # phase: capture the stdout for eaching line allowing read and write
                with open(output_file, "a+", encoding="utf-8") as file_handler:
                    file_handler.write(line.decode("utf-8"))
            process.wait()
        if process.returncode == 0:
            return {"msg": "success", "code": 0, "run_id": run_id}
        return {"msg": "error occurred", "error": "Process failed",
                "code": process.returncode, "run_id": run_id}
    except subprocess.CalledProcessError as error:
        return {"msg": "error occurred",
                "error": str(error), "run_id": run_id}
