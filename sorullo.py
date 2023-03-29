import os
import discord
import openai

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.messages = True

class ChatBot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        print(f'{message.author} said {message.content} in {message.channel} at {message.created_at}')
        
        input_content= message.content # change to [message.content] when gpt-4 API is available
        
        # Enable this when gpt-4 API is available
        # if message.attachments:
        #     for attachment in message.attachments:
        #         image_bytes = await attachment.read()
        #         input_content.append({"image": image_bytes})
                
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", # change to "gpt-4" when available
            messages=[{"role": "user", "content": input_content}]
        )
        
        assistant_response = response['choices'][0]['message']['content']
        await message.channel.send(assistant_response)

client = ChatBot(intents=intents)
client.run(DISCORD_TOKEN)