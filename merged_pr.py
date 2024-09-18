import os
import requests
import subprocess

token = os.getenv('GITHUB_TOKEN')
username = os.getenv('GITHUB_USERNAME')

url = f"https://api.github.com/search/issues?q=author:{username}+is:pr+is:merged"

headers = {
    'Authorization': f'token {token}'
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    repo_list = set()

    if len(data['items']) == 0:
        repo_list.add("No merged pull requests found.\n")
    else:
        for item in data['items']:
            repo_url = item['repository_url']
            repo_name = repo_url.replace('https://api.github.com/repos/', '')

            repo_response = requests.get(repo_url, headers=headers)
            if repo_response.status_code == 200:
                repo_data = repo_response.json()
                if repo_data['owner']['login'] != username:
                    repo_list.add(f"[{repo_name}](https://github.com/{repo_name})")
            else:
                print(f"Failed to fetch repository details: {repo_response.status_code}")

    readme_path = 'README.md'
    if not os.path.isfile(readme_path):
        print("README.md does not exist, creating a new one.")
        with open(readme_path, 'w') as file:
            file.write("")
    
    with open(readme_path, 'w') as file:
        file.write("")
    
    with open(readme_path, 'a') as file:
        file.write(f"\n\[ 👨‍💻 [Gist graveyard](https://gist.github.com/{username}/) | ⭐ [Given stars](https://github.com/{username}/stars?tab=readme-ov-file#awesome-stars-) \]\n\nI worked on the following projects:\n")

    sorted_repos = sorted(repo_list, key=lambda x: x.lower())
    with open(readme_path, 'a') as file:
        file.writelines([f"- {repo}\n" for repo in sorted_repos])

    subprocess.run(["git", "config", "--global", "user.name", "github-actions[bot]"], check=True)
    subprocess.run(["git", "config", "--global", "user.email", "github-actions@github.com"], check=True)
  
    status_result = subprocess.run(["git", "status", "--porcelain"], stdout=subprocess.PIPE, text=True)
    if status_result.stdout:
        commit_result = subprocess.run(["git", "commit", "-am", "Update README.md with merged PRs"], text=True, capture_output=True)
        
        if commit_result.returncode == 0:
            subprocess.run(["git", "push"], check=True)
            print("Changes committed and pushed.")
        else:
            print(f"Failed to commit changes: {commit_result.stderr}")
    else:
        print("No changes to commit. Skipping commit.")
    
    print(f"Updated README.md with {len(sorted_repos)} unique repositories where PRs were merged.")
    exit(0)
else:
    print(f"Failed to fetch PRs: {response.status_code}")
    print(response.text)
    exit(1)
