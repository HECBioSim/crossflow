from crossflow import filehandling
import tempfile
import os.path as op
import os
import pytest

def test_data_protocol(tmpdir):
    d = tmpdir.mkdir('sub')
    p = d.join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler()
    l = fh.load(p)
    q = d.join("hello2.txt")
    ql = l.save(q)
    assert q.read() == p.read()

def test_file_protocol(tmpdir):
    d = tmpdir.mkdir('sub')
    p = d.join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler(tmpdir)
    l = fh.load(p)
    q = d.join("hello2.txt")
    ql = l.save(q)
    assert q.read() == p.read()

def test_s3_protocol(tmpdir):
    d = tmpdir.mkdir('sub')
    p = d.join("hello.txt")
    p.write("content")
    fh = filehandling.FileHandler('s3://laughtongroup.charlie.bucket0/crossflow')
    l = fh.load(p)
    q = d.join("hello2.txt")
    ql = l.save(q)
    assert q.read() == p.read()

