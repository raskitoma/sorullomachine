from io import BytesIO
import os
from urllib.parse import urlparse
import discord
# import openai
from discord.ext import commands
from discord import File
import requests
import logging, coloredlogs
from PIL import Image
from openai import OpenAI

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL")
OPENAI_MODEL_IMG = os.getenv("OPENAI_MODEL_IMG")
aiClient = OpenAI()
aiClient.api_key = OPENAI_API_KEY

intents = discord.Intents.default()
intents.messages = True

COMMANDS_PREFIX = "!"
BTN_TIMEOUT = 120
VARIANTS_DEFAULT = 4
LABEL_VARIANT = "V"
LABEL_UPSCALE = "U"
DEFAULT_SCALE_FACTOR = 2
CONTEXT_SEPARATOR = "|"

# Helper functions
async def find_replies_to(ctx, user:discord.Member):
    bot_messages =[]
    async for message in ctx.channel.history(limit=1000):
        if message.author == client.user and len(message.mentions)>0:
            if message.mentions[0] == user:
                bot_messages.append(message)
    return bot_messages

async def find_last_image(bot_messages, user:discord.Member):
    for message in bot_messages:
        if message.content == f'{user.mention} here are the pictures that my ones and zeroes painted:':
            image_url = message.embeds[0].image.proxy_url
            break
    return get_image_from_url(image_url)

def upscale_image(my_image, scale_factor=1.5):

    img = Image.open(BytesIO(my_image))

    width, height = img.size
    new_width, new_height = width * scale_factor, height * scale_factor

    upscaled_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    return upscaled_img
    
def get_image_from_url(url):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        return response.content
    else:
        return None

def extract_domain(url):
    parsed_url = urlparse(url)
    domain = parsed_url.scheme + '://' + parsed_url.netloc
    return domain

def create_embed_image_objects(response):
    my_embeds = []
    for image in response:
        url = image.url
        embed = discord.Embed(url=extract_domain(url))
        embed.set_image(url=url)
        my_embeds.append(embed)
    return my_embeds

def create_buttons_variants(response):
    my_buttons = []
    for i, _ in enumerate(response):
        label = f'{LABEL_VARIANT}{i+1}'
        url = response[i].url
        button = VariantButton(label=label, custom_id=label, row=0, kurl=url)
        my_buttons.append(button)
    return my_buttons

def create_buttons_upscale(response):
    my_buttons = []
    for i, _ in enumerate(response):
        label = f'{LABEL_UPSCALE}{i+1}'
        url = response[i].url
        button = UpscaleButton(label=label, custom_id=label, row=1, kurl=url)
        my_buttons.append(button)
    return my_buttons

# extra classes
class ButtonView(discord.ui.View):
    def __init__(self, buttons):
        super().__init__()
        for button in buttons:
            self.add_item(button)
    
class VariantButton(discord.ui.Button):
    def __init__(self, label, custom_id, row, kurl):
        super().__init__(label=label, custom_id=custom_id, row=row)
        self.kurl = kurl

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def callback(self, interaction: discord.Interaction):
        await interaction.channel.typing()
        await interaction.response.defer()
        response = get_image_from_url(self.kurl)
        if response is None:
            await interaction.response.send_message(f"I'm sorry {interaction.user.mention}, I can't find any image to generate a variant.", reference=interaction.message.to_reference())
            return
        response = aiClient.images.create_variation(
            image=response,
            n=VARIANTS_DEFAULT,
            size="1024x1024"
        )
        image_data = response.data
        my_embeds = create_embed_image_objects(image_data)
        buttons = create_buttons_variants(image_data)
        buttons1 = create_buttons_upscale(image_data)
        buttons_all = ButtonView(buttons + buttons1)
        message = f"{interaction.user.mention} here are variations of {self.label}:"
        await interaction.channel.send(content=message, embeds=my_embeds, view=buttons_all, reference=interaction.message.to_reference())

