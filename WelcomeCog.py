import random
import sqlite3
import nextcord
from nextcord.ext import commands

class WelcomeCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('welcome_data.db')  # Подключение к базе данных
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS custom_welcome_messages
             (server_id INTEGER PRIMARY KEY, message TEXT)''')  # Создаем таблицу, если её нет
        self.c.execute('''CREATE TABLE IF NOT EXISTS welcome_gifs
             (server_id INTEGER PRIMARY KEY, gif_url TEXT)''')  # Создаем таблицу, если её нет

        # Predefined GIFs
        self.gifs = [
            "https://imgur.com/1GJjhIy",
            "https://data.whicdn.com/images/315441551/original.gif",
            "https://i.pinimg.com/originals/aa/02/43/aa024380afc3587bad3cb6f8adbf1aab.gif",
            "https://78.media.tumblr.com/c7fe775814145d8a59f3629b72802357/tumblr_pc03twL37F1uvobnmo1_540.gif",
            "https://media.discordapp.net/attachments/939883368089264138/951454299018387506/d92df69c090bb9f8b402fdabe7840681.jpg"
            # Add more GIF URLs here as needed
        ]

    def __del__(self):
        self.conn.close()  # Закрываем соединение с базой данных при завершении работы

    @commands.Cog.listener()
    async def on_member_join(self, member):
        now = nextcord.utils.utcnow()
        server_id = member.guild.id

        self.c.execute('SELECT message FROM custom_welcome_messages WHERE server_id = ?', (server_id,))
        result = self.c.fetchone()

        if result:
            message = result[0]
        else:
            message = "Hello!"

        # Get a random predefined GIF
        gif_url = random.choice(self.gifs)

        emb = nextcord.Embed(title=f'Welcome to {member.guild.name}', color=0x2b2d31)
        emb.add_field(name="Welcome Message", value=message, inline=False)
        emb.set_author(name=f'{member.name}#{member.discriminator}')
        emb.set_footer(text=f'You ID: {member.id} • {now.hour}:{now.minute}')
        emb.set_image(url=gif_url)

        await member.send(embed=emb)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def set_welcome_message(self, ctx, server_id: int, *, message):
        """
        `.set_welcome_message <ID YOU SERVER> <Main text>`
        """
        self.c.execute('INSERT OR REPLACE INTO custom_welcome_messages (server_id, message) VALUES (?, ?)',
                       (server_id, message))
        self.conn.commit()
        await ctx.send(f"Custom welcome message set successfully for server ID: {server_id}.")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def list_custom_welcome_messages(self, ctx):
        """
        `.list_custom_welcome_messages`
        """
        self.c.execute('SELECT * FROM custom_welcome_messages')
        messages = self.c.fetchall()
        await ctx.send("Custom Welcome Messages:")
        for server_id, message in messages:
            await ctx.send(f"Server ID: {server_id}, Message: {message}")

def setup(bot):
    bot.add_cog(WelcomeCog(bot))
