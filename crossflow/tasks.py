"""
Crossflow tasks: wrappers round subprocess calls and python functions for
execution on a crossflow cluster
"""
import re
import subprocess
import os
import os.path as op
import tempfile
import shutil
import copy
import glob
from math import log10
from .filehandling import FileHandler
from . import config

STDOUT = "STDOUT"
DEBUGINFO = "DEBUGINFO"


def _gen_filenames(pattern, n_files):
    """
    Generate a list of filenames consistent with a pattern.
    """
    if "?" not in pattern and "*" not in pattern:
        raise ValueError("Error - the pattern must contain * or ?")
    fieldwidth = int(log10(n_files)) + 1
    if "*" in pattern:
        w = pattern.split("*")
        template = "{}{{:0{}d}}{}".format(w[0], fieldwidth, w[1])
    else:
        w = pattern.split("?")
        if pattern.count("?") < fieldwidth:
            raise ValueError("Error - too many files for this pattern")
        template = "{}{{:0{}d}}{}".format(w[0], pattern.count("?"), w[-1])
    filenames = [template.format(i) for i in range(n_files)]
    return filenames


class SubprocessTask(object):
    """
    A task that runs a command-line executable
    """

    def __init__(self, template):
        """
        Arguments:
            template (str): a template for the command to be executed
        """
        self.template = template
        self.inputs = []
        self.outputs = []
        self.constants = []
        self.STDOUT = None
        self.filehandler = FileHandler(config.stage_point)

        self.variables = []
        for key in re.findall(r"{.*?}", self.template):
            self.variables.append(key[1:-1])

    def __call__(self, *args):
        return self.run(*args)

    def set_inputs(self, inputs):
        """
        Set the inputs the task requires
        """
        if not isinstance(inputs, list):
            raise TypeError(
                "Error - inputs must be of type list,"
                " not of type {}".format(type(inputs))
            )
        self.inputs = inputs

    def set_outputs(self, outputs):
        """
        Set the outputs the task produces
        """
        if not isinstance(outputs, list):
            raise TypeError(
                "Error - outputs must be of type list,"
                " not of type {}".format(type(outputs))
            )
        self.outputs = outputs

    def set_constant(self, key, value):
        """
        Set a constant for the task
        If it was previously defined as an input variable, remove it from
        that list.
        """
        d = {"name": key}
        try:
            d["value"] = self.filehandler.load(value)
        except IOError:
            d["value"] = value
        self.constants.append(d)

        if key in self.inputs:
            self.inputs.remove(key)

    def copy(self):
        """
        Return a copy of the task
        """
        return copy.deepcopy(self)

    def run(self, *args):
        """
        Run the task with the given inputs.
        Args:
            args: positional arguments whose order should match self.inputs

        Returns:
            tuple : outputs in the order they appear in
                self.outputs
        """
        outputs = []
        td = tempfile.mkdtemp()
        var_dict = {}
        for i in range(len(args)):
            if self.inputs[i] in self.variables:
                var_dict[self.inputs[i]] = args[i]
            else:
                if isinstance(args[i], list):
                    fnames = _gen_filenames(self.inputs[i], len(args[i]))
                    for j, f in enumerate(args[i]):
                        if not hasattr(f, "save"):
                            f = self.filehandler.load(f)
                        f.save(op.join(td, fnames[j]))
                else:
                    f = args[i]
                    if not hasattr(f, "save"):
                        f = self.filehandler.load(f)
                    f.save(op.join(td, self.inputs[i]))
        for d in self.constants:
            if hasattr(d["value"], "result"):
                dtmp = d["value"].result()
                if hasattr(dtmp, "save"):
                    dtmp.save(op.join(td, d["name"]))
                else:
                    var_dict[d["name"]] = dtmp
            else:
                try:
                    d["value"].save(op.join(td, d["name"]))
                except AttributeError:
                    var_dict[d["name"]] = d["value"]
        cmd = self.template.format(**var_dict)
        try:
            result = subprocess.run(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=td,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            result = CalledProcessError(e)
            if DEBUGINFO not in self.outputs:
                raise result

        self.STDOUT = result.stdout.decode()
        for outfile in self.outputs:
            if outfile not in [STDOUT, DEBUGINFO]:
                outfile = op.join(td, outfile)
            if "*" in outfile or "?" in outfile:
                outf = glob.glob(outfile)
                outf.sort()
                outputs.append([self.filehandler.load(f) for f in outf])
            else:
                if op.exists(outfile):
                    outputs.append(self.filehandler.load(outfile))
                elif outfile == STDOUT:
                    outputs.append(self.STDOUT)
                elif outfile == DEBUGINFO:
                    outputs.append(result)
                else:
                    outputs.append(None)
        shutil.rmtree(td, ignore_errors=True)

        if len(outputs) == 1:
            outputs = outputs[0]
        else:
            outputs = tuple(outputs)
        return outputs


class FunctionTask(object):
    def __init__(self, func):
        """
        Arguments:
            func: the Python function to wrap
        """
        self.func = func
        self.inputs = []
        self.outputs = []
        self.constants = {}
        self.tmpdir = None
        self.filehandler = FileHandler(config.stage_point)

    def __call__(self, *args):
        return self.run(*args)

    def set_inputs(self, inputs):
        """
        Set the inputs the task requires
        """
        self.inputs = inputs

    def set_outputs(self, outputs):
        """
        Set the outputs the task produces
        """
        self.outputs = outputs

    def set_constant(self, key, value):
        """
        Set a parameters for the task
        """
        try:
            self.constants[key] = self.filehandler.load(value)
        except IOError:
            self.constants[key] = value

    def copy(self):
        """
        Return a copy of the task
        """
        return copy.copy(self)

    def run(self, *args):
        """
        Run the task/function with the given arguments.

        Returns:
            Whatever the function returns, with output files converted
                to FileHandle objects
        """
        td = tempfile.mkdtemp()
        os.chdir(td)
        indict = {}
        for i, v in enumerate(args):
            if isinstance(v, dict):
                for k in v:
                    if k in self.inputs:
                        f = v[k]
                        try:
                            f = self.filehandler.load(f)
                        except IOError:
                            pass
                        try:
                            indict[k] = f.save(os.path.basename(v[k].path))
                        except AttributeError:
                            indict[k] = f
            else:
                try:
                    v = self.filehandler.load(v)
                except IOError:
                    pass
                try:
                    indict[self.inputs[i]] = v.save(os.path.basename(v.path))
                except AttributeError:
                    indict[self.inputs[i]] = v
        for k in self.constants:
            try:
                indict[k] = self.constants[k].save(
                    os.path.basename(self.constants[k].path)
                )
            except AttributeError:
                indict[k] = self.constants[k]
        result = self.func(**indict)
        if not isinstance(result, list):
            result = [result]
        outputs = []
        for i, v in enumerate(result):
            if isinstance(v, str):
                if os.path.exists(v):
                    outputs.append(self.filehandler.load(v))
                else:
                    outputs.append(v)
            else:
                outputs.append(v)
            shutil.rmtree(td, ignore_errors=True)

        if len(outputs) == 1:
            outputs = outputs[0]
        else:
            outputs = tuple(outputs)
        return outputs


class XflowError(Exception):
    """
    Base class for Crossflow exceptions.
    """

    pass


class CalledProcessError(XflowError):
    """
    Exception raised if a task fails with an error.

    A cosmetic wrapper round subprocess.CalledProcessError
    """

    def __init__(self, e):
        self.cmd = e.cmd
        self.returncode = e.returncode
        self.stdout = e.stdout
        self.stderr = e.stderr
        self.output = self.stdout

    def __str__(self):
        message = f'Error: command "{self.cmd}"'
        message += f" failed with return code {self.returncode};"
        message += f' STDOUT="{self.stdout}"; STDERR="{self.stderr}"'
        return message
