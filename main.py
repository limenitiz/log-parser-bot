from LogParserBot import *
from decouple import config

import datetime

TOKEN = config('DISCORD_TOKEN', default=None)
client = LogParserBot()
client.run(TOKEN)
