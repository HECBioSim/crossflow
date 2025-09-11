Crossflow Clients
-----------------

The ``crossflow.clients`` sub-package provides a Client through which
one can execute tasks on distributed resources. At its heart a
``crossflow.clients.Client()`` is a 
`dask.distributed <https://distributed.dask.org/en/latest/>`_ client,
and new users are strongly encouraged to read the documentation there to
understand how Crossflow works.

Creating a crossflow.Client
~~~~~~~~~~~~~~~~~~~~~~~~~~~

A Crossflow client provides access to a cluster of workers. These may be
remote machines, or a set of worker processes on the current compute
resource (see the dask documentation for more details on the many
different ways a cluster object can be created). The crossflow.Client is
initialised with the identity of the cluster it will serve:

.. code:: python

   from crossflow.clients import Client
   from distributed import LocalCluster # Just one way of creating a cluster
   cluster = LocalCluster()
   my_client = Client(cluster)

As a shortcut (typically for testing purposes), a local cluster may be
created on the fly, to serve the Client:

.. code:: python


   my_client = Client()

Using a crossflow.Client
~~~~~~~~~~~~~~~~~~~~~~~~

A crossflow.Task is sent to a crossflow.Client for execution using the
client’s .submit() or .map() method.

Running a single job:

.. code:: python


   output_future, logfile_future = my_client.submit(my_othertool_task, 'input1.dat', 'input2.dat')

Compare with the interactive version above:

1. The outputs (output_future, logfile_future) are now Futures - again,
   see the dask documentation for more detail, but also notice the
   difference: dask’s .submit() method always returns a single Future,
   while crossflow’s one returns one Future per expected output.

Running a set of jobs in parallel:

.. code:: python


   xs = ['input1a.dat', 'input1b.dat', 'input1c.dat']
   ys = ['input2a.dat', 'input2b.dat', 'input2c.dat']
   output_futures, logfile_futures = my_client.map(my_othertool_task, xs, ys)

In this case the .map() method returns lists of Futures. The individual
jobs are scheduled to the workers in the compute cluster in whatever way
is most efficient, if there are enough of them to run all four jobs in
parallel, they will.

For more details on Crossflow Clients, see :doc:`here <clients_advanced>`
