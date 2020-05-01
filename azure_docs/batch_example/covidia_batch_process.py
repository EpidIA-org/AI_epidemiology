
# general imports
from pprint import pprint
import io, os, sys, time, json, uuid, glob
from datetime import datetime, timedelta
from dotenv import load_dotenv

# azure batch
import azure.batch.batch_auth as batchauth
import azure.batch._batch_service_client as batch
import azure.batch.models as batchmodels

# azure storage
import azure.storage.blob as azureblob

# ## Loading Configuration
# Before executing, make sure you create a .env file with the following format:
# 
# ```
# BATCH_SERVICE_URL=<batch_service_url>
# BATCH_ACCOUNT_NAME=<batch_account_name>
# BATCH_ACCOUNT_KEY=<batch_account_key>
# BATCH_STORAGE_ACCOUNT_NAME=<storage_account_name>
# BATCH_STORAGE_ACCOUNT_KEY=<storage_account_key>
# ```
# 
# This .env file is not added on the repo to avoid surfacing sensitive data.

load_dotenv()

batch_service_url = os.getenv("BATCH_SERVICE_URL")
batch_account_name = os.getenv("BATCH_ACCOUNT_NAME")
batch_account_key = os.getenv("BATCH_ACCOUNT_KEY")
storage_account_name = os.getenv("BATCH_STORAGE_ACCOUNT_NAME")
storage_account_key = os.getenv("BATCH_STORAGE_ACCOUNT_KEY")

print(batch_service_url)

# Create Clients

# create the batch client to create pools, jobs and tasks on Azure Batch
credentials = batchauth.SharedKeyCredentials(
       batch_account_name,
       batch_account_key)

batch_client = batch.BatchServiceClient(
        credentials,
        batch_url=batch_service_url)

print("[INFO] Connected to Azure Batch")

# Create the blob client, for use in obtaining references to
# blob storage containers and uploading files to containers.
blob_client = azureblob.BlockBlobService(
    account_name = storage_account_name,
    account_key = storage_account_key)

print("[INFO] Connected to Azure Storage")

# Create Storage Containers
# This will create an application container to hold the Python setup file.
# Additionally it will create an input and output container to store any input files to feed to each task and to collect the output of the tasks

# Use the blob client to create the containers in Azure Storage if they
# don't yet exist.
app_container_name = "application"
input_container_name = "input"
output_container_name = "output"

blob_client.create_container(app_container_name, fail_on_exist=False)
blob_client.create_container(input_container_name, fail_on_exist=False)
blob_client.create_container(output_container_name, fail_on_exist=False)

print("[INFO] Created Storage Containers")

# Helper Azure Storage Methods

def upload_blob_and_create_sas(block_blob_client, container_name, file_name, blob_name, hours=24):

    block_blob_client.create_container(
        container_name,
        fail_on_exist=False)

    block_blob_client.create_blob_from_path(
        container_name,
        blob_name,
        file_name)

    print("Uploaded", file_name, "to container", container_name)

    expiry = datetime.utcnow() + timedelta(hours=hours)
    sas_token = block_blob_client.generate_blob_shared_access_signature(
        container_name,
        blob_name,
        permission=azureblob.BlobPermissions.READ,
        expiry=expiry)

    sas_url = block_blob_client.make_blob_url(
        container_name,
        blob_name,
        sas_token=sas_token)

    return sas_url

def create_container_sas_token(block_blob_client, container_name, permission, hours=24):
 
    expiry = datetime.utcnow() + timedelta(hours=hours)
    sas_token = block_blob_client.generate_container_shared_access_signature(
        container_name, permission=permission, expiry=expiry)

    valid_sas_url = "https://{}.blob.core.windows.net/{}?{}".format(
        block_blob_client.account_name, container_name, sas_token
    )
    
    return valid_sas_url

# python install script
setup_file_name = "installPython.sh"
# folder to store the zipped file and install script
resource_folder = "batch_resources"
# ssh key file
ssh_file_name = "myKey"

# get file paths for upload
setup_file_path = os.path.join(resource_folder, setup_file_name)
ssh_file_path = os.path.join(resource_folder, ssh_file_name)

# upload install script to application container
setupFileSas = upload_blob_and_create_sas(blob_client, app_container_name, setup_file_path, setup_file_name)
sshKeySas = upload_blob_and_create_sas(blob_client, app_container_name, ssh_file_path, ssh_file_name)

# Creating Azure Batch Pool
# A pool is the central compute resource for Azure Batch. It's composed of several machines that will be assigned tasks once a job is created.
# In here, we setup a pool of Ubuntu nodes and create a start task to make sure Python is installed. As machines get added to the pool, this task will imediately run before any tasks are assigned to the nodes.

# let's read the configuration
settings_file = "batch_settings.json"

with open(settings_file) as f:
    settings = json.load(f)

pprint(settings, indent=2)

# Defining a StartTask
# Runs on all nodes on startup. This will reference the install script to make sure Python is installed on each node

