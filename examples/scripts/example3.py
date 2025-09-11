# Crossflow:
#
# A simple workflow, illustrating, scatter, parallel execution, and gather
# processes.
#
# A large text file is split into a number of separate ones, each of these
# has its lines reversed (last to first), and then the chunks are recombined.
#
from pathlib import Path

from crossflow import clients, tasks


def run(client):
    # Create the initial text file:
    here = Path(".")
    input_file = here / "input.txt"
    with input_file.open("w") as f:
        for i in range(50):
            f.write("line {}\n".format(i))

    # Create a SubprocessTask that will split up the input file:
    splitter = tasks.SubprocessTask("split -l 10 input.txt")
    splitter.set_inputs(["input.txt"])
    splitter.set_outputs(["xaa", "xab", "xac", "xad", "xae"])

    # Create a SubprocessTask to reverse the order of the lines in a file:
    reverser = tasks.SubprocessTask("tail -r input > output")
    reverser.set_inputs(["input"])
    reverser.set_outputs(["output"])

    # Create a Subprocesstask that will join input files together:
    joiner = tasks.SubprocessTask("cat * > output")
    joiner.set_inputs(["*"])
    joiner.set_outputs(["output"])

    # Here is the workflow, using .submit() and .map() methods.
    # First split the file into pieces:
    pieces = client.submit(splitter, input_file)

    # 'pieces' is a tuple, convert to a list and process each
    # piece in parallel:
    reversed_pieces = client.map(reverser, list(pieces))

    # Stitch the reversed pieces back together again:
    output = client.submit(joiner, reversed_pieces)

    # The client returns outputs as Futures, so call their result()
    # method to get the actual data:
    output_filehandle = output.result()

    # Save the output FileHandle object as a file, and list its contents:
    output_file = here / "processed.txt"
    output_filehandle.save(output_file)
    return output_file


if __name__ == "__main__":
    # Create a local compute cluster and the client to serve it:
    client = clients.Client()
    output_file = run(client)
    print(output_file.read_text())

    # Close the client and compute cluster:
    client.close()
