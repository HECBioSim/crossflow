import os
import subprocess


def test_client():
    SCRIPTLOC = os.path.dirname(os.path.dirname(__file__))
    RUNSCRIPT = os.path.join(SCRIPTLOC, "run_client_tests")

    subprocess.run(RUNSCRIPT, check=True)
