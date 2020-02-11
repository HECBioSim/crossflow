# Crossflow:
#
# A simple workflow, illustrating, scatter, parallel execution, and gather
# processes.
#
# A large text file is split into a number of separate ones, each of these
# has its lines reversed (last to first), and then the chunks are recombined.
#
from crossflow import clients, kernels, filehandling
from pathlib import Path

def run(client):
    # Create the initial text file:
    here = Path('.')
    input_file = here /'input.txt'
    with input_file.open('w') as f:
        for i in range(50):
            f.write('line {}\n'.format(i))
    # Create a SubprocessKernel that will split up the input file:
    splitter = kernels.SubprocessKernel('split -l 10 input.txt')
    splitter.set_inputs(['input.txt'])
    splitter.set_outputs(['xaa', 'xab', 'xac', 'xad', 'xae'])
    # Create a SubprocessKernel to reverse the order of the lines in a file:
    reverser = kernels.SubprocessKernel('tail -r input > output')
    reverser.set_inputs(['input'])
    reverser.set_outputs(['output'])
    # Create a Subprocesskernel that will join input files together:
    joiner = kernels.SubprocessKernel('cat * > output')
    joiner.set_inputs(['*'])
    joiner.set_outputs(['output'])
    # Convert the input datafiles into Crossflow FileHandle objects:
    fh = filehandling.FileHandler()
    input_data = fh.load(input_file)
    # Here is the workflow, using .submit() and .map() methods.
    # First split the file into pieces:
    pieces = client.submit(splitter, input_data)
    # 'pieces' is a tuple, convert to a list and process each
    # piece in parallel:
    reversed_pieces = client.map(reverser, list(pieces))
    # Stitch the reversed pieces back together again:
    output = client.submit(joiner, reversed_pieces)
    # The client returns outputs as Futures, so call their result()
    # method to get the actual data:
    output_filehandle = output.result()
    # Save the output FileHandle object as a file, and list its contents:
    output_file = here / 'processed.txt'
    output_filehandle.save(output_file)
    return output_file

if __name__ == '__main__':
    # Create a local compute cluster and the client to serve it:
    client = clients.Client(local=True)
    output_file = run(client)
    print(output_file.read_text())
    # Close the client and compute cluster:
    client.close()
