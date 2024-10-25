import boto3

eks_client = boto3.client('eks')
ec2_client = boto3.client('ec2')

def lambda_handler(event, context):
    cluster_name = event['cluster_name']
    
    node_groups = eks_client.list_nodegroups(clusterName=cluster_name)['nodegroups']
    
    if not node_groups:
        return {"status": "No node groups found for the cluster.", "updates": []}
    
    ami_updates = []
    
    for node_group in node_groups:

        node_group_desc = eks_client.describe_nodegroup(clusterName=cluster_name, nodegroupName=node_group)
        current_ami = node_group_desc['nodegroup']['amiType']

        latest_ami_info = ec2_client.describe_images(
            Filters=[
                {'Name': 'name', 'Values': [f"amazon-eks-node-{node_group}*"]},
                {'Name': 'state', 'Values': ['available']},
            ]
        )
        
        if latest_ami_info['Images']:
            latest_ami = None
            latest_date = None

            for img in latest_ami_info['Images']:
                if latest_date is None or img['CreationDate'] > latest_date:
                    latest_date = img['CreationDate']
                    latest_ami = img['ImageId']
            
            if latest_ami != current_ami:
                ami_updates.append((node_group, latest_ami))
    
    return {
        "status": "Node groups checked.",
        "updates": ami_updates  
    }
