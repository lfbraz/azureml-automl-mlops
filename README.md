# Azure AutoML (Automated Machine Learning) integrated in a MLOps
Here we will demonstrate how to create a multi-stages MLOps integrated with an Azure AutoML experiment.

This tutorial was created for learning purposes, please feel free to adapt the code for your needs or to suggest modifications. 😃

---

### Prerequisites:

1. Have an Azure Subscription
2. Create an Azure Machine Learning Workspace
3. Create an Azure DevOps project
4. Install [Azure ML extension](https://marketplace.visualstudio.com/items?itemName=ms-air-aiagility.vss-services-azureml&targetId=09d19ee8-b94a-4f99-a763-11cc0fe1a111&utm_source=vstsproduct&utm_medium=ExtHubManageList) in your Azure DevOps organization (This extension will be used to connect Azure DevOps with Azure ML Workspace)
5. A service connection configured in your Azure DevOps project (see [How to set up your service connection](#how-to-set-up-your-service-connection))

### Configure your Azure DevOps Pipeline

#### How to set up your service connection

In your project click in *"Project settings -> Service Connections -> New service connection"*. Use *Azure Resource Manager* and *Service principal (automatic)* options and select your Azure Subscription and Machine Learning Workspace

![service connection](images/service-connection.PNG?raw=true)

#### Release Pipeline

With the service connection we are able to create a new [Release Pipeline](https://docs.microsoft.com/en-us/azure/devops/pipelines/release/?view=azure-devops) (in your *Azure Devops project*) to deploy Azure ML models:

![New Release Pipeline](images/new-release-pipeline.PNG?raw=true)

In our case we have an Azure DevOps project named **MLOps-LAB**, please feel free to use your own Azure DevOps project.

Now we will add the model artifacts. We will use two sources: A **Repository source** (can be *Azure DevOps Repos, Github*, etc.) and an **Azure ML Model Artifact** (the model you have registered in your Azure ML Workspace):

![Artifacts](images/artifacts.PNG?raw=true)

The **Repository source** will contain your deployment configs (`aciDeploymentConfig.yml` or `aksDeploymentConfig.yml`, `conda_env_v_1_0_0.yml`, `inferenceConfig.yml` and `score.py`). In this [folder](https://github.com/lfbraz/azure-mlops/tree/master/azureml/config) we have some examples of these files.  

In the **Azure ML Model Artifact** we will connect the Azure DevOps with our Azure ML Workspace using the `Service Connection` we created before:

![AzureML Artifact](images/add-azureml-artifact.jpg?raw=true)

Now with the artifacts configured we can add the stages of this Release Pipeline. In this example we will create two stages: **QA** (pre-production) and **Production**:

![Stages](images/stages.PNG?raw=true)

### QA (pre-production)

In this step we will get the artifact (model) to deploy an endpoint (api) based on it. We will create some *tasks* using `az-cli` with the [machine learning extension](https://docs.microsoft.com/en-us/azure/machine-learning/reference-azure-machine-learning-cli#:~:text=The%20Azure%20Machine%20Learning%20CLI%20is%20an%20extension,allows%20you%20to%20automate%20your%20machine%20learning%20activities.).

Three tasks will be used:

1. Install prereqs (To install azure-cli-ml): `az extension add -n azure-cli-ml`
2. Deploy Model to QA (To deploy the model artifact to QA Workspace): `az ml model deploy`
3. Check endpoint state (A loop to check if the endpoint is in "Healthy" state): `az ml endpoint realtime show`

These tasks will use [Azure DevOps variables](https://go.microsoft.com/fwlink/?linkid=865972) to be easy to replicate to others models as well. The `.yml` files of each task can be seen in this [folder](release-tasks/qa/) and they can be used to create a *Pipeline* or a *Release Pipeline* (in this case just create an **Azure Cli Task** associated with the QA stage and add the code in `inlineScript` section of each `.yml` file).

![Stages](images/tasks-qa-stage.PNG?raw=true)


### Pre-deployment approval

We can add a Pre-deployment condition to be able to request approval before deploying to **Production** stage. It is useful to validate the **QA** endpoint before putting it on **Production**.

Click on:
![Add Pre-Deployment condition](images/add-pre-deployment-condition.PNG?raw=true)

To open the options to define one (or many) approvers:

![Pre-Deployment condition config](images/pre-deployment-condition-config.PNG?raw=true)

### Production

After the approval condition, in this step we will download the model version from QA Workspace and deploy it to Prod Workspace. It will allow us to separe the environments and can be useful to use Workspaces for example separated in two different Resources Groups.

Five tasks will be used:

1. Install prereqs: `az extension add -n azure-cli-ml`
2. Download model from QA: `az ml model download`
3. Register model to PROD: `az ml model register`
4. Deploy model to PROD: `az ml model deploy`
5. Check endpoint state : `az ml endpoint realtime show`

All set up 😃. Now we can configure the trigger to this **Release**.

### Trigger

We can use a **Continuous deployment trigger** to create a new release every time a new AzureML model is registered: 

![Continuous deployment trigger](images/continuous-deployment.PNG?raw=true)

When a new version of the model is registered in the Azure ML Workspace a new Release will be trigger:

![New model](images/new-registered-model.PNG?raw=true)

![Release QA](images/release-qa.PNG?raw=true)

![Waiting for approval](images/waiting-for-approval.PNG?raw=true)

After the deployed succeded the approver will receive an email similar with this:

![Approval notification](images/approver-notification.PNG?raw=true)

![OK to production](images/approval-OK.PNG?raw=true)

After the approval, the next stage **(deploy to Production)** will be triggered:

![production](images/release-prod.PNG?raw=true)

When all the stages are completed we can see the **endpoints** in Azure ML Workspace:

![endpoints](images/ml-endpoints.PNG?raw=true)  
  
  
![complete](images/final-release.PNG?raw=true)

