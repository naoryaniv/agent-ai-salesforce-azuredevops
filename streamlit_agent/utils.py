import requests
import base64
import json
from bs4 import BeautifulSoup


# Converts texts from HTML to readable text content. Based on the library beautifulsoup4
def extract_plain_text(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n").strip()

# Get prompt text
def prompt_text(file_name):
    with open(file_name, 'r', encoding='utf-8') as file:
        content = file.read()

    return content


# Get all projects from Azure Devops (TFS)
def get_projects(organization, personal_access_token):
    url = f'http://tfs:8080/tfs/{organization}/_apis/projects?api-version=6.1-preview.2'

    authorization = str(base64.b64encode(bytes(':'+personal_access_token, 'ascii')), 'ascii')

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic '+authorization
    }

    response = requests.get(url, headers=headers).json()

    pull_projects_list = response["value"]

    projects_list =[]

    for project in pull_projects_list:
        projects_list.append(project["name"])

    return projects_list

# Get all work_items of some type based on the selected project
def get_work_items_by_type(organization, project, personal_access_token, work_item_type, area_path):
    # Authorization Header
    authorization = base64.b64encode(f":{personal_access_token}".encode("ascii")).decode("ascii")
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": "Basic " + authorization
    }

    # Query with filtering by 'Area Path'
    wiql_url = f"http://tfs:8080/tfs/{organization}/{project}/_apis/wit/wiql?api-version=6.1-preview.2"
    wiql_query = {
        "query": f"""
        SELECT [System.Id], [System.Title], [System.Description]
        FROM WorkItems
        WHERE [System.WorkItemType] = '{work_item_type}'
        AND [System.AreaPath] UNDER '{area_path}'
        """
    }

    response = requests.post(wiql_url, headers=headers, json=wiql_query)
    response.raise_for_status()
    result = response.json()

    ids = [item["id"] for item in result.get("workItems", [])]
    if not ids:
        return []

    ids_str = ",".join(map(str, ids))
    details_url = f"http://tfs:8080/tfs/{organization}/_apis/wit/workitems?ids={ids_str}&api-version=6.1-preview.2"
    response = requests.get(details_url, headers=headers)
    response.raise_for_status()

    items = response.json().get("value", [])

    features_list = []
    for item in items:
        features_list.append({
            "id": item["id"],
            "title": item["fields"].get("System.Title", ""),
            "description": item["fields"].get("System.Description", "")
        })

    return features_list

# Sending a request to openai to create tasks
def request_to_openai(client, prompt, feature_description, model, temperature):
    response = client.chat.completions.create( 
            model = model,
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": feature_description}
            ],
            temperature = temperature
            #max_tokens = max_tokens
        )

    tasks = response.choices[0].message.content
    tasks = json.loads(tasks) 


    return tasks



def create_work_items_in_tfs(organization, selected_project, personal_access_token, work_item_type, **kwargs):
    work_items = kwargs.get('work_items')
    feature_id = kwargs.get('feature_id')

    url = f'http://tfs:8080/tfs/{organization}/{selected_project}/_apis/wit/workitems/${work_item_type}?api-version=6.1-preview.2'

    authorization = str(base64.b64encode(bytes(':'+personal_access_token, 'ascii')), 'ascii')

    headers = {
        'Content-Type': 'application/json-patch+json',
        'Authorization': 'Basic ' + authorization
    }

    for work_item in work_items:
        work_item_data = [
            {
                "op": "add",
                "path": "/fields/System.Title",
                "from": None,
                "value": work_item["title"]
            },
            {
                "op": "add",
                "path": "/fields/System.Description",
                "from": None,
                "value": work_item["description"]
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Scheduling.Effort",
                "from": None,
                "value": work_item["effort"]
            },
            {
                "op": "add",
                "path": "/fields/Microsoft.VSTS.Common.Priority",
                "from": None,
                "value": work_item["priority"]
            }]
        
        
        if work_item_type == 'Feature':
            
            work_item_data.append(
                {
                    "op": "add",
                    "path": "/fields/System.AreaPath",
                    "value": f"{selected_project}"
                })


        if work_item_type == 'Product Backlog Item':
            work_item_data.append(
            {
                "op": "add",
                "path": "/relations/-",
                "value": {
                    "rel": "System.LinkTypes.Hierarchy-Reverse",
                    "url": f"http://tfs:8080/tfs/{organization}/{selected_project}/_apis/wit/workitems/{feature_id}",
                    "attributes": {
                        "comment": "This task was created using AI"
                    }
                }
            })


        response = requests.post(url, headers=headers, data=json.dumps(work_item_data))

        if response.status_code == 200 or response.status_code == 201:
            print("The backlog created successfully")
            print(response.json()["id"])
        else:
            print("Error occure while create backlog")
            print(response.status_code, response.text)


def get_project_teams(organization, personal_access_token, selected_project):
    url = f'http://tfs:8080/tfs/{organization}/_apis/projects/{selected_project}/teams?api-version=6.1-preview.2'

    authorization = str(base64.b64encode(bytes(':'+personal_access_token, 'ascii')), 'ascii')

    headers = {
        'Accept': 'application/json',
        'Authorization': 'Basic '+authorization
    }

    response = requests.get(url, headers=headers).json()

    teams_project_list = response["value"]

    teams =[]

    for team in teams_project_list:
        teams.append(team["name"])
    
    return teams