# create an elevated identity to run the start task - needed whenever you require sudo access
user = batchmodels.AutoUserSpecification(scope=batchmodels.AutoUserScope.pool, elevation_level=batchmodels.ElevationLevel.admin)
user_identity = batchmodels.UserIdentity(auto_user=user)   

# setup the task command - executing the shell script that install python. 
command_line = f"/bin/bash -c \"sudo sh {setup_file_name}\""

# setup the start task
startTask = batchmodels.StartTask(
        command_line=command_line,
        wait_for_success = True,
        user_identity = user_identity,
        resource_files = [batchmodels.ResourceFile(
                         file_path = setup_file_name,
                         http_url = setupFileSas)])

print("Start task:")
print(f"CommandLine: {command_line}")
print(f"ResourceFiles:")
for f in startTask.resource_files:
    print(f"\t{f.http_url}")

# Creating the Pool

# checking configuration
poolId = settings["poolId"]
vmSize = settings["vmSize"]
dedicatedNodes = settings["dedicatedVmCount"]
lowPriorityNodes = settings["lowPriorityVmCount"]

print(f"Creating pool {poolId} with:")
print("Size:",vmSize)
print("Number of dedicated nodes:",dedicatedNodes)
print("Number of low priority nodes:",lowPriorityNodes)

# setup pool
pool = batchmodels.PoolAddParameter(
    id=poolId,
    virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
        image_reference=batchmodels.ImageReference(
            publisher="Canonical",
            offer="UbuntuServer",
            sku="18.04-LTS",
            version="latest"
        ),
        node_agent_sku_id="batch.node.ubuntu 18.04"),
    vm_size=vmSize,
    target_dedicated_nodes=dedicatedNodes,
    target_low_priority_nodes=lowPriorityNodes,
    start_task=startTask)

# create pool
try:
    print("Attempting to create pool:", pool.id)
    batch_client.pool.add(pool)
    print("Created pool:", pool.id)
except batchmodels.BatchErrorException as e:
    if e.error.code != "PoolExists":
        raise
    else:
        print("Pool {!r} already exists".format(pool.id))

def wait_for_all_nodes_state(batch_client, pool, node_state):
    print('Waiting for all nodes in pool {} to reach one of: {!r}\n'.format(
        pool.id, node_state))
    i = 0
    targetNodes = pool.target_dedicated_nodes + pool.target_low_priority_nodes
    while True:
        # refresh pool to ensure that there is no resize error
        pool = batch_client.pool.get(pool.id)
        if pool.resize_errors is not None:
            resize_errors = "\n".join([repr(e) for e in pool.resize_errors])
            raise RuntimeError(
                'resize error encountered for pool {}:\n{}'.format(
                    pool.id, resize_errors))
        nodes = list(batch_client.compute_node.list(pool.id))
        if (len(nodes) >= targetNodes and
                all(node.state in node_state for node in nodes)):
            return nodes
        i += 1
        if i % 3 == 0:
            print('waiting for {} nodes to reach desired state...'.format(
                targetNodes))
        time.sleep(10)

# we check if all nodes are up before we continue
nodes = wait_for_all_nodes_state(batch_client, pool, [batchmodels.ComputeNodeState.idle, batchmodels.ComputeNodeState.running])

# show all nodes
for n in nodes:
    print(n.id, n.state, n.is_dedicated)

# Creating a Job to run on the Pool
# We will now create a job and an associated Prep task to ensure the application is downloaded, extracted to a known location and all python packages are installed via pip

# creating a unique job Id
job_id = settings["jobIdPrefix"] + "_" + datetime.now().strftime("%Y-%m-%d_%H-%M")

# setup git repo details
git_repo_url = "git@github.com:Covid-IA/AI_epidemiology.git"
git_branch = "dev"
git_repo_name = "AI_epidemiology"
git_app_folder = "azure_docs/batch_example/sample_application"

# setup the task command:
# copies ssh key file to shared dir
# makes sure the directory is clean (if we're reusing machines in the pool)
# clones the repo by adding the SSH key to the SSH agent and using the SSH url from github
# moves to the directory inside the repo
# installs python requirements
command_line = f"/bin/bash -c \"mv {ssh_file_name} $AZ_BATCH_NODE_SHARED_DIR && "\
               f"cd $AZ_BATCH_NODE_SHARED_DIR && "\
               f"rm {git_repo_name} -rf && "\
               f"ssh-agent bash -c 'ssh-add {ssh_file_name} && git clone -b {git_branch} {git_repo_url}' && "\
               f"cd {git_repo_name}/{git_app_folder} && "\
               f"pip3 install -r requirements.txt \""

# create an elevated identity to run the start task
user = batchmodels.AutoUserSpecification(scope=batchmodels.AutoUserScope.pool, elevation_level=batchmodels.ElevationLevel.admin)
user_identity = batchmodels.UserIdentity(auto_user=user)   

