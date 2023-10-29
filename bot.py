from Hub import hubmain
import requests
import json
import os
import threading
import openai
import re
import random
import memory
import asyncio
import curl



# OpenAI Key
API_KEY = hubmain.OAI
# Models: text-davinci-003,text-curie-001,text-babbage-001,text-ada-001
MODEL = 'text-davinci-003'
# Telegram  bot token
BOT_TOKEN = hubmain.TG
# Defining the bot's personality
#BOT_PERSONALITY = ''

chatbot_prompt = """
          As an advanced chatbot, your primary goal is to assist users to the best of your ability. This may involve answering questions, providing helpful information, or completing tasks based on user input. In order to effectively assist users, it is important to be detailed and thorough in your responses. Use examples and evidence to support your points and justify your recommendations or solutions.
          <conversation history>
          User: <user input>
          Chatbot:"""







# Functionto get response from OpenAI's chatbot
def openAI(, user_input):


    BOT_PERSONALITY = chatbot_prompt.replace(
        "<conversation history>", chatbot_prompt).replace("<user input>", user_input)

    prompt = BOT_PERSONALITY + user_input

    print(prompt)

    response = requests.post(
        'https://api.openai.com/v1/completions',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'model': MODEL, 'prompt': prompt, 'temperature': 0.4, 'max_tokens': 300}
    )

    result = response.json()
    final_result = ''.join(choice['text'] for choice in result['choices'])
    return final_result


def openAImage(prompt):

    resp = requests.post(
        'https://api.openai.com/v1/images/generations',
        headers={'Authorization': f'Bearer {API_KEY}'},
        json={'prompt': prompt, 'n': 1, 'size': '1024x1024'}
    )
    response_text = json.loads(resp.text)

    return response_text['data'][0]['url']


#Send message to a specific telegram group
def telegram_bot_sendtext(bot_message, chat_id, msg_id):

    data = {
        'chat_id': chat_id,
        'text': bot_message,
        'reply_to_message_id': msg_id
    }
    response = requests.post(
        'https://api.telegram.org/bot' + BOT_TOKEN + '/sendMessage',
        json=data
    )
    return response.json()


def telegram_bot_sendimage(image_url, group_id, msg_id):

    data = {
        'chat_id': group_id,
        'photo': image_url,
        'reply_to_message_id': msg_id
    }
    url = 'https://api.telegram.org/bot' + BOT_TOKEN + '/sendPhoto'

    response = requests.post(url, data=data)
    return response.json()


# 4. Function that retrieves the latest requests from users in a Telegram group,
# generates a response using OpenAI, and sends the response back to the group.

conversation_history = ""


def Chatbot():

    global conversation_history

    # Retrieve last ID message from text file
    cwd = os.getcwd()
    filename = cwd + '/chatgpt.txt'
    if not os.path.exists(filename):
        with open(filename, "w") as f:
            f.write("1")


    with open(filename) as f:
        last_update = f.read()

    # Check for new messages in Telegram
    url = f'https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update}'
    response = requests.get(url)
    data = json.loads(response.content)

    for result in data['result']:
        try:
            # Checking for new message
            if float(result['update_id']) > float(last_update):
                # Checking for new messages that did not come from chatGPT
                if not result['message']['from']['is_bot']:
                    last_update = str(int(result['update_id']))

                    # Retrieving message ID of the sender of the request
                    msg_id = str(int(result['message']['message_id']))

                    # Retrieving the chat ID
                    chat_id = str(result['message']['chat']['id'])

                    # Checking if user wants an image
                    if 'Image of' in result['message']['text']:
                        prompt = result['message']['text'].replace("Image of", "")
                        bot_response = openAImage(prompt)
                        print(telegram_bot_sendimage(bot_response, chat_id, msg_id))
                    # Checking that user mentionned chatbot's username in message
                    if '' in result['message']['text']:
                        uinput = result['message']['text'].replace("", "")
                        # Calling OpenAI API using the bot's personality
                        bot_response = openAI(conversation_history, uinput)
                        # Sending back response to telegram group
                        print(telegram_bot_sendtext(bot_response, chat_id, msg_id))
                        conversation_history += f"User: {uinput}\nChatbot: {bot_response}\n"
                    # Verifying that the user is responding to the ChatGPT bot
                    if 'reply_to_message' in result['message']:
                        if result['message']['reply_to_message']['from']['is_bot']:
                            prompt = result['message']['text']
                            bot_response = openAI(f"{conversation_history}{prompt}")
                            print(telegram_bot_sendtext(bot_response, chat_id, msg_id))
        except Exception as e:
            print(e)

    # Updating file with last update ID
    with open(filename, 'w') as f:
        f.write(last_update)

    return "done"


# 5 Running a check every 5 seconds to check for new messages
def main():
    timertime = 5
    Chatbot()
    # 5 sec timer
    threading.Timer(timertime, main).start()


# Run the main function
if __name__ == "__main__":
    main()