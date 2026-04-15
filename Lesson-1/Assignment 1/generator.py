import requests

url = "http://localhost:11434/api/generate"

def ask_model(prompt):
    data = {
        "model":"mistral",
        "prompt":prompt,
        "stream":False
    }

    res = requests.post(url,json=data)
    return res.json()["response"]

print(ask_model("Write a Terraform script to deploy an AWS EC2 instance and an S3 bucket, ensuring the S3 bucket has versioning enabled and is private."))