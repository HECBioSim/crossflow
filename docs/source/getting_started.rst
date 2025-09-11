Getting Started
===============

Requirements
----------------

* Python >= 3.11

Installation
----------------
To install the released version:

.. code-block:: bash

    pip install crossflow

To install the latest development version:

.. code-block:: bash

    git clone https://github.com/CharlieLaughton/crossflow.git

.. code-block:: bash

    cd crossflow

.. code-block:: bash

    pip install .

Crossflow 101
----------------

An introduction to the fundamentals of Crossflow

Workflows are a common feature of much computational science. In a
workflow, the work to be done requires more than one piece of software,
and the output from one becomes the input to the next, in some form of
chain. Classically one would write a bash script or similar to do the
job, e.g.:

::

   #!/usr/bin/env bash
   input_file=input.dat
   intermediate_file=intermediate.dat
   result_file=result.dat

   executable1 -i $input_file -o $intermediate_file
   executable2 -i $intermediate_file -o $result_file

This is OK for basic use but:

-  what if your workflow has loops, conditional executions, etc?
-  what happens if you want to do things at scale?

Crossflow is designed to make this easier. Key points are:

1. The workflow becomes a Python program, and can make use of all
   programming workflow constructs (loops, if/then/else, etc.)
2. To do this, it provides a simple approach to turning command line
   tools into Python functions - this is ``crossflow.tasks``.
3. It provides a way to hand the processing of individual workflow steps
   out to a distributed cluster of workers - this is
   ``crossflow.clients``.
4. It provides a way to pass data between these functions without
   relying on the filesystem - this is ``crossflow.filehandling``.

Here we look at each of these components in turn.
