#emailed: acechazegaming@gmail.com
# password: Confluent@123

import os
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

@app.route('/')
def home():
    return '<h2>Welcome to the GitHub OAuth App</h2><a href="/login/github">Login with GitHub</a>'

@app.route("/login/github")
def login_github():
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={CLIENT_ID}&scope=user,repo"
    )
    return redirect(github_auth_url)

@app.route("/callback")
def github_callback():
    code = request.args.get("code")

    # Exchange code for access token
    token_res = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "code": code,
        },
    )
    access_token = token_res.json().get("access_token")

    headers = {"Authorization": f"token {access_token}"}

    # Fetch user profile
    user_res = requests.get("https://api.github.com/user", headers=headers)
    user_data = user_res.json()
    username = user_data.get("login")

    # Fetch user repos
    repos_res = requests.get("https://api.github.com/user/repos", headers=headers)
    repos = repos_res.json()

    # Summarize projects
    summarized_repos = []
    languages = set()
    most_starred = {"name": None, "stars": -1}

    for repo in repos:
        languages.add(repo.get("language"))
        stars = repo.get("stargazers_count", 0)
        if stars > most_starred["stars"]:
            most_starred = {"name": repo.get("name"), "stars": stars}

        summarized_repos.append({
            "name": repo.get("name"),
            "description": repo.get("description"),
            "stars": stars,
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language"),
        })

    # Fetch README.md from user's profile repo (username/username)
    readme_text = ""
    readme_url = f"https://api.github.com/repos/{username}/{username}/readme"
    readme_res = requests.get(readme_url, headers=headers)

    if readme_res.status_code == 200:
        readme_data = readme_res.json()
        encoded_content = readme_data.get("content")
        if encoded_content:
            import base64
            readme_text = base64.b64decode(encoded_content).decode("utf-8")

    response = {
        "profile": {
            "login": user_data.get("login"),
            "name": user_data.get("name"),
            "avatar_url": user_data.get("avatar_url"),
            "bio": user_data.get("bio"),
            "public_repos": user_data.get("public_repos"),
        },
        "summary": {
            "total_projects": len(repos),
            "top_languages": list(filter(None, languages)),
            "most_starred": most_starred,
        },
        "repos": summarized_repos,
        "profile_readme": readme_text  # <-- Add README content here
    }

    return jsonify(response)


#@app.route("/callback")
# def github_callback():
#     code = request.args.get("code")

#     # Exchange code for access token
#     token_res = requests.post(
#         "https://github.com/login/oauth/access_token",
#         headers={"Accept": "application/json"},
#         data={
#             "client_id": CLIENT_ID,
#             "client_secret": CLIENT_SECRET,
#             "code": code,
#         },
#     )
#     access_token = token_res.json().get("access_token")

#     # Fetch user profile
#     user_res = requests.get(
#         "https://api.github.com/user",
#         headers={"Authorization": f"token {access_token}"},
#     )
#     user_data = user_res.json()

#     # Fetch user repos
#     repos_res = requests.get(
#         "https://api.github.com/user/repos",
#         headers={"Authorization": f"token {access_token}"},
#     )
#     repos = repos_res.json()

#     # Summarize projects
#     summarized_repos = []
#     languages = set()
#     most_starred = {"name": None, "stars": -1}

#     for repo in repos:
#         languages.add(repo.get("language"))
#         stars = repo.get("stargazers_count", 0)
#         if stars > most_starred["stars"]:
#             most_starred = {"name": repo.get("name"), "stars": stars}

#         summarized_repos.append({
#             "name": repo.get("name"),
#             "description": repo.get("description"),
#             "stars": stars,
#             "forks": repo.get("forks_count", 0),
#             "language": repo.get("language"),
#         })

#     response = {
#         "profile": {
#             "login": user_data.get("login"),
#             "name": user_data.get("name"),
#             "avatar_url": user_data.get("avatar_url"),
#             "bio": user_data.get("bio"),
#             "public_repos": user_data.get("public_repos"),
#         },
#         "summary": {
#             "total_projects": len(repos),
#             "top_languages": list(filter(None, languages)),
#             "most_starred": most_starred,
#         },
#         "repos": summarized_repos,
#     }

#     return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)

