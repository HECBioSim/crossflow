# Crossflow:
#
# Basic example of how to create tasks, load input data, and
# run via a client
# Note that because we are creating a local cluster on the fly, and
# the associated client, this part of the process must be done in
# __main__
#
from crossflow import clients, tasks
from pathlib import Path


def run(client):
    # Create two short text files:
    here = Path('.')
    input_file1 = here / 'file1.txt'
    input_file1.write_text('content\n')
    input_file2 = here / 'file2.txt'
    input_file2.write_text('more content\n')

    # Create a Subprocesstask that will join input files together:
    joiner = tasks.SubprocessTask('cat * > output')
    joiner.set_inputs(['*'])
    joiner.set_outputs(['output'])

    # The task expects an arbitrary number of input files, so put the inputs
    # into a list:
    inputs = [input_file1, input_file2]

    # Send the job to the client via the submit() method:
    output = client.submit(joiner, inputs)

    # The client returns outputs as Futures, so call their result() method
    # to get the actual data:
    output_filehandle = output.result()

    # Save the output FileHandle object as a file, and list its contents:
    output_file = here / 'joined.txt'
    output_filehandle.save(output_file)
    return output_file


if __name__ == '__main__':
    # Create a local compute cluster and the client to serve it:
    client = clients.Client()
    output_file = run(client)
    print(output_file.read_text())
    # Close the client and compute cluster:
    client.close()
