Crossflow FileHandles
---------------------

Command line tools typically take file *names* as arguments:

.. code:: bash


   executable -i input.dat -o output.dat

This has issues if you want to do the computing on a distributed system
where there is no shared filesystem. Crossflow ``FileHandles`` wrap data
files as serialisable Python objects that can be safely passed around a
network. Crossflow ``Tasks`` and ``Clients`` natively understand these
as the equivalents of the filenames one would use for the equivalent
command line call.

In normal use, FileHandles are created automatically by ``Tasks`` and/or
``Clients`` as required, the user just has to extract the required data
from FileHandles returned by Tasks/Clients.

So for example, in:

.. code:: python

   output_future = client.submit(my_task, 'input.dat')
   output = output_future.result()

``input.dat`` - the name of a local file - is converted by the client
into a ``FileHandle`` before being sent for processing, and ``output``
is a ``FileHandle`` which the user will (probably) want to convert back
to a conventional file, using one of the methods a ``FileHandle``
provides.

Methods of crossflow.FileHandles
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The .save() method of a ``crossflow.FileHandle`` creates a conventional
local file with the object’s contents:

.. code:: python


   output.save('output.txt')

In addition, ``crossflow.FileHandles`` follow a limited subset of the
``pathlib.Path`` API. The file handles themselves are ‘path-like’ and
can be used in place of paths in many circumstances, e.g.:

.. code:: python

   with open(output) as f:
       data = f.read()

If your 3rd-party Python library is more picky (e.g. expects paths to be
strings), then you can use the idiom:

.. code:: python

   result = my_fussy_function(str(output))

In a ``Path``-like manner, ``FileHandles`` have ``.read_binary()`` and
``.read_text()`` methods, e.g.:

.. code:: python


   print(output.read_text()) # prints the contents of output to the screen

For more details on FileHandles, see :doc:`here <filehandles_advanced>`
