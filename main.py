import requests, os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from query import query
import openai


load_dotenv()
app = FastAPI()
allowed_origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def generate_prompt(user_prompt):
    return """You are a creative and witty wordsmith well known for your ability to coin novel, humorous new names.
    Please generate a list of 5 Ethereum .ens names {}.
    Avoid use of controversial concepts relating to religion, profanity, sex or violence.""".format(user_prompt)



@app.get("/")
def read_root():
    return {"Welcome to the SPACE ID GIFTS AI API"}



@app.get("/fetch-dids/{user_info}")
async def fetch_recommended_DIDs(user_info: str):

    cleaned_info = user_info.strip()

    openai.api_key = os.getenv("OPENAI_API_KEY")

    response = openai.Completion.create(
        model="gpt-3.5-turbo-instruct",
        prompt=generate_prompt(cleaned_info),
        temperature=1.1,
        max_tokens=120
    )

    result = response.choices[0].text
    token_stats = response.usage

    raw_names = result.split("\n")
    names = []

    for name in raw_names:
        if name:
            if name[-3:] == "ENS": name = name[:-3]
            names.append(name.split(".")[1].strip().replace('"', ''))

    print(names)
    print(token_stats)

    final = []
    url = "https://graphigo.prd.space.id/query"

    for name in names:

        curr = {}

        # Variables for the GraphQL query
        variables = {
            "input": {
                "query": name,
                "buyNow": 1,
                "domainStatuses": ["REGISTERED", "UNREGISTERED"],
                "first": 30
            }
        }

        # Send POST request to the API endpoint with the GraphQL query and variables
        response = requests.post(url, json={"query": query, "variables": variables})
        space_id_response = None

        if response.status_code == 200:
            data = response.json()
            space_id_response = data["data"]["domains"]["exactMatch"]
        else:
            print(f"Error: Unable to fetch data from the API. Status code: {response.status_code}")
            print(response)

        links = []
        prices = []

        if not space_id_response:
            print("spaceID no response, exiting program")
            exit()

        for id in space_id_response:
            links.append(f"https://space.id/name/{str(id['tld']['tldID'])}/" + str(
                id["tokenId"] + "?name=" + str(id["name"] + "&tldName=" + str(id['tld']['tldName']))))
            prices.append(id["listPrice"])

        curr["name"] = name
        curr["links"] = links
        curr["prices"] = prices
        final.append(curr)

    print(final)
    return final

