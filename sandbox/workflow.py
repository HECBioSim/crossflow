from distributed import LocalCluster
from crossflow.clients import Client

def run(client):
   # simple job - ask the client to tell us about itself:
   print(client)

if __name__ == '__main__':
    # create the cluster:
    cluster = LocalCluster()
    # connect a client:
    client = Client(cluster)
    # run the job:
    run(client)
