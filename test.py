

import requests

import base64


# with open("mydata.jsonl", 'rb') as f:
#     content = f.read()
#     encoded_content = base64.b64encode(content)
#
#
# data = {
#     "content": encoded_content,
# }
# r = requests.post("http://localhost:5000/fine_tuning", json=data)
# print(r.text)


data = {
    "question": "1+1=?",
    "model_id": "ft:gpt-3.5-turbo-0613:personal::87ELReW7"
}
r = requests.post("http://127.0.0.1:5000/chat", json=data)
print(r.text)