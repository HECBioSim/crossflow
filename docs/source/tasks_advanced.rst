Advanced Tasks
===============

Here we go into ``Crossflow.Tasks`` in more detail, see
:doc:`here <tasks>` for the basics.

SubprocessTasks: More on templates
----------------------------------

“Cryptic” input and output files
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``SubprocessTasks`` are instantiated with a template, a generic version
of the command line that should be executed, e.g.:

.. code:: python

   my_task = SubprocessTask('my_executable -i input.dat -o output.dat')
   my_task.set_inputs(['input.dat'])
   my_task.set_outputs(['output.dat'])

Sometimes a command line tool produces an output file whose name is
hard-wired and so does not appear in the template. As long as you know
what the name will be, this does not matter. E.g., suppose
``my_executable`` also always produces a file called ``logfile``:

::

   my_task = SubprocessTask('my_executable -i input.dat -o output.dat')
   my_task.set_inputs(['input.dat'])
   my_task.set_outputs(['output.dat', 'logfile'])

The same applies to input files, e.g. if your executable also expects a
file called ‘config.dat’ to be present, you might write:

::

   my_task = SubprocessTask('my_executable -i input.dat -o output.dat')
   my_task.set_inputs(['input.dat', 'config.dat'])
   my_task.set_outputs(['output.dat', 'logfile'])

Input variables that are not filenames
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

By default, all variables are assumed to be the names of input or output
files, but you can specify string variables (or variables that can be
represented as strings) by surrounding them by braces (“{}”) in the
template. E.g.:

::

   tail_task = SubprocessTask('tail -n {n_lines} input.dat > output.dat')
   tail_task.set_inputs(['input.dat', 'n_lines'])
   tail_task.set_outputs(['output.dat'])

   last15 = tail_task('data.txt', 15)

Wildcards
~~~~~~~~~

The template string can contain wildcards ("*" or “?”), the
corresponding variable (input or output) then becomes a list of values.
E.g.:

::

   cat_task = SubprocessTask('cat file* > output.dat')
   cat_task.set_inputs(['file*'])
   cat_task.set_outputs(['output.dat'])
   inputs = ['data1', 'data2', 'data3', 'data4']

   output = cat_task(inputs)

SubprocessTasks: Constants
--------------------------

If some of the inputs to your ``SubprocessTask`` are going to be
constants over many calls, you can mark them as such, in which case they
do not appear in the argument list when the task is run. E.g. if a task
will always use data from a file ‘constant.dat’ you could write:

.. code:: python

   my_task = SubprocessTask('my_executable -i variable.dat -c constants -o output.dat')
   my_task.set_inputs(['variable.dat', 'constants'])
   my_task.set_outputs(['output.dat'])
   my_task.set_constant('constants', 'constant.dat')

   output1 = my_task('input1.dat') # Note 'constant.dat' does not need to be specified
   output2 = my_task('input2.dat')

FunctionTasks
-------------

Though the most common reason to use Crossflow is to provide an
interface to tools usually used from the command line, tasks can also be
created to wrap conventional Python functions. The most likely scenario
for this is where the Python function is compute intensive and so needs
to be executed on a distributed worker, or where it needs to access a
large unit of data that resides on a worker from a previous computation.

``FunctionTasks`` are instantiated with the Python function they wrap:

.. code:: python

   def mult(x, y):
       return x * y

   mult_task = FunctionTask(mult)
   mult_task.set_inputs(['x', 'y'])
   mult_task.set_outputs('xy')

   result = mult_task(7.5, 8.4)

Debugging Tasks
---------------

If an attempt to run a task results in an error, by default an exception
will be raised. If instead you want to be notified about the error, but
want execution of the script to continue, then you can include the
pseudo-variable ``crossflow.DEBUGINFO`` in the list of outputs from your
task:

::

   awk_task = SubprocessTask('awk -f awkscript input.dat > output.dat')
   awk_task.set_inputs(['awkscript', 'input.dat'])
   awk_task.set_outputs(['output.dat'])

   # Will raise an exception if awkscript contains errors:
   output = awk_task('awkscript', 'infile.txt')

   awk_task.set_outputs(['output.dat', crossflow.DEBUGINFO])
   # Will not raise an exception if awkscript contains errors:
   output, debuginfo = awk_task('awkscript', 'infile.txt')
   ...
   (examine debuginfo to decide what to do)
   ...
