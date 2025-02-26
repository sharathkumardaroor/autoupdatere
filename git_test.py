import os
import subprocess
import json

def git_commit_and_push(repo_path, commit_message, branch='main'):
    try:
        # Change to the repository directory
        os.chdir(repo_path)
        
        # Stage all changes
        subprocess.run(['git', 'add', '--all'], check=True)
        
        # Commit changes
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push to the origin
        subprocess.run(['git', 'push', 'origin', branch], check=True)
        
        print(f"Successfully pushed changes for repo: {repo_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error occurred for repo: {repo_path}\n{e}")

# Read the JSON file
with open('repos.json', 'r') as file:
    data = json.load(file)

repos = data["repos"]
commit_message = data["commit_message"]

# Loop through each repository and perform the Git operations
for repo_path in repos:
    git_commit_and_push(repo_path, commit_message)
