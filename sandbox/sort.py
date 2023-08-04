from distributed import LocalCluster
from crossflow.clients import Client
from crossflow.tasks import SubprocessTask
from crossflow.filehandling import FileHandler

sort = SubprocessTask('sort -n -o sorted_file input_file')
sort.set_inputs(['input_file'])
sort.set_outputs(['sorted_file'])

def run(cluster):
    print(cluster)
    client = Client(cluster)
    print(client)
    input_file = 'test.dat'
    output = client.submit(sort, input_file)
    output_file = 'sorted.dat'
    output.result().save(output_file)
    

if __name__ == '__main__':
    cluster = LocalCluster()
    run(cluster)
    cluster.close()
