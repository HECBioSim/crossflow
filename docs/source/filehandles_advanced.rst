Advanced File Handling
=======================

Here we go into ``Crossflow.FileHandle`` in more detail, see
:doc:`here <filehandles>` for the basics.

Crossflow is designed for use on distributed computing clusters, and
does not require that all the workers can see the same filesystem. To
achieve this, all input and output files are converted to portable
objects. Most of this is done behind the scenes by ``crossflow.Tasks``
and ``crossflow.Clients`` and mostly requires no user intervention, but
on occasion this is helpful.

Crossflow File Handling basics
------------------------------

When a ``crossflow.Task`` that takes file names as arguments is run, the
following takes place;

1. The input file is ‘loaded’ into a ``crossflow.FileHandle`` object.
2. The objects, along with the function to be evaluated, are sent to the
   worker process.
3. The worker unpacks the ``FileHandles`` into suitably-named files in
   the working directory.
4. The task function is executed.
5. Output files are loaded into ``FileHandle`` objects and returned from
   the worker.

What exactly is meant by ‘loading’ a file can be varied. By default,
each ``FileHandle`` contains a compressed copy of the data in the file
it is constructed from. This means quite a lot of data may flow between
the parent process and the workers, but is normally fast. As an
alternative, file handling can be configured so that ‘loading’ means
making a copy of the input file in a place that is accessible to both
parent process and workers.

Configuring Crossflow to use a shared filesystem for file staging
-----------------------------------------------------------------

If there is a filesystem that is NFS mounted on all workers, then a
directory on this filesystem may be configured as a ‘stage_point’ for
crossflow:

.. code:: python

   import crossflow
   from crossflow import tasks, clients

   crossflow.set_stage_point('/usr/shared/tmp')

   my_task = tasks.SubprocessTask('cat a b > c')
   my_task.set_inputs(['a', 'b'])
   my_task.set_outputs(['c'])

   # Connect to an existing distributed cluster:
   my_client = client.Client(scheduler_file='scheduler.json')

   # Submit the job. Files pass to/from the workers via copies in /usr/shared/tmp:
   joined = my_client.submit('file1.txt', 'file2.txt')

Configuring Crossflow to use an S3 bucket for file staging
----------------------------------------------------------

If you have an S3 bucket that can be visible on all workers, then this
can be configured as a ‘stage_point’ for crossflow:

.. code:: python

   import crossflow
   from crossflow import tasks, clients

   crossflow.set_stage_point('s3://groupname.username.crossflowbucket')

   my_task = tasks.SubprocessTask('cat a b > c')
   my_task.set_inputs(['a', 'b'])
   my_task.set_outputs(['c'])

   # Connect to an existing distributed cluster:
   my_client = client.Client(scheduler_file='scheduler.json')

   # Submit the job. Files pass to/from the workers via copies in the s3 bucket:
   joined = my_client.submit('file1.txt', 'file2.txt')
