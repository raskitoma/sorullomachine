import os
import discord
import openai
from discord.ext import commands

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GPT4AVAILABLE = os.getenv("GPT4AVAILABLE")
openai.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.messages = True

COMMANDS_PREFIX = "!"

class ChatBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                   
    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')
        
    async def on_message(self, message):
        if message.author == self.user:
            return
        if message.content.startswith(f'<@{self.user.id}> {COMMANDS_PREFIX}'):
            message.content = message.content.replace(f'<@{self.user.id}> {COMMANDS_PREFIX}', f'{COMMANDS_PREFIX}')
        print(f'{message.created_at} - Channel: {message.channel} | {message.author} said: {message.content}')
        await self.process_commands(message)
        

client = ChatBot(command_prefix=COMMANDS_PREFIX, intents=intents)

client.remove_command("help")

@client.group(invoke_without_command=True)
async def help(ctx):
    await ctx.send(f'''
    Hello {ctx.author.mention}, these are the commands:
    ```
  - !help                  : This message
  - !hello                 : Make Sorullo say hello to you,
  - !generate <text>       : Generate text with GPT-3,
  - !pintame <text>        : Generate an image with DALL-E,
  - !analyze <text> <image>: Analyze a message with GPT-4
                             (not available at the moment).
    ```
    ''')


@client.command()
async def hello(ctx):
    await ctx.send(f'Hello {ctx.author.mention}!: oye sorullo, el negrito es el único tuyo, https://youtu.be/H3JW7-fsHL8?t=136')

@client.command()
async def generate(ctx):
    message = ctx.message.content.replace(f'{COMMANDS_PREFIX}generate ', '')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message},
        ]
        
    )
    await ctx.send(response['choices'][0]['message']['content'])
        
@client.command()
async def pintame(ctx):
    prompt = ctx.message.content.replace(f'{COMMANDS_PREFIX}pintame ', '')
    response = openai.Image.create(
        prompt=prompt,
        n=2,
        size="1024x1024"
    )
    result = response["data"][0]["url"]
    await ctx.send(result)
    
@client.command()
async def analyze(ctx, *, message):
    if GPT4AVAILABLE == "False":
        await ctx.send("GPT-4 API is not available at the moment.")
        
    input_content= [message.content]
    
    if message.attachments:
        for attachment in message.attachments:
            image_bytes = await attachment.read()
            input_content.append({"image": image_bytes})
            
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": input_content}]
    )
    
    assistant_response = response['choices'][0]['message']['content']
    await ctx.send(assistant_response)


client.run(DISCORD_TOKEN)

