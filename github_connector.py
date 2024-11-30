import os
import requests


def fetch_github_contributions(user_name):
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_GARDEN_AUTH')}"
    }
    query = """
    query($userName:String!) {
      user(login: $userName){
        contributionsCollection {
          contributionCalendar {
            totalContributions
            weeks {
              contributionDays {
                contributionCount
                date
              }
            }
          }
        }
      }
    }
    """
    variables = {
        "userName": user_name
    }
    response = requests.post(url, json={'query': query, 'variables': variables}, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.text}")


def get_github_user_name():
    url = "https://api.github.com/graphql"
    headers = {
        "Authorization": f"Bearer {os.getenv('GITHUB_GARDEN_AUTH')}"
    }
    query = """
    query {
      viewer {
        login
      }
    }
    """
    response = requests.post(url, json={'query': query}, headers=headers)
    if response.status_code == 200:
        return response.json()['data']['viewer']['login']
    else:
        raise Exception(f"Query failed to run by returning code of {response.status_code}. {response.text}")


def get_github_contributions():
    user_name = get_github_user_name()
    response = fetch_github_contributions(user_name)
    return response

