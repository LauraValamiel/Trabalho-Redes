
import http.client

import json

conn = http.client.HTTPSConnection("chatgpt-42.p.rapidapi.com")

payload = json.dumps({
    "messages": [{
            "role": "user",
            "content": "Quando aconteceu a segunda guerra mundial?"
        }],
    "system_prompt": "Responda de forma breve, direta e completa, sem adicionar detalhes desnecessários.",
    "temperature": 0.4,
    "top_k": 50,
    "top_p": 0.6,
    "max_tokens": 100,
    "web_access": True
})

headers = {
    'x-rapidapi-key': "e4d17f4bb2msha2c77db24214d13p176ceejsnf53f781b2d35",
    'x-rapidapi-host': "chatgpt-42.p.rapidapi.com",
    'Content-Type': "application/json"
}

conn.request("POST", "/conversationgpt4-2", payload, headers)

resposta = conn.getresponse()

data = resposta.read()

print(data.decode("utf-8"))
