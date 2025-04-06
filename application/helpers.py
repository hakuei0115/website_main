import requests
import json
import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from config import TEXT_PATH


def is_active(current_path:str, nav_path:str) -> str:
    """Returns a string that shows which page is active in the navigation menu."""

    if current_path == nav_path:
        return "is-active"
    
    return ""


def get_skills(file_path:str) -> tuple:
    """Returns three lists one for each type of cards in the JSON file."""

    try:
        with open(file_path) as file:
            data = json.load(file)
    except FileNotFoundError:
        print(f"ERROR! File could not be found for path: {file_path}.")
    except json.JSONDecodeError as error:
        print(f"ERROR! {error}.")
    except Exception as error:
        print(f"ERROR! {error}.")

    # Storing the information based on the type of card
    languages = [card for card in data["cards"] if card["type"] == "language"]
    frameworks = [card for card in data["cards"] if card["type"] in ["library", "framework"]]
    technologies = [card for card in data["cards"] if card["type"] == "technology"]

    return languages, frameworks, technologies


def get_repositories() -> list:
    """Returns a list of dictionaries which contains information about each public repository on my GitHub profile."""

    github_token = os.environ["GITHUB_ACCESS"]
    url = "https://api.github.com/users/hakuei0115/repos"
    params = {"per_page": 1000}
    headers = {"Authorization": f"token {github_token}"}

    try:
        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:
            data = json.loads(response.text)

            repo_list = []

            # Iterate through each repository and add the information needed to the list
            for repo in data:
                # Retrieve information only for non-forked repositories
                if not repo["fork"]:
                    # Check for the README repository so it won't be included
                    if "BogdanOtava" not in repo["name"]:
                        repo_info = {}
                        repo_info["name"] = repo["name"]
                        repo_info["description"] = repo["description"]
                        repo_info["url"] = repo["html_url"]

                        # Get all languages used in the repository
                        languages = repo["languages_url"]
                        languages_response = requests.get(languages)
                        languages_data = languages_response.json()
                        sorted_languages = sorted(languages_data.items(), key=lambda x: x[1], reverse=True)

                        # Get top three most used languages in repository
                        top_languages = [lang[0] for lang in sorted_languages[:3]]
                        repo_info["languages"] = top_languages

                        # Add the repository dictionary to the list of repositories
                        repo_list.append(repo_info)

            return repo_list
        else:
            print(f"ERROR! {response.status_code} - {response.reason}.")
    except requests.exceptions.Timeout:
        print("Request timed out.")
    except requests.exceptions.TooManyRedirects:
        print("Too many redirects.")
    except requests.exceptions.RequestException as error:
        print(f"ERROR! {error}.")


def get_language_image(language:str) -> str:
    """Returns the image of a programming language from 'skills.json'."""

    try:
        with open(f"{TEXT_PATH}/skills.json") as file:
            data = json.load(file)
    except FileNotFoundError as error:
        print(f"ERROR! {error}.")
    else:
        for card in data.get("cards", []):
            if card.get("type") == "language" and card.get("title", "").lower() == language.lower():
                return card.get("image")
            
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_text(prompt: str) -> str:
    try:
        messages: list[ChatCompletionMessageParam] = [
            {
                "role": "system",
                "content": (
                    "你是一位有趣又資深的全端工程師，擅長用淺顯易懂的方式教初學者前後端技術，"
                    "請用繁體中文回答使用者的問題。"
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ]

        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini-2024-07-18"),
            messages=messages,
            temperature=0.7,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"OpenAI Error: {e}")
        return "系統錯誤，請稍後再試～"