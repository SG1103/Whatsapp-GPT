from twilio.rest import Client
from Hub import hubmain
import openai
import requests
from flask import Flask, request
import threading
import json
import pydub
import os

# OpenAI Key
API_KEY = hubmain.OAI
# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001
MODEL = 'text-davinci-003'
# Telegram  bot token
BOT_TOKEN = hubmain.TG2
# Elevenlabs Key
eleven_lab_key = hubmain.EL
# Defining the bot's personality
# BOT_PERSONALITY = ''

account_sid = 'AC735c71e77aebdf6f8740e7f335e5f327'
auth_token = '3e7b542ff7bf6312e69ce54639783ba4'
client = Client(account_sid, auth_token)


openai.api_key = API_KEY

def openAIGPT(user_input):

    response = openai.ChatCompletion.create(

        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Who won the world series in 2020?"},
            {"role": "assistant", "content": "The Los Angeles Dodgers won the World Series in 2020."},
            {"role": "user", "content": user_input}
        ]
    )

    final_result = response['choices'][0]['message']['content']

    return final_result



def openAIvoice(prompt):

    transcript = openai.Audio.transcribe("whisper-1", prompt)

    return transcript["text"]

url = 'https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM'

headers = {
    'accept': 'audio/mpeg',
    'xi-api-key': eleven_lab_key,
    'Content-Type': 'application/json'
}

data = {
    "text": "string",
    "voice_settings": {
        "stability": 0,
        "similarity_boost": 0
    }
}

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    with open('audio.mp3', 'wb') as f:
        f.write(response.content)
else:
    print('Error:', response.text)


def whatsapp_sendtext(bot_message, number):

    message = client.messages.create(
        from_='whatsapp:+447723478623',
        body=bot_message,
        to= number
    )
message = client.messages.create(
    from_='whatsapp:+447723478623',
    media_url=['https://server6.mp3quran.net/thubti/112.mp3'],
    to='whatsapp:+447915897908'
)

print(1)

number = 'whatsapp:+447915897908')