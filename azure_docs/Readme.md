# How to setup dev environment

## Dev machines

- covidia-dev-temp.westeurope.cloudapp.azure.com (temporary)
  - Standard DS15 v2 (20 vcpus, 140 GiB memory)
  - Linux (ubuntu 18.04)
  - 150 Gb SSD (can be increased)
- covidia-dev-01.francecentral.cloudapp.azure.com (not available yet)
- covidia-dev-02.francecentral.cloudapp.azure.com (not available yet)

### Pre-requisite
You need an account on the dev machine you want to work on. 

If you don't have one, ask someone with root access to SSH to the machine and perform the following steps:

```
sudo useradd -m <your-username>
echo "<your-username>:Passw0rd!" | sudo chpasswd
sudo passwd -e <your-username>
sudo chown -R <your-username> /home/<your-username>
sudo usermod -a -G sudo <your-username>
sudo usermod -s /bin/bash <your-username>
```

### Connectivity Checks

#### Ensure you can SSH into the machine by running:
```
ssh <your-username>@covidia-dev-temp.westeurope.cloudapp.azure.com
```
User Passw0rd! as the password - it should ask you to change your password on first login

#### Ensure you can reach Jupyter Hub on the machine:
  - Example: https://covidia-dev-temp.westeurope.cloudapp.azure.com:8000 
  - notice the **https**
  - use the same username and password as before

### GitHub access

- Go to the GitHub repo: https://github.com/Covid-IA/AI_epidemiology
- Click your user icon on the top-right and choose **Settings**
- Developer Settings -> **Personal access tokens**
- Generate a new token, **add the "repo" scope** and then copy the token to a safe place (you won't see it again)

On the dev machine apply the following steps using the alias you just created:
```
ssh <your-username>@covidia-dev-temp.westeurope.cloudapp.azure.com
cd notebooks
git clone https://github.com/Covid-IA/AI_epidemiology.git
git config --global user.email "email@example.com"
git config --global user.name "<your-git-alias-here>"
git config --global credential.helper cache
git config --global credential.helper 'cache --timeout=720000'
cs AI_epidemiology
git pull 
```

This will clone the repository to the folder /home/your-username/notebooks/AI_epidemiology which you can also access through the JupyterHub interface.

The first time you commit or try to pull changes from the repository you will be asked for your Git password, but it should then be cached for 200 hours.

## Using VS Code
If you use VS Code as an IDE, you can run it in your local machine and use the **Remote-SSH: Connect to Host** command to work with your local workstation but keep the code running on the remote machine:

1. Ctrl+Shift+P -> Remote-SSH: Connect to Host
2. Enter: your-user@covidia-dev-temp.westeurope.cloudapp.azure.com
3. Once done, choose "Open Folder" and choose the: /home/your-user/notebooks/AI_epidemiology/
4. When you do "New Terminal" it will open a remote terminal on the machine, allowing you to run your code there.

## Additional information about DSVM

All these machines are built with the Data Science Virtual Machine offering from Microsoft, which includes most usual data science tools already pre-configured for you.

DSVM information:
https://azure.microsoft.com/en-us/services/virtual-machines/data-science-virtual-machines/

What's included: https://docs.microsoft.com/en-us/azure/machine-learning/data-science-virtual-machine/tools-included

You can connect through SSH to these machines or use the Jupyter Hub interface. Alternatively, you can also use X2Go to connect to the graphical desktop interface and work from there (there are many development tools and IDEs pre-configured):
https://docs.microsoft.com/en-us/azure/machine-learning/data-science-virtual-machine/dsvm-ubuntu-intro#how-to-access-the-ubuntu-data-science-virtual-machine

Data Science with a Linux Data Science Virtual Machine in Azure:
https://docs.microsoft.com/en-us/azure/machine-learning/data-science-virtual-machine/linux-dsvm-walkthrough

## Useful Tools

### Azure Portal (not a tool, just a link)
https://portal.azure.com

### Azure Storage Explorer
https://azure.microsoft.com/en-us/features/storage-explorer/

As all our data will be stored in an Azure Storage we created for this, this allows you to explore data and upload or download files.

The storage account currently being used for IA is: **covidiastorage**

### Azure Batch Explorer
https://azure.github.io/BatchExplorer/

This is only required if you are using the Azure Batch service which we currently believe is the best choice for the simulation models.

Azure Batch: https://azure.microsoft.com/en-us/services/batch/

Documentation: https://docs.microsoft.com/en-us/azure/batch/batch-technical-overview