class UpscaleButton(discord.ui.Button):
    def __init__(self, label, custom_id, row, kurl):
        super().__init__(label=label, custom_id=custom_id, row=row)
        self.kurl = kurl

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return True

    async def callback(self, interaction: discord.Interaction):
        await interaction.channel.typing()
        await interaction.response.defer()
        response = get_image_from_url(self.kurl)
        if response is None:
            await interaction.response.send_message(f"I'm sorry {interaction.user.mention}, I can't find any image to upscale.", reference=interaction.message.to_reference())
            return
        new_image = upscale_image(response, scale_factor=DEFAULT_SCALE_FACTOR)
        img_buffer = BytesIO()
        new_image.save(img_buffer, format="PNG")
        img_buffer.seek(0)
        image_file = File(fp=img_buffer, filename="upscaled.png")
        message = f"{interaction.user.mention} here is the upscaled image:"
        await interaction.channel.send(content=message, file=image_file, reference=interaction.message.to_reference())

# Bot class
class ChatBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
                   
    async def on_ready(self):
        logger.info(f'{self.user} has connected to Discord!')
        
    async def on_message(self, message):
        if message.author == self.user:
            return
        
        if self.user.mentioned_in(message):
            await message.channel.typing()
            content_without_mention = message.content.replace(f'<@{self.user.id}>', '').strip()
            
            logger.info(f'{message.created_at} - Channel: {message.channel} | {message.author} said: {content_without_mention}')
            
            if not content_without_mention.startswith(COMMANDS_PREFIX):
                message.content = f'{COMMANDS_PREFIX}generate {content_without_mention}'
            else:
                message.content = content_without_mention
                
        await self.process_commands(message) 
        
# Bot commands
client = ChatBot(command_prefix=COMMANDS_PREFIX, intents=intents)

# Removing default help to put our own
client.remove_command("help")

# Creating help command
@client.group(invoke_without_command=True)
async def help(ctx):
    embed = discord.Embed(
        title="Sorullo",
        description="Sorullo is a bot that uses OpenAI and DALL-E to analyze and generate text and images.",
    )
    embed.set_image(url="https://i.scdn.co/image/ab6761610000e5eb281b74d7d806bf014a15fcad")
    embed.set_author(
        name="Raskitoma",
        url="https://raskitoma.com",
    )
    embed.set_footer(
        text="Sorullo Bot by Raskitoma, version 2.0a",
        icon_url="https://raskitoma.com/assets/media/rask-favicon.svg"
    )
    await ctx.send(f'''
    Hello {ctx.author.mention} - available commands:
    ```
  - !help            : This message
  - !whoami          : Get more info about this bot,
  - !hello           : Make Sorullo say hello to you,
  - !generate <text> : Generate text,
  - !imagine <text>  : Generate images with DALL-E,
  - !variants        : Generate variants of an image, sent on a
                       previous message,
  - !analyze <context> | <text>  : Analyze a message.
                       If you don't provide a context, Sorullo 
                       will use the full text you provide.
                       Attach an image if you want
                       an analysis of it.
    ```
    ''', embed=embed, reference=ctx.message.to_reference())

# Creating hello command
@client.command()
async def hello(ctx):
    await ctx.channel.typing()
    await ctx.send(f'Hello {ctx.author.mention}!: oye sorullo, el negrito es el único tuyo, https://youtu.be/H3JW7-fsHL8?t=136', reference=ctx.message.to_reference())

# Creating whoami command
@client.command()
async def whoami(ctx):
    embed = discord.Embed(
        title="Sorullo",
        description="Sorullo is a bot that uses GPT and DALL-E to analyze and generate text and images.",
    )
    embed.set_image(url="https://i.scdn.co/image/ab6761610000e5eb281b74d7d806bf014a15fcad")
    embed.set_author(
        name="Raskitoma",
        url="https://raskitoma.com",
    )
    embed.set_footer(
        text="Sorullo Bot by Raskitoma, version 2.0a",
        icon_url="https://raskitoma.com/assets/media/rask-favicon.svg"
    )
    
    response = aiClient.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role" : "system",
                "content" : "You are a discord bot and you are going to introduce yourself. You can use, in your response, markdown, since your response will be used in discord. You must give your response in no more than 1500 characters"
            },
            {
                "role" : "user",
                "content" : "Biography of singer Johnny Ventura in english, no more that 2 paragraphs, max 1500 letters in total length"
            }
        ]
    )
    
    full_response = f"Hi, {ctx.author.mention} I'm a bot that uses OpenAI technologies (GPT and DALL-E) to analyze and generate text and images. My name, is based on a song called \"Capullo y Sorullo\" by Johnny Ventura. \n{ response.choices[0].message.content }"
    
    await ctx.send(full_response, embed=embed, reference=ctx.message.to_reference())