# setup the start task
jobTask = batchmodels.JobPreparationTask(
        command_line = command_line,
        user_identity = user_identity,
        wait_for_success = True,
        resource_files = [batchmodels.ResourceFile(
                         file_path = ssh_file_name,
                         http_url = sshKeySas)])

print("Job Preparation task:")
print(f"CommandLine: {command_line}")
print(f"ResourceFiles:")
for f in jobTask.resource_files:
    print(f"\t{f.http_url}")


# setup job
job = batchmodels.JobAddParameter(
    id=job_id,
    pool_info=batchmodels.PoolInformation(pool_id=pool.id),
    job_preparation_task = jobTask)

# create job
print('Creating job [{}]...'.format(job.id))

try:
    batch_client.job.add(job)
except batchmodels.batch_error.BatchErrorException as err:
    print_batch_exception(err)
    if err.error.code != "JobExists":
        raise
    else:
        print("Job {!r} already exists".format(job_id))

# ## Adding Tasks to the Job
# Now that our application is correctly configured and we made sure Python is installed in all nodes, we need to setup a task to run a work item. We can launch many tasks inside the same job and Azure Batch will assign it to any VMs in the pool.
# 
# In this example, we will create as many tasks as files in input_data (a local folder in this repo). This is a simple way of doing paralel processing of a large file when splits can be done. Another option is simple iterating over an array of parameter values and creating a task for each different value. We illustrate here the most complicated scenario which involves passing different input files to the script and uploading those files to the input container in the storage account.
# 
# These tasks also write output to storage. The main.py script writes an output file and we configure the task to upload these files to the output container we created earlier. It is done after the task ends successfully

# get a sas url for write access to output container. This will be used so we can persist task output files
output_container_sas = create_container_sas_token(blob_client, container_name=output_container_name, permission=azureblob.BlobPermissions.WRITE)
print(output_container_sas)

# we get a list of input files
file_list = glob.glob("input_data/*.dat")

# initialize task counter
i = 0
for f in file_list:
    # increment task counter
    i = i + 1
    
    # create a task id
    task_id = "Process-" + str(i)
    print("\nCreating task",task_id)
    
    # grab file name
    input_file = f.split("/")[-1:][0]
    output_file = input_file.replace(".dat","_output.csv")
    
    # upload file to azure storage
    input_file_sas = upload_blob_and_create_sas(blob_client, input_container_name, f, input_file)
    
    # setup task command
    taskCommand = f"/bin/bash -c \"cd $AZ_BATCH_NODE_SHARED_DIR/{git_repo_name}/{git_app_folder}" + \
                  f"&& python3 main.py -i $AZ_BATCH_TASK_WORKING_DIR/{input_file} -o $AZ_BATCH_TASK_WORKING_DIR/{output_file}\""
    print(taskCommand)
    
    # create an elevated identity to run the start task
    user = batchmodels.AutoUserSpecification(scope=batchmodels.AutoUserScope.pool, elevation_level=batchmodels.ElevationLevel.admin)
    user_identity = batchmodels.UserIdentity(auto_user=user)   
   
    # setup output files destination
    containerDest = batchmodels.OutputFileBlobContainerDestination(container_url = output_container_sas, path = task_id)
    outputFileDestination = batchmodels.OutputFileDestination(container = containerDest)
    
    # setup output files upload condition
    uploadCondition = batchmodels.OutputFileUploadCondition.task_success
    uploadOptions = batchmodels.OutputFileUploadOptions(upload_condition = uploadCondition)
    
    # output files
    output_files = [batchmodels.OutputFile(destination = outputFileDestination,
                                        upload_options = uploadOptions,
                                        file_pattern="*output.csv")]
    
    
    # create task
    task = batchmodels.TaskAddParameter(
    id = task_id,
    command_line=taskCommand,
    user_identity=user_identity,
    resource_files=[batchmodels.ResourceFile(
                        file_path=input_file,
                        http_url=input_file_sas)],
    output_files=output_files)
    
    
    batch_client.task.add(job_id=job.id, task=task)

# Monitoring Tasks

def wait_for_tasks_to_complete(batch_client, job_id, timeout):

    time_to_timeout_at = datetime.now() + timeout

    while datetime.now() < time_to_timeout_at:
        print("Checking if all tasks are complete...")
        tasks = batch_client.task.list(job_id)

        incomplete_tasks = [task for task in tasks if
                            task.state != batchmodels.TaskState.completed]
        if not incomplete_tasks:
            return
        time.sleep(30)

    raise TimeoutError("Timed out waiting for tasks to complete")

wait_for_tasks_to_complete(batch_client, job.id, timedelta(minutes=120))
print("All Tasks Complete!")

# UNCOMMENT THIS TO REMOVE THE JOB
#batch_client.job.delete(job.id)

# UNCOMMENT THIS TO REMOVE THE POOL
#batch_client.pool.delete(pool.id)

