from discord.ext import commands
from discord.ext.commands import Context
from discord.errors import NotFound
from discord import TextChannel
from discord import Message
from discord import File

import datetime
import re

from visit_info import VisitInfo
from visit_info import VisitPairs
from visit_info import write_visits_to_file


def str_to_datetime_components(string: str) -> list:
    """Replace ' ' -> '-' and ':' -> '-' in string,
    and create list of integers using '-' as separator

    example: "2022-01-01 12:00" -> [2022, 1, 1. 12, 0]
    example: "2022.01.01 12:00" -> [2022, 1, 1. 12, 0]

    :param string: datetime
    :return: list of integers
    """
    return list(map(int, string.replace('.', '-').replace(' ', '-').replace(':', '-').split('-')))


def find_channel_on_server(ctx: Context, name: str) -> TextChannel:
    """Find channel on server by name
    :param ctx: Context
    :param name: string channel name
    :return: TextChannel or None
    """
    for channel in ctx.guild.channels:
        if channel.name == name:
            return channel


async def get_messages(channel: TextChannel, after: datetime, before: datetime):
    """Get messages by date
    :param channel: TextChannel
    :param after: datetime
    :param before: datetime
    :return: list messages
    """
    return await channel.history(after=after, before=before).flatten()


async def parse_message(ctx: Context, message: Message):
    """Parse message using regexp
    :param ctx: Context
    :param message: Message
    :return: user_id, user_display_name, type_visit, channel_name, message_datetime
    """
    text = str(message.clean_content)
    user_id = int(re.search("ID: \d*", text).group(0).replace("ID: ", ""))
    type_visit = str(re.search("joined|left", text).group(0))
    channel_name = str(re.search("channel \w*", text).group(0).replace("channel ", ""))

    try:
        user = await ctx.guild.fetch_member(user_id)
        user_display_name = user.display_name
    except NotFound:
        user_display_name = 'NotFoundOnServer'

    return user_id, user_display_name, type_visit, channel_name, message.created_at


class LogParserBot(commands.Bot):
    def __init__(self, command_prefix='--', **options):
        super().__init__(command_prefix, **options)
        self.add_cog(LogParserCog(self))  # add commands for bot


class LogParserCog(commands.Cog):
    @commands.has_role("staff")
    @commands.command(name="get-visitors-channel-datetime")
    async def get_visitors(self, ctx: Context, channel_name: str,
                           after_datetime_str: str,
                           before_datetime_str: str,
                           parsed_channel="лог-посещений"):
        """function return info about
        :param after_datetime_str: "year-month-day hour:minute" or "year.month.day hour:minute"

        :param before_datetime_str: "year-month-day hour:minute" or "year.month.day hour:minute"
        :return: file .tsv
        line format: username_on_server<tab>joined_time<tab>left_time<tab>time_listened\n
        """
        channel = find_channel_on_server(ctx, parsed_channel)

        components = str_to_datetime_components(after_datetime_str)
        after_datetime = datetime.datetime(
            year=components[0],
            month=components[1],
            day=components[2],
            hour=components[3],
            minute=components[4]
        )

        components = str_to_datetime_components(before_datetime_str)
        before_datetime = datetime.datetime(
            year=components[0],
            month=components[1],
            day=components[2],
            hour=components[3],
            minute=components[4]
        )

        # создается список visit_list посещений VisitInfo голосового канала channel_name
        visit_list = list()
        # которые соответствуют временному промежутку after_datetime ~ before_datetime
        for message in await get_messages(channel, after_datetime, before_datetime):
            parsed_message = await parse_message(ctx, message)
            visit = VisitInfo(*parsed_message)
            if visit.channel_name == channel_name:
                visit_list.append(visit)

        # затем он сортируется по user_id
        visit_list.sort(key=lambda x: x.user_id, reverse=True)

        # и передается классу VisitPairs, который ищет парные сообщения joined-left
        await ctx.send(file=File(write_visits_to_file(
            VisitPairs(visit_list).get_all_visits_string()
        )))

    @commands.has_role("staff")
    @commands.command(name="get-visitors-channel-today")
    async def get_visitors_today(self, ctx: Context, channel_name: str):
        """
        :return: file .tsv
        line format: username_on_server<tab>joined_time<tab>left_time<tab>time_listened\n
        """
        after_datetime_str = \
            f'{datetime.datetime.now().year}-' \
            f'{datetime.datetime.now().month}-' \
            f'{datetime.datetime.now().day} ' \
            '00:00'

        before_datetime_str = \
            f'{datetime.datetime.now().year}-' \
            f'{datetime.datetime.now().month}-' \
            f'{datetime.datetime.now().day} ' \
            '23:59'

        await self.get_visitors(ctx, channel_name, after_datetime_str, before_datetime_str)

    @commands.has_role("staff")
    @commands.command(name="get-visitors-channel-day")
    async def get_visitors_day(self, ctx: Context, channel_name: str, day: int):
        """
        :param day: integer
        :return: file .tsv
        line format: username_on_server<tab>joined_time<tab>left_time<tab>time_listened\n
        """
        after_datetime_str = \
            f'{datetime.datetime.now().year}-' \
            f'{datetime.datetime.now().month}-' \
            f'{day} ' \
            '00:00'

        before_datetime_str = \
            f'{datetime.datetime.now().year}-' \
            f'{datetime.datetime.now().month}-' \
            f'{day} ' \
            '23:59'

        await self.get_visitors(ctx, channel_name, after_datetime_str, before_datetime_str)

    @commands.has_role("staff")
    @commands.command(name="get-1")
    async def get_1(self, ctx: Context, channel_name: str,
                           after_datetime_str: str,
                           before_datetime_str: str):
        """Short command for call get-visitors-channel-datetime"""
        await self.get_visitors(ctx, channel_name,
                           after_datetime_str,
                           before_datetime_str)

    @commands.has_role("staff")
    @commands.command(name="get-2")
    async def get_2(self, ctx: Context, channel_name: str):
        """Short command for call get-visitors-channel-today"""
        await self.get_visitors_today(ctx, channel_name)

    @commands.has_role("staff")
    @commands.command(name="get-3")
    async def get_3(self, ctx: Context, channel_name: str, day: int):
        """Short command for call get-visitors-channel-day"""
        await self.get_visitors_day(ctx, channel_name, day)


