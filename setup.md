# de-reddit-reports 2024 Data Engineering Setup Guide

## Table of Contents
1. [Configure SSH Keys](#configure-ssh-keys)
2. [Create a Virtual Machine](#create-a-virtual-machine)
3. [SSH: Aliasing Credentials with Config File](#ssh-aliasing-credentials-with-config-file)
4. [Configure the Virtual Machine](#configure-the-virtual-machine)
   - [Installing Anaconda](#installing-anaconda)
   - [Installing Docker](#installing-docker)
   - [Installing docker-compose](#installing-docker-compose)
   - [Installing Terraform](#installing-terraform)
   - [Creating a Service Account](#creating-a-service-account)
   - [Authenticate GCP using the service account credentials](#authenticate-gcp-using-the-service-account-credentials)
   - [Installing Pyspark](#installing-pyspark)
   - [Cloning the course repo](#cloning-the-course-repo)
5. [Open a Remote Connection from Visual Studio Code](#open-a-remote-connection-from-visual-studio-code)
6. [Conclusion](#conclusion)

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
1. Go to Compute Engine > VM Instances  
   ![create_vm](./README_resources/setup/create_vm.PNG) 
2. Click on Create Instance.  
   ![create_vm_instance](./README_resources/setup/create_vm_instance.PNG) 
3. Populate the configurations for the VM with the following details (Name and Region can be as per your preference):  
  *  Change name to <*preferred-name*>
  *  Select Region 
  *  Under Machine Config, select *series* - *E2* , *Machine type* - *e2-standard-4* 
  *  Under Boot Disk, select *Image type* - *Ubuntu 20.04 LTS*, *size* - *40 GB* 
  *  Leave the rest of the configurations to default values and click Create
4. This will spin up a virtual machine instance for you. In order to ssh into this instance, run the following command:   
    ```bash
       ssh -i <PATH_TO_PRIVATE_KEY> <USERNAME>@<EXTERNAL_IP>
    ```
    *  Here's an example on my system:  
       ![ssh_login](./README_resources/setup/ssh_login.PNG)
5. You can also configure an ssh alias, which is a convenient way to store the ssh details in a config file.

## SSH: Aliasing Credentials with Config File
**Setting up Config file**
1. To set up an SSH alias, you first need to locate your SSH config file. This file is located in the .ssh directory in your home directory. The file is typically called config. If the file does not exist, you can create it.  
2. Once you have located the config file, open it in a text editor. You can use any text editor you like, such as nano or vim or VS Code. To create an alias, add the following lines to the file:  
  ![config_file](./README_resources/setup/config_file.PNG)
3. The above credentials are to establish an SSH connection to a running Google Virtual Machine Instance. Here:  
  *  de-zoomcamp is the alias.
  *  34.123.38.8 is the external IP Address of the running VM instance.  
  *  faisal is the username.  
  *  c:/Users/Admin/.ssh/gcp is the path of the private key file.
  *  <*optional*> LocalForward - it forwards local port 8888 to the SSH server's local address (127.0.0.1) on port 8888.  

**Connecting to Virtual Machine**
1. Once you have created your alias, you can connect to the virtual machine by running the following command:
    ```bash
    ssh de-zoomcamp
    ```  
    * Here is the result:  
    ![ssh_login_via_config](./README_resources/setup/ssh_login_via_config.PNG)  

## Configure the Virtual Machine
### Installing Anaconda  
1. Visit [Anaconda's website](https://www.anaconda.com/download) and copy the link to Linux 64-Bit Installer  
   ![anaconda_linux_installer](./README_resources/setup/anaconda_linux_installer.PNG)  
2. Download the file in the VM:  
   ```bash
       wget https://repo.anaconda.com/archive/Anaconda3-2023.09-0-Linux-x86_64.sh
   ```  
3. Run the downloaded file:  
   ```bash
      bash  Anaconda3-2023.09-0-Linux-x86_64.sh
   ```  
4. Keep pressing Enter to scroll down and enter yes to accept the license terms.
5. Press Enter to confirm the default location.
6. Enter yes to run the conda init when asked.
7. To automatically activate the Conda base environment upon logging into your VM:    
    *  do *__vim ~/.bashrc__*  
    *  Go to the end of the file and press 'i' to activate insert mode  
    *  Paste to the end, `eval "$(/path/to/your/anaconda3/bin/conda shell.bash hook)"`
    *  Press __Esc__ to exit insert mode, then type `:wq` to save and exit __vim__ editor
    *  type logout
    *  Type `ssh de-zoomcamp` to login back into the VM, and it will show `(base)` representing conda activation  
    * Here is the result:  
    ![conda_activate](./README_resources/setup/condo_activate.PNG)  


### Installing Docker  
1. Run the following commands:  
   ```bash
     sudo apt-get update
     sudo apt-get upgrade
     sudo apt-get install docker.io 
   ```  
2. This will install docker but you'll not be able to run it without sudo. It'll throw a permission denied error when trying to run a container as `docker run hello-world`  
  *  Error:  
     ![docker_run_permission_error](./README_resources/setup/docker_run_permission_error.PNG)
3. To run docker without sudo, run the following commands:  
   ```bash
      sudo groupadd docker
      sudo gpasswd -a $USER docker
      sudo service docker restart
   ```  
4. Log out of the ssh session and log back in to re-evaluate the group memberships and try running the docker run hello-world command.  
   It works now, without using sudo  
   ![docker_run_success](./README_resources/setup/docker_run_success.PNG)


### Installing docker-compose  
1. go to [Docker Compose Releases](https://github.com/docker/compose/releases/tag/v2.24.1).  
   Copy the link to the latest [release](https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-linux-x86_64)  
2. Create a new bin folder in VM and download the asset into it:  
   ```bash
      cd ~
      mkdir bin
      cd bin
      wget https://github.com/docker/compose/releases/download/v2.24.1/docker-compose-linux-x86_64 -O docker-compose
   ```  
3. This will create a new file docker-compose in the bin folder.
4. Make this file executable:  
   `chmod +x docker-compose`  
5. Next, add the bin folder to the path:  
    *  Go to the home directory: `cd ~`  
    *  Open the .bashrc file: `nano .bashrc`  
    *  Paste the following to the end of the `.bashrc` file:
       `export PATH="${HOME}/bin:${PATH}"`  
    * Press `Ctrl+O` > `enter` > `Ctrl+X`  
6. docker-compose installed successfully.  
   ![docker-compose_installed](./README_resources/setup/docker-compose_installed.PNG)  


### Installing Terraform  
1. From terraform's [installation website](https://developer.hashicorp.com/terraform/install), Copy the link for Linux's AMD64 file.
2. Go to the bin folder created previously and download the file using `wget`:  
   ```bash
      cd ~/bin
      wget https://releases.hashicorp.com/terraform/1.7.4/terraform_1.7.4_linux_amd64.zip
   ```  
3. To unzip this file, install the unzip package: `sudo apt-get install unzip`  
4. Unzip the file: `unzip terraform_1.7.4_linux_amd64.zip`  
5. There will be a terraform executable file extracted. You can delete the zip file.
6. Since this file is in the bin folder and the bin folder is in the path, everything is set up.
7. Try running the following command to verify terraform's installation: `terraform --version`  
   ![terraform_installed](./README_resources/setup/terraform_installed.PNG)  


### Creating a service account  
1. In your GCP project, go to IAM and Admin > Service Accounts  
   ![iam](./README_resources/setup/iam.PNG)
2. Click on the "Create Service Account" button at the top and provide the service account name.  
3. Assign the following roles to this service account:  
   ![assign_roles_to_service_account](./README_resources/setup/assign_roles_to_service_account.PNG)  
4. Click Save. The service account is now created.
5. To generate keys for this service account, click on the 3-dot menu and then on "manage keys"  
   ![manage_keys](./README_resources/setup/manage_keys.png)  
6. On the following page, click on Add Key > Create new key> JSON format. Click Create.
7. This will download a JSON file. This is to be uploaded to the VM using SFTP (or just drag and drop via VS Code).
8. Next, create a folder in *home dir* `.gcp` and upload the JSON credentials file into it  


### Authenticate GCP using the service account credentials  
1. To authenticate GCP, we need to set an environment variable  
    *  `$GOOGLE_APPLICATION_CREDENTIALS` to point to the service account JSON file:  
       ```bash
          export GOOGLE_APPLICATION_CREDENTIALS=/home/faisal/.gcp/<credentials-filename>.json
       ```  
2. Next, authenticate GCP using the following command:  
   ```bash
      gcloud auth activate-service-account --key-file $GOOGLE_APPLICATION_CREDENTIALS
   ```


   




  

  


