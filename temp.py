from ibm_watsonx_ai import APIClient
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

credentials = Credentials(
    url = "https://us-south.ml.cloud.ibm.com",
    api_key = "mR2ik9iLFnRLY2LLDoJpdmbj3W9l3sNqaQtdbWEKkyex"
)

client = APIClient(credentials)

params = {
    "time_limit": 10000,
    "max_new_token": 100
}

model_id = "meta-llama/llama-3-8b-instruct"
project_id = "8c4cdab3-8dad-4aa3-aa2f-bb056d48e036"
space_id = None # optional
verify = False

model = ModelInference(
  model_id=model_id,
  api_client=client,
  params=params,
  project_id=project_id,
  space_id=space_id,
  verify=verify,
)

messages = [
  {
    "role": "system",
    "content": "You are a helpful assistant."
  },
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "How far is Paris from Bangalore?"
      }
    ]
  },
  {
    "role": "assistant",
    "content": "The distance between Paris, France, and Bangalore, India, is approximately 7,800 kilometers (4,850 miles)"
  },
  {
    "role": "user",
    "content": [
      {
        "type": "text",
        "text": "What is the flight distance?"
      }
    ]
  }
]

print(model.chat(messages=messages))