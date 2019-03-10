"""BESS database template."""
import psycopg2
import psycopg2.extras
from discord.ext import commands


class Database(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = psycopg2.connect((f"dbname={self.bot.config['db']['name']}"
                                      f" user={self.bot.config['db']['user']} "
                                      "password="
                                      f"{self.bot.config['db']['pass']}"))
        self.cur = self.conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor)

    def cog_unload(self):
        self.cur.close()
        self.conn.close()
        print("Database connection culled.")
