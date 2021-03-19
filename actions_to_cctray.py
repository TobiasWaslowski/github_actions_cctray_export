import requests
import json
import os
import sys
from xml.etree.ElementTree import Element, SubElement, tostring

GITHUB_PERSONAL_TOKEN = os.environ['GITHUB_TOKEN']
TEAM = os.environ['GITHUB_TEAM']
ORGANISATION = os.environ['GITHUB_ORGANISATION']
API_BASE = "https://api.github.com"

authorization_header = {
    'Authorization': 'Bearer ' + GITHUB_PERSONAL_TOKEN
}

cctray_attributes = {
    'name': '',
    'lastBuildStatus': '',  # conclusion
    'lastBuildTime': '',  # created_at
    'activity': '',  # Sleeping <=> Completed?
    'webUrl': '',  # html_url
    'lastBuildLabel': ''  # head_sha, 7 digits
}

# You're gonna encounter this cctray_data_struct throughout the code.
# Basically, this data structure aggregates data from multiple calls to the Github API.
# Because we first have to get the repository names, then get the corresponding workflows,
# then the most recent workflow runs and then the jobs corresponding with those runs,
# it's kind of hard to implement a sensible data structure to collect all these data points, but
# I did my best. Just refer back to this whenever you get confused in the code. :)

"""
cctray_data_struct =
[
# repo
    {
        'name': '',
        'workflows': [
            {
                'workflow_id': '',
                'most_recent_run_id': ''
            }
        ]
    }
]
"""


# Directly parses the JSON response of any call to the Github API
def get_json_response_from_endpoint(endpoint):
    url = API_BASE + endpoint
    print("Requesting url: {}".format(url), file=sys.stderr)
    response = requests.get(url, headers=authorization_header)
    response_string = response.content.decode('utf-8')
    response_json = json.loads(response_string)
    return response_json


# Extracts repository names from a JSON array of respositories
def get_repo_names():
    response_json = get_json_response_from_endpoint(f"/orgs/{ORGANISATION}/teams/{TEAM}/repos")
    repo_name_list = []
    for repo in response_json:
        repo_name_list.append(repo['name'])
    return repo_name_list


# Initializes the data structure aggregating the data required for the cctray.xml
def initialize_cctray_data_struct_with_names(repository_names):
    cctray_data_struct = []
    for name in repository_names:
        cctray_data_struct.append({
            'name': name,
            'workflows': []
        })
    return cctray_data_struct


# Gets all workflows of a single repository
def get_repo_workflows(repo_name):
    response = get_json_response_from_endpoint(f"/repos/{ORGANISATION}/{repo_name}/actions/workflows")
    return response['workflows']


# Gets all workflows belonging to each repository and appends them to the cctray_data_struct
def append_workflow_data_to_cctray_data_struct(cctray_data_struct):
    for repo in cctray_data_struct:
        workflows = get_repo_workflows(repo['name'])
        for workflow in workflows:
            repo['workflows'].append({
                    'workflow_id': workflow['id'],
                    'most_recent_run_id': ''
                })
    return cctray_data_struct


# This function mutates the passed data structure. It takes a map <name, list<workflow_ids>> and maps it to
# <name, list<map<workflow_id, most_recent_run_id>>>
def append_most_recent_workflow_runs_to_cctray_data_struct(cctray_data_struct):
    for repo_entry in cctray_data_struct:
        for workflow in repo_entry['workflows']:
            most_recent_run_id = get_most_recent_workflow_run_id(repo_entry, workflow)
            workflow['most_recent_run_id'] = most_recent_run_id
    return cctray_data_struct


def get_most_recent_workflow_run_id(repo_entry, workflow):
    response = get_json_response_from_endpoint(
        f"/repos/{ORGANISATION}/{repo_entry['name']}/actions/workflows/{workflow['workflow_id']}/runs?page=1&per_page=1")
    return response['workflow_runs'][0]['id']


# The cctray data struct doesn't need all the data about the jobs that the Github API provides, so this function
# helps filter out all the unnecessary information.
def get_relevant_job_data_associated_with_run(run_id, repo_name):
    job_list = []
    jobs = get_jobs_associated_with_run(repo_name, run_id)
    for job in jobs:
        job_list.append({
            'name': job['name'],
            'lastBuildStatus': job['conclusion'],
            'lastBuildTime': job['started_at'],
            'activity': job['status'],
            'webUrl': job['html_url'],
            'lastBuildLabel': job['head_sha']
        })
    return job_list


def get_jobs_associated_with_run(repo_name, run_id):
    response = get_json_response_from_endpoint(f"/repos/{ORGANISATION}/{repo_name}/actions/runs/{run_id}/jobs")
    return response['jobs']


# Appends relevant data about the jobs associated with each most recent workflow run to the cctray data struct
def append_job_data_to_cctray_data_struct(cctray_data_struct):
    for repo in cctray_data_struct:
        for workflow in repo['workflows']:
            run_jobs = get_relevant_job_data_associated_with_run(workflow['most_recent_run_id'], repo['name'])
            workflow['jobs'] = run_jobs
    return cctray_data_struct


def turn_dict_into_cctray_xml(helper_struct):
    root = Element("Projects")
    for repo in helper_struct:
        for workflow in repo['workflows']:
            jobs = workflow['jobs']
            for job in jobs:
                project = SubElement(root, "Project", attrib=cctray_attributes)
                project.set('name', "{} :: {}".format(repo['name'], job['name']))
                project.set('lastBuildStatus', map_cctray_last_build_status_to_github_actions_status(job['lastBuildStatus']))
                project.set('lastBuildTime', job['lastBuildTime'])
                project.set('activity', map_cctray_activity_to_github_actions_activity(job['activity']))
                project.set('webUrl', job['webUrl'])
                project.set('lastBuildLabel', job['lastBuildLabel'][0:6])
    return root


def map_cctray_last_build_status_to_github_actions_status(job_status):
    if job_status == "success":
        return "Success"
    elif job_status == "failure":
        return "Failure"
    #elif job_status == "queued":
    #    return "Exception"
    else:
        return "Unknown"


def map_cctray_activity_to_github_actions_activity(job_activity):
    if job_activity == "completed":
        return "Sleeping"
    elif job_activity == "in_progress":
        return "Building"
    elif job_activity == "queued":
         return "CheckingModifications"
    else:
        return "Unknown"


def main():
    repo_name_list = get_repo_names()
    cctray_data_struct = initialize_cctray_data_struct_with_names(repo_name_list)
    cctray_data_struct_with_workflows = append_workflow_data_to_cctray_data_struct(cctray_data_struct)
    cctray_data_struct_with_most_recent_runs = append_most_recent_workflow_runs_to_cctray_data_struct(cctray_data_struct_with_workflows)
    complete_cctray_object = append_job_data_to_cctray_data_struct(cctray_data_struct_with_most_recent_runs)
    xml = turn_dict_into_cctray_xml(complete_cctray_object)

    print(tostring(xml).decode('utf-8'))


main()

