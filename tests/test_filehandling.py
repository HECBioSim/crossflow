from crossflow import filehandling
import os.path as op


def test_data_protocol(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    q = d.join("hello2.txt")
    pf.save(q)
    assert q.read() == p.read()
    assert pf.read_text() == "content"
    r = d.join("hello3.txt")
    rf = fh.create(r)
    assert not op.exists(r)
    rf.write_text("content")
    assert rf.read_text() == "content"


def test_config(tmpdir):
    filehandling.set_stage_point(tmpdir)
    fh = filehandling.FileHandler()
    assert fh.stage_point == tmpdir


def test_cleanup(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    tmppath = str(pf)
    assert op.exists(tmppath)
    del pf
    assert not op.exists(tmppath)


def test_file_protocol(tmpdir):
    d = tmpdir.mkdir("sub")
    p = d.join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler(tmpdir)
    pf = fh.load(p)
    q = d.join("hello2.txt")
    pf.save(q)
    assert q.read() == p.read()
    assert pf.read_text() == "content"


"""
def test_s3_protocol(tmpdir):
    d = tmpdir.mkdir('sub')
    p = d.join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler('s3://bucker_name')
    l = fh.load(p)
    q = d.join("hello2.txt")
    ql = l.save(q)
    assert q.read() == p.read()
    assert l.read_text() == 'content'
"""