# Creating generate command using GPT
@client.command()
async def generate(ctx):
    message = ctx.message.content.replace(f'{COMMANDS_PREFIX}generate ', '')
    try:
        response = aiClient.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role" : "system",
                    "content" : "You are a discord bot, you try to give your most accurate response and you can use markdown to stylish your response since you are writing into discord. Also your reponse will be consice, precise and no more than 1700 characters in total lenght."
                },
                {
                    "role" : "user",
                    "content" : message
                }
            ]
        )

        full_response = f"{ctx.author.mention} { response.choices[0].message.content }"
    except Exception as e:
        full_response = f"I'm sorry {ctx.author.mention}, I can't generate text right now."
        logger.error(e)    
    await ctx.send(full_response, reference=ctx.message.to_reference())
        
# Creating imagine command using DALL-E        
@client.command()
async def imagine(ctx):
    prompt = ctx.message.content.replace(f'{COMMANDS_PREFIX}imagine ', '')
    try:
        response = aiClient.images.generate(
            model=OPENAI_MODEL_IMG,
            prompt=prompt,
            n=1,
            quality="hd"
        )
        image_data = response.data
        my_embeds = create_embed_image_objects(image_data)
        buttons = create_buttons_variants(image_data)
        buttons1 = create_buttons_upscale(image_data)
        buttons_all = ButtonView(buttons + buttons1)
        message = f"{ctx.author.mention} here are the pictures that my ones and zeroes imagined:"
        await ctx.send(message, embeds=my_embeds, view=buttons_all, reference=ctx.message.to_reference())
    except Exception as e:
        await ctx.send(f"I'm really sorry {ctx.author.mention}, I can't imagine anything right now, have a headache.", reference=ctx.message.to_reference())
        logger.error(e)
        
# Creating variants command using DALL-E and one of the previous images        
@client.command()
async def variants(ctx):
    get_last_replies = await find_replies_to(ctx, ctx.author)
    image = await find_last_image(get_last_replies, ctx.author)
    if image is None:
        await ctx.send(f"I'm sorry {ctx.author.mention}, I can't find any image to generate a variant.", reference=ctx.message.to_reference())
        return
    try:
        response = aiClient.images.create_variation(
            model=OPENAI_MODEL_IMG,
            image=image,
            n=VARIANTS_DEFAULT,
            size="1024x1024"
        )
        image_data = response.data
        my_embeds = create_embed_image_objects(image_data)
        buttons = create_buttons_variants(image_data)
        buttons1 = create_buttons_upscale(image_data)
        buttons_all = ButtonView(buttons + buttons1)
        message = f"{ctx.author.mention} here is a variation of the previous pic:"
        await ctx.send(message, embeds=my_embeds, view=buttons_all, reference=ctx.message.to_reference())
    except Exception as e:
        await ctx.send(f"I'm sorry {ctx.author.mention}, I can't generate a variant right now, have a headache.", reference=ctx.message.to_reference())
        logger.error(e)
        
# Creating analyze command using GPT-4    
@client.command()
async def analyze(ctx):
    logger.info('starting...')
    context = None
    messagetoai = ctx.message.content.replace(f'{COMMANDS_PREFIX}analyze ', '')

    # Lets figure out if there's a context   
    if CONTEXT_SEPARATOR in messagetoai:
        context, messagetoai = messagetoai.split(CONTEXT_SEPARATOR)

    image_url = None
    
    attachments = ctx.message.attachments
    
    if attachments:
        for attachment in attachments:
            if attachment.content_type and attachment.content_type.startswith('image/'):
                image_url = attachment.url
                break
    
    messages = []
    
    if context:
        messages.append({
            "role" : "system",
            "content" : f"{ context }. Please be very precise on your response, its lenght must be in no more than 1800 characters or you can split in multiple messages. Use markdown for the answer is desired."
        })
        
    user_content = [
        { "type" : "text", "text" : messagetoai }
    ]
    
    if image_url:
        user_content.append( 
            { 
                "type" : "image_url",
                "image_url" : { 
                    "url" : image_url 
                }
            } 
        )
        
    messages.append({
        "role" : "user",
        "content" : user_content
    })

    response = aiClient.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages
    )
    
    assistant_response = response.choices[0].message.content
    await ctx.send(assistant_response, reference=ctx.message.to_reference())

# Logging setup
logger = logging.getLogger('sorullo')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
coloredlogs.install()

# Start bot
client.run(DISCORD_TOKEN)
