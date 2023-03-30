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
  - !whoami                : Get more info about this bot,
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
async def whoami(ctx):
    embed = discord.Embed(
        title="Sorullo",
        description="Sorullo is a bot that uses GPT-4(not available yet!), GPT-3 and DALL-E to analyze and generate text and images.",
    )
    embed.set_image(url="https://i.scdn.co/image/ab6761610000e5eb281b74d7d806bf014a15fcad")
    embed.set_author(
        name="Raskitoma",
        url="https://raskitoma.com",
    )
    embed.set_footer(
        text="Sorullo Bot by Raskitoma, version 1.0a",
        icon_url="https://raskitoma.com/assets/media/rask-favicon.svg"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Biografía de cantante Johnny Ventura"},
        ]
    )
    full_response = f'''Hi, {ctx.author.mention} here are more details about me:
    
I'm a bot that uses GPT-4(not available yet!), GPT-3 and DALL-E to analyze and generate text and images.

I'm currently under development, so I'm not very smart yet, but I'm learning.
    
Here is more info about my name, based on a song called "Capullo y Sorullo" by Johnny Ventura:

{response['choices'][0]['message']['content']}
'''
    await ctx.send(full_response, embed=embed)


@client.command()
async def generate(ctx):
    message = ctx.message.content.replace(f'{COMMANDS_PREFIX}generate ', '')
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": message},
        ]
        
    )
    full_response = f"{ctx.author.mention} here is what I got:\n{response['choices'][0]['message']['content']}"
    await ctx.send(full_response)
        
@client.command()
async def pintame(ctx):
    prompt = ctx.message.content.replace(f'{COMMANDS_PREFIX}pintame ', '')
    response = openai.Image.create(
        prompt=prompt,
        n=2,
        size="1024x1024"
    )
    embed = discord.Embed()
    result = response["data"][0]["url"]
    embed.set_image(url=result)
    full_response = f"{ctx.author.mention} here is what I painted:"
    await ctx.send(full_response, embed=embed)
    
@client.command()
async def analyze(ctx):
    if GPT4AVAILABLE == "False":
        await ctx.send(f"I'm sorry {ctx.author.mention}, GPT-4 API is not available at the moment.")
        
    input_content= [ctx.message.content]
    
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            image_bytes = await attachment.read()
            input_content.append({"image": image_bytes})
            
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": input_content}]
    )
    
    assistant_response = response['choices'][0]['message']['content']
    await ctx.send(assistant_response)


client.run(DISCORD_TOKEN)

