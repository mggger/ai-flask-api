

import requests

import base64


# with open("mydata.jsonl", 'rb') as f:
#     content = f.read()
#     encoded_content = base64.b64encode(content)
#
#
# data = {
#     "content": encoded_content,
#     "n_epochs": 2
# }
# r = requests.post("http://localhost:5000/fine_tuning", json=data)
# print(r.text)



import sys


# data = {
#     "question": "《深圳市住房公积金贷款管理规定》的链接是？"
# }
# r = requests.post("http://52.77.238.141:5000/chat", json=data)
# answer = r.json()['answer']
# print(answer)


#print(r.text.decode("utf-8"))



# with open("/Users/home/Downloads/test.docx", 'rb') as f:
#     content = f.read()
#     encoded_content = base64.b64encode(content)
#
#
data = {
    "text": "1+1=2",
    "model_id": "text-embedding-ada-002"
}
r = requests.post("http://52.77.238.141:5000/embeddings/train", json=data)
print(r.text)