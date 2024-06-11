from crossflow import filehandling, tasks
import pytest


def test_subprocess_task_no_filehandles(tmpdir):
    sk = tasks.SubprocessTask("cat file.txt")
    sk.set_inputs(["file.txt"])
    sk.set_outputs([tasks.STDOUT])
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    result = sk(p)
    assert result == "content"


def test_subprocess_task_stdout(tmpdir):
    sk = tasks.SubprocessTask("cat file.txt")
    sk.set_inputs(["file.txt"])
    sk.set_outputs([tasks.STDOUT])
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    result = sk(pf)
    assert result == "content"

def test_subprocess_task_constant_filehandle(tmpdir):
    sk = tasks.SubprocessTask("cat file.txt")
    sk.set_inputs(["file.txt"])
    sk.set_outputs([tasks.STDOUT])
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    sk.set_constant('file.txt', pf)
    result = sk()
    assert result == "content"


def test_subprocess_task_fileout(tmpdir):
    sk = tasks.SubprocessTask("cat file.txt > out.dat")
    sk.set_inputs(["file.txt"])
    sk.set_outputs(["out.dat"])
    p = tmpdir.mkdir("sub").join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    result = sk(pf)
    assert isinstance(result, filehandling.FileHandle)


def test_subprocess_task_globinputs_2(tmpdir):
    sk = tasks.SubprocessTask("cat file?.txt > out.dat")
    sk.set_inputs(["file?.txt"])
    sk.set_outputs(["out.dat"])
    d = tmpdir.mkdir("sub")
    p = d.join("file1.txt")
    q = d.join("file2.txt")
    p.write("content\n")
    q.write("more content\n")
    fh = filehandling.FileHandler()
    pf = [fh.load(x) for x in [p, q]]
    result = sk(pf)
    r = d.join("output.dat")
    result.save(r)
    assert r.read() == "content\nmore content\n"

def test_subprocess_task_globinputs_1(tmpdir):
    sk = tasks.SubprocessTask("cat *.txt > out.dat")
    sk.set_inputs(["*.txt"])
    sk.set_outputs(["out.dat"])
    d = tmpdir.mkdir("sub")
    p = d.join("file1.txt")
    q = d.join("file2.txt")
    p.write("content\n")
    q.write("more content\n")
    fh = filehandling.FileHandler()
    pf = [fh.load(x) for x in [p, q]]
    result = sk(pf)
    r = d.join("output.dat")
    result.save(r)
    assert r.read() == "content\nmore content\n"


def test_subprocess_task_globoutputs(tmpdir):
    sk = tasks.SubprocessTask("split -l 1 input.txt")
    sk.set_inputs(["input.txt"])
    sk.set_outputs(["x*"])
    d = tmpdir.mkdir("sub")
    p = d.join("lines.txt")
    p.write("line 1\nline 2\nline 3\n")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    result = sk(pf)
    assert len(result) == 3


def test_subprocess_task_fails():
    with pytest.raises(tasks.XflowError):
        sk = tasks.SubprocessTask("foo -bar")
        sk.set_outputs([tasks.STDOUT])
        sk()


def test_subprocess_task_catch_fail():
    sk = tasks.SubprocessTask("foo -bar")
    sk.set_outputs([tasks.DEBUGINFO])
    result = sk()
    assert isinstance(result, tasks.XflowError)

def test_subprocesstask_with_constant():
    sk = tasks.SubprocessTask("head -{n} file.txt > out.dat")
    sk.set_inputs(["n", "file.txt"])
    sk.set_outputs(["out.dat"])
    sk.set_constant('n', 1)
    fh = filehandling.FileHandler()
    pf = fh.create("tmp.txt")
    pf.write_text('line 1\nline 2\nline 3')
    result = sk(pf)
    assert result.read_text() == 'line 1\n'
    
def test_function_task_basic():
    def mult(a, b):
        return a * b

    fk = tasks.FunctionTask(mult)
    fk.set_inputs(["a", "b"])
    fk.set_outputs(["ab"])
    result = fk.run(3, 4)
    assert result == 12


def test_function_task_with_filehandles(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("lines.txt")
    p.write("line 1\nline 2\nline 3\n")
    fh = filehandling.FileHandler()
    pf = fh.load(p)

    def linecount(a):
        with open(a) as f:
            lines = f.readlines()
        return len(lines)

    fk = tasks.FunctionTask(linecount)
    fk.set_inputs(["a"])
    fk.set_outputs(["nlines"])
    result = fk.run(pf)
    assert result == 3

def test_function_task_with_output_filehandles(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("lines.txt")
    p.write("line 1\nline 2\nline 3\n")
    fh = filehandling.FileHandler()
    pf = fh.load(p)

    def duplicate(a):
        with open(a) as f:
            data = f.read()
        with open('out.dat', 'w') as f:
            f.write(data)
        return 'out.dat'

    fk = tasks.FunctionTask(duplicate)
    fk.set_inputs(["a"])
    fk.set_outputs(["out.dat"])
    result = fk.run(pf)
    assert isinstance(result, filehandling.FileHandle)

def test_function_task_with_constant_filehandles(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("lines.txt")
    p.write("line 1\nline 2\nline 3\n")
    fh = filehandling.FileHandler()
    pf = fh.load(p)

    def linecount(a):
        with open(a) as f:
            lines = f.readlines()
        return len(lines)

    fk = tasks.FunctionTask(linecount)
    fk.set_inputs(["a"])
    fk.set_outputs(["nlines"])
    fk.set_constant('a', pf)
    result = fk.run()
    assert result == 3


def test_function_task_with_filehandles_dict(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("lines.txt")
    p.write("line 1\nline 2\nline 3\n")
    fh = filehandling.FileHandler()
    pf = fh.load(p)

    def linecount(a):
        with open(a) as f:
            lines = f.readlines()
        return len(lines)

    fk = tasks.FunctionTask(linecount)
    fk.set_inputs(["a"])
    fk.set_outputs(["nlines"])
    result = fk.run({'a':pf})
    assert result == 3


def test_function_task_no_filehandles(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("lines.txt")
    p.write("line 1\nline 2\nline 3\n")

    def linecount(a):
        with open(a) as f:
            lines = f.readlines()
        return len(lines)

    fk = tasks.FunctionTask(linecount)
    fk.set_inputs(["a"])
    fk.set_outputs(["nlines"])
    result = fk.run(p)
    assert result == 3
