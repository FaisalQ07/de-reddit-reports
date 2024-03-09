# de-reddit-reports 2024 Data Engineering Project Setup Guide

## Table of Contents
1. [Cloning the course repo](#cloning-the-course-repo)
2. [Add Service Account keyfile](#add-service-account-keyfile)
3. [Reddit developer account creation ](#reddit-developer-account-creation-and-configuration)
4. [Configure Reddit credentials](#configure-reddit-credentials)
5. [Configure Terraform](#configure-terraform)
6. [Terraform authentication and execution](#terraform-authentication-and-execution)
7. [Setup Mage-ai](#setup-mage-ai)
   - [Build Mage Image](#build-mage-image)
   - [Run Mage as Container](#run-mage-as-container)
   - [Port Forwarding](#port-forwarding)
   - [Configure io_config.yaml](#configure-io_configyaml)
8. [Setup Google CLI in Mage-ai Container](#setup-google-cli-in-mage-ai-container)
9. [Setup DBT project as sub-folder](#setup-dbt-project-as-sub-folder)
10. [Go back](#go-back)
11. [Go to Project Readme](#go-to-project-readme)


## Cloning the course repo 
Clone the [course repo](https://github.com/FaisalQ07/de-reddit-reports.git) into the Virtual Machine. Your final folder structure should look something like this:  
![cline_repo](./README_resources/project_setup_images/clone_repo.PNG)

## Add Service Account keyfile  
1. Create a folder `keys` under project `de-reddit-reports` as: `mkdir keys`
2. Add the JSON credentials keyfile created in the section [Creating a service account](./vm_setup.md/#creating-a-service-account) to keys folder
3. Make sure to add folder `keys` to the file `.gitignore`


## Reddit developer account creation
To extract Reddit data, one needs to utilize its Application Programming Interface (API). This entails following a series of steps to configure and set up access.  
1. Create a [Reddit account](https://www.reddit.com/register/).  
2. Navigate [here](https://www.reddit.com/prefs/apps) and create an app. Make sure you select "script" from the radio buttons during the setup process.
3. Take a note of a few things once this is setup:
    *  App name
    *  App ID
    *  API Secret Key


## Configure Reddit credentials  
1. Create a file `.env` under project folder `de-reddit-reports`
2. Add the following variables:  
    *  **PROJECT_NAME**=magic-de-reddit-reports
    *  **REDDIT_APP_NAME**=<*App name*> from [Reddit developer account creation](#reddit-developer-account-creation) step
    *  **REDDIT_APP_ID**=<*App ID*> from [Reddit developer account creation](#reddit-developer-account-creation) step
    *  **REDDIT_SECRET**=<*API Secret Key*> from [Reddit developer account creation](#reddit-developer-account-creation) step
3. As best practice, Mage-ai expects sensitive variables to be added to `.env` file. Mage-ai automatically adds .env to    gitignore. 
4. These variables become available in Mage-ai container volume to be accessed.  
   More about it in the section [Configure io_config.yaml](#configure-io_configyaml)


## Configure Terraform  
1. Open the file `variables.tf` under folder `terraform`
2. Edit the following variables. For simplicity, create project with the same name to avoid a lot of editing. You can change the region to the one closest to your geo-location for cost efficiency.  
    *  variable "project_id" -  Replace the default with `project_id` of your GCP project
    *  variable "region"     -  Replace the default with `region` of your chosing for GCS bucket creation
    *  variable "reddit_terra_dataset_id" - Replace the default with `dataset_id` of your chosing for BigQuery datset creation


## Terraform authentication and execution  
1. Create a variable `GOOGLE_CREDENTIALS` and make it point to the credentials keyfile path (covered in [Add Service Account keyfile](#add-service-account-keyfile))  
    ```bash
       export GOOGLE_CREDENTIALS='/home/user/keys/<credential-file>.json'
    ```
2. Terraform uses variable `GOOGLE_CREDENTIALS` to authenticate Terraform with GCP to manage resources.
3. Run the below commands in order to setup GCP infrastructure defined in `main.tf`  
    *  `terraform init`
    *  `terraform plan`
    * `terraform apply`
4. Login to GCP account and verify if the resources are created. It should create -   
    *  Google Storage Bucket - `reddit-terra-bucket`
    *  Google BigQuery Dataset - `reddit_dataset`


## Setup Mage-ai
Mage setup includes the following steps: 
### Build Mage Image  
1. Execute the below command from the project directory path containing `Dockerfile` to build the image named `mageai_with_gcloud_sdk_dbt`
   ```bash
      docker build -t mageai_with_gcloud_sdk_dbt .
   ```  

### Run Mage as Container  
1. Execute the below command to run the image `mageai_with_gcloud_sdk_dbt` as a container  
   ```bash
      docker-compose up
   ```

### Port Forwarding  
1. Forward port 6789 in your editor to be able to access Mage container.   
   If using VS Code  
    *  go-to `PORTS` tab in the terminal window.  
    *  Click on `Add Port`.  
    *  Under `Port`, type 6789 and it should automatically populate the next column named `Forwarded Address`.  
    * Click on the glob icon in red to access the Mage container in Browser.  
    ![port_forwarding](./README_resources/project_setup_images/port_forwarding.PNG) 

### Configure io_config.yaml
1. In the Mage GUI, click on the files icon on the left vertical pane.  
   ![mage_files](./README_resources/project_setup_images/mage_files.png)  
2. Select the file named io.config.yaml  
   ![select_io_config](./README_resources/project_setup_images/select_io_config.png)  
3. Under the section `# Google`:  
    *  Edit the value for variable`GOOGLE_SERVICE_ACC_KEY_FILEPATH`. Set it to: `/home/src/keys/<credential-file>.json`
4. At the end of the file, add the following:  
    ```bash
       # Reddit
       REDDIT_APP_NAME: "{{ env_var('REDDIT_APP_NAME') }}"
       REDDIT_APP_ID: "{{ env_var('REDDIT_APP_ID') }}"
       REDDIT_SECRET: "{{ env_var('REDDIT_SECRET') }}"
    ```
5. This makes reddit variables accessible in the Mage Code blocks.  
   For python, it can be accessed as:  
   ```bash
      import os
      os.getenv("REDDIT_APP_NAME")
   ```

## Setup Google CLI in Mage-ai Container  
The steps [Build Mage Image](#build-mage-image), and [Run Mage as Container](#run-mage-as-container) download and installs Google Cloud SDK in the Mage-ai container.  
1. To verify if gcloud cli is installed, Open terminal in Mage-ai container and run cmd: `gcloud --version`. It should provide the version details.    
   ![gcloud_version_mage-ai](./README_resources/project_setup_images/gcloud_version_mage-ai.PNG)  
2. To authenticate with gcloud using a service account JSON file, use following steps:  
   *  Set the GOOGLE_APPLICATION_CREDENTIALS Environment Variable:
      ```bash
         export GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/key-file.json
      ```  
   *  Run gcloud auth activate-service-account Command:  
      ```bash
         gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS
      ```  
   * Verify Authentication:  
     You can verify that you are authenticated by running a command like `gcloud auth list` or `gcloud projects list`. This will show the authenticated account and the available projects.


## Setup DBT project as sub-folder  
The steps [Build Mage Image](#build-mage-image), and [Run Mage as Container](#run-mage-as-container) installs dbt-core and dbt bigquery connectors in the Mage-ai container.  
To setup the dbt project, below two docs links helps  
  *  [Add an existing dbt project to Mage](https://docs.mage.ai/dbt/add-existing-dbt)
  *  [DBT Core Setup](https://docs.getdbt.com/docs/core/about-core-setup)  

Steps to create DBT project `reddit_dbt`:
1. cd to `magic-de-reddit-reports/dbt/`
2. Run cmd `dbt init` to initialize a new dbt project and answer following questions:  
    *  Enter a name for your project (letters, digits, underscore): <**dbt project name**> 
    *  Which database would you like to use? <# **corresponding bigquery**>  
    *  Desired authentication method option (enter a number): <*select 2* for **service account**>
    *  keyfile (/path/to/bigquery/keyfile.json): <**path to [/keys/keyfile.json](#add-service-account-keyfile)**>  
    *  project (GCP project id): <**GCP project-id** >  
    *  dataset (the name of your dbt dataset): <**BigQuery dataset-name**>
    *  threads (1 or more): <**4**>
    *  ob_execution_timeout_seconds [300]: <*Leave blank for default*>  
    *  Desired location option (enter a number): <*Select the number corresponding to your geo-location,* **US** *in this case*>
   ![dbt_init](./README_resources/project_setup_images/dbt_init.PNG)  
3. Step 2 makes Profile **reddit_dbt** written to **/home/src/magic-de-reddit-reports/dbt/profiles.yml** using target's profile_template.yml and your supplied values. 
4. As per Mage-ai docs for [existing dbt projects](https://docs.mage.ai/dbt/add-existing-dbt), copy the profiles.yml code from step 3 and paste into the root of the reddit_dbt project as file **/dbt/reddit_dbt/profiles.yml**.  
5. Run 'dbt debug' to validate the connection.  
   ![dbt_debug](./README_resources/project_setup_images/dbt_debug.PNG)  




## Go back   
[Go back](./vm_setup.md)

### Go to Project Readme  
[GO to Readme Page](./README.md)