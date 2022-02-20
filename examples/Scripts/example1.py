# Crossflow:
#
# Basic example of how to create tasks, load input data, and
# run locally (without using a client)
#
from crossflow import tasks
from pathlib import Path
# Create two short text files:
here = Path('.')
file1 = here /'file1.txt'
file1.write_text('content\n')
file2 = here / 'file2.txt'
file2.write_text('more content\n')
# Create a Subprocesstask that will join input files together:
joiner = tasks.SubprocessTask('cat * > output')
joiner.set_inputs(['*'])
joiner.set_outputs(['output'])
# The task expects an arbitrary number of input files, so put the inputs
# into a list, and then call the task's .run() method:
inputs = [file1, file2]
joined = joiner.run(inputs) 
# Save the output FileHandle object as a file, and list its contents:
output = here / 'joined.txt'
joined.save(output)
print(output.read_text())

