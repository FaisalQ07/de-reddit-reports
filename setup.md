# de-reddit-reports 2024 Data Engineering Setup Guide

## Table of Contents
1. [Configure SSH Keys](#configure-ssh-keys)
2. [Create a Virtual Machine](#create-a-virtual-machine)
3. [Configure the Virtual Machine](#configure-the-virtual-machine)
   - [Installing Anaconda](#installing-anaconda)
   - [Installing Docker](#installing-docker)
   - [Installing docker-compose](#installing-docker-compose)
   - [Installing Pgcli](#installing-pgcli)
   - [Installing Terraform](#installing-terraform)
   - [Creating a Service Account](#creating-a-service-account)
   - [Authenticate GCP using the service account credentials](#authenticate-gcp-using-the-service-account-credentials)
   - [Installing Pyspark](#installing-pyspark)
   - [Cloning the course repo](#cloning-the-course-repo)
4. [Open a Remote Connection from Visual Studio Code](#open-a-remote-connection-from-visual-studio-code)
5. [Conclusion](#conclusion)

## Configure SSH Keys
1. Generate a new SSH key with the following commands:
    ```bash
    cd ~/.ssh
    ssh-keygen -t rsa -f <key-file-name> -C <username> -b 2048
    ```
2. It'll raise a prompt to enter a passphrase. You can leave it and press enter. If it asks for confirmation, press enter again. Here's an example:  
![alt text](./README_resources/setup/ssh_keygen.PNG)  
3. This generates 2 files in the .ssh folder, one for the public (gcp.pub) and one for the private key (gcp).
4. Next, upload the public key to GCP with the following steps:
    * Open the gcp.pub file and copy its contents. Or you can use the cat command to display the contents in the terminal.
    * Go to the Google Cloud console > Compute Engine > Settings > Metadata.
      ![vm_metadata image](./README_resources/setup/vm_metadata.PNG)
    * Click on SSH Keys > Add SSH Keys  
      ![add_ssh_key](./README_resources/setup/add_ssh_key.PNG)
    * Paste the contents of the public key that you copied previously on the text box and click Save.
5. Now, you can connect to your Google VMs using the following command:
    ```bash
    ssh -i <PATH_TO_PRIVATE_KEY> <USERNAME>@<EXTERNAL_IP>
    ```

## Create a Virtual Machine
To set up a Virtual Machine:  
1.  Go to Compute Engine > VM Instances
