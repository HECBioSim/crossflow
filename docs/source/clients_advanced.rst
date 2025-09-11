Advanced Clients
=================

Here we go into ``crossflow.clients`` in more detail, see
:doc:`here <clients>` for the basics.

Currently there is only one Crossflow Client. Under the hood, this is
basically a Dask.distributed client, and for a full understanding of how
this works please see the Dask.distributed documentation. Here we
concentrate on some of the extras the Crossflow Client offers.

Transparent file handling
-------------------------

The Crossflow ``Client`` understands crossflow ``FileHandles`` and
converts to/from them as required. The only place where some user
awareness is generally required is in dealing with the outputs returned
by client ``.submit()`` and ``.map()`` methods. These are
``concurrent.Futures``, and while they may be passed on to further tasks
in the workflow as-is, to extract their data locally one must first call
their ``.result()`` method and then either save the data to a local file
with the ``FileHandle``\ ’s ``.save()`` method, or, if working
interactively, maybe view the contents via the ``FileHandle``\ ’s
``.read_text()`` method:

.. code:: python

   # Submit the job:
   output = client.submit(my_task, 'input.dat')
   # Wait for the job to finish and print the output to the screen:
   print(output.result().read_text())

Multiple return values
~~~~~~~~~~~~~~~~~~~~~~

The ``Dask.distributed`` client’s ``.submit()`` method always returns a
single future, even if the function it is executing returns multiple
values, e.g.:

.. code:: python

   cluster = distributed.LocalCluster()
   dask_client = distributed.Client(cluster)

   def sumprod(a, b):
       return a+b, a * b

   result = dask_client.submit(sumprod, 5, 7) # result is a Future for a tuple

In contrast, a Crossflow client returns one future per expected output
value:

.. code:: python

   cluster = distributed.LocalCluster()
   crossflow_client = clients.Client(cluster)

   def sumprod(a, b):
       return a+b, a * b

   sumprod_task = FunctionTask(sumprod)
   sumprod_task.set_inputs(['a', 'b'])
   sumprod_task.set_outputs(['sum', 'prod'])

   sum, prod = crossflow_client.submit(sumprod_task, 5, 7) # result is a pair of futures.

The Crossflow client’s ``.map()`` method functions similarly, returning
one list of Futures per output variable:

.. code:: python

   sums, prods = crossflow_client.map(sumprod_task, [5,6,7], [7,8,9]) # result is a pair of lists of futures.
   assert len(sums) == 3
