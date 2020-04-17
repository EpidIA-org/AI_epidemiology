# Using Azure Batch

This folder includes a Python notebook that handles all the automation of Azure Batch.

Azure Batch allows you to define a **Pool** of machines running any operating system. These machines will sit idle until some task is assigned to them. We configure **Jobs** to be run on those machines (on demand, or on a schedule). Each job is a collection of **Tasks**. A task is just some execution of a work item (usually the execution of a application, like rendering a frame on an animation job, or processing a subset of data on large data science projects). As we create jobs and tasks, Azure Batch will manage the execution of these work items within the pool.

Everything can be setup on the portal, but a good practice is to automate all steps through code.

Inside the sample_application folder there is a Python application built with no information of Azure Batch or Azure Storage. It simply reads one of the files in the input_data folder, applies some transformations and writes an output file. It's a dummy application built as an example. Nevertheless, we can make this application run in Azure Batch and retrieve/store data from Azure Storage without changing its code.

## Running the demo (1/2)

While executing the **Covidia Batch** notebook several steps are taken:

1. The configuration file settings.json is read to configure access to the Azure Batch account and a support Azure Storage account where we keep all the needed files

2. In the Storage Account we create 3 containers:
    - application: to store the application we want to run in Batch
    - input: to store any input files for the tasks
    - output: to store the output of each task

3. We zip the contents of the sample_application folder and upload it to the application container in Azure Storage
4. We create a shell script to install Python and we upload it to the application container in Azure Storage
5. Using the Azure Batch Python SDK, we create a pool of machines based on the chosen configuration - we also setup a StartTask at the Pool level which will make sure Python and Pip are installed in each of the nodes. As machines are added to the pool, this task will be run to ensure each node is ready once a task is started.
6. We create a Job to gather all our tasks - a Job Preparation Task is defined to download the sample_application from Azure Storage, decompress it and copy it to a known location. We also install any python packages required by the application through it's requirements.txt file
7. We create one task per file in the input_data folder, essentially creating 60 tasks. Each task consists of a single execution of the sample_application passing one of the files as input. The output files are also collected and automatically sent to Azure Storage and kept on the output container
8. After waiting for all tasks to complete, we clean up the job and pool to drop the cost to zero.

## Running the demo (2/2)

A slightly different approach is shown in the covidia_batch_process.py file. In this case, instead of zipping the sample application and uploading it to Azure Storage, we instead run **git clone** on the Azure Batch node machines to pull this repository and "install" the application locally.

The only complexity is, given that this is a private repo we need to authenticate when running git operations. For that, we need to create an SSH key first (public/private pair), add the public part to the GitHub repo and add make sure each node of the pool has a copy of the private key. Using a username and password will always require the password to be added interactively, which prevents automation, so SSH key is the only viable option.

Before running the script do the following steps

1. Execute the following command on a terminal window, making sure you are on the same folder as these instructions:
```bash
mkdir ssh_keys
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

2. When prompted to "Enter a file in which to save the key", choose ssh_keys/myKey

3. No need to add a password (just press enter)

4. Open the ssh_keys/myKey.pub in a text editor and copy the contents. If you're working on the remote machine, you can cat the output to the shell, select it with the mouse and press Ctrl+Shift+C

```bash
cat ssh_keys/myKey.pub
``` 

5. Go to GitHub, click your profile photo, click Settings and then choose the **SSH and GPG keys** menu

6. Click **New SSH key**

7. Add a title such as "Batch key" and paste the key into the "Key" field

8. Click **Add SSH Key**

This takes care of the public part of the key. Now we need to make sure we copy the private key to each node. We'll do this through Azure Storage and adding the private key as a reference file for the Job.

1. Copy the private key to the batch_resources folder
```
cp ssh_keys/myKey batch_resources
```

2. The script will make sure to copy this key to Azure Storage and add it to the Job Preparation task.

3. To configure the job preparation task, make sure to check the following variables in the **covidia_batch_process.py** script:

```python
git_repo_url = "git@github.com:Covid-IA/AI_epidemiology.git"
git_branch = "dev"
git_repo_name = "AI_epidemiology"
git_app_folder = "azure_docs/batch_example/sample_application"
```

## How to adapt to your own Script

- It's easy to change the notebook to compress and upload your application instead of the sample_application.
- Your application should include a requirements.txt file with all the packages that are needed.
- Change the settings.json file to define the size of the pool, name of the jobs, etc.
- The only part that really needs changing is the Tasks generation as that is specific to your application (e.g which arguments to pass, how outputs are collected, etc.)

