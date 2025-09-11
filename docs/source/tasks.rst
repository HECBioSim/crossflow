Crossflow Tasks
---------------

The ``crossflow.tasks`` subpackage provides methods to turn tools that
would usually be used via the command line into Python functions. The
basic concept is that a tool that is used from the commmand line
something like:

::

   #!bash

   my_tool -i input.dat -o output.dat

becomes, in Python:

::

   output = my_tool_task(input)

``Where my_tool_task`` is a ``crossflow.SubprocessTask`` for
``my_tool``, and ``input`` and ``output`` are ‘path-like’ Python objects
that in some way or other point at a file of data. This might be as
simple as strings, e.g. “myproject/input.dat”, but can be more complex -
see crossflow FileHandles later.

Creating a crossflow.SubprocessTask
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This is a three step process:

1. The task is created on the basis of a ``template``, a string with a
   generalised version of the command you wish to execute.
2. The inputs for the task are specified.
3. The outputs from the task are specified.

Thus:

::

   #!python

   my_tool_task = crossflow.tasks.SubprocessTask('my_tool -i x.in -o x.out')
   my_tool_task.set_inputs(['x.in'])
   my_tool_task.set_outputs(['x.out'])

Note that the names of files used in the template string are arbitrary,
‘my_tool -i a -o b’ would do just as well, as long as the corresponding
names (‘a’, ‘b’) were used in .set_inputs() and .set_outputs().

If the tool takes multiple files as inputs, and/or produces multiple
output files, the process is the same:

::

   #!python

   my_othertool_task = crossflow.tasks.SubprocessTask('my_othertool -x x.in -y y.in -o x.out -l logfile')
   my_othertool_task.set_inputs(['x.in', 'y.in'])
   my_othertool_task.set_outputs(['x.out', 'logfile'])

There is no restriction on the order that inputs and outputs are
specified in the template string, but the resulting task will expect its
inputs to be provided in the order they are given in .set_inputs() and
the tuple of outputs the task produces will be in the order they are
specified in .set_outputs().

For more advanced aspects of ``SubprocessTask`` creation, see :doc:`here <tasks_advanced>`.

Running a crossflow.SubprocessTask
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Although it is primarily expected that tasks will be run via a
``crossflow.Client``, they can also be executed directly:

::

   #!python

   output, logfile = my_othertool('input1.dat', 'input2.dat')
