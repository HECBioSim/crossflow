#!/usr/bin/env python
from pathlib import Path

import pytest

from crossflow import clients, filehandling, tasks


@pytest.fixture(scope="session")
def myclient(request):
    newclient = clients.Client()

    def delete_client():
        newclient.close()

    request.addfinalizer(delete_client)
    return newclient


def test_function_test(myclient, tmpdir):
    def testit(f):
        return f

    fk = tasks.FunctionTask(testit)
    fk.set_inputs(["f"])
    fk.set_outputs(["x"])
    p = tmpdir / "hello.txt"
    p.write_text("content", encoding="utf-8")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    result = myclient.submit(fk, pf)
    try:
        assert isinstance(result.result(), filehandling.FileHandle)
    except AssertionError:
        print("Error: result.result() = {}".format(result.result()))
        raise


def test_function_test_no_filehandler(myclient, tmpdir):
    def testit(f):
        return f

    fk = tasks.FunctionTask(testit)
    fk.set_inputs(["f"])
    fk.set_outputs(["x"])
    p = tmpdir / "hello.txt"
    p.write_text("content", encoding="utf-8")
    result = myclient.submit(fk, p)
    try:
        assert isinstance(result.result(), filehandling.FileHandle)
    except AssertionError:
        print("Error: result.result() = {}".format(result.result()))
        raise


def test_subprocess_test_data(myclient, tmpdir):
    sk = tasks.SubprocessTask("cat file.txt")
    sk.set_inputs(["file.txt"])
    sk.set_outputs([tasks.STDOUT])
    p = tmpdir / "hello.txt"
    p.write_text("content", encoding="utf-8")
    fh = filehandling.FileHandler()
    pf = fh.load(p)
    ll = myclient.upload(pf)
    result = myclient.submit(sk, ll)
    try:
        assert result.result() == "content"
    except AssertionError:
        print("Error: result.result() = {}".format(result.result()))


def test_subprocess_test_no_filehandler(myclient, tmpdir):
    sk = tasks.SubprocessTask("cat file.txt")
    sk.set_inputs(["file.txt"])
    sk.set_outputs([tasks.STDOUT])
    p = tmpdir / "hello.txt"
    p.write_text("content", encoding="utf-8")
    result = myclient.submit(sk, p)
    try:
        assert result.result() == "content"
    except AssertionError:
        print("Error: result.result() = {}".format(result.result()))


def test_subprocess_test_file(myclient, tmpdir):
    sk = tasks.SubprocessTask("cat file.txt")
    sk.set_inputs(["file.txt"])
    sk.set_outputs([tasks.STDOUT])
    p = tmpdir / "hello.txt"
    p.write_text("content", encoding="utf-8")
    fh = filehandling.FileHandler(tmpdir)
    pf = fh.load(p)
    ll = myclient.upload(pf)
    result = myclient.submit(sk, ll)
    try:
        assert result.result() == "content"
    except AssertionError:
        print("Error: result.result() = {}".format(result.result()))


# def test_subprocess_test_s3(myclient, tmpdir):
#    sk = tasks.SubprocessTask('cat file.txt')
#    sk.set_inputs(['file.txt'])
#    sk.set_outputs([tasks.STDOUT])
#    p = tmpdir / "hello.txt"
#    p.write_text("content", encoding="utf-8")
#    fh = filehandling.FileHandler('s3://bucket_name')
#    fp = fh.load(p)
#    ll = myclient.upload(fp)
#    result = myclient.submit(sk, ll)
#    try:
#        assert result.result() == 'content'
#    except AssertionError:
#        print('Error: result.result() = {}'.format(result.result()))
