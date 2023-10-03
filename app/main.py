from typing import Optional

from fastapi import FastAPI, Body
from fastapi.middleware.cors import CORSMiddleware
app = FastAPI()

import pandas as pd
from neo4j import GraphDatabase
import json
driver = GraphDatabase.driver("neo4j://192.168.10.225:7687", auth=("neo4j", "test"))
session = driver.session()
from langchain.agents import create_pandas_dataframe_agent , create_csv_agent
from langchain.chat_models import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain.llms import OpenAI
import pandas as pd
api_key = "xxxx"
chat_model = ChatOpenAI(openai_api_key=api_key)


origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def prepAnswer(answer):
    arr = answer.split("\n")
    found_code = False;
    arr_code = []
    for i in arr:
        if i == "```cypher" or (i == "```" and found_code == False):
            print("I'm in",i)
            arr_code = [] #Reset arr_code use last code
            found_code = True
            print("f->t")
        elif found_code == True and i != "```":
            arr_code.append(i)
        elif i == "```" and found_code == True:
            print("t -> f")
            found_code = False
    if arr_code == []:
        return answer
    return "\n".join(arr_code[:])

def combinePrompt(question):
    prompt_template = open("./app/prompt_template.txt").read().format(question=question)
    return prompt_template

@app.post("/query")
async def query(question: str):
    prompt = combinePrompt(question)
    print("===prompt===")
    print(prompt)
    answer = chat_model.predict(prompt)
    print("===answer===")
    print(answer)
    code = prepAnswer(answer)
    print("===code===")
    print(code)
    return {"code": code}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
