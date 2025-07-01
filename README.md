#  Tasks Builder – AI-Powered Feature for Azure Devops

Agent AI Salesforce is an intelligent assistant for automatically breaking down high-level features into actionable tasks in Azure DevOps (TFS). It leverages OpenAI's GPT models and integrates directly with your existing Azure Devops environment to streamline workflows for both technical and business teams.

![TFS App](https://github.com/user-attachments/assets/2d824011-0cd2-4895-9b1f-47bc7c02730a)
---

## Features

* **Create feature**: Create feature based on title, description and more fields.
* **Create tasks from features**: Automatically split a feature into sub-tasks based on its description.
* **Task generation & linking**: Create `Work Item` tasks in Azure Devops and link them to their originating feature.
* **Multilingual support**: Dual-language interface with full support for Hebrew (RTL).
* **Visual UI**: Modern Streamlit-based interface with background and styling support.

---

##  Installation

1. Clone the repository:

git clone https://github.com/naoryaniv/agent-ai-salesforce-azuredevops.git
cd agent-ai-salesforce-azuredevops


2. Install the requirements:

pip install -r requirements.txt


3. Configure your credentials and settings in `.env` file (Azure Devops + OpenAI).

---

##  Tools

* **Streamlit** – Interactive front-end framework.
* **OpenAI API** – Smart task generation via GPT.
* **Azure Devops REST API** – Read/write access to Azure DevOps work items.

---

##  Setup

### Authentication - usage custom variables

Remove the word example from the .env.example file and fill the following values are set:

* PERSONAL_ACCESS_TOKEN: A personal access token generated from your Azure DevOps account is required.
* OPENAI_API_KEY: generate key from OpenAI, Please note! Tokens are required.
* Optional proxy support via the `OPENAI_PROXY_URL` variable
---

Run the script using the following command:
streamlit run app.py

> **Note**: The app can run locally or on an internal server. Make sure your network allows access to Azure Devops.

---

##  Example Usage

### Managing Custom Tasks

* Select a project from the dropdown
* Choose an existing feature
* The feature description is sent to Ai agent
* Tasks are generated with ai agent and created in Azure Devops with fields and parent linkage

### Creating new feature

* Go to 'Create Feature' in the navigation menu
* Select a project
* Fill in the required fields
* Click Create
* The feature will be created in the selected project


### Managing AI Flow

* Uses a pre-defined prompt in `prompt.txt`
* Input: Feature description → Output: structured task list in JSON

---

##  Development

### Building from source

* Core logic resides in `app.py` and `utils.py`
* Language files available under `languages/`
* Easily extendable for additional languages or configurations

---

##  License

MIT License.

---

##  Issues and Support

If you encounter issues or want to contribute, please open an Issue or Pull Request on:
[GitHub repository](https://github.com/naoryaniv/agent-ai-salesforce-azuredevops/issues)
