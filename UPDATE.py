import boto3
import threading

eks_client = boto3.client('eks')

def update_node_group(cluster_name, node_group, latest_ami):
    eks_client.update_nodegroup_version(
        clusterName=cluster_name,
        nodegroupName=node_group,
        launchTemplate={
            'name': node_group,  
            'version': latest_ami
        }
    )

def lambda_handler(event, context):

    cluster_name = event.get('cluster_name') 
    updates = event.get('updates', [])
    
    if not cluster_name or not updates:
        return {"status": "No updates required or missing cluster name."}

    threads = []
    for node_group, latest_ami in updates:
        thread = threading.Thread(target=update_node_group, args=(cluster_name, node_group, latest_ami))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    return {
        "status": "Node groups updated successfully.",
        "updated_node_groups": [node_group for node_group, _ in updates]
    }
