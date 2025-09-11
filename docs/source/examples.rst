Putting it all together: a simple example
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Here we create a ``SubprocessTask`` to reverse the order of the lines in
a file, submit the job to a local ``Client``, and then retrieve and view
the result.

.. code:: python

   from crossflow import clients, tasks, filehandling
   from pathlib import Path

   # Create a short text file:
   here = Path('.')
   inp_file = here /'input.txt'
   with inp_file.open('w') as f:
       for i in range(10):
           f.write('line {}\n'.format(i))

   # Create a SubprocessTask that will reverse the lines in a file:
   reverser = tasks.SubprocessTask('tail -r input > output')
   reverser.set_inputs(['input'])
   reverser.set_outputs(['output'])

   # Create a local client to run the job, and submit it:
   client = clients.Client()
   output = client.submit(reverser, inp_file)

   # output is a Future; collect its result(), convert this FileHandle object to a file, and list its contents:
   output_file = here / 'joined.txt'
   output.result().save(output_file)
   print(output_file.read_text()) # or: print(output.result().read_text())

::

   line 9
   line 8
   line 7
   line 6
   line 5
   line 4
   line 3
   line 2
   line 1
   line 0

