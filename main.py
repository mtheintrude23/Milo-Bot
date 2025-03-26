import discord
from colorama import Fore, Style
from tabulate import tabulate
import nextcord
from discord import channel
from easy_pil import Editor, Canvas, Font, load_image_async
from discord.ext import commands, tasks
from discord import File
from io import BytesIO
import aiohttp
import requests
import psutil
import json
import os
import datetime
from datetime import datetime, date, timezone, timedelta
import asyncio
import random
import time
import re
import pytz 
from discord.ui import Select, Button, View, Modal, TextInput
from PIL import Image, ImageDraw, ImageFont
import traceback
import platform
import io
import contextlib
import textwrap
from collections import deque
from collections import defaultdict

user_commands = {}
default_prefix = ["!","!"]
prefixes = {}

def load_prefixes():
    global prefixes
    if os.path.exists('prefix.json'):
        with open('prefix.json', 'r') as f:
            prefixes = json.load(f)

load_prefixes()

def get_prefix(bot, message):
    guild_id = message.guild.id
    return prefixes.get(guild_id, default_prefix)

def save_prefixes():
    with open('prefix.json', 'w') as f:
        json.dump(prefixes, f, indent=4)

intent = discord.Intents.all()

bot = commands.Bot(command_prefix=get_prefix,
                   owner_id=1219514896778133594,
                   intents=intent,
                   case_insensitive=True)
bot.remove_command("help")

def load_manage_id():
    try:
        with open("manage_id.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_manage_id(data):
    with open("manage_id.json", "w") as file:
        json.dump(data, file, indent=2)

class Paginator(discord.ui.View):
    def __init__(self, pages , ctx):
        super().__init__(timeout=180)  # View sẽ tự động hết hạn sau 180 giây
        self.pages = pages
        self.current_page = 0
        self.ctx = ctx

        self.prev_button = discord.ui.Button(emoji="<:muitentrai:1297154558384144384>", style=discord.ButtonStyle.primary)
        self.home_button = discord.ui.Button(emoji="<:home:1297154827012542609>", style=discord.ButtonStyle.primary)
        self.next_button = discord.ui.Button(emoji="<:muitenphai:1297154785610301450>", style=discord.ButtonStyle.primary)

        self.prev_button.callback = self.previous_page
        self.home_button.callback = self.home_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.home_button)
        self.add_item(self.next_button)

    async def home_page(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        self.current_page = 0
        embed=discord.Embed(title="**Milo Hỗ Trợ**",description=f"<:chamxanhbien:1275686480240705546> Xin chào {self.ctx.author.mention} \n <:chamxanhbien:1275686480240705546> Dưới đây là các danh mục hỗ trợ của mình \n \n > <a:mlcash:1266979222816296980> `:` Economy \n > <:mlcoin2:1334078299265171499> `:` Casino \n > <:pet:1310148666773737472> `:` Animal \n > <:mod:1266978084205232148> `:` Moderation \n > <a:giveaway:1270686359228649504> `:` Giveaway \n > <a:hello:1266976140380213300> `:` Welcome & Goodbye \n > <a:utils:1286955353187160084> `:` Utils",color=discord.Color.orange())
        await interaction.response.edit_message(embed=embed)

    async def previous_page(self, interaction: discord.Interaction):
        data = load_manage_id()
        user_id = str(self.ctx.author.id)
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])
        else:
            await interaction.response.defer()

    async def next_page(self, interaction: discord.Interaction):
        data = load_manage_id()
        user_id = str(self.ctx.author.id)
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])
        else:
            await interaction.response.defer()

    async def on_timeout(self):
        # Khi hết thời gian, xóa các nút và cập nhật tin nhắn
        for child in self.children:
            child.disabled = True  # Vô hiệu hóa các nút
        await self.message.edit(view=None) 

    # Hàm tạo Embed dựa trên trang hiện tại
    def get_embed(self):
        embed = discord.Embed(
            title=f"Page {self.current_page + 1}/{len(self.pages)}",
            description=self.pages[self.current_page],
            color=discord.Color.blue()
        )
        return embed

# Command cho bot
@bot.hybrid_command(name="help",help="Xem danh sách lệnh của bot.")
@commands.cooldown(1, 10, commands.BucketType.user)
async def help(ctx):
    pages = [
        discord.Embed(title="**Milo Hỗ Trợ**",description=f"<:chamxanhbien:1275686480240705546> Xin chào {ctx.author.mention} \n <:chamxanhbien:1275686480240705546> Dưới đây là các danh mục hỗ trợ của mình \n \n > <a:mlcash:1266979222816296980> `:` Economy \n > <:mlcoin2:1334078299265171499> `:` Casino \n > <:pet:1310148666773737472> `:` Animal \n > <:mod:1266978084205232148> `:` Moderation \n > <a:giveaway:1270686359228649504> `:` Giveaway \n > <a:hello:1266976140380213300> `:` Welcome & Goodbye \n > <a:utils:1286955353187160084> `:` Utils",color=discord.Color.orange()),
        discord.Embed(title="Economy",description="`cash`: Xem số coin mà bạn đang có \n `daily`: Điểm danh hàng ngày \n `work`: Làm việc kiếm coin \n `give`: Chuyển coin cho ai đó \n `lb`: Xem top 10 người nhiều coin nhất \n `cf`: Chơi tung đồng xu \n `bank`: Mở ngân hàng \n `tk`: Tạo tài khoản",color=discord.Color.green()),
        discord.Embed(title="Casino",description="`coinflip`: Chơi tung đồng xu \n `blackjack`: Chơi blackjack \n `slot`: Slot",color=discord.Color.brand_green()),
        discord.Embed(title="Animal",description="`hunt`: Săn thú \n `zoo`: Xem chuồng thú",color=discord.Color.blurple()),
        discord.Embed(
                title="Moderation",
                description="`ban`: Cấm người dùng khỏi máy chủ \n `kick`: Đuổi người dùng ra khỏi máy chủ \n `mute`: Cấm chat người dùng \n `unban`: Bỏ cấm người dùng \n `unmute`: Xóa cấm chat cho người dùng \n `clear`: Xóa tin nhắn \n `lock`: Khóa kênh \n `unlock`: Mở khóa kênh \n `addrole`: Thêm role cho người dùng \n `removerole`: Xóa role của người dùng \n `createchannel`: Tạo kênh text hoặc voice \n `removechannel`: Xóa kênh \n `channelper`: Chỉnh quyền của kênh cho từng role \n `hide`: Ẩn kênh \n `show`: Hiện kênh \n `createrole`: Tạo role \n `removerole`: Xóa role \n `roleper`: Chỉnh quyền cho role",
                color=discord.Color.blue()
            ),
        discord.Embed(
                title="Giveaway",
                description="`sga`: Bắt đầu một giveaway \n `endga`: Kết thúc một giveaway \n `rrga`: Rorell một giveaway \n `fga`: Tạo nhiều giveaway cùng lúc (tối đa 10)",
                color=discord.Color.gold()
            ),
        discord.Embed(
                title="Welcome",
                description="`setbg`: Chỉnh hình ảnh để bot gửi \n `setchannel`: Chỉnh kênh và tin nhắn bot sẽ gửi \n `testwc`: Xem trước welcome \n `setgoodbyebg`: Chỉnh hình ảnh để bot gửi \n `setgoodbyechannel`: Chỉnh kênh và tin nhắn bot sẽ gửi \n `testgb`: Xem trước goodbye",
                color=discord.Color.purple()
            ),
        discord.Embed(
                title="Utils",
                description="`Ping`: Xem ping của bot \n `serverinfo`: Xem thông tin server \n `userinfo`: Xem thông tin user \n `roleinfo`: Xem thông tin role \n `afk`: Đặt trạng thái thành afk \n `avt`: Xem avatar của ai đó \n `banner`: Xem banner của ai đó \n `gopy`: Góp ý cho bot \n `rpbug`: Báo cáo lỗi \n `guildlink`: Link server hỗ trợ \n `invite`: Link mời bot \n `linksv`: Lấy link invite của server qua id (bot cần ở server đó) \n `prefix`: Chỉnh prefix của bot \n `ver`: Xem phiên bản hiện tại của bot \n `level`: Xem level của bạn \n `rank`: Xem top nhưng người có level cao nhất \n `disable` : Vô hiệu hóa lệnh của bot \n `enable` : Kích hoạt lệnh của bot",
                color=discord.Color.yellow()
            )
    ]

    async def select_callback(interaction):
        selected_option = interaction.data['values'][0]

        if interaction.user != ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như danh sách này không dành cho bạn.", ephemeral=True)
            return

        if selected_option == 'economy':
            embed = discord.Embed(
                title="Economy",
                description="`cash`: Xem số coin mà bạn đang có \n `daily`: Điểm danh hàng ngày \n `work`: Làm việc kiếm coin \n `give`: Chuyển coin cho ai đó \n `lb`: Xem top 10 người nhiều coin nhất \n `cf`: Chơi tung đồng xu",
                color=discord.Color.brand_green()
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif selected_option == 'casino':
            embed = discord.Embed(
                title="Casino",
                description="`coinflip`: Chơi tung đồng xu \n `blackjack`: Chơi blackjack \n `slot`: Slot",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif selected_option == 'animal':
            embed = discord.Embed(
                title="Animal",
                description="`hunt`: Săn thú \n `zoo`: Xem chuồng thú",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif selected_option == 'moderation':
            embed = discord.Embed(
                title="Moderation",
                description="`ban`: Cấm người dùng khỏi máy chủ \n `kick`: Đuổi người dùng ra khỏi máy chủ \n `mute`: Cấm chat người dùng \n `unban`: Bỏ cấm người dùng \n `unmute`: Xóa cấm chat cho người dùng \n `clear`: Xóa tin nhắn \n `lock`: Khóa kênh \n `unlock`: Mở khóa kênh \n `addrole`: Thêm role cho người dùng \n `removerole`: Xóa role của người dùng \n `createchannel`: Tạo kênh text hoặc voice \n `removechannel`: Xóa kênh \n `channelper`: Chỉnh quyền của kênh cho từng role \n `hide`: Ẩn kênh \n `show`: Hiện kênh \n `createrole`: Tạo role \n `removerole`: Xóa role \n `roleper`: Chỉnh quyền cho role",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif selected_option == 'giveaway':
            embed = discord.Embed(
                title="Giveaway",
                description="`sga`: Bắt đầu một giveaway \n `endga`: Kết thúc một giveaway \n `rrga`: Rorell một giveaway \n `fga`: Tạo nhiều giveaway cùng lúc (tối đa 10)",
                color=discord.Color.gold()
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif selected_option == 'welcome':
            embed = discord.Embed(
                title="Welcome",
                description="`setbg`: Chỉnh hình ảnh để bot gửi \n `setchannel`: Chỉnh kênh và tin nhắn bot sẽ gửi \n `testwc`: Xem trước welcome \n `setgoodbyebg`: Chỉnh hình ảnh để bot gửi \n `setgoodbyechannel`: Chỉnh kênh và tin nhắn bot sẽ gửi \n `testgb`: Xem trước goodbye",
                color=discord.Color.purple()
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)
        elif selected_option == 'utils':
            embed = discord.Embed(
                title="Utils",
                description="`Ping`: Xem ping của bot \n `afk`: Đặt trạng thái thành afk \n `avt`: Xem avatar của ai đó \n `banner`: Xem banner của ai đó \n `gopy`: Góp ý cho bot \n `rpbug`: Báo cáo lỗi \n `linksv`: Lấy link invite của server qua id (bot cần ở server đó) \n `prefix`: Chỉnh prefix của bot \n `uptime`: Xem thời gian bot đã hoạt động \n `status`: Xem trạng thái của bot \n `ver`: Xem phiên bản hiện tại của bot \n `tts`: Phát âm thanh từ văn bản với ngôn ngữ lựa chọn \n `level`: Xem level của bạn \n `rank`: Xem top nhưng người có level cao nhất \n `disable` : Vô hiệu hóa lệnh của bot \n `enable` : Kích hoạt lệnh của bot \n `setautorole` : Kích hoạt auto role \n `removeautorole` : Vô hiệu hóa auto role",
                color=discord.Color.yellow()
            )
            await interaction.response.send_message(embed=embed,ephemeral=True)

    select = Select(
        min_values=1,
        max_values=1,
        placeholder="Danh Mục Hỗ Trợ",
        options=[
            discord.SelectOption(emoji="<a:mlcash:1266979222816296980>", label="Economy", value="economy"),
            discord.SelectOption(emoji="<:mlcoin2:1334078299265171499>",label="Casino",value="casino"),
            discord.SelectOption(emoji="<:pet:1310148666773737472>",label="Animal",value="animal"),
            discord.SelectOption(emoji="<:mod:1266978084205232148>", label="Moderation", value="moderation"),
            discord.SelectOption(emoji="<a:give:1270686359228649504>", label="Giveaway", value="giveaway"),
            discord.SelectOption(emoji="<a:hello:1266976140380213300>", label="Welcome", value="welcome"),
            discord.SelectOption(emoji="<a:utils:1286955353187160084>",label="Utils",value="utils"),
        ]
    )

    select.callback = select_callback
    view = Paginator(pages,ctx)
    view.add_item(select)

    select_message = await ctx.send(embed=pages[0],view=view)

    # Xóa Select sau khi timeout
    async def remove_select_after_timeout():
        await asyncio.sleep(180)  # Chờ 180 giây
        await select_message.edit(view=None)  # Xóa Select

    bot.loop.create_task(remove_select_after_timeout())

load_prefixes()

def get_prefix(bot, message):
    guild_id = message.guild.id
    return prefixes.get(guild_id, default_prefix)

@bot.command(name="prefix",help="Chỉnh prefix của bot")
@commands.has_permissions(administrator=True)
async def prefix(ctx, new_prefix):
    guild_id = ctx.guild.id
    prefixes[guild_id] = new_prefix
    save_prefixes()
    message = ['Tuyệt!','Bơ phạch!','10 đỉm!']

    prefix_message = random.choice(message)
    await ctx.send(f"<:checked:1307210920082145330> | Đã chỉnh prefix thành: {new_prefix}! {prefix_message}")

def load_econ():
    try:
        with open("econ.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    for user_id, user_info in data.items():
        if 'cash' in user_info:
            user_info['cash'] = int(user_info['cash'])
    return data

def save_econ(data):
    with open("econ.json", "w") as file:
        json.dump(data, file, indent=2)

def load_micoin():
    try:
        with open("micoin.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_micoin(data):
    with open("micoin.json", "w") as file:
        json.dump(data, file, indent=2)

def load_premium_data():
    try:
        with open('premium_data.json', 'r') as file:
            data = json.load(file)
            if 'users' not in data:
                data['users'] = {}
            if 'codes' not in data:
                data['codes'] = {}
            return data
    except FileNotFoundError:
        return {'users': {}, 'codes': {}}

premium_data = load_premium_data()

def save_premium_data():
    with open('premium_data.json', 'w') as file:
        json.dump(premium_data, file)

def is_premium(user_id):
    return str(user_id) in premium_data['users'] and datetime.now() < datetime.fromisoformat(premium_data['users'][str(user_id)])

@bot.command(name="mypre", help="Kiểm tra gói Premium đang dùng")
async def mypre(ctx):
    user_id = str(ctx.author.id)
    embed = discord.Embed(title="Premium Status", color=discord.Color.green())
    if user_id in premium_data['users']:
        expiration_date = datetime.fromisoformat(premium_data['users'][user_id])
        remaining_days = (expiration_date - datetime.now()).days
        embed.description = f"Bạn đang sử dụng gói Premium, còn {remaining_days} ngày nữa."
    else:
        embed.description = "Bạn không có gói Premium nào."
    await ctx.send(embed=embed)

@tasks.loop(seconds=10)
async def reset_daily():
    now = datetime.now()
    start_of_day = datetime.combine(date.today(), datetime.min.time())
    end_of_day = start_of_day + timedelta(days=1) - timedelta(seconds=1)
    
    if start_of_day < now < end_of_day:
        d = load_econ()
        for a, b in d.items():
            d[a]["dailied"] = False
        save_econ(d)

@bot.command(name="cash", help="Xem số coin của bạn")
@commands.cooldown(1, 10, commands.BucketType.user)
async def cash(ctx):
    user_id = str(ctx.author.id)
    data = load_econ()

    if user_id not in data:
        data[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}

    cash_amount = data[user_id]["cash"]
    formatted_cash = f"{cash_amount:,d}".replace(",", ".")
    await ctx.send(f"Bạn đang có **__{formatted_cash}__** <:mlcoin:1330026986667769867>.")

@bot.command(name="micash", help="Xem số coin của bạn")
@commands.cooldown(1, 10, commands.BucketType.user)
async def micash(ctx):
    user_id = str(ctx.author.id)
    data = load_micoin()

    if user_id not in data:
        data[user_id] = {"cash": 0}

    cash_amount = data[user_id]["cash"]
    formatted_cash = f"{cash_amount:,d}".replace(",", ".")
    await ctx.send(f"Bạn đang có **__{formatted_cash}__** <:micoin:1307211365890654248>.")

@bot.command(name="daily", help="Điểm danh hàng ngày")
@commands.cooldown(1, 10, commands.BucketType.user)
async def daily(ctx):
    user_id = str(ctx.author.id)
    data = load_econ()
    micoin = load_micoin()
    event = load_event()

    if user_id not in data:
        data[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}
    
    if user_id not in micoin:
        micoin[user_id] = {"cash": 0}

    today = str(ctx.message.created_at.date())

    if data[user_id]["last_daily_claim"] != today:
        if is_premium(ctx.author.id):
            data[user_id]["cash"] += 1000
            micoin[user_id]["cash"] += 10
            data[user_id]["last_daily_claim"] = today
            save_econ(data)
            save_micoin(micoin) 
            embed = discord.Embed(description=f"<a:star:1330027018884087808> | **{ctx.author.name}**, Bạn đã nhận được **1.000 <:mlcoin:1330026986667769867>** và **10** <:micoin:1307211365890654248>", color=discord.Color.blue())
            await ctx.send(embed=embed)
        else:
            data[user_id]["cash"] += 500
            data[user_id]["last_daily_claim"] = today
            save_econ(data)
            embed = discord.Embed(description=f"<a:star:1330027018884087808> | **{ctx.author.name}**, Bạn đã nhận được **500** <:mlcoin:1330026986667769867>", color=discord.Color.blue())
            await ctx.send(embed=embed)
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn đã nhận quà hôm nay rồi.")

@bot.command(aliases=["adddaily", "adl"])
async def add_daily(ctx, member: str):
    econ = load_econ()
    data = load_manage_id()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)
    member_id = str(member_get.id)

    # Kiểm tra quyền hạn người dùng (admin hoặc owner)
    if user_id in data['owner_id'] or user_id in data['admin_id']:
        # Lấy ngày hôm qua
        yesterday = (datetime.now() - timedelta(days=1)).date()

        # Kiểm tra nếu member_id tồn tại trong econ, nếu không thì khởi tạo
        if user_id not in data:
            data[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}

        # Cập nhật ngày nhận thưởng của member
        econ[member_id]['last_daily_claim'] = str(yesterday)

        save_econ(econ)

        await ctx.send(f"<:checked:1307210920082145330> | Đã đặt lại điểm danh hàng ngày cho {member_get.name}.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(aliases=["removedaily", "rdl"])
async def remove_daily(ctx, member: str):
    econ = load_econ()
    data = load_manage_id()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)
    member_id = str(member_get.id)

    # Kiểm tra quyền hạn người dùng (admin hoặc owner)
    if user_id in data['owner_id'] or user_id in data['admin_id']:
        # Lấy ngày hôm qua

        # Kiểm tra nếu member_id tồn tại trong econ, nếu không thì khởi tạo
        if user_id not in data:
            data[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}

        # Cập nhật ngày nhận thưởng của member
        econ[member_id]['last_daily_claim'] = str(ctx.message.created_at.date())

        save_econ(econ)

        await ctx.send(f"<:checked:1307210920082145330> | Đã đặt điểm danh hàng ngày cho {member_get.name}.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(name="addcoin", aliases=["ac", "acoin"])
async def add_coin(ctx, member: str, amount: int):
    data = load_manage_id()
    econ = load_econ()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)

    if user_id in data.get('owner_id', []) or user_id in data.get('admin_id', []):
        member_id = str(member_get.id)

        # Initialize user data if not present
        if member_id not in econ:
            econ[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}

        econ[member_id]['cash'] += amount
        save_econ(econ)
        cash_amount = amount
        formatted_cash = f"{cash_amount:,d}".replace(",", ".")

        await ctx.send(f"<:checked:1307210920082145330> | Đã thêm **{formatted_cash}** <:mlcoin:1330026986667769867> cho `{member_get.display_name}`")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(name="removecoin", aliases=["rc", "rcoin"])
async def remove_coin(ctx, member: str, amount: int):
    data = load_manage_id()
    econ = load_econ()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)

    if user_id in data.get('owner_id', []) or user_id in data.get('admin_id', []):
        member_id = str(member_get.id)

        # Initialize user data if not present
        if member_id not in econ:
            econ[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}

        # Check if the user has enough coins
        if econ[member_id]['cash'] < amount:
            await ctx.send(f"<:cancel:1307210917594796032> | {member_get.display_name} không có đủ coin để xóa")
            return

        econ[member_id]['cash'] -= amount
        save_econ(econ)
        cash_amount = amount
        formatted_cash = f"{cash_amount:,d}".replace(",", ".")

        await ctx.send(f"<:checked:1307210920082145330> | Đã xóa **{formatted_cash}** <:mlcoin:1330026986667769867> của `{member_get.display_name}`")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(name="addmicoin", aliases=["amc","amicoin"])
async def add_micoin(ctx, member: str, amount: int):
    data = load_manage_id()
    econ = load_micoin()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)
    member_id = str(member_get.id)

    if user_id in data['owner_id'] or data['admin_id']:
        user_id = str(member.id)
        data = load_econ()

        if member_id not in econ:
            econ[user_id] = {'cash': 0}

        econ[member_id]['cash'] += amount
        save_micoin(econ)
        await ctx.send(f"<:checked:1307210920082145330> | Đã thêm **{amount}** <:micoin:1307211365890654248> cho `{member.display_name}`")

    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(name="removemicoin", aliases=["rmc","rmicoin"])
async def remove_micoin(ctx, member: str, amount: int):
    data = load_manage_id()
    econ = load_micoin()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)
    member_id = str(member_get.id)

    if user_id in data['owner_id'] or data['admin_id']:
        if member_id not in econ:
            econ[user_id] = {'cash': 0}
        
        if econ[member_id]['cash'] < amount:
            await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} không có đủ coin để xóa")

        econ[member_id]['cash'] -= amount
        save_micoin(econ)
        await ctx.send(f"<:checked:1307210920082145330> | Đã xóa **{amount}** <:micoin:1307211365890654248> của `{member.display_name}`")

    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(aliases=["addpray", "apy"])
async def add_pray(ctx, member: str, amount: int):
    data = load_manage_id()
    pray = load_pray()
    user_id = str(ctx.author.id)

    if user_id in data['owner_id'] or user_id in data['admin_id']:
        if amount <= 0:
            await ctx.send("<:cancel:1307210917594796032> | Bạn phải thêm ít nhất 1 điểm.")
            return

        try:
            member_get = await get_user_from_input(ctx, member)
            member_id = str(member_get.id)
        except ValueError:
            await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng này.")
            return

        if member_id not in pray:
            pray[member_id] = {'pray': 0}

        pray[member_id]['pray'] += amount
        save_pray(pray)
        await ctx.send(f"<:checked:1307210920082145330> | Đã thêm {amount} điểm may mắn cho {member_get.display_name}.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(aliases=["removepray", "rpy"])
async def remove_pray(ctx, member: str, amount: int):
    data = load_manage_id()
    pray = load_pray()
    user_id = str(ctx.author.id)

    if user_id in data['owner_id'] or user_id in data['admin_id']:
    # Validate amount
        if amount <= 0:
            await ctx.send("<:cancel:1307210917594796032> | Bạn phải xóa ít nhất 1 điểm.")
            return

        try:
            member_get = await get_user_from_input(ctx, member)
            member_id = str(member_get.id)
        except ValueError:
            await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng này.")
            return

        # Ensure the member exists in pray data
        if member_id not in pray:
            pray[member_id] = {'pray': 0}

        pray[member_id]['pray'] -= amount
        save_pray(pray)
        await ctx.send(f"<:checked:1307210920082145330> | Đã xóa {amount} điểm may mắn của {member_get.display_name}.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

def load_banga():
    try:
        with open("banga.json", "r") as f:
            banga = json.load(f)
    except FileNotFoundError:
        banga = {}
    return banga

def save_banga(data):
    with open("banga.json", "w") as file:
        json.dump(data, file, indent=2)

@bot.command(name="banga", help="Ban người dùng tạo ga toàn cầu/trong server")
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def banga(ctx, member: str, choose: str, *, reason=None):
    mi = load_manage_id()
    data = load_banga()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)
    member_id = str(member_get.id)
    server_id = str(ctx.guild.id)

    if choose == "guild":
        if 'guild' not in data:
            data['guild'] = {}
        if server_id not in data['guild']:
            data['guild'][server_id] = []
        if member_id not in data['guild'][server_id]:
            data['guild'][server_id].append(member_id)
            save_banga(data)
            await ctx.send(f"<:checked:1307210920082145330> | Đã cấm **{member_get.display_name}** tạo giveaway trong máy chủ")
        else:
            await ctx.send(f"<:cancel:1307210917594796032> | **{member_get.display_name}** đã bị cấm tạo giveaway trong máy chủ")

    elif choose == "global":
        if user_id in mi['owner_id'] or mi['admin_id']:
            if 'global' not in data:
                data['global'] = []
            if member_id not in data['global']:
                data['global'].append(member_id)
                save_banga(data)
                await ctx.send(f"<:checked:1307210920082145330> | Đã cấm **{member_get.display_name}** tạo giveaway trên toàn cầu")
            else:
                await ctx.send(f"<:cancel:1307210917594796032> | {member_get.display_name} đã bị cấm tạo giveaway trên toàn cầu")
        else:
            await ctx.send(f"<:cancel:1307210917594796032> | Bạn không có quyền cấm {member_get.display_name} tạo giveaway trên toàn cầu.")

@bot.command(name="unbanga", help="Unban người dùng tạo ga toàn cầu/trong server")
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def banga(ctx, member: str, choose: str, *, reason=None):
    mi = load_manage_id()
    data = load_banga()
    user_id = str(ctx.author.id)
    member_get = await get_user_from_input(ctx, member)
    member_id = str(member_get.id)
    server_id = str(ctx.guild.id)

    if choose == "guild":
        if 'guild' not in data:
            data['guild'] = {}
        if server_id not in data['guild']:
            data['guild'][server_id] = []
        if member_id not in data['guild'][server_id]:
            data['guild'][server_id].remove(member_id)
            save_banga(data)
            await ctx.send(f"<:checked:1307210920082145330> | Đã bỏ cấm **{member_get.display_name}** tạo giveaway trong máy chủ")
        else:
            await ctx.send(f"<:cancel:1307210917594796032> | **{member_get.display_name}** không bị cấm tạo giveaway trong máy chủ")

    elif choose == "global":
        if user_id in mi['owner_id'] or mi['admin_id']:
            if 'global' not in data:
                data['global'] = []
            if member_id not in data['global']:
                data['global'].remove(member_id)
                save_banga(data)
                await ctx.send(f"<:checked:1307210920082145330> | Đã bỏ cấm **{member_get.display_name}** tạo giveaway trên toàn cầu")
            else:
                await ctx.send(f"<:cancel:1307210917594796032> | **{member_get.display_name}** không bị cấm tạo giveaway trên toàn cầu")
        else:
            await ctx.send(f"<:cancel:1307210917594796032> | Bạn không có quyền bỏ cấm {member_get.display_name} tạo giveaway trên toàn cầu.")

@bot.command(name="addagrule", aliases=["aar"])
async def add_agrule(ctx, member: str):
    mi = load_manage_id()
    data = load_agreementsrule()

    # Ensure 'user' key exists in data
    if 'user' not in data:
        data['user'] = {}

    user_id = str(ctx.author.id)

    try:
        member_get = await get_user_from_input(ctx, member)
        member_id = str(member_get.id)
    except ValueError:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng này.")
        return

    if user_id in mi['owner_id'] or user_id in mi['admin_id']:
        if data['user'].get(member_id) is not True:
            data['user'][member_id] = True
            save_agreementsrule(data)
            await ctx.send(f"<:checked:1307210920082145330> | Đã thêm **{member_get.display_name}** vào danh sách đồng ý quy tắc.")
        else:
            await ctx.send(f"<:cancel:1307210917594796032> | **{member_get.display_name}** đã đồng ý quy tắc.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command(name="removeagrule", aliases=["rar"])
async def remove_agrule(ctx, member: str):
    mi = load_manage_id()
    data = load_agreementsrule()

    # Ensure 'user' key exists in data
    if 'user' not in data:
        data['user'] = {}

    user_id = str(ctx.author.id)

    try:
        member_get = await get_user_from_input(ctx, member)
        member_id = str(member_get.id)
    except ValueError:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng này.")
        return

    if user_id in mi['owner_id'] or user_id in mi['admin_id']:
        if data['user'].get(member_id) is True:
            data['user'][member_id] = False
            save_agreementsrule(data)
            await ctx.send(f"<:checked:1307210920082145330> | Đã xóa **{member_get.display_name}** khỏi danh sách đồng ý quy tắc.")
        else:
            await ctx.send(f"<:cancel:1307210917594796032> | **{member_get.display_name}** chưa đồng ý quy tắc.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

async def get_user_from_input(ctx, user_input):
    try:
        # Check if input is a mention
        if user_input.startswith("<@") and user_input.endswith(">"):  
            user_id = int(user_input[2:-1]) if user_input[2] != "!" else int(user_input[3:-1])  # Handle <@!user>
            return await ctx.guild.fetch_member(user_id)
        else:  # If input is a user ID
            return await ctx.guild.fetch_member(int(user_input))  
    except Exception:
        return None  # Return None if user is not found

@bot.command(name="addpre", help="Thêm người dùng vào danh sách Premium")
async def addpre(ctx, user_input: str, duration_days: int):
    data = load_manage_id()
    user_id = str(ctx.author.id)

    # Check if the author has permission to use the command
    if user_id not in data['owner_id'] and user_id not in data['admin_id']:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")
        return

    # Get the user object based on the input (mention or ID)
    user = await get_user_from_input(ctx, user_input)

    if user is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng.")
        return

    expiration_date = datetime.now() + timedelta(days=duration_days)
    premium_data['users'][str(user.id)] = expiration_date.isoformat()
    save_premium_data()
    await ctx.send(f"<:checked:1307210920082145330> | Đã thêm premium {expiration_date} ngày cho **{user.name}**")

@bot.command(name="removepre", help="Thu hồi quyền Premium từ người dùng")
async def removepre(ctx, user_input: str):
    data = load_manage_id()
    user_id = str(ctx.author.id)

    # Check if the author has permission to use the command
    if user_id not in data['owner_id'] and user_id not in data['admin_id']:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")
        return

    # Get the user object based on the input (mention or ID)
    user = await get_user_from_input(ctx, user_input)

    if user is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng.")
        return

    if str(user.id) in premium_data['users']:
        del premium_data['users'][str(user.id)]
        save_premium_data()
        await ctx.send(f"<:checked:1307210920082145330> | Đã thu hồi Premium từ {user.name}.")
    else:
        await ctx.send(f"<:cancel:1307210917594796032> | {user.name} không có premium")

@bot.command(name="makecode", help="Tạo mã Premium")
async def makecode(ctx, code: str, duration_days: int):
    data = load_manage_id()
    user_id = str(ctx.author.id)

    if user_id not in data['owner_id'] or data['admin_id']:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")
        return

    if code in premium_data['codes']:
        await ctx.send(f"<:cancel:1307210917594796032> | Mã {code} đã tồn tại.")
    else:
        expiration_date = datetime.now() + timedelta(days=duration_days)
        premium_data['codes'][code] = expiration_date.isoformat()
        save_premium_data()
        await ctx.send(f"<:checked:1307210920082145330> | Đã tạo mã Premium: {code} với hạn sử dụng đến {expiration_date}.")

@bot.command(name="givecode", help="Nhận Premium bằng mã code")
async def givecode(ctx, code: str):
    if code in premium_data['codes']:
        expiration_date = datetime.fromisoformat(premium_data['codes'][code])
        if datetime.now() <= expiration_date:
            premium_data['users'][str(ctx.author.id)] = expiration_date.isoformat()
            del premium_data['codes'][code]
            save_premium_data()
            await ctx.send(f"<:checked:1307210920082145330> | Bạn đã nhận được Premium đến ngày {expiration_date}.")
        else:
            del premium_data['codes'][code]
            save_premium_data()
            await ctx.send("<:cancel:1307210917594796032> | Mã này đã hết hạn.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Mã không hợp lệ.")

webhook_tk = 'https://discordapp.com/api/webhooks/1333429671643316295/5SORlIZabR_ISsCWL0piiq3Bux6LEs24VG25qPYRd_svY7gspooWVwJoqo64SuwbCSR2'

async def send_tk_webhook(content, embed=None):
    async with aiohttp.ClientSession() as session:
        payload = {'content': content}
        if embed:
            payload['embeds'] = [embed.to_dict()]
        async with session.post(webhook_tk, json=payload) as response:
            if response.status != 204:
                print(f"Failed to send log to webhook: {response.status}, {await response.text()}")

def load_tk():
    try:
        with open("tk.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_tk(data):
    with open("tk.json", "w") as file:
        json.dump(data, file, indent=2)

class DangnhapModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Đăng nhập")
        self.ctx = ctx
        self.name_input = TextInput(label="Hãy nhập id", placeholder="id (6 chữ số)", required=True)
        self.name_input1 = TextInput(label="Hãy nhập mật khẩu", placeholder="mk", required=True)
        self.add_item(self.name_input)
        self.add_item(self.name_input1)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_tk()  # Lấy dữ liệu tài khoản
        user_id = str(self.ctx.author.id)  # ID người dùng thực hiện đăng nhập
        id = self.name_input.value  # ID người dùng nhập
        mk = self.name_input1.value  # Mật khẩu người dùng nhập

        # Kiểm tra ID có phải 6 chữ số và chỉ chứa số
        if not id.isdigit() or len(id) != 6:
            await interaction.response.send_message("<:cancel:1307210917594796032> | ID phải là 6 chữ số.", ephemeral=True)
            return

        if not data:
            data = []

        # Tìm kiếm ID trong danh sách data
        account_data = next((account for account in data if account['id'] == id), None)

        if account_data:
            # Kiểm tra mật khẩu đúng không
            if mk == account_data['mk']:
                if account_data['logined'] != None:
                    await interaction.response.send_message("<:cancel:1307210917594796032> | Tài khoản đã được đăng nhập.", ephemeral=True)
                    return
                
                account_data['logined'] = user_id  # Thêm user_id vào phần logined

                save_tk(data)  # Lưu lại dữ liệu

                embed = discord.Embed(title=f"{self.ctx.author.display_name} <:baolixi:1330034297771655301> {account_data['id']}", 
                              description="<:member:1280718179714469899> | Bạn hiện đang ở trong tài khoản", 
                              color=discord.Color.yellow())
                view = InTKView(self.ctx)
                await interaction.response.edit_message(embed=embed, view=view)
                await interaction.followup.send("<:checked:1307210920082145330> | Bạn đã đăng nhập thành công", ephemeral=True)
            else:
                await interaction.response.send_message("<:cancel:1307210917594796032> | Mật khẩu không đúng", ephemeral=True)
        else:
            await interaction.response.send_message("<:cancel:1307210917594796032> | ID không tồn tại", ephemeral=True)

class DangKiModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Đăng kí")
        self.ctx = ctx
        self.id_input = TextInput(label="Hãy nhập id", placeholder="id (6 chữ số)", required=True)
        self.mk_input = TextInput(label="Hãy nhập mật khẩu", placeholder="mk", required=True)
        self.add_item(self.id_input)
        self.add_item(self.mk_input)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_tk()  # data is a list
        id = self.id_input.value
        mk = self.mk_input.value

        # Validate ID
        if not id.isdigit() or len(id) != 6:
            await interaction.response.send_message("<:cancel:1307210917594796032> | ID phải là 6 chữ số.", ephemeral=True)
            return

        # Check if ID already exists
        if any(isinstance(user_info, dict) and user_info.get('id') == id for user_info in data):  # Ensure user_info is a dict
            await interaction.response.send_message("<:cancel:1307210917594796032> | ID đã tồn tại.", ephemeral=True)
            return

        # Append new entry to the list
        new_entry = {
            'id': id,
            'mk': mk,
            'owner': str(self.ctx.author.id),
            'logined': None,
            'bank': 0
        }
        data.append(new_entry)
        save_tk(data)

        await interaction.response.send_message("<:checked:1307210920082145330>| Bạn đã đăng kí thành công. Hãy đăng nhập", ephemeral=True)

        embed=discord.Embed(title="Tài khoản mới được tạo",description=f"**ID:** ||{id}|| \n**Mật khẩu:** ||{mk}|| \n **Chủ tài khoản:** {self.ctx.author.mention} ({self.ctx.author.id})",color=discord.Color.yellow())
        await send_tk_webhook(content="",embed=embed)

class ForgotPasswordModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Quên mật khẩu")
        self.ctx = ctx
        self.user_id_input = TextInput(label="Nhập user id", placeholder="User ID", required=True)
        self.add_item(self.user_id_input)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_tk()
        user_id = str(self.user_id_input.value)

        account = next((acc for acc in data if acc['owner'] == user_id), None)

        if account:
            # Tạo view với nút Đúng và Không
            class ConfirmResetView(View):
                def __init__(self, target_user, ctx, account):
                    super().__init__(timeout=180)
                    self.ctx = ctx
                    self.target_user = target_user
                    self.account = account

                @discord.ui.button(label="Đúng", style=discord.ButtonStyle.green)
                async def dung(self, interaction: discord.Interaction, button: Button):
                    if interaction.user != self.target_user:
                        await interaction.response.send_message("<:cancel:1307210917594796032> | Nút này không dành cho bạn.", ephemeral=True)
                        return

                    # Gửi thông tin tài khoản qua DM
                    dm_channel = await self.ctx.author.create_dm()
                    embed=discord.Embed(title=f"Thông tin tài khoản của {self.target_user.display_name}",description=(
                        f"**ID:** ||{self.account['id']}|| \n"
                        f"**Mật khẩu:** ||{self.account['mk']}|| \n \n"
                        f"<a:warn:1268085072767090790> | Vui lòng không chia sẻ thông tin này cho người khác."),color=discord.Color.yellow())
                    await dm_channel.send(embed=embed)
                    embed=discord.Embed(title=f"Yêu cầu lấy lại thông tin tài khoản",description="Yêu cầu đã được thực hiện.",color=discord.Color.green())
                    await interaction.response.edit_message(embed=embed,view=None)
                
                @discord.ui.button(label="Không", style=discord.ButtonStyle.green)
                async def khong(self, interaction: discord.Interaction, button: Button):
                    if interaction.user != self.target_user:
                        await interaction.response.send_message("<:cancel:1307210917594796032> | Nút này không dành cho bạn.", ephemeral=True)
                        return
                    
                    embed=discord.Embed(title=f"Yêu cầu lấy lại thông tin tài khoản",description="Yêu cầu đã bị hủy.",color=discord.Color.red())
                    await interaction.response.edit_message(embed=embed,view=None)
            try:
                target_user = await self.ctx.bot.fetch_user(int(user_id))
                dm_channel = await target_user.create_dm()
                embed=discord.Embed(title="Yêu cầu lấy lại thông tin tài khoản",description="Xin chào \n Chúng tôi nhận được yêu cầu lại thông tin tài khoản của bạn. \n \n Nếu bạn là người yêu cầu, vui lòng ấn vào nút 'Đúng' để nhận được thông tin tài khoản. \n \n Nút phía dưới sẽ bị vô hiệu hóa trong 180 giây. \n \n Cảm ơn \n Milo Team",color=discord.Color.yellow())
        
                embed.set_footer(text=f"Yêu cầu bởi {self.ctx.author.display_name}")
                await dm_channel.send(embed=embed, view=ConfirmResetView(target_user, self.ctx, account))
                await interaction.response.send_message("<:checked:1307210920082145330> | Thành công.", ephemeral=True)
            except discord.Forbidden:
                await interaction.response.send_message("<:cancel:1307210917594796032> | Không thể gửi tin nhắn qua DM.", ephemeral=True)
        else:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Không tìm thấy tài khoản với ID đã nhập.", ephemeral=True)

class TKView(View):
    def __init__(self, ctx):
        super().__init__(timeout=180)
        self.ctx = ctx

    @discord.ui.button(label="Đăng nhập", style=discord.ButtonStyle.blurple)
    async def dang_nhap(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_tk()

        if not data:
            data = []
        
        modal = DangnhapModal(self.ctx)
        await interaction.response.send_modal(modal)
        
        save_tk(data)
    
    @discord.ui.button(label="Đăng kí", style=discord.ButtonStyle.blurple)
    async def dang_ki(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_tk()

        if not data:
            data = []
        
        modal = DangKiModal(self.ctx)
        await interaction.response.send_modal(modal)
        
        save_tk(data)
    
    @discord.ui.button(label="Quên mật khẩu", style=discord.ButtonStyle.gray)
    async def quen_mat_khau(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        data = load_tk()

        if not data:
            data = []

        modal = ForgotPasswordModal(self.ctx)
        await interaction.response.send_modal(modal)

class ChangePasswordModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Đổi mật khẩu")
        self.ctx = ctx
        self.old_password = TextInput(label="Nhập mật khẩu cũ", placeholder="Mật khẩu cũ", required=True)
        self.new_password = TextInput(label="Nhập mật khẩu mới", placeholder="Mật khẩu mới", required=True)
        self.add_item(self.old_password)
        self.add_item(self.new_password)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_tk()  # Load account data
        user_id = str(self.ctx.author.id)

        # Find the logged-in user in data
        logged_user = next((user_info for user_info in data if user_info.get('logined') == user_id), None)

        # Check if the old password matches
        if self.old_password.value != logged_user['mk']:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Mật khẩu cũ không đúng.", ephemeral=True)
            return
        
        if self.new_password.value == logged_user['mk']:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Mật khẩu mới không được trùng với mật khẩu cũ.", ephemeral=True)
            return

        # Update to the new password
        logged_user['mk'] = self.new_password.value
        save_tk(data)  # Save the updated data

        await interaction.response.send_message("<:checked:1307210920082145330> | Mật khẩu đã được thay đổi thành công!", ephemeral=True)

        embed=discord.Embed(title="Mật khẩu tài khoản đã được đổi",description=f"**ID:** {logged_user['id']} \n**Mật khẩu cũ:** ||{self.old_password.value}|| \n**Mật khẩu mới:** ||{self.new_password.value}|| \n**Người thực hiện:** {self.ctx.author.mention} ({self.ctx.author.id})",color=discord.Color.yellow())
        await send_tk_webhook(content="",embed=embed)

class InTKView(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx
    
    @discord.ui.button(label="Đổi mật khẩu", style=discord.ButtonStyle.blurple)
    async def doi_mat_khau(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        modal = ChangePasswordModal(self.ctx)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="Đăng xuất", style=discord.ButtonStyle.red)
    async def dang_xuat(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        data = load_tk()  # Lấy dữ liệu tài khoản
        user_id = str(self.ctx.author.id)

        if not data:
            data = []

        # Duyệt qua dữ liệu và tìm user đã đăng nhập
        for user_info in data:
            if user_info.get('logined') == user_id:
                user_info['logined'] = None  # Đặt lại logined thành None

        save_tk(data)  # Lưu lại dữ liệu

        embed = discord.Embed(
            title=f"{self.ctx.author.display_name} <:baolixi:1330034297771655301> {user_info['id']}",
            description="<:checked:1307210920082145330> | Đã đăng xuất tài khoản!",
            color=discord.Color.green()
        )

        await interaction.response.edit_message(embed=embed, view=None)

@bot.command(name="tk", help="Xem tài khoản của bạn")
async def tk(ctx):
    data = load_tk()  # Lấy dữ liệu tài khoản
    user_id = str(ctx.author.id)

    if not data:
        data = []
        save_tk(data)

    # Kiểm tra xem user_id có đang đăng nhập không
    logged = next((user_info for user_info in data if user_info.get('logined') == user_id), None)

    if logged:
        # Khi người dùng đã đăng nhập
        embed = discord.Embed(title=f"{ctx.author.display_name} <:baolixi:1330034297771655301> {logged['id']}", 
                              description="<:member:1280718179714469899> | Bạn hiện đang ở trong tài khoản", 
                              color=discord.Color.yellow())
        view = InTKView(ctx)
        await ctx.send(embed=embed, view=view)
    else:
        # Khi người dùng chưa đăng nhập
        embed = discord.Embed(description="Vui lòng đăng kí hoặc đăng nhập \n \n <a:warn:1268085072767090790> | lưu ý: tuyệt đối không được để lộ hoặc chia sẻ id tài khoản và mật khẩu cho người khác!", 
                              color=discord.Color.green())
        view = TKView(ctx)
        await ctx.send(embed=embed, view=view)

webhook_bank = 'https://discordapp.com/api/webhooks/1333437569073152021/rZioIe6y7penpbgzZS4kSfpkOdg7KtbvcIf_jrtAZs2ZMF5DKAXfd8wITPY4xlEt-Spf'

async def send_bank_webhook(content, embed=None):
    async with aiohttp.ClientSession() as session:
        payload = {'content': content}
        if embed:
            payload['embeds'] = [embed.to_dict()]
        async with session.post(webhook_bank, json=payload) as response:
            if response.status != 204:
                print(f"Failed to send log to webhook: {response.status}, {await response.text()}")

class GuiTienModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Gửi tiền")
        self.ctx = ctx
        self.name_input = TextInput(label="Hãy số tiền bạn muốn gửi", placeholder="Số tiền", required=True)
        self.add_item(self.name_input)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_tk()  # Loads bank data
        econ = load_econ()  # Loads econ data
        user_id = str(self.ctx.author.id)
        coin = int(self.name_input.value)

        if coin < 1:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn phải gửi ít nhất 1 <:mlcoin:1330026986667769867>.", ephemeral=True)
            return

        if user_id not in econ:
            econ[user_id] = {'cash': 0, 'last_daily_claim': datetime.utcnow().isoformat(), 'dailied': False}
        
        if econ[user_id]['cash'] < coin:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không đủ <:mlcoin:1330026986667769867> để gửi.", ephemeral=True)
            return

        econ[user_id]['cash'] -= coin  # Subtract from user's cash
        # Find the user in the bank data who is logged in
        logged_in_user = next((user_info for user_info in data if user_info.get('logined') == user_id), None)

        if logged_in_user:
            # If the user is logged in, add the coins to their bank
            logged_in_user['bank'] += coin
            save_econ(econ)  # Saves updated econ data
            save_tk(data)  # Saves updated bank data
            await interaction.response.send_message("<:checked:1307210920082145330> | Bạn đã gửi tiền thành công.", ephemeral=True)
        else:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn chưa đăng nhập.", ephemeral=True)
        
        embed=discord.Embed(title="Giao dịch mới (gửi tiền)",description=f"**ID:** {logged_in_user['id']} \n **Người thực hiện:** {self.ctx.author.mention} ({self.ctx.author.id}) \n **Số tiền:** {coin}",color=discord.Color.yellow())
        await send_bank_webhook(content="",embed=embed)

class RutTienModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Rút tiền")
        self.ctx = ctx
        self.name_input = TextInput(label="Hãy số tiền bạn muốn rút", placeholder="Số tiền", required=True)
        self.add_item(self.name_input)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_tk()  # Loads bank data
        econ = load_econ()  # Loads econ data
        user_id = str(self.ctx.author.id)
        coin = int(self.name_input.value)

        if coin < 1:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn phải rút ít nhất 1 <:mlcoin:1330026986667769867>.", ephemeral=True)
            return

        if user_id not in econ:
            econ[user_id] = {'cash': 0, 'last_daily_claim': datetime.utcnow().isoformat(), 'dailied': False}

        # Tìm người dùng đã đăng nhập trong data
        logged_in_user = next((user_info for user_info in data if user_info.get('logined') == user_id), None)

        if not logged_in_user:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn chưa đăng nhập.", ephemeral=True)
            return

        # Kiểm tra số dư trong bank của người dùng đã đăng nhập
        if logged_in_user['bank'] < coin:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không đủ <:mlcoin:1330026986667769867> để rút.", ephemeral=True)
            return

        logged_in_user['bank'] -= coin  # Trừ tiền từ bank của người dùng đã đăng nhập
        econ[user_id]['cash'] += coin  # Cộng tiền vào cash của user trong econ

        save_econ(econ)  # Lưu lại dữ liệu econ
        save_tk(data)  # Lưu lại dữ liệu bank

        await interaction.response.send_message("<:checked:1307210920082145330> | Bạn đã rút tiền thành công.", ephemeral=True)

        embed=discord.Embed(title="Giao dịch mới (rút tiền)",description=f"**ID:** {logged_in_user['id']} \n **Người thực hiện:** {self.ctx.author.mention} ({self.ctx.author.id}) \n **Số tiền:** {coin}",color=discord.Color.yellow())
        await send_bank_webhook(content="",embed=embed)

class ChuyenTienModal(Modal):
    def __init__(self, ctx):
        super().__init__(title="Chuyển tiền")
        self.ctx = ctx
        self.name_input = TextInput(label="Hãy nhập ID người muốn chuyển", placeholder="ID (6 chữ số)", required=True)
        self.name_input1 = TextInput(label="Hãy nhập số tiền muốn chuyển", placeholder="Số tiền", required=True)
        self.add_item(self.name_input)
        self.add_item(self.name_input1)

    async def on_submit(self, interaction: discord.Interaction):
        data = load_tk()  # Tải dữ liệu tài khoản
        user_id = str(self.ctx.author.id)
        receiver_id = self.name_input.value
        coin = int(self.name_input1.value)

        # Kiểm tra số tiền hợp lệ
        if coin < 1:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn phải chuyển ít nhất 1 <:mlcoin:1330026986667769867>.", ephemeral=True)
            return

        # Tìm tài khoản người gửi đã đăng nhập
        sender = next((user for user in data if user.get('logined') == user_id), None)
        if not sender:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn chưa đăng nhập tài khoản.", ephemeral=True)
            return

        # Tìm người nhận
        receiver = next((user for user in data if user.get('id') == receiver_id), None)
        if not receiver:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Không tìm thấy tài khoản người nhận.", ephemeral=True)
            return

        # Kiểm tra số dư của người gửi
        if sender['bank'] < coin:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không đủ <:mlcoin:1330026986667769867> để chuyển.", ephemeral=True)
            return

        # Cập nhật dữ liệu
        sender['bank'] -= coin
        receiver['bank'] += coin

        save_tk(data)  # Lưu lại dữ liệu

        await interaction.response.send_message(
            f"<:checked:1307210920082145330> | Bạn đã chuyển thành công {coin} <:mlcoin:1330026986667769867> tới ID: {receiver_id}.",
            ephemeral=True
        )

        embed=discord.Embed(title="Giao dịch mới (chuyển tiền)",description=f"**ID gửi:** {sender['id']} \n **ID nhận:** {receiver['id']} \n **Số tiền:** {coin}",color=discord.Color.yellow())
        await send_bank_webhook(content="",embed=embed)

class BankView(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="Gửi tiền", style=discord.ButtonStyle.blurple)
    async def gui_tien(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        modal = GuiTienModal(self.ctx)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Rút tiền", style=discord.ButtonStyle.blurple)
    async def rut_tien(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        modal = RutTienModal(self.ctx)
        await interaction.response.send_modal(modal)
    
    @discord.ui.button(label="Chuyển tiền", style=discord.ButtonStyle.blurple)
    async def chuyen_tien(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        modal = ChuyenTienModal(self.ctx)
        await interaction.response.send_modal(modal)

@bot.command(name="bank", help="Xem ngân hàng")
async def bank(ctx):
    data = load_tk()  # Tải dữ liệu tài khoản từ tệp
    user_id = str(ctx.author.id)

    # Tìm tài khoản đăng nhập hiện tại của người dùng
    logged_account = next((account for account in data if account.get('logined') == user_id), None)

    if not logged_account:
        await ctx.send("<:cancel:1307210917594796032> | Bạn cần đăng nhập tài khoản để sử dụng bank.")
        return

    # Lấy số tiền trong ngân hàng của tài khoản đăng nhập
    current_balance = logged_account.get('bank', 0)

    # Định dạng số tiền với dấu chấm ngăn cách mỗi 3 chữ số
    formatted_cash = f"{current_balance:,d}".replace(",", ".")

    # Gửi embed với thông tin tài khoản
    embed = discord.Embed(
        description=f"<a:mlcash:1266979222816296980> | Bạn đang có **__{formatted_cash}__** trong tài khoản.",
        color=discord.Color.green()
    )
    view = BankView(ctx)
    await ctx.send(embed=embed, view=view)

@bot.command(aliases=["as"])
async def addstaff(ctx , member: str , type: str):
    # Try to get the member from a mention or ID
    try:
        if member.startswith("<@") and member.endswith(">"):  # Mention case (@user)
            member_id = int(member[2:-1]) if member[2] != "!" else int(member[3:-1])  # Remove the <@! and > part
            member = await ctx.guild.fetch_member(member_id)
        else:  # Member ID case
            member = await ctx.guild.fetch_member(int(member))
        
        data = load_manage_id()
        member_id = str(member.id)

        if data == {}:
            data = {'owner_id': [], "admin_id": [],"tester_id": []}

        # Check if author has the correct permissions
        if ctx.author.id in [847341889015644171, 925963869271240744, 1213350197149827074]:
            # Check if the member is not already in the lists
            if type == "owner":
                if member_id not in data['owner_id']:
                    data['owner_id'].append(member_id)
                    await ctx.send(f"<:checked:1307210920082145330> | Đã thêm {member.display_name} vào danh sách {type} bot")
                else:
                    await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} đã là {type} bot")
            elif type == "admin":
                if member_id not in data['admin_id']:
                    data['admin_id'].append(member_id)
                    await ctx.send(f"<:checked:1307210920082145330> | Đã thêm {member.display_name} vào danh sách {type} bot")
                else:
                    await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} đã là {type} bot")
            elif type == "tester":
                if member_id not in data['tester_id']:
                    data['tester_id'].append(member_id)
                    await ctx.send(f"<:checked:1307210920082145330> | Đã thêm {member.display_name} vào danh sách {type} bot")
                else:
                    await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} đã là {type} bot")
            else:
                await ctx.send(f"<:cancel:1307210917594796032> | {type} không tồn tại.")
            
            save_manage_id(data)
        else:
            await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền dùng lệnh này.")
    
    except Exception as e:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng.")

@bot.command(aliases=["rs"])
async def removestaff(ctx , member: str , type: str):
    # Try to get the member from a mention or ID
    try:
        if member.startswith("<@") and member.endswith(">"):  # Mention case (@user)
            member_id = int(member[2:-1]) if member[2] != "!" else int(member[3:-1])  # Remove the <@! and > part
            member = await ctx.guild.fetch_member(member_id)
        else:  # Member ID case
            member = await ctx.guild.fetch_member(int(member))
        
        data = load_manage_id()
        member_id = str(member.id)

        if data == {}:
            data = {'owner_id': [], "admin_id": [],"tester_id": []}

        # Check if author has the correct permissions
        if ctx.author.id in [847341889015644171, 925963869271240744, 1213350197149827074]:
            # Check if the member is in the lists
            if type == "owner":
                if member_id in data['owner_id']:
                    data['owner_id'].remove(member_id)
                    await ctx.send(f"<:checked:1307210920082145330> | Đã xóa {member.display_name} vào khỏi sách {type} bot")
                else:
                    await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} không phải là {type} bot")
            elif type == "admin":
                if member_id in data['admin_id']:
                    data['admin_id'].remove(member_id)
                    await ctx.send(f"<:checked:1307210920082145330> | Đã xóa {member.display_name} vào khỏi sách {type} bot")
                else:
                    await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} không phải là {type} bot")
            elif type == "tester":
                if member_id in data['tester_id']:
                    data['tester_id'].remove(member_id)
                    await ctx.send(f"<:checked:1307210920082145330> | Đã xóa {member.display_name} vào khỏi sách {type} bot")
                else:
                    await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} không phải là {type} bot")

            save_manage_id(data)
        else:
            await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền dùng lệnh này.")
    
    except Exception as e:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng.")
ongoing_transactions = {}
econ_data = load_econ()
@bot.command(name='send', description='Chuyển tiền cho người dùng')  
async def send(ctx, user: discord.User = None, amount: int = None):  
    if amount <= 0:  
        await ctx.send('Số tiền không hợp lệ! Vui lòng nhập một số dương.')  
        return  
 
    if ctx.author.id == user.id:  
        await ctx.send(f'**💳 | {ctx.author.mention}** đã gửi **{amount} mlcoin** cho... **{user.mention}**... *nhưng... tại sao lại vậy?*')  
        return  
 
    if user.bot:  
        await ctx.send(f":no_entry_sign: | **{ctx.author.display_name},** Bạn không thể gửi mlcoin cho bot!", delete_after=5)  
        return  
    if check_ongoing(ctx.author.id, user.id):  
        await ctx.send(f':no_entry_sign: | **{user.mention}** đã có một giao dịch mlcoin đang diễn ra!', delete_after=5)  
        return  

    add_ongoing(ctx.author.id, user.id) 

    confirmation_view = View(timeout=900)  
    confirm_button = Button(label='Xác nhận', emoji="<:checked:1261242796916998144>", style=discord.ButtonStyle.success)  
    decline_button = Button(label='Hủy bỏ', emoji="<:cancel:1261242787353858120>", style=discord.ButtonStyle.danger)  
    async def confirm_callback(interaction):  
        success = await send_money(ctx.author, user, amount)  
        if success:  
            await interaction.response.edit_message(content=f'**💳 | {ctx.author.mention}** đã chuyển **{amount} mlcoin** cho **{user.mention}**!', view=None, embed=None)  
        else:  
            await interaction.response.edit_message(content=f'**:no_entry_sign: | ****{ctx.author.mention}** không có đủ mlcoin để hoàn thành giao dịch này.', view=None, embed=None, delete_after=7)  
        remove_ongoing(ctx.author.id, user.id)  

    async def decline_callback(interaction): 
        embed.color = 0xFF0000 
        await interaction.response.edit_message(content=f'**{ctx.author.mention},** đã hủy bỏ giao dịch.', view=None, embed=embed)  
        remove_ongoing(ctx.author.id, user.id)  
    confirm_button.callback = confirm_callback  
    decline_button.callback = decline_callback  
    confirmation_view.add_item(confirm_button)  
    confirmation_view.add_item(decline_button)   

    embed = discord.Embed(  
        description=(  
            f"\nĐể xác nhận giao dịch này, hãy nhấn <:checked:1338409935150518356> Xác nhận." +  
            f"\nĐể hủy bỏ giao dịch này, hãy nhấn <:cancel:1338409962229203007> Hủy bỏ." +  
            f"\n\n⚠️*Việc trao đổi tiền đồng lấy bất cứ thứ gì có giá trị bằng tiền là trái với quy định của chúng tôi. Điều này bao gồm tiền thật, tiền điện tử, nitro hoặc bất cứ thứ gì tương tự. Bạn sẽ bị* ***cấm*** *cho việc làm này.*" +  
            f"\n\n**<@{ctx.author.id}> sẽ gửi <@{user.id}>:**" +  
            f"\n```fix\n{amount} mlcoin\n```"  
        ),  
        color=0x73dafa  
    ) 
    embed.set_author(name=f"{ctx.author.display_name}, Bạn sắp chuyển mlcoin cho {user.display_name}", icon_url=ctx.author.avatar.url) 
    embed.timestamp = datetime.now(timezone.utc)
    message = await ctx.send(embed=embed, view=confirmation_view)
    def check(interaction):  
        return interaction.user == ctx.author and interaction.message.id == message.id  

    try:  
        await bot.wait_for('interaction', timeout=60, check=check)  
    except asyncio.TimeoutError:  
        embed.color = 0x808080  
        confirmation_view.children[0].disabled = True  
        confirmation_view.children[1].disabled = True  
        cts = f'⚠️ Tin nhắn này hiện đã không còn hoạt động.'  
        try:  
            await message.edit(content=cts, embed=embed, view=confirmation_view)  
        except Exception as err:  
            print(err)  
            print(f'[{message.id}] Không thể chỉnh sửa tin nhắn')  

    remove_ongoing(ctx.author.id, user.id)   
async def send_money(author, user, amount):  
    author_id = str(author.id)  

    if author_id not in econ_data or econ_data[author_id]['cash'] < amount:  
        return False  

    econ_data[author_id]['cash'] -= amount  

    user_id = str(user.id)  
    if user_id not in econ_data:  
        econ_data[user_id] = {'cash': 0}  

    econ_data[user_id]['cash'] += amount  

    save_econ(econ_data) 
    return True  
def add_ongoing(user1, user2):  
    ongoing_transactions[user1] = True  
    ongoing_transactions[user2] = True  

def remove_ongoing(user1, user2):  
    ongoing_transactions.pop(user1, None)  
    ongoing_transactions.pop(user2, None)  

def check_ongoing(user1, user2):  
    return ongoing_transactions.get(user1) or ongoing_transactions.get(user2)  
@bot.hybrid_command(name='give', description='Chuyển tiền cho người dùng')  
async def give(ctx, amount: int = None, user: discord.User = None):  
    if amount <= 0:  
        await ctx.send('Số tiền không hợp lệ! Vui lòng nhập một số dương.')  
        return  
 
    if ctx.author.id == user.id:  
        await ctx.send(f'**💳 | {ctx.author.mention}** đã gửi **{amount} mlcoin** cho... **{user.mention}**... *nhưng... tại sao lại vậy?*')  
        return  
 
    if user.bot:  
        await ctx.send(f":no_entry_sign: | **{ctx.author.display_name},** Bạn không thể gửi mlcoin cho bot!", delete_after=5)  
        return  
    if check_ongoing(ctx.author.id, user.id):  
        await ctx.send(f':no_entry_sign: | **{user.mention}** đã có một giao dịch mlcoin đang diễn ra!', delete_after=5)  
        return  

    add_ongoing(ctx.author.id, user.id) 

    confirmation_view = View(timeout=900)  
    confirm_button = Button(label='Xác nhận', emoji="<:checked:1261242796916998144>", style=discord.ButtonStyle.success)  
    decline_button = Button(label='Hủy bỏ', emoji="<:cancel:1261242787353858120>", style=discord.ButtonStyle.danger)  
    async def confirm_callback(interaction):  
        success = await send_money(ctx.author, user, amount)  
        if success: 
            await asyncio.sleep(1) 
            await interaction.response.edit_message(content=f'**💳 | {ctx.author.mention}** đã chuyển **{amount} mlcoin** cho **{user.mention}**!', view=None, embed=None)  
        else:  
            await interaction.response.edit_message(content=f'**:no_entry_sign: | ****{ctx.author.mention}** không có đủ mlcoin để hoàn thành giao dịch này.', view=None, embed=None, delete_after=7)  
        remove_ongoing(ctx.author.id, user.id)  

    async def decline_callback(interaction): 
        embed.color = 0xFF0000 
        await interaction.response.edit_message(content=f'**{ctx.author.mention},** đã hủy bỏ giao dịch.', view=None, embed=embed)  
        remove_ongoing(ctx.author.id, user.id)  
    confirm_button.callback = confirm_callback  
    decline_button.callback = decline_callback  
    confirmation_view.add_item(confirm_button)  
    confirmation_view.add_item(decline_button)   

    embed = discord.Embed( 
        description=(  
            f"\nĐể xác nhận giao dịch này, hãy nhấn <:checked:1338409935150518356> Xác nhận." +  
            f"\nĐể hủy bỏ giao dịch này, hãy nhấn <:cancel:1338409962229203007> Hủy bỏ." +  
            f"\n\n⚠️*Việc trao đổi tiền đồng lấy bất cứ thứ gì có giá trị bằng tiền là trái với quy định của chúng tôi. Điều này bao gồm tiền thật, tiền điện tử, nitro hoặc bất cứ thứ gì tương tự. Bạn sẽ bị* ***cấm*** *cho việc làm này.*" +  
            f"\n\n**<@{ctx.author.id}> sẽ gửi <@{user.id}>:**" +  
            f"\n```fix\n{amount} mlcoin\n```"  
        ),  
        color=0x73dafa  
    ) 
    embed.set_author(name=f"{ctx.author.display_name}, Bạn sắp chuyển mlcoin cho {user.display_name}", icon_url=ctx.author.avatar.url) 
    embed.timestamp = datetime.now(timezone.utc)
    message = await ctx.send(embed=embed, view=confirmation_view)
    def check(interaction):  
        return interaction.user == ctx.author and interaction.message.id == message.id  

    try:  
        await bot.wait_for('interaction', timeout=60, check=check)  
    except asyncio.TimeoutError:  
        embed.color = 0x808080  
        confirmation_view.children[0].disabled = True  
        confirmation_view.children[1].disabled = True  
        cts = f'⚠️ Tin nhắn này hiện đã không còn hoạt động.'  
        try:  
            await message.edit(content=cts, embed=embed, view=confirmation_view)  
        except Exception as err:  
            print(err)  
            print(f'[{message.id}] Không thể chỉnh sửa tin nhắn')  

    remove_ongoing(ctx.author.id, user.id)   
async def send_money(author, user, amount):  
    author_id = str(author.id)  

    if author_id not in econ_data or econ_data[author_id]['cash'] < amount:  
        return False  

    econ_data[author_id]['cash'] -= amount  

    user_id = str(user.id)  
    if user_id not in econ_data:  
        econ_data[user_id] = {'cash': 0}  

    econ_data[user_id]['cash'] += amount  

    save_econ(econ_data) 
    return True  
def add_ongoing(user1, user2):  
    ongoing_transactions[user1] = True  
    ongoing_transactions[user2] = True  

def remove_ongoing(user1, user2):  
    ongoing_transactions.pop(user1, None)  
    ongoing_transactions.pop(user2, None)  

def check_ongoing(user1, user2):  
    return ongoing_transactions.get(user1) or ongoing_transactions.get(user2)  
@bot.command(name="work", help="Làm việc")
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    user_id = str(ctx.author.id)
    data = load_econ()
    if user_id not in data:
        data[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}
    
    cong_viec = [
        "hack nick fai fai của",
        "trộm chó của",
        "ám sát",
        "lấy trộm xe máy của",
        "đột nhập vào nhà của",
        "phá hoại công việc của",
        "gọi điện lừa đảo",
        "viết bài khen ngợi",
        "đi chơi với",
        "giúp việc cho",
        "đấu võ với",
        "bán hàng đa cấp cho",
        "vẽ bậy lên tường nhà của",
        "dọn dẹp nhà cửa cho",
        "làm trợ lý cá nhân cho",
        "lái xe taxi cho",
        "cứu mạng",
        "làm bữa tối cho",
        "đóng giả làm bạn thân của",
        "đi mua đồ hộ"
        ]

    all_members = [member for member in ctx.guild.members if member != ctx.author]

    doi_tuong = random.choice(all_members)

    cong_viec_random = random.choice(cong_viec)

    work_coin = random.randint(100, 1000)

    data[user_id]['cash'] += work_coin

    save_econ(data)

    await ctx.send(f"Bạn đã {cong_viec_random} {doi_tuong} và nhận được **{work_coin}** <:mlcoin:1330026986667769867>")

@bot.command(name="coinflip", aliases=["cf"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def coinflip(ctx, amount: int,choose:str="head"):
    user_id = str(ctx.author.id)
    data = load_econ()

    if user_id not in data:
        data[user_id] = {'cash': 0,'last_daily_claim': datetime.now(timezone.utc).isoformat(),'dailied': False}

    if data[user_id]['cash'] < amount:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có đủ tiền để cược.")
        return

    if amount < 1:
        await ctx.send("<:cancel:1307210917594796032> | Bạn cần cược ít nhất **1** <:mlcoin:1330026986667769867>.>")
        return

    result_msg = f"**{ctx.author.display_name}**, đã đặt cược {amount} <:mlcoin:1330026986667769867> và chọn {choose}\nĐồng xu đang quay... <a:mlspincoin:1330026991327379548>"
    mess = await ctx.send(result_msg)
    await asyncio.sleep(3)
    coin_flip = random.randint(1, 2)
    if coin_flip == 1:
        if random.random() < 0.7:
            win = False
        else:
            win = True
    else:
        if random.random() < 0.7:
            win = False
        else:
            win = True
    emoji = "<:ml_coin:1246279542172291163>" if win else "<:cointail:1330158583211626627>"
    if (choose == "head" and win) or (choose == "tail" and not win):
        await mess.edit(content=f"**{ctx.author.display_name}**, đã đặt cược {amount} <:mlcoin:1330026986667769867> và chọn {choose}.\nĐồng xu đang quay... {emoji} Bạn đã thắng {amount} <:ml_coin:1246279542172291163>")
        data[user_id]['cash'] += amount
    else:        
        await mess.edit(content=f"**{ctx.author.display_name}**, đã đặt cược {amount} <:mlcoin:1330026986667769867> và chọn {choose}.\nĐồng xu đang quay... {emoji} Bạn đã thua {amount} <:ml_coin:1246279542172291163>")
        data[user_id]['cash'] -= amount
    
max_bet = 250000
slot_emojis = [
    '<:eggplant:1330026969605214218>',
    '<:heart:1330042597598822503>',
    '<:cherry:1330026963989168230>',
]
moving = '<a:slot:1330023056881483879>'
cowoncy = '<:mlcoin:1330026986667769867>'

@bot.command(name="slot",help="Chơi slot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def slots(ctx, amount: str):
    user = ctx.author
    all_in = amount.lower() == 'all'
    amount = int(amount) if amount.isdigit() else 0

    if not all_in and amount <= 0:
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn phải cược ít nhất 1 <:mlcoin:1330026986667769867>.")
        return
    data = load_econ()
    user_id = str(user.id)
    if user_id not in data:
        data[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}

    user_cowoncy = data[user_id]['cash']

    if all_in:
        amount = user_cowoncy

    if amount > max_bet:
        amount = max_bet

    if user_cowoncy < amount:
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn không đủ <:mlcoin:1330026986667769867> để cược.")
        return
    rand = random.uniform(0, 100)
    win = 0
    if rand <= 33:
        win = 0 
        rslots = [slot_emojis[0]] * 3
    elif rand <= 66:
        win = amount * 2 
        rslots = [slot_emojis[1]] * 3
    else:
        win = amount 
        rslots = [slot_emojis[2]] * 3

    winmsg = f"{cowoncy} {win}" if win > 0 else f"{amount}"
    data[user_id]['cash'] += win - amount
    save_econ(data)
    machine = (
        f"**  `___SLOTS___`**\n` ` {moving} {moving} {moving} ` ` {user.display_name} bet {cowoncy} {amount}\n"
        f"  `|         |`\n  `|         |`"
    )
    message = await ctx.send(machine)

    await asyncio.sleep(1)
    machine = (
        f"**  `___SLOTS___`**\n` ` {rslots[0]} {moving} {moving} ` ` {user.display_name} bet {cowoncy} {amount}\n"
        f"  `|         |`\n  `|         |`"
    )
    await message.edit(content=machine)

    await asyncio.sleep(0.7)
    machine = (
        f"**  `___SLOTS___`**\n` ` {rslots[0]} {moving} {rslots[2]} ` ` {user.display_name} bet {cowoncy} {amount}\n"
        f"  `|         |`\n  `|         |`"
    )
    await message.edit(content=machine)

    await asyncio.sleep(1)
    machine = (
        f"**  `___SLOTS___`**\n` ` {rslots[0]} {rslots[1]} {rslots[2]} ` ` {user.display_name} bet {cowoncy} {amount}\n"
        f"  `|         |`   và bạn đã thắng {winmsg} <:mlcoin:1330026986667769867>\n"
        f"  `|         |`"
    )
    await message.edit(content=machine)

@bot.command(name="leaderboard ", aliases=['lb'])
@commands.cooldown(1, 10, commands.BucketType.user)
async def leaderboard (ctx,*,type:str):
    if type == "coin":
        data = load_econ()
        lb = sorted(data.items(), key=lambda x: x[1]["cash"], reverse=True)[:10]

        embed = discord.Embed(title="Bảng xếp hạng",
                            description="Top 10 người chơi giàu nhất",
                            color=0x00ff00)
        for i, user in enumerate(lb, start=1):
            try:
                member = await ctx.guild.fetch_member(int(user[0]))
                formatted_cash = f"{user[1]['cash']:,d}".replace(",", ".")
                embed.add_field(name=f"{i}. {member.name}",
                                value=f"{formatted_cash} <:mlcoin:1330026986667769867>",
                                inline=False)
            except discord.NotFound:
                continue
        await ctx.send(embed=embed)
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bảng xếp hạng không tồn tại")

@bot.command(name="ver", help="Xem phiên bản hiện tại của bot")
@commands.cooldown(1, 10, commands.BucketType.user)
async def ver(ctx):
    embed = discord.Embed(title="Version 4.5.3", color=discord.Color.blue())
    await ctx.send(embed=embed)

def load_giveaways():
    try:
        with open("giveaway.json", 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

def save_giveaways(giveaways):
    with open("giveaway.json", 'w') as file:
        json.dump(giveaways, file, indent=4)

def load_giveaways_data():
    try:
        with open("giveaway_data.json", 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

def save_giveaways_data(giveaways):
    with open("giveaway_data.json", 'w') as file:
        json.dump(giveaways, file, indent=4)

def parse_duration(duration_str):
    match = re.match(r'(\d+)([smhd])', duration_str)
    if not match:
        return None
    value, unit = int(match.group(1)), match.group(2)
    if unit == 's':
        return value
    elif unit == 'm':
        return value * 60
    elif unit == 'h':
        return value * 3600
    elif unit == 'd':
        return value * 86400
    return None

def discord_timestamp(dt):
    return f'<t:{int(dt.timestamp())}:R>'

@bot.hybrid_command(name="sga", help="Tạo một giveaway")
@commands.has_permissions(manage_messages=True)
@commands.cooldown(1, 20, commands.BucketType.user)
async def start_giveaway(ctx, duration: str, num_winners: int, *, giveaway_name: str):
    giveaways_data = load_giveaways_data()
    guild_id = str(ctx.guild.id)
    allowed_roles = giveaways_data.get(guild_id, {}).get("allowed_roles", [])
    user_roles = [role.id for role in ctx.author.roles]
    banga = load_banga()
    user_id = str(ctx.author.id)
    server_id = str(ctx.guild.id)
    
    if 'guild' in banga and server_id in banga['guild'] and user_id in banga['guild'][server_id]:
        await ctx.send("<:cancel:1307210917594796032> | Bạn đã bị cấm tạo giveaway trong máy chủ này.")
        return
    if 'global' in banga and user_id in banga['global']:
        await ctx.send("<:cancel:1307210917594796032> | Bạn đã bị cấm tạo giveaway trên toàn cầu.")
        return

    seconds = parse_duration(duration)
    if seconds is None:
        await ctx.send("Thời gian không hợp lệ! Vui lòng sử dụng định dạng <s/m/h/d>.")
        return

    end_time_utc = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    end_time_vn = end_time_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=7)))

    embed = discord.Embed(
        title=f"**{giveaway_name}**",
        description=(
            f"<a:bia:1330026957567557694> Nhấn emoji <a:ga:1330044906043084912> bên dưới để tham gia!\n"
            f"<a:clock:1330026965750644836> Đếm ngược: {discord_timestamp(end_time_vn)}\n"
            f"<:comet:1330044904231145492> Tổ chức bởi: {ctx.author.mention}"),
        color=discord.Color.yellow()
    )

    guild = ctx.guild.name
    icon = ctx.guild.icon.url if ctx.guild.icon else 'https://media.discordapp.net/attachments/1260159594349596775/1335107287219572807/png.png?ex=679ef70e&is=679da58e&hm=f5a1ffd093c15b28e4953fba504fd131108d362a1004832b789d93d1ff447c01&=&format=webp&quality=lossless&width=202&height=202'

    embed.set_footer(text=f"Giveaways với {num_winners} giải")
    embed.timestamp = end_time_vn
    embed.set_author(name=ctx.guild.name, icon_url=icon)
    embed.set_thumbnail(url=ctx.author.avatar.url)

    message = await ctx.send(content=f"<a:vayduoi1:1330027026131980348> **GIVEAWAY ĐÃ BẮT ĐẦU** <a:vayduoi2:1330027027876806758>", embed=embed)
    await message.add_reaction("<:417968419984375808:1310061529860673617>")

    giveaway = load_giveaways()
    giveaway[str(message.id)] = {
        "message_id": message.id,
        "channel_id": ctx.channel.id,
        "num_winners": num_winners,
        "name": giveaway_name,
        "author_id": ctx.author.id,
        "end_time": end_time_utc.timestamp(),
        "active": True
    }
    save_giveaways(giveaway)

    await ctx.message.delete()

    print(f"{Fore.YELLOW}[LOG]{Style.RESET_ALL} Đợi {seconds} giây để kết thúc giveaway ID {message.id}")

    await asyncio.sleep(seconds)

    if giveaway.get(str(message.id), {}).get("active", False):
        print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Đang gọi hàm end_giveaway cho ID {message.id}")
        await end_giveaway(ctx, message.id, guild, icon)
    else:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Giveaway {message.id} đã bị hủy trước thời gian kết thúc.")


@bot.command(name="endgiveaway", help="Kết thúc một giveaway", aliases=['ega', 'endga'])
async def end_giveaway_command(ctx, message_id: str):
    giveaway = load_giveaways()
    match = re.match(r'.*/channels/\d+/(\d+)/(\d+)', message_id)
    guild = ctx.guild.name
    icon =  ctx.guild.icon.url if ctx.guild.icon else 'https://media.discordapp.net/attachments/1260159594349596775/1335107287219572807/png.png?ex=679ef70e&is=679da58e&hm=f5a1ffd093c15b28e4953fba504fd131108d362a1004832b789d93d1ff447c01&=&format=webp&quality=lossless&width=202&height=202'
    if match:
        message_id = int(match.group(2))
    elif message_id.isdigit():
        message_id = int(message_id)
    else:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy giveaway.")
        return

    if str(message_id) in giveaway:
        if giveaway[str(message_id)]["author_id"] == ctx.author.id:
            await end_giveaway(ctx, message_id, guild, icon)
        else:
            await ctx.send("<:cancel:1307210917594796032> | Bạn không thể kết thúc giveaway này.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy giveaway.")  
# Hàm kết thúc giveaway
async def end_giveaway(ctx, message_id, guild, icon):
    print(f"{Fore.YELLOW}[LOG]{Style.RESET_ALL} Bắt đầu kết thúc giveaway {message_id}")

    giveaway_data = load_giveaways()
    if str(message_id) not in giveaway_data:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Không tìm thấy giveaway ID {message_id} trong dữ liệu.")
        return

    giveaway = giveaway_data[str(message_id)]
    if not giveaway["active"]:
        print(f"{Fore.YELLOW}[LOG]{Style.RESET_ALL} Giveaway {message_id} đã kết thúc trước đó.")
        return

    giveaway["active"] = False
    save_giveaways(giveaway_data)

    channel = bot.get_channel(giveaway["channel_id"])
    if not channel:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Không tìm thấy kênh có ID {giveaway['channel_id']}.")
        return

    try:
        message = await channel.fetch_message(giveaway["message_id"])
    except discord.NotFound:
        print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} Không tìm thấy tin nhắn giveaway ID {message_id}.")
        return

    num_winners = giveaway["num_winners"]

    banga = load_banga()
    server_id = str(channel.guild.id)

    users = []
    for reaction in message.reactions:
        if str(reaction.emoji) == "<:417968419984375808:1310061529860673617>":
            users = [user async for user in reaction.users() if not user.bot]
            break

    banned_users_guild = set(banga.get('guild', {}).get(server_id, []))
    banned_users_global = set(banga.get('global', []))

    participants = [user for user in users if str(user.id) not in banned_users_guild and str(user.id) not in banned_users_global]

    if participants:
        winners = random.sample(participants, min(len(participants), num_winners))
        winners_mentions = ", ".join([winner.mention for winner in winners])

        author = await bot.fetch_user(giveaway["author_id"])
        embed = discord.Embed(
            title=giveaway["name"],
            description=f"<:comet:1330044904231145492> **Xin Chúc Mừng**\nNgười thắng: {winners_mentions}\nTổ chức bởi: {author.mention}",
            color=discord.Color.orange()
        )
        embed.set_author(name=f"{guild}", icon_url=icon)
        if winners:
            embed.set_thumbnail(url=winners[0].avatar.url)

        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        embed.set_footer(text=f"Kết thúc lúc")
        embed.timestamp = vietnam_tz

        await message.edit(content=f" **GIVEAWAY ĐÃ KẾT THÚC** ", embed=embed)
        await message.channel.send(f"Xin chúc mừng **{winners_mentions}** đã thắng giveaway **{giveaway['name']}** tổ chức bởi {author.mention}!")
    else:
        author = await bot.fetch_user(giveaway["author_id"])
        embed = discord.Embed(
            title=giveaway["name"],
            description=f"<:comet:1330044904231145492> Không có ai tham gia giveaway.\nTổ chức bởi: {author.mention}",
            color=discord.Color.default()
        )
        await message.edit(content=f" **GIVEAWAY ĐÃ KẾT THÚC**", embed=embed)

    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} Giveaway {message_id} đã kết thúc thành công.")
@bot.command(name="rrga", help="Reroll giveaway")
@commands.has_permissions(manage_messages=True)
async def reroll_giveaway_command(ctx, message_id: str):
    giveaway_data = load_giveaways()
    match = re.match(r'.*/channels/\d+/(\d+)/(\d+)', message_id)
    if match:
        message_id = int(match.group(2))
    elif message_id.isdigit():
        message_id = int(message_id)
    else:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy giveaway.")
        return
    if str(message_id) not in giveaway_data:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy giveaway.")
        return
    if giveaway_data[str(message_id)]['author_id'] != ctx.author.id:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không thể reroll giveaway này.")
        return
    giveaway = giveaway_data[str(message_id)]
    if giveaway["active"]:
        await ctx.send("<:cancel:1307210917594796032> | Giveaway chưa kết thúc.")
        return
    channel = bot.get_channel(giveaway["channel_id"])
    message = await channel.fetch_message(giveaway["message_id"])
    banga = load_banga()
    server_id = str(channel.guild.id)
    users = [user async for user in message.reactions[0].users() if user != bot.user]
    banned_users_guild = set(banga.get('guild', {}).get(server_id, []))
    banned_users_global = set(banga.get('global', []))
    participants = [user for user in users if str(user.id) not in banned_users_guild and str(user.id) not in banned_users_global]

    if len(participants) > 0:
        new_winner = random.choice(participants)
        author = await bot.fetch_user(giveaway["author_id"])

        embed = discord.Embed(
            title=giveaway["name"],
            description=(f"<:comet:1330044904231145492> Người thắng mới: {new_winner.mention}\n"
                         f"<a:bia:1330026957567557694> Tổ chức bởi: {author.mention}"),
            color=discord.Color.orange()
        )
        embed.set_thumbnail(url=new_winner.avatar.url)

        vietnam_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        end_time_vn = datetime.fromtimestamp(giveaway['end_time'], vietnam_tz)
        embed.set_footer(text=f"Reroll lúc")
        embed.timestamp = vietnam_tz

        await message.edit(content=f"<a:ga:1330044906043084912> **GIVEAWAY ĐÃ REROLL** <a:ga:1330044906043084912>", embed=embed)
        await message.channel.send(f"<a:ga:1330044906043084912> Chúc mừng **{new_winner.mention}** đã thắng **{giveaway['name']}** tổ chức bởi {author.mention}")
    
@bot.command(name="fga", help="Tạo nhiều giveaway flash cùng lúc")
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 30, commands.BucketType.user)
async def giveaway_flash(ctx, num_giveaways: int, duration: str, num_winners: int, *, giveaway_name: str):
    if num_giveaways > 10:
        await ctx.send("<:cancel:1307210917594796032> | Số lượng flash giveaway tối đa là 10.")
        return
    seconds = parse_duration(duration)
    guild = ctx.guild.name
    icon = ctx.guild.icon.url if ctx.guild.icon else 'https://media.discordapp.net/attachments/1260159594349596775/1335107287219572807/png.png?ex=679ef70e&is=679da58e&hm=f5a1ffd093c15b28e4953fba504fd131108d362a1004832b789d93d1ff447c01&=&format=webp&quality=lossless&width=202&height=202'
    message_ids = []
    for i in range(num_giveaways):
        giveaway_name_with_index = f"{giveaway_name} #{i + 1}"
        message = await create_flash_giveaway(ctx, seconds, num_winners, giveaway_name_with_index, icon, guild)
        if message:
            message_ids.append(message.id)
    await ctx.message.delete()
    for message_id in message_ids:
        asyncio.create_task(end_giveaway_after_delay(ctx, message_id, seconds, icon, guild))

async def end_giveaway_after_delay(ctx, message_id, seconds, icon, guild):
    await asyncio.sleep(seconds)
    await end_giveaway(ctx, message_id, icon, guild)

async def create_flash_giveaway(ctx, seconds, num_winners, giveaway_name, icon, guild):
    try:
        end_time_utc = datetime.now(timezone.utc) + timedelta(seconds=seconds)
        end_time_vn = end_time_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=7)))
        embed.set_author(name=guild, icon_url=icon)
        embed = discord.Embed(
            title=f"**{giveaway_name}**",
            description=(f"<a:bia:1330026957567557694> Nhấn emoji <a:ml_ga:1247414297756303460> bên dưới để tham gia!\n"
                         f"<a:clock:1330026965750644836> Đếm ngược: {discord_timestamp(end_time_vn)}\n"
                         f"<:comet:1330044904231145492> Tổ chức bởi: {ctx.author.mention}"),
            color=discord.Color.yellow()
        )

        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        created_at_vn = ctx.message.created_at.astimezone(vn_tz)

        embed.set_footer(text=f"Giveaways với {num_winners} giải")
        embed.timestamp = created_at_vn
        embed.set_thumbnail(url=ctx.author.avatar.url)

        # Send the giveaway message
        message = await ctx.send(content=f"<a:vayduoi1:1330027026131980348> **GIVEAWAY ĐÃ BẮT ĐẦU** <a:vayduoi2:1330027027876806758>", embed=embed)
        await message.add_reaction("<a:ga:1330044906043084912>")

        # Load the existing giveaways
        giveaway = load_giveaways()

        # Store the giveaway details with a unique message ID
        giveaway[str(message.id)] = {
            "message_id": message.id,
            "channel_id": ctx.channel.id,
            "num_winners": num_winners,
            "name": giveaway_name,
            "author_id": ctx.author.id,
            "end_time": end_time_utc.timestamp(),
            "active": True
        }

        # Save the updated giveaways
        save_giveaways(giveaway)

        return message  # Return the message object for later use

    except Exception as e:
        print(f"Error in giveaway {giveaway_name}: {e}")
        return None

def load_ga_config():
    try:
        with open("ga_config.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_ga_config(data):
    with open("ga_config.json", "w") as file:
        json.dump(data, file, indent=2)

class SetGiveawayChannel1View(View):
    def __init__(self, ctx, channel):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.channel = channel

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        data[guild_id]['channel']['channel_1'] = channel_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Kênh giveaway 1 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_1']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Kênh giveaway 1 đã được đặt là kênh <#{data[guild_id]['channel']['channel_1']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayChannel2View(View):
    def __init__(self, ctx, channel):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.channel = channel

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        data[guild_id]['channel']['channel_2'] = channel_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Kênh giveaway 2 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_2']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Kênh giveaway 2 đã được đặt là kênh <#{data[guild_id]['channel']['channel_2']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayChannel3View(View):
    def __init__(self, ctx, channel):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.channel = channel

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        data[guild_id]['channel']['channel_3'] = channel_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Kênh giveaway 3 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_3']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Kênh giveaway 3 đã được đặt là kênh <#{data[guild_id]['channel']['channel_3']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayChannel4View(View):
    def __init__(self, ctx, channel):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.channel = channel

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        data[guild_id]['channel']['channel_4'] = channel_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Kênh giveaway 4 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_4']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Kênh giveaway 4 đã được đặt là kênh <#{data[guild_id]['channel']['channel_4']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayChannel5View(View):
    def __init__(self, ctx, channel):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.channel = channel

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        data[guild_id]['channel']['channel_5'] = channel_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Kênh giveaway 5 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_5']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Kênh giveaway 5 đã được đặt là kênh <#{data[guild_id]['channel']['channel_5']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayChannelView(View):
    def __init__(self, ctx, channel):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.channel = channel

    @discord.ui.button(label="Channel 1", style=discord.ButtonStyle.green)
    async def channel_1(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        if data[guild_id]['channel']['channel_1'] != None:
            embed = discord.Embed(description=f"Kênh giveaway 1 đã được đặt là kênh <#{data[guild_id]['channel']['channel_1']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayChannel1View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['channel']['channel_1'] = channel_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Kênh giveaway 1 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_1']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Channel 2", style=discord.ButtonStyle.green)
    async def channel_2(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        if data[guild_id]['channel']['channel_2'] != None:
            embed = discord.Embed(description=f"Kênh giveaway 2 đã được đặt là kênh <#{data[guild_id]['channel']['channel_2']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayChannel2View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['channel']['channel_2'] = channel_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Kênh giveaway 2 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_2']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Channel 3", style=discord.ButtonStyle.green)
    async def channel_3(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        if data[guild_id]['channel']['channel_3'] != None:
            embed = discord.Embed(description=f"Kênh giveaway 3 đã được đặt là kênh <#{data[guild_id]['channel']['channel_3']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayChannel3View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['channel']['channel_3'] = channel_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Kênh giveaway 3 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_3']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Channel 4", style=discord.ButtonStyle.green)
    async def channel_4(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        if not is_premium(self.ctx.author.id):
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không có premium.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        if data[guild_id]['channel']['channel_4'] != None:
            embed = discord.Embed(description=f"Kênh giveaway 4 đã được đặt là kênh <#{data[guild_id]['channel']['channel_4']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayChannel4View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['channel']['channel_4'] = channel_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Kênh giveaway 4 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_4']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Channel 5", style=discord.ButtonStyle.green)
    async def channel_5(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        if not is_premium(self.ctx.author.id):
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không có premium.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        channel_id = str(self.channel.id)

        if data[guild_id]['channel']['channel_5'] != None:
            embed = discord.Embed(description=f"Kênh giveaway 5 đã được đặt là kênh <#{data[guild_id]['channel']['channel_5']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayChannel5View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['channel']['channel_5'] = channel_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Kênh giveaway 5 đã được đặt thành kênh <#{data[guild_id]['channel']['channel_5']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)

@bot.command(name="setgiveawaychannel", aliases=["setgachannel"])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def setgiveawaychannel(ctx, channel: discord.TextChannel):
    data = load_ga_config()
    guild_id = str(ctx.guild.id)

    if guild_id not in data:
        data[guild_id] = {'channel': {}, 'role': {}, 'fixgachannel': {} , 'rerollgachannel': {} , 'endgachannel': {}}
    
    if not data[guild_id]['channel']:
        data[guild_id]['channel'] = {'channel_1': None, 'channel_2': None, 'channel_3': None, 'channel_4': None, 'channel_5': None}
    
    if not data[guild_id]['fixgachannel']:
        data[guild_id]['fixgachannell'] = {'channel_1': None, 'channel_2': None, 'channel_3': None}
    
    if not data[guild_id]['rerollgachannel']:
        data[guild_id]['rerollgachannel'] = {'channel_1': None, 'channel_2': None, 'channel_3': None}
    
    if not data[guild_id]['endgachannel']:
        data[guild_id]['endgachannel'] = {'channel_1': None, 'channel_2': None, 'channel_3': None}
    
    if not data[guild_id]['role']:
        data[guild_id]['role'] = {'role_1': None, 'role_2': None, 'role_3': None, 'role_4': None, 'role_5': None}

    save_ga_config(data)
    
    view = SetGiveawayChannelView(ctx, channel)

    embed = discord.Embed(description=f"Bạn muốn đặt kênh {channel.mention} thành kênh giveaway số mấy?", color=discord.Color.yellow())

    await ctx.send(embed=embed, view=view)

class SetGiveawayRole1View(View):
    def __init__(self, ctx, role):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.role = role

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        data[guild_id]['role']['role_1'] = role_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Role giveaway 1 đã được đặt thành role <@&{data[guild_id]['role']['role_1']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Role giveaway 1 đã được đặt là role <@&{data[guild_id]['role']['role_1']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayRole2View(View):
    def __init__(self, ctx, role):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.role = role

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        data[guild_id]['role']['role_2'] = role_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Role giveaway 2 đã được đặt thành role <@&{data[guild_id]['role']['role_2']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Role giveaway 2 đã được đặt là role <@&{data[guild_id]['role']['role_2']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayRole3View(View):
    def __init__(self, ctx, role):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.role = role

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        data[guild_id]['role']['role_3'] = role_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Role giveaway 3 đã được đặt thành role <@&{data[guild_id]['role']['role_3']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Role giveaway 3 đã được đặt là role <@&{data[guild_id]['role']['role_3']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayRole4View(View):
    def __init__(self, ctx, role):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.role = role

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        data[guild_id]['role']['role_4'] = role_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Role giveaway 4 đã được đặt thành role <@&{data[guild_id]['role']['role_4']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Role giveaway 4 đã được đặt là role <@&{data[guild_id]['role']['role_4']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayRole5View(View):
    def __init__(self, ctx, role):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.role = role

    @discord.ui.button(label="Chắc chắn", style=discord.ButtonStyle.green)
    async def chac_chan(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        data[guild_id]['role']['role_5'] = role_id

        save_ga_config(data)

        embed = discord.Embed(description=f"Role giveaway 5 đã được đặt thành role <@&{data[guild_id]['role']['role_5']}>.",color=discord.Color.green())

        await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Không", style=discord.ButtonStyle.red)
    async def khong(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
    
        embed = discord.Embed(description=f"Role giveaway 5 đã được đặt là role <@&{data[guild_id]['role']['role_5']}>. \n Bạn chắc muốn đổi thành {self.channel.mention} chứ?",color=discord.Color.red())

        await interaction.response.edit_message(embed=embed,view=None)

class SetGiveawayRoleView(View):
    def __init__(self, ctx, role):
        super().__init__(timeout=None)
        self.ctx = ctx
        self.role = role

    @discord.ui.button(label="Role 1", style=discord.ButtonStyle.green)
    async def role_1(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        if data[guild_id]['role']['role_1'] != None:
            embed = discord.Embed(description=f"Role giveaway 1 đã được đặt là role <@&{data[guild_id]['role']['role_1']}>. \n Bạn chắc muốn đổi thành {self.role.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayRole1View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['role']['role_1'] = role_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Role giveaway 1 đã được đặt thành kênh <@&{data[guild_id]['role']['role_1']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Role 2", style=discord.ButtonStyle.green)
    async def role_2(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        if data[guild_id]['role']['role_2'] != None:
            embed = discord.Embed(description=f"Role giveaway 2 đã được đặt là role <@&{data[guild_id]['role']['role_2']}>. \n Bạn chắc muốn đổi thành {self.role.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayRole1View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['role']['role_2'] = role_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Role giveaway 2 đã được đặt thành kênh <@&{data[guild_id]['role']['role_2']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Role 3", style=discord.ButtonStyle.green)
    async def role_3(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        if data[guild_id]['role']['role_3'] != None:
            embed = discord.Embed(description=f"Role giveaway 3 đã được đặt là role <@&{data[guild_id]['role']['role_3']}>. \n Bạn chắc muốn đổi thành {self.role.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayRole1View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['role']['role_3'] = role_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Role giveaway 3 đã được đặt thành kênh <@&{data[guild_id]['role']['role_3']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Role 4", style=discord.ButtonStyle.green)
    async def role_4(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        if not is_premium(str(self.ctx.author.id)):
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không có premium.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        if data[guild_id]['role']['role_4'] != None:
            embed = discord.Embed(description=f"Role giveaway 1 đã được đặt là role <@&{data[guild_id]['role']['role_4']}>. \n Bạn chắc muốn đổi thành {self.role.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayRole1View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['role']['role_4'] = role_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Role giveaway 4 đã được đặt thành kênh <@&{data[guild_id]['role']['role_4']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)
    
    @discord.ui.button(label="Role 5", style=discord.ButtonStyle.green)
    async def role_5(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return

        if not is_premium(str(self.ctx.author.id)):
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không có premium.", ephemeral=True)
            return
        
        data = load_ga_config()
        guild_id = str(self.ctx.guild.id)
        role_id = str(self.role.id)

        if data[guild_id]['role']['role_5'] != None:
            embed = discord.Embed(description=f"Role giveaway 5 đã được đặt là role <@&{data[guild_id]['role']['role_5']}>. \n Bạn chắc muốn đổi thành {self.role.mention} chứ?",color=discord.Color.yellow())
            view = SetGiveawayRole1View(self.ctx,self.channel)
            await interaction.response.edit_message(embed=embed,view=view)
        else:
            data[guild_id]['role']['role_5'] = role_id

            save_ga_config(data)

            embed = discord.Embed(description=f"Role giveaway 5 đã được đặt thành kênh <@&{data[guild_id]['role']['role_5']}>.",color=discord.Color.green())

            await interaction.response.edit_message(embed=embed,view=None)

@bot.command(name="setgiveawayrole", aliases=["setgarole"])
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def set_giveaway_channel(ctx, role: str):
    data = load_ga_config()
    guild_id = str(ctx.guild.id)
    role = await get_role_from_input(role)
    if role is None:
        await ctx.send("<:cancel:1307210917594796032> | Role không tồn tại")

    if guild_id not in data:
        data[guild_id] = {'channel': {}, 'role': {}, 'fixgachannel': {} , 'rerollgachannel': {} , 'endgachannel': {}}
    
    if not data[guild_id]['channel']:
        data[guild_id]['channel'] = {'channel_1': None, 'channel_2': None, 'channel_3': None, 'channel_4': None, 'channel_5': None}
    
    if not data[guild_id]['fixgachannel']:
        data[guild_id]['fixgachannell'] = {'channel_1': None, 'channel_2': None, 'channel_3': None}
    
    if not data[guild_id]['rerollgachannel']:
        data[guild_id]['rerollgachannel'] = {'channel_1': None, 'channel_2': None, 'channel_3': None}
    
    if not data[guild_id]['endgachannel']:
        data[guild_id]['endgachannel'] = {'channel_1': None, 'channel_2': None, 'channel_3': None}
    
    if not data[guild_id]['role']:
        data[guild_id]['role'] = {'role_1': None, 'role_2': None, 'role_3': None, 'role_4': None, 'role_5': None}

    save_ga_config(data)
    
    view = SetGiveawayRoleView(ctx, channel)

    embed = discord.Embed(description=f"Bạn muốn đặt role {role.mention} thành role được tạo giveaway số mấy?", color=discord.Color.yellow())

    await ctx.send(embed=embed, view=view)

@bot.command(name="ping")
async def ping(ctx):
    try:
        start_time = time.time()
        message = await ctx.send("**<a:loading:1330026979906293821> | Đang lấy dữ liệu...**")
        
        end_time = time.time()
        system_latency = int(bot.latency * 1000)  # Độ trễ hệ thống (ms)
        ws_latency = int(bot.latency * 1000)  # Độ trễ WebSocket (ms)
        cluster_latency = ws_latency  # Độ trễ cụm (ms)
        
        # Tính toán thời gian uptime
        current_time = time.time()
        uptime_seconds = int(current_time - bot.start_time)  # Đảm bảo bot.start_time là float
        uptime = datetime.fromtimestamp(bot.start_time, tz=timezone.utc)
        
        # Lấy thời gian hiện tại theo múi giờ Việt Nam
        current_time_utc = discord.utils.utcnow()
        vn_tz = pytz.timezone('Asia/Ho_Chi_Minh')
        current_time_vn = current_time_utc.astimezone(vn_tz)
        
        # Tạo embed
        embed = discord.Embed(
            title=f"{bot.user}",
            color=discord.Color.blue()
        )
        embed.description = (
            f"* Độ Trễ Hệ Thống: `{system_latency}ms`\n"
            f"* Độ Trễ WebSocket: `{ws_latency}ms`\n"
            f"* Cluster 1: `{cluster_latency}ms`\n\n"
            f"* Uptime: <t:{int(uptime.timestamp())}:d> <t:{int(uptime.timestamp())}:R>"
        )
        embed.set_footer(text=f"Yêu cầu bởi {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_thumbnail(url=bot.user.avatar.url)
        embed.timestamp = current_time_utc

        await message.edit(content=None, embed=embed)

    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command(name="say", help="Bot nói từ bạn cho")
async def say(ctx, *, text):
    await ctx.message.delete()
    await ctx.send(text)

@bot.command(name="clear", help="Xóa tin nhắn")
@commands.has_permissions(moderate_members=True)
async def clear(ctx, amt: int):
    deleted = await ctx.channel.purge(limit=amt + 1)
    msg = await ctx.send(f"<:checked:1307210920082145330> |  Đã xóa {len(deleted) - 1} tin nhắn!")
    await msg.delete(delay=3)

@bot.command(name="ban", help="Cấm người dùng")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không thể tự cấm chính mình.")
        return

    try:
        await member.ban(reason=reason)
        await ctx.send(f"<:checked:1307210920082145330> |  **{member.name}** đã bị cấm **|** {reason}")
    except discord.Forbidden:
        await ctx.send("<:cancel:1307210917594796032> | Người này có quyền cao hơn hoặc bằng bạn.")
    except discord.HTTPException:
        await ctx.send("<:checked:1307210920082145330> | Đã xảy ra lỗi khi cố gắng cấm người dùng này.")

@bot.command(name="unban", help="Unban người dùng")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member: discord.User):
    await ctx.guild.unban(member)
    await ctx.send(f"<:checked:1307210920082145330> | {member.name} đã được gỡ lệnh cấm")

@bot.command(name="kick", help="Kick người dùng")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason=None):
    if member == ctx.author:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không thể tự kick chính mình.")
        return

    try:
        await member.kick(reason=reason)
        await ctx.send(f"<:checked:1307210920082145330> | **{member.name}** đã bị kick **|** {reason}")
    except discord.Forbidden:
        await ctx.send("<:cancel:1307210917594796032> | Người này có quyền cao hơn hoặc bằng bạn.")
    except discord.HTTPException:
        await ctx.send("<:checked:1307210920082145330> | Đã xảy ra lỗi khi cố gắng kick người dùng này.")

@bot.command(name="mute", help="Mute người dùng")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, time: str, *, reason=None):
    time_multipliers = {
        "s": 1,
        "m": 60,
        "h": 3600,
        "d": 86400
    }

    time_unit = time[-1]
    if time_unit in time_multipliers:
        try:
            if member == ctx.author:
                await ctx.send("<:cancel:1307210917594796032> | Bạn không thể mute chính mình")
                return
            duration = int(time[:-1]) * time_multipliers[time_unit]
            newtime = timedelta(seconds=duration)
            await member.edit(timed_out_until=discord.utils.utcnow() + newtime)
            await ctx.send(f"<:checked:1307210920082145330> | **{member.name}** đã bị mute **|** {reason}")
        except ValueError:
            await ctx.send("<:cancel:1307210917594796032> | Thời gian không hợp lệ.")
        except discord.Forbidden:
            await ctx.send("<:cancel:1307210917594796032> | Người này có quyền cao hơn hoặc bằng bạn.")
        except discord.HTTPException:
            await ctx.send("<:checked:1307210920082145330> | Đã xảy ra lỗi khi cố gắng mute người dùng này.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Đơn vị thời gian không hợp lệ. Vui lòng sử dụng s (giây), m (phút), h (giờ) hoặc d (ngày).")

@bot.command(name="unmute", help="Unmute người dùng")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.edit(timed_out_until=None)
    await ctx.send(f"<:checked:1307210920082145330> | **{member.name}** đã được gỡ mute")

async def get_role_from_input(ctx, role_input):
    try:
        # Check if input is a mention (either <@&role_id> or <@!role_id>)
        if role_input.startswith("<@&") and role_input.endswith(">"):
            role_id = int(role_input[3:-1])  # Extract role ID from mention
        elif role_input.startswith("<@!") and role_input.endswith(">"):
            role_id = int(role_input[3:-1])  # Extract role ID from mention
        else:
            role_id = int(role_input)  # If input is a direct role ID

        # Fetch the role from the guild
        return ctx.guild.get_role(role_id)
    except Exception:
        return None  # Return None if role is not found

@bot.command(name="addrole", help="Add role cho ai đó")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: str, role: str):
    role = await get_role_from_input(ctx,role)
    if role is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy role.")
    member = await get_member_from_input(ctx,member)
    if member is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy member.")

    if role >= ctx.author.top_role or role >= ctx.guild.me.top_role:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không thể thêm role này vì nó ngang hàng hoặc cao hơn role của bạn.")
        return

    await member.add_roles(role)
    embed = discord.Embed(
        description=f"<:checked:1307210920082145330> | Đã thêm role {role.mention} cho {member.mention}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command(name="removerole", help="Remove role của ai đó")
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: str, role: str):
    role = await get_role_from_input(ctx,role)
    if role is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy role.")
    member = await get_member_from_input(ctx,member)
    if member is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy member.")

    if role >= ctx.author.top_role or role >= ctx.guild.me.top_role:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không thể xóa role này vì nó ngang hàng hoặc cao hơn role của bạn.")
        return

    await member.remove_roles(role)
    embed = discord.Embed(
        description=f"<:checked:1307210920082145330> | Đã xóa role {role.mention} của {member.mention}.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(administrator=True)
async def roleper(ctx, role: discord.Role, perm: str, value: bool):
    perms = role.permissions
    if hasattr(perms, perm):
        setattr(perms, perm, value)
        await role.edit(permissions=perms)
        await ctx.send(f"<:checked:1307210920082145330> | Đã cập nhật quyền `{perm}` cho role {role.name} thành {value}")
    else:
        await ctx.send(f"<:cancel:1307210917594796032> | Quyền `{perm}` không tồn tại.")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def hide(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.view_channel = False
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send(f"<:checked:1307210920082145330> | Đã ẩn kênh {channel.mention}")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def show(ctx, channel: discord.TextChannel = None):
    channel = channel or ctx.channel
    overwrite = channel.overwrites_for(ctx.guild.default_role)
    overwrite.view_channel = True
    await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send(f"<:checked:1307210920082145330> | Đã hiện kênh {channel.mention}.")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_roles=True)
async def createrole(ctx, name: str, color: discord.Color = discord.Color.default()):
    guild = ctx.guild
    await guild.create_role(name=name, color=color)
    await ctx.send(f'<:checked:1307210920082145330> | Role `{name}` đã được tạo thành công.')

@bot.command()
@commands.has_permissions(manage_roles=True)
async def deleterole(ctx, role: discord.Role):
    await role.delete()
    await ctx.send(f'<:checked:1307210920082145330> | Thành công xóa role `{role.name}`')
    
@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def createchannel(ctx, name: str, channel_type: str = "text"):
    guild = ctx.guild
    if channel_type.lower() == "text":
        await guild.create_text_channel(name)
        await ctx.send(f'<:checked:1307210920082145330> | Kênh văn bản `{name}` đã được tạo thành công.')
    elif channel_type.lower() == "voice":
        await guild.create_voice_channel(name)
        await ctx.send(f'<:checked:1307210920082145330> | Kênh thoại `{name}` đã được tạo thành công.')
    else:
        await ctx.send('<:cancel:1307210917594796032> | Bot chỉ hỗ trợ "text" hoặc "voice".')

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_channels=True)
async def removechannel(ctx, channel: discord.TextChannel):
    await channel.delete()
    await ctx.send(f'<:checked:1307210920082145330> | Thành công xóa kênh `{channel.name}`')

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
@commands.has_permissions(manage_roles=True, manage_channels=True)
async def channelper(ctx, role: str, channel: discord.TextChannel, perm: str, value: bool):
    if role.lower() == 'everyone':
        target_role = ctx.guild.default_role
    else:
        target_role = discord.utils.get(ctx.guild.roles, mention=role)
    
    if not target_role:
        await ctx.send(f'<:cancel:1307210917594796032> | Role `{role}` không tồn tại.')
        return
    
    overwrite = channel.overwrites_for(target_role)
    
    if hasattr(overwrite, perm):
        setattr(overwrite, perm, value)
        await channel.set_permissions(target_role, overwrite=overwrite)
        await ctx.send(f'<:checked:1307210920082145330> | Đã cập nhật quyền `{perm}` cho role {target_role.name} trong kênh {channel.name} thành {value}.')
    else:
        await ctx.send(f'<:cancel:1261242787353858120> | Quyền `{perm}` không tồn tại.')

@bot.command(name="avt", help="Xem avatar của ai đó")
@commands.cooldown(1, 10, commands.BucketType.user)
async def avt(ctx, *, member: discord.Member = None):
    if not member:
        member = ctx.author
    userAvatar = member.avatar.url
    embed = discord.Embed(title=f"Avatar của {member}",
                          color=discord.Color.yellow())
    embed.set_image(url=userAvatar)
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author}",
                     icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

@bot.command(name="banner", help="Xem banner của ai đó")
@commands.cooldown(1, 10, commands.BucketType.user)
async def banner(ctx, *, member: discord.Member = None):
    if not member:
        member = ctx.author
    userBanner = member.banner.url
    embed = discord.Embed(title=f"Banner của {member.name}",
                          color=discord.Color.blue())
    embed.set_image(url=userBanner)
    embed.set_footer(text=f"Yêu cầu bởi {ctx.author}",
                     icon_url=ctx.author.avatar.url)
    await ctx.send(embed=embed)

# Load server_data từ file welcome.json nếu có sẵn
def load_server_data():
    global server_data
    try:
        with open('welcome.json', 'r') as f:
            server_data = json.load(f)
    except FileNotFoundError:
        server_data = {}

# Gọi hàm load_server_data khi khởi động bot
load_server_data()

@bot.event
async def on_member_join(member):
    global server_data
    guild_id = str(member.guild.id)

    if guild_id in server_data:
        welcome_channel_id = server_data[guild_id]['welcome_channel_id']
        background_image_path = server_data[guild_id]['background_image_path']
        channel = bot.get_channel(welcome_channel_id)
        welcome_message = server_data[guild_id].get('welcome_message')

        if channel is None:
            return

        # Count only members in the specified server
        member_count = member.guild.member_count
        # Load background image
        background = Editor(background_image_path)

        # Load and process profile image
        profile_image = await load_image_async(str(member.avatar.url if member.avatar else "https://t4.ftcdn.net/jpg/05/49/98/39/360_F_549983970_bRCkYfk0P6PP5fKbMhZMIb07mCJ6esXL.jpg"))
        profile = Editor(profile_image).resize((150, 150)).circle_image()

        # Paste profile image onto background
        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

        # Define fonts
        poppins = Font("Itim.ttf", size=50)
        poppins_small = Font("Itim.ttf", size=35)
        welcome_message = welcome_message.format(member=member, guild_name=member.guild.name, member_count=member_count)
        # Generate welcome message
        background.text((400, 260), 'Xin Chào', font=poppins, color='#03E5FB', align="center")
        background.text((400, 325), f'{member.name}#{member.discriminator}', font=poppins_small, color='#CEFB03', align="center")
        background.text((400, 390), f'Bạn Là Thành Viên Thứ {member_count} của server', font=poppins_small, color='lightgreen', align="center")

        # Create an embed with the demo image
        file = File(fp=background.image_bytes, filename="wcimage.png")
        embed = discord.Embed(title=welcome_message, color=0x00FF00)  # Green color
        embed.set_author(name=member.name, icon_url=member.avatar.url if member.avatar else "https://t4.ftcdn.net/jpg/05/49/98/39/360_F_549983970_bRCkYfk0P6PP5fKbMhZMIb07mCJ6esXL.jpg")
        embed.set_thumbnail(url=member.avatar.url if member.avatar else "https://t4.ftcdn.net/jpg/05/49/98/39/360_F_549983970_bRCkYfk0P6PP5fKbMhZMIb07mCJ6esXL.jpg")
        embed.set_image(url="attachment://wcimage.png")

        await channel.send(content=f"{member.mention}" , embed=embed , file=file)

@bot.command(name="setbg",help="Đặt backgound cho welcome")
@commands.has_permissions(administrator=True)
@commands.cooldown(1, 10, commands.BucketType.user)
async def setbg(ctx, url):
    guild_id = str(ctx.guild.id)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.send('<:cancel:1307210917594796032> | Tải xuống hình ảnh thất bại.')
                return
            data = BytesIO(await response.read())
            with open(f'{guild_id}_background.jpg', 'wb') as f:
                f.write(data.getbuffer())

            server_data[guild_id] = server_data.get(guild_id, {})
            server_data[guild_id]['background_image_path'] = f'{guild_id}_background.jpg'

            with open('server_data.json', 'w') as f:
                json.dump(server_data, f)

    # Send a demo image
    background = Editor(f'{guild_id}_background.jpg')
    member_count = ctx.guild.member_count  # Count all members in the server
    profile_image = await load_image_async(str(ctx.author.avatar.url))
    profile = Editor(profile_image).resize((150, 150)).circle_image()

    # Paste profile image onto background
    background.paste(profile, (325, 90))
    background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

    # Define fonts
    poppins = Font("Itim.ttf", size=50)
    poppins_small = Font("Itim.ttf", size=35)

    # Generate welcome message
    welcome_message = f'Hình ảnh xem trước cho server {ctx.guild.name}:'
    background.text((400, 260), 'Xem trước', font=poppins, color='#03FBF3', align="center")
    background.text((400, 325), f'{ctx.author.name}#{ctx.author.discriminator}', font=poppins_small, color='#CEFB03', align="center")
    background.text((400, 390), f'Tổng thành viên: {member_count}', font=poppins_small, color='lightgreen', align="center")


    file = File(fp=background.image_bytes, filename="skibidi.png")
    await ctx.send(welcome_message, file=file)
    await ctx.send('<:checked:1307210920082145330> | Đã set backgruond.')

@bot.command(name="setchannel",help="Đặt kênh để bot gửi tin nhắn welcome")
async def setchannel(ctx, channel: discord.TextChannel, *, welcome_message: str):
    guild_id = str(ctx.guild.id)
    
    # Tạo một entry mới cho server nếu chưa tồn tại
    if guild_id not in server_data:
        server_data[guild_id] = {}
    
    # Lưu welcome channel id và welcome message vào server_data
    server_data[guild_id]['welcome_channel_id'] = channel.id
    server_data[guild_id]['welcome_message'] = welcome_message
    
    # Lưu server_data vào file JSON
    with open('server_data.json', 'w') as f:
        json.dump(server_data, f)
    
    await ctx.send(f'<:checked:1307210920082145330> | Đã đặt kênh chào mừng là {channel.mention} với tin nhắn: {welcome_message}')

@bot.command(name="testwc",help="Xem tin nhắn welcome")
async def testwc(ctx):
    guild_id = str(ctx.guild.id)
    
    # Ensure the guild has a background image set
    if guild_id not in server_data or 'background_image_path' not in server_data[guild_id]:
        await ctx.send('<:cancel:1307210917594796032> | Server chưa có backguond.')
        return
    
    background_image_path = server_data[guild_id]['background_image_path']
    welcome_message = server_data[guild_id].get('welcome_message')

    # Load the background image
    background = Editor(background_image_path)
    member_count = ctx.guild.member_count  # Count all members in the server
    
    # Load and process profile image of the command invoker
    profile_image = await load_image_async(str(ctx.author.avatar.url))
    profile = Editor((profile_image)).resize((150, 150)).circle_image()

    # Paste profile image onto background
    background.paste(profile, (325, 90))
    background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

    # Define fonts
    poppins = Font("Itim.ttf", size=50)
    poppins_small = Font("Itim.ttf", size=35)
    welcome_message = welcome_message.format(member=ctx.author, guild_name=ctx.guild.name, member_count=member_count)
    # Generate welcome message
    background.text((400, 260), 'Xem trước', font=poppins, color='#03FBF3', align="center")
    background.text((400, 325), f'{ctx.author.name}#{ctx.author.discriminator}', font=poppins_small, color='#F0FB03', align="center")
    background.text((400, 390), f'Tổng thành viên: {member_count}', font=poppins_small, color='lightgreen', align="center")    

    # Create an embed with the demo image
    file = File(fp=background.image_bytes, filename="demo.png")    
    embed = discord.Embed(title=welcome_message, color=0x00FF00)  # Green color
    embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
    embed.set_image(url="attachment://demo.png")
    embed.add_field(name="Tổng thành viên", value=member_count, inline=False)
        
    # Send embed with image file
    await ctx.send(content=ctx.author.mention, embed=embed, file=file)

if os.path.exists('goodbye.json'):
    with open('goodbye.json', 'r') as f:
        server_data = json.load(f)
else:
    server_data = {}

@bot.event
async def on_member_remove(member):
    guild_id = str(member.guild.id)

    if guild_id in server_data:
        goodbye_channel_id = server_data[guild_id].get('goodbye_channel_id')
        background_image_path = server_data[guild_id].get('background_image_path')
        goodbye_message = server_data[guild_id].get('goodbye_message')

        if goodbye_channel_id is None or background_image_path is None:
            return
        channel = bot.get_channel(goodbye_channel_id)
        if channel is None:
            return

        member_count = member.guild.member_count
        try:
            background = Editor(background_image_path)
            profile_image = await load_image_async(str(member.avatar.url if member.avatar else "https://default-avatar-url.com"))
            profile = Editor(profile_image).resize((150, 150)).circle_image()

            # Position the profile image
            profile_position = (325, 50)  # Adjusted for better alignment
            background.paste(profile, profile_position)
            background.ellipse(profile_position, 150, 150, outline="white", stroke_width=5)

            # Fonts
            poppins = Font("Itim.ttf", size=50)
            poppins_small = Font("Itim.ttf", size=35)
            goodbye_message = goodbye_message.format(member=member, guild_name=member.guild.name, member_count=member_count)

            # Goodbye text positions
            background.text((400, 250), 'Tạm Biệt', font=poppins, color='#FB0303', align="center")
            background.text((400, 320), f'{member.name}#{member.discriminator}', font=poppins_small, color='#CEFB03', align="center")
            background.text((400, 390), f'Server Còn Lại {member_count} thành viên', font=poppins_small, color='lightgreen', align="center")

            file = File(fp=background.image_bytes, filename="gbimage.png")
            embed = discord.Embed(title=goodbye_message, color=0xFF0000)
            embed.set_author(name=member.name, icon_url=member.avatar.url if member.avatar else "https://default-avatar-url.com")
            embed.set_image(url="attachment://gbimage.png")

            await channel.send(embed=embed, file=file)
        except Exception as e:
            print(f"Error creating farewell image: {e}")

@bot.command(name="setgoodbyebg", help="Đặt background cho goodbyee")
async def setgoodbyebg(ctx, url):
    guild_id = str(ctx.guild.id)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status != 200:
                await ctx.send('<:cancel:1307210917594796032> | Tải xuống hình ảnh thất bại.')
                return
            data = BytesIO(await response.read())
            with open(f'{guild_id}_background.jpg', 'wb') as f:
                f.write(data.getbuffer())

            server_data[guild_id] = server_data.get(guild_id, {})
            server_data[guild_id]['background_image_path'] = f'{guild_id}_background.jpg'

            # Lưu dữ liệu vào goodbye.json
            with open('goodbye.json', 'w') as f:
                json.dump(server_data, f)

    await send_demo_image(ctx, f'{guild_id}_background.jpg')

async def send_demo_image(ctx, background_path):
    try:
        background = Editor(background_path)
        member_count = ctx.guild.member_count
        profile_image = await load_image_async(str(ctx.author.avatar.url))
        profile = Editor(profile_image).resize((150, 150)).circle_image()

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

        poppins = Font("Itim.ttf", size=50)
        poppins_small = Font("Itim.ttf", size=35)

        background.text((400, 260), 'Xem trước', font=poppins, color='#03FBF3', align="center")
        background.text((400, 325), f'{ctx.author.name}#{ctx.author.discriminator}', font=poppins_small, color='#CEFB03', align="center")
        background.text((400, 390), f'Tổng thành viên: {member_count}', font=poppins_small, color='lightgreen', align="center")

        file = File(fp=background.image_bytes, filename="skibidi.png")
        await ctx.send("Hình ảnh xem trước:", file=file)
        await ctx.send('<:checked:1307210920082145330> | Đã set backguond.')
    except Exception as e:
        await ctx.send(f"Error generating demo image: {e}")

@bot.command(name="setgoodbyechannel", help="Đặt kênh để bot gửi tin nhắn tạm biệt")
async def setgoodbyechannel(ctx, channel: discord.TextChannel, *, goodbye_message: str):
    guild_id = str(ctx.guild.id)

    server_data[guild_id] = server_data.get(guild_id, {})
    server_data[guild_id]['goodbye_channel_id'] = channel.id
    server_data[guild_id]['goodbye_message'] = goodbye_message

    # Lưu dữ liệu vào goodbye.json
    with open('goodbye.json', 'w') as f:
        json.dump(server_data, f)

    await ctx.send(f'<:checked:1307210920082145330> | Đã đặt kênh tạm biệt là {channel.mention} với tin nhắn: {goodbye_message}')

@bot.command(name="testgb", help="Xem tin nhắn tạm biệt")
async def testgb(ctx):
    guild_id = str(ctx.guild.id)

    if guild_id not in server_data or 'background_image_path' not in server_data[guild_id]:
        await ctx.send('Không tìm thấy background.')
        return

    background_image_path = server_data[guild_id]['background_image_path']
    goodbye_message = server_data[guild_id].get('goodbye_message', "Goodbye {member} from {guild_name}. There are now {member_count} members left.")

    try:
        background = Editor(background_image_path)
        member_count = ctx.guild.member_count
        profile_image = await load_image_async(str(ctx.author.avatar.url))
        profile = Editor(profile_image).resize((150, 150)).circle_image()

        background.paste(profile, (325, 90))
        background.ellipse((325, 90), 150, 150, outline="white", stroke_width=5)

        poppins = Font("Itim.ttf", size=50)
        poppins_small = Font("Itim.ttf", size=35)
        goodbye_message = goodbye_message.format(member=ctx.author, guild_name=ctx.guild.name, member_count=member_count)

        background.text((400, 260), 'Xem trước', font=poppins, color='#FB0303', align="center")
        background.text((400, 325), f'{ctx.author.name}#{ctx.author.discriminator}', font=poppins_small, color='#F0FB03', align="center")
        background.text((400, 390), f'Server Còn Lại {member_count} thành viên', font=poppins_small, color='lightgreen', align="center")

        file = File(fp=background.image_bytes, filename="gb_demo.png")
        embed = discord.Embed(title=goodbye_message, color=0xFF0000)
        embed.set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
        embed.set_image(url="attachment://gb_demo.png")

        await ctx.send(embed=embed, file=file)
    except Exception as e:
        await ctx.send(f"Error generating goodbye message: {e}")

def load_server_data():
    global server_data
    try:
        with open('goodbye.json', 'r') as f:
            server_data = json.load(f)
    except FileNotFoundError:
        server_data = {}

load_server_data()

bot.start_time2 = datetime.now(timezone.utc)
    
@bot.command(name="gopy", help="Góp ý cho bot")
async def gopy(ctx, *, gopy_text):
    await ctx.message.delete()
    gopy_channel_id = 1242994160038838272  # Replace with the actual ID of the feedback channel
    gopy_channel = bot.get_channel(gopy_channel_id)
    # Check if gopy_channel exists
    if gopy_channel:
        user_id = ctx.author.id
        server_id = ctx.guild.id  # Access the guild ID
        await gopy_channel.send(
            f'Góp ý bởi {ctx.author.name}({user_id}) tại server {server_id}: {gopy_text}'
        )
        await ctx.send("<:checked:1307210920082145330> | Góp ý của bạn đã được gửi.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Có lỗi xảy ra với kênh log.")

#report bug command
@bot.command(name="rpbug", help="Báo cáo lỗi cho chúng mình")
async def rpbug(ctx, *, rpbug_text):
    await ctx.message.delete()
    rpbug_channel_id = 1244840992574799882  # Replace with the actual ID of the feedback channel
    rpbug_channel = bot.get_channel(rpbug_channel_id)
    # Check if rpbug_channel exists
    if rpbug_channel:
        user_id = ctx.author.id
        server_id = ctx.guild.id  # Access the guild ID
        await rpbug_channel.send(
            f'Báo lỗi bởi {ctx.author.name}({user_id}) tại server {server_id}: {rpbug_text}'
        )
        await ctx.send("<:checked:1307210920082145330> | Đơn báo cáo của bạn đã được gửi.")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Có lỗi xảy ra với kênh log.")

def load_banned_users():
    try:
        with open('banned_users.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_banned_users(banned_users):
    with open('banned_users.json', 'w') as file:
        json.dump(banned_users, file)

banned_users = load_banned_users()

def is_banned(user_id):
    return str(user_id) in banned_users

@bot.check
async def globally_block_banned_users(ctx):
    if is_banned(ctx.author.id):
        message = await ctx.send(f"{ctx.author.mention} | Bạn đã bị cấm dùng bot.")
        await message.delete(delay=3)
        return False
    return True

# Helper function to get a member from mention or ID
async def get_member_from_input(ctx, member_input):
    try:
        if member_input.startswith("<@") and member_input.endswith(">"):  # Mention case (@user)
            member_id = int(member_input[2:-1]) if member_input[2] != "!" else int(member_input[3:-1])  # Handle <@!user>
            return await ctx.guild.fetch_member(member_id)
        else:  # Member ID case
            return await ctx.guild.fetch_member(int(member_input))
    except Exception as e:
        return None  # Return None if not found or invalid

# Command to ban a user from using the bot
@bot.command(aliases=["bb"])
async def banbot(ctx, member_input: str):
    data = load_manage_id()
    user_id = str(ctx.author.id)

    # Get the member object using the helper function
    member = await get_member_from_input(ctx, member_input)

    if member is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng.")
        return

    # Correct permission check: make sure the user is either owner or admin
    if user_id in data['owner_id'] or user_id in data['admin_id']:
        if is_banned(member.id):
            await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} đã bị cấm dùng bot.")
            return

        banned_users.append(str(member.id))
        save_banned_users(banned_users)
        await ctx.send(f"<:checked:1307210920082145330> | Thành công cấm {member.display_name} dùng bot.")
    
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

# Command to unban a user from using the bot
@bot.command(aliases=["ubb"])
async def unbanbot(ctx, member_input: str):
    data = load_manage_id()
    user_id = str(ctx.author.id)

    # Get the member object using the helper function
    member = await get_member_from_input(ctx, member_input)

    if member is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng.")
        return

    # Correct permission check: make sure the user is either owner or admin
    if user_id in data['owner_id'] or user_id in data['admin_id']:
        if not is_banned(member.id):
            await ctx.send(f"<:cancel:1307210917594796032> | {member.display_name} không bị cấm dùng bot.")
            return

        banned_users.remove(str(member.id))
        save_banned_users(banned_users)
        await ctx.send(f"<:checked:1307210920082145330> | Thành công gỡ cấm {member.display_name} khỏi bot.")
    
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

# Command to check if a user is banned
@bot.command(aliases=["cbb"])
async def checkbanbot(ctx, member_input: str):
    # Get the member object using the helper function
    member = await get_member_from_input(ctx, member_input)

    if member is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy người dùng.")
        return

    if is_banned(member.id):
        await ctx.send(f"{member.display_name} bị cấm dùng bot.")
    else:
        await ctx.send(f"{member.display_name} không bị cấm dùng bot.")

SPAM_LIMIT = 5
SPAM_INTERVAL = 10000

@bot.event
async def on_command(ctx):
    global user_commands  # Ensure we are using the global variable
    user_id = ctx.author.id
    current_time = time.time()

    if user_id not in user_commands:
        user_commands[user_id] = []

    # Remove old timestamps
    user_commands[user_id] = [timestamp for timestamp in user_commands[user_id] if current_time - timestamp < SPAM_INTERVAL]

    # Add new timestamp
    user_commands[user_id].append(current_time)

    # Check if user exceeded the spam limit
    if len(user_commands[user_id]) > SPAM_LIMIT:
        banned_users.append(str(user_id))
        save_banned_users(banned_users)
        await ctx.send(f"{ctx.author.mention} đã bị cấm dùng bot vì spam.")
        del user_commands[user_id]  # Remove the user from tracking to save memory

# Event to prevent banned users from using any command
@bot.before_invoke
async def before_any_command(ctx):
    if is_banned(ctx.author.id):
        await ctx.send(f"{ctx.author.mention}, bạn bị cấm dùng bot.")
        return

@bot.command(name="invite", help="Bot gửi link mời bot")
async def invite(ctx):
    embed = discord.Embed(
        title=
        "[Ấn vào để mởi tôi vào server của bạn.](https://discord.com/oauth2/authorize?client_id=1325314772895531028)",
        color=discord.Color.blue())
    await ctx.send(embed=embed)

@bot.command(name="guildlink", help="Bot gửi link server hỗ trợ")
async def guildlink(ctx):
    await ctx.send("<:love:1330363524811063429> | Hãy tham gia server discord của chúng tôi để yêu cầu trợ giúp hoặc chỉ để vui chơi! \n <:baolixi:1330034297771655301> | https://discord.gg/QxqkBWf5vr")

@bot.command(name="linksv", help="Lấy link invite của server qua id (bot cần ở server đó)")
async def linksv(ctx, *, id_sv):
    server = bot.get_guild(int(id_sv))
    if server:
        invite_link = await server.text_channels[0].create_invite()
        await ctx.send(f'Link server: {invite_link}')
    else:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy server với id được cung cấp.")

@bot.command()
async def stats(ctx):
    total_guilds = len(bot.guilds)
    total_users = sum(guild.member_count for guild in bot.guilds)
    total_channels = sum(len(guild.channels) for guild in bot.guilds)
    websocket_ping = round(bot.latency * 1000)
    os_info = platform.system()
    architecture = platform.machine()
    cores = psutil.cpu_count(logical=True)
    cpu_usage = f"{psutil.cpu_percent()}%"
    memory = psutil.virtual_memory()
    bot_ram_usage = psutil.Process().memory_info().rss / (1024 ** 2)
    bot_ram_available = memory.total / (1024 ** 3)
    bot_ram_percent = f"{(bot_ram_usage / (bot_ram_available * 1024)) * 100:.1f}%"
    overall_ram_used = memory.used / (1024 ** 3)
    overall_ram_available = memory.total / (1024 ** 3)
    overall_ram_percent = f"{memory.percent}%"
    python_version = platform.python_version()
    uptime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - bot.start_time).total_seconds())))

    embed = discord.Embed(title="Bot Information",description =  f"❒ Total guilds: {total_guilds} \n ❒ Total users: {total_users} \n ❒ Total channels: {total_channels} \n ❒ Websocket Ping: {websocket_ping} ms \n ",color=0x00ff00)
    embed.set_thumbnail(url=bot.user.avatar.url)  # Set bot's avatar as the thumbnail
    
    embed.add_field(name="CPU", value=f"❯ **OS:** {os_info} [{architecture}]\n❯ **Cores:** {cores}\n❯ **Usage:** {cpu_usage}", inline=True)
    embed.add_field(name="Bot's RAM", value=f"❯ **Used:** {bot_ram_usage:.2f} MB\n❯ **Available:** {bot_ram_available:.2f} GB\n❯ **Usage:** {bot_ram_percent}", inline=True)
    embed.add_field(name="Overall RAM", value=f"❯ **Used:** {overall_ram_used:.2f} GB\n❯ **Available:** {overall_ram_available:.2f} GB\n❯ **Usage:** {overall_ram_percent}", inline=True)
    embed.add_field(name="Python Version", value=python_version, inline=False)
    embed.add_field(name="Uptime", value=f"```{uptime}```", inline=False)

    await ctx.send(embed=embed)

def load_jp():
    try:
        with open("jp.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_jp(data):
    with open("jp.json", "w") as file:
        json.dump(data, file, indent=2)

MAX_BET = 250000

def get_time_left():
    now = datetime.utcnow()
    next_midnight = datetime.combine(now.date(), datetime.min.time()) + timedelta(days=1)
    time_left = next_midnight - now
    hours, remainder = divmod(time_left.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{hours}h {minutes}m {seconds}s'

@bot.command(aliases=["jp"])
async def lottery(ctx, amount: int = None):
    if amount is None:
        await display_status(ctx)
        return

    if amount <= 0:
        await ctx.send("<:cancel:1307210917594796032> | Số tiền cược phải lớn hơn 1 <:mlcoin:1330026986667769867>.")
        return

    user_id = str(ctx.author.id)
    user = load_jp()
    econ = load_econ()

    if user_id not in user:
        user[user_id] = {'lottery': {'amount': 0, 'valid': False}}

    # Đảm bảo 'cash' là số nguyên
    econ[user_id]['cash'] = int(econ[user_id].get('cash', 0))

    if amount > econ[user_id]['cash']:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không đủ <:mlcoin:1330026986667769867> để cược.")
        return

    if 'lottery' in user[user_id]:
        prev_bet = user[user_id]['lottery']['amount']
        if prev_bet >= MAX_BET:
            await ctx.send(f"<:cancel:1307210917594796032> | Bạn chỉ có thể cược tối đa {MAX_BET} <:mlcoin:1330026986667769867>.")
            return
        amount = min(amount, MAX_BET - prev_bet)

    econ[user_id]['cash'] -= amount
    user[user_id]['lottery'] = {'amount': user[user_id]['lottery']['amount'] + amount, 'valid': True}
    save_jp(user)
    save_econ(econ)

    total_amount = sum(user[u]['lottery']['amount'] for u in user if 'lottery' in user[u])
    chance = (amount / total_amount) * 100 if total_amount > 0 else 100

    embed = discord.Embed(
        description='Loterie kết thúc hàng ngày lúc 12AM PST!',
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text='*Tỷ lệ thắng và jackpot có thể thay đổi theo thời gian')
    embed.set_author(name=f"Xổ số của {ctx.author.name}")
    embed.add_field(name='Bạn đã thêm', value=f'```fix\n{amount} mlcoin```', inline=True)
    embed.add_field(name='Tổng số tiền cược của bạn', value=f'```fix\n{amount} mlcoin```', inline=True)
    embed.add_field(name='Cơ hội thắng', value=f'```fix\n{chance:.2f}%```', inline=True)
    embed.add_field(name='Jackpot hiện tại', value=f'```fix\n{total_amount + 500} mlcoin```', inline=True)
    embed.add_field(name='Kết thúc trong', value=f'```fix\n{get_time_left()}```', inline=True)

    await ctx.send(embed=embed)

async def display_status(ctx):
    user_id = str(ctx.author.id)
    user_data = load_jp()
    econ_data = load_econ()
    
    # Đảm bảo người dùng có dữ liệu
    if user_id in user_data and 'lottery' in user_data[user_id]:
        bet = user_data[user_id]['lottery']['amount']
    else:
        bet = 0

    total_amount = sum(user_data[u]['lottery']['amount'] for u in user_data if 'lottery' in user_data[u])
    chance = (bet / total_amount) * 100 if total_amount > 0 else 100

    embed = discord.Embed(
        description='Loterie kết thúc hàng ngày lúc 12AM PST! Chúc may mắn!!',
        color=0x00ff00,
        timestamp=datetime.utcnow()
    )
    embed.set_footer(text='*Tỷ lệ thắng và jackpot có thể thay đổi theo thời gian')
    embed.set_author(name=f"Xổ số của {ctx.author.name}")
    embed.add_field(name='Tổng số tiền cược của bạn', value=f'```fix\n{bet} mlcoin```', inline=True)
    embed.add_field(name='Cơ hội thắng', value=f'```fix\n{chance:.2f}%```', inline=True)
    embed.add_field(name='Số lượng người tham gia', value=f'```fix\n{len(user_data)} users```', inline=True)
    embed.add_field(name='Jackpot hiện tại', value=f'```fix\n{total_amount + 500} mlcoin```', inline=True)
    embed.add_field(name='Kết thúc trong', value=f'```fix\n{get_time_left()}```', inline=True)

    await ctx.send(embed=embed)

# # Đọc và lưu dữ liệu xoso
# def load_xoso():
#     try:
#         with open("xoso.json", "r") as f:
#             return json.load(f)
#     except FileNotFoundError:
#         return {'sotrung': [0, 0, 0, 0, 0, 0], 'user': {}}

# def save_xoso(data):
#     with open("xoso.json", "w") as f:
#         json.dump(data, f, indent=2)

# # Lệnh đặt cược xổ số
# @bot.command(name="xoso")
# async def xoso(ctx, amount: int, mumber: str):
#     xoso = load_xoso()
#     econ = load_econ()
#     user_id = str(ctx.author.id)

#     # Nếu cược nhỏ hơn 1
#     if amount < 1:
#         await ctx.send("<:cancel:1307210917594796032> | Bạn cần đặt cược ít nhất 1 <:mlcoin:1307211294981492827>.")
#         return

#     # Kiểm tra số lượng số người chơi chọn (6 số)
#     if len(mumber) != 6:
#         await ctx.send("<:cancel:1307210917594796032> | Bạn cần chọn chính xác 6 số.")
#         return

#     # Nếu người chơi chưa tham gia cược trước
#     if user_id not in xoso['user']:
#         xoso['user'][user_id] = {'cuoc': amount, 'mumber': mumber}
    
#     if user_id in xoso['user']:
#         await ctx.send("<:cancel:1307210917594796032> | Bạn đã đặt cược.")
#         return
    
#     econ[user_id]['cash'] -= amount

#     save_xoso(xoso)
#     save_econ(econ)

#     await ctx.send(f"<:checked:1307210920082145330> | Bạn đã cược {amount} <:mlcoin:1307211294981492827> với các số {mumber}")

# # Hàm để quay xổ số mỗi 3 tiếng
# @tasks.loop(hours=3)
# async def draw_lottery():
#     channel = bot.get_channel(1307308264119205948)  # Thay YOUR_CHANNEL_ID bằng ID kênh nơi thông báo kết quả xổ số
#     xoso = load_xoso()
#     econ = load_econ()
    
#     # Random ra 6 số cho sổ trung
#     sotrung = [random.randint(0, 9) for _ in range(6)]
#     xoso['sotrung'] = sotrung

#     # Kiểm tra xem ai trúng số
#     winners = []
#     for user_id, data in xoso['user'].items():
#         if data['mumber'] == ''.join(map(str, sotrung)):
#             winners.append(user_id)
#             xoso['user'][user_id]['cuoc'] *= 2  # Nhân đôi số tiền cược của người trúng
#             save_xoso(xoso)
#             econ[user_id]['cash'] += xoso['user'][user_id]['cuoc']

#     # Cập nhật lại dữ liệu xoso
#     save_xoso(xoso)

#     # Thông báo kết quả xổ số
#     embed = discord.Embed(
#         title="Kết quả xổ số",
#         description=f"Số trúng của lần quay xổ số này là: **{' '.join(map(str, sotrung))}**",
#         color=0x00ff00,
#         timestamp=datetime.now(timezone.utc)
#     )

#     if winners:
#         embed.add_field(name="Người thắng cuộc", value=f"<@{'>, <@'.join(winners)}>", inline=False)
#     else:
#         embed.add_field(name="Không có người thắng", value="Không có người nào trúng số lần này.", inline=False)

#     await channel.send(content="<@&1307308298457972818>",embed=embed)

@bot.command(name="serverlist", aliases=["svlist"],help="Xem danh sách các server mà bot đang hoạt động")
async def server_list(ctx):
    data = load_manage_id()
    user_id = str(ctx.author.id)
    if user_id in data['owner_id'] or data['admin_id']:
        for guild in bot.guilds:
            await ctx.send(f"Name: {guild.name} \n Id: {guild.id}")
    else:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")

@bot.command()
async def afk(ctx, *, message=None):
    user_id = str(ctx.author.id)
    afk_data = {"message": message or "AFK.", "channel_id": ctx.channel.id}

    # Ensure afk.json exists
    if not os.path.exists("afk.json"):
        with open("afk.json", "w") as file:
            json.dump({}, file)

    # Load and update AFK data
    with open("afk.json", "r") as file:
        data = json.load(file)

    data[user_id] = afk_data

    with open("afk.json", "w") as file:
        json.dump(data, file, indent=4)

    await ctx.send(f"{ctx.author.mention} đã AFK: {afk_data['message']}")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore bot messages

    # Ensure afk.json exists
    if not os.path.exists("afk.json"):
        with open("afk.json", "w") as file:
            json.dump({}, file)

    # Load AFK data
    with open("afk.json", "r") as file:
        data = json.load(file)

    # Check if someone mentions an AFK user
    for user_id, afk_info in data.items():
        if f"<@{user_id}>" in message.content:
            await message.channel.send(
                f"`{message.author.display_name}` đang AFK: {afk_info['message']}"
            )
            break

    # Check if an AFK user sends a message
    user_id = str(message.author.id)
    if user_id in data:
        await message.channel.send(f"Chào mừng trở lại {message.author.mention}.")
        del data[user_id]

        # Update afk.json
        with open("afk.json", "w") as file:
            json.dump(data, file, indent=4)

    # Process commands
    await bot.process_commands(message)

@bot.command(name="lock", help="Khóa kênh")
@commands.has_permissions(manage_channels=True)
async def lock(ctx, channel: discord.TextChannel = None):
    await ctx.message.delete()
    if not channel:
        channel = ctx.channel
    await ctx.send(f"<:checked:1307210920082145330> | Đã khóa kênh {channel.mention}")

@bot.command(name="unlock", help="Mở khóa kênh")
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    await ctx.message.delete()
    if not channel:
        channel = ctx.channel
    await ctx.send(f"<:checked:1307210920082145330> | Đã mở khóa kênh {channel.mention}")
        
econ_data = load_econ()

class BetModal(Modal):
    def __init__(self, user, emoji, bets, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.emoji = emoji
        self.bets = bets

        self.add_item(TextInput(label="Nhập số tiền cược", placeholder="Số tiền bạn muốn cược", required=True))

    async def callback(self, interaction: discord.Interaction):
        amount = self.children[0].value

        try:
            amount = int(amount)
            if amount <= 0:
                raise ValueError("Số tiền phải lớn hơn 0.")
        except ValueError:
            await interaction.response.send_message("Vui lòng nhập một số tiền hợp lệ!", ephemeral=True)
            return

        # Check user balance
        user_id = str(self.user.id)
        if user_id not in econ_data or econ_data[user_id]['cash'] < amount:
            await interaction.response.send_message("Bạn không đủ tiền để cược!", ephemeral=True)
            return

        # Deduct bet amount
        econ_data[user_id]['cash'] -= amount
        save_econ(econ_data)

        # Save bet
        if user_id not in self.bets:
            self.bets[user_id] = {}
        self.bets[user_id][self.emoji] = amount

        await interaction.response.send_message(f"Bạn đã đặt cược {amount} vào {self.emoji}", ephemeral=True)

class BauCuaView(View):
    def __init__(self, emojis, bets, end_time):
        super().__init__(timeout=None)
        self.emojis = emojis
        self.bets = bets
        self.end_time = end_time

        for emoji in emojis:
            self.add_item(Button(label=emoji, emoji=emoji, style=discord.ButtonStyle.primary, custom_id=emoji))

    async def interaction_check(self, interaction: discord.Interaction):
        if datetime.utcnow() > self.end_time:
            await interaction.response.send_message("Thời gian đặt cược đã kết thúc!", ephemeral=True)
            return False
        return True

    async def on_button_click(self, interaction: discord.Interaction):
        modal = BetModal(user=interaction.user, emoji=interaction.data['custom_id'], bets=self.bets, title="Đặt cược")
        await interaction.response.send_modal(modal)

@bot.command(name="baucua", help="Bắt đầu trò chơi bầu cua cá cọp")
async def bau_cua(ctx):
    emojis = ['🍐', '🦀', '🍤', '🐅', '🐓', '🦌']
    bets = {}

    end_time_utc = datetime.utcnow() + timedelta(seconds=60)
    end_time_vn = end_time_utc.replace(tzinfo=timezone.utc).astimezone(timezone(timedelta(hours=7)))

    embed = discord.Embed(
        title="Bầu cua cá cọp",
        description=(
            f"Thời gian đặt cược: <t:{int(end_time_vn.timestamp())}:R>\n\n"
            + '\n'.join([f"{emojis[i]}: {name}" for i, name in enumerate(["Bầu", "Cua", "Tôm", "Cọp", "Gà", "Nai"])])),
        color=discord.Color.yellow()
    )

    view = BauCuaView(emojis=emojis, bets=bets, end_time=end_time_utc)
    message = await ctx.send(embed=embed, view=view)

    await discord.utils.sleep_until(20)
    view.stop()

    # Calculate results
    result = random.sample(emojis, 3)
    winners = {}

    for user_id, user_bets in bets.items():
        for emoji, amount in user_bets.items():
            if emoji in result:
                if user_id not in winners:
                    winners[user_id] = 0
                winners[user_id] += amount * 2

    # Update balances
    for user_id, winnings in winners.items():
        if user_id not in econ_data:
            econ_data[user_id] = {"cash": 0}
        econ_data[user_id]['cash'] += winnings
    save_econ(econ_data)

    # Announce results
    winner_mentions = [f"<@{user_id}>" for user_id in winners.keys()]
    if winners:
        result_msg = (
            f"**Kết quả:** {' '.join(result)}\n"
            f"Chúc mừng {', '.join(winner_mentions)} đã thắng cược!"
        )
    else:
        result_msg = f"**Kết quả:** {' '.join(result)}\nKhông có ai thắng cược."

    await message.edit(content=result_msg, embed=None, view=None)

@bot.command(name="action", help="Bot gửi gif tương ứng")
async def action(ctx, action_type,member: discord.Member=None):
    valid_actions = ['cuddle','slap', 'pat','feed','hug','kiss','tickle']
    #valid_actions = [
    #    'smug', 'woof', 'gasm', '8ball', 'goose', 'cuddle', 'avatar', 'slap',
    #    'v3', 'pat', 'gecg', 'feed', 'fox_girl', 'lizard', 'neko', 'hug',
    #    'meow', 'kiss', 'wallpaper', 'tickle', 'spank', 'waifu', 'lewd', 'ngif'
    #]

    if action_type not in valid_actions:
        await ctx.send(
            f'Không tìm thấy hành động bạn yêu cầu,hãy thử dùng hành động: {", ".join(valid_actions)}')
        return
    
    url = f"https://nekos.life/api/v2/img/{action_type}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        image_url = data['url']
        embed = discord.Embed(title=f"{ctx.author.name} đã {action_type.capitalize()} {member}!",
                              color=0xFFC0CB)
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send(
            f"Failed to fetch image: {response.status_code} - {response.text}")

@bot.command(name="serverinfo",aliases=["svinfo","infoserver","si"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def serverinfo(ctx):
    guild = ctx.guild

    embed = discord.Embed(
        title=guild.name,
        description="Thông tin về máy chủ",
        color=discord.Color.blue(),
    )
    # Thumbnail là icon của server
    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)
    
    total_members = guild.member_count
    bots = len([member for member in guild.members if member.bot])
    humans = total_members - bots

    # Các thông tin chính
    embed.add_field(name="**Owner**", value=f"{guild.owner.name} ({guild.owner.mention})", inline=True)
    embed.add_field(name="**<:member:1280718179714469899> Member**", value=f"Tổng: {total_members} \n Người: {humans} \n Bot: {bots}", inline=True)
    embed.add_field(name="**Roles**", value=len(guild.roles), inline=True)
    embed.add_field(name="**<a:channel:1281077086240641171> Channels**", value=f"<:text_channel:1315199436380442706> Text: {len(guild.text_channels)} \n <:voice_channel:1315199439446741003> Voice: {len(guild.voice_channels)}", inline=True)

    # Thông tin Boost
    boost_count = guild.premium_subscription_count
    boost_tier = guild.premium_tier
    embed.add_field(name="**Boost**", value=f"{boost_count} Boosts (Cấp {boost_tier})", inline=True)

    # ID và thời gian tạo server
    embed.set_footer(text=f"ID: {guild.id} ・ Tạo ngày: {guild.created_at.strftime('%d/%m/%Y %I:%M %p')}")

    await ctx.send(embed=embed)

@bot.command(name="userinfo", aliases=["infouser", "ui"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def userinfo(ctx, member_input:str=None):
    if member_input is None:
        member = ctx.author.id
    # Nếu không có member được đề cập, mặc định là người dùng gửi lệnh
    member = await get_user_from_input(ctx, member_input)
    if member is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy user.")
        return

     # Lấy danh sách vai trò của người dùng (trừ vai trò @everyone)
    roles = [role.mention for role in member.roles if role != ctx.guild.default_role]

    # Chỉ hiển thị 9 vai trò đầu tiên, thêm thông báo nếu còn dư
    displayed_roles = roles[:9]
    remaining_roles_count = len(roles) - 9
    roles_text = ", ".join(displayed_roles)
    if remaining_roles_count > 0:
        roles_text += f", +{remaining_roles_count}"

    # Lấy danh sách quyền
    permissions = [perm[0].replace('_', ' ').title() for perm in member.guild_permissions if perm[1]]

    # Tạo embed
    embed = discord.Embed(
        title=f"Thông tin người dùng - {member.name}",
        color=discord.Color.yellow()
    )

    important_permissions = {
        "administrator": "Administrator",
        "kick_members": "Kick Members",
        "ban_members": "Ban Members",
        "manage_roles": "Manage Roles",
        "manage_channels": "Manage Channels",
        "manage_nicknames": "Manage Nicknames",
        "mute_members": "Mute Members",
        "view_audit_log": "View Audit Log"
    }
    user_permissions = [
        name for perm, name in important_permissions.items() if getattr(member.guild_permissions, perm)
    ]

    badges = []
    if member.public_flags.staff:
        badges.append("<:discord_staff:1315218569897709619>")
    if member.public_flags.partner:
        badges.append("<:discord_partner:1315218950212288542>")
    if member.public_flags.hypesquad:
        badges.append("<:hypesquad:1315218571718164520>")
    if member.public_flags.bug_hunter:
        badges.append("<:bug_hunter:1315217562321031179>")
    if member.public_flags.verified_bot_developer:
        badges.append("<:early_bot_developer:1315219583539482648>")
    if member.public_flags.early_supporter:
        badges.append("<:early_supporter:1315218810629918731>")
    if member.public_flags.hypesquad_balance:
        badges.append("<:hypesquad_balance:1315217347748958228>")
    if member.public_flags.hypesquad_bravery:
        badges.append("<:hypesquad_bravery:1315217350118871090>")
    if member.public_flags.hypesquad_brilliance:
        badges.append("<:hypesquad_brilliance:1315217351960035399>")
    
    badges_text = ", ".join(badges) if badges else "Không có huy hiệu"

    # Thêm avatar
    embed.set_thumbnail(url=member.avatar.url if member.avatar else None)

    # Các thông tin chính
    embed.add_field(name="**Tên**", value=f"{member.name} ({member.mention})", inline=True)
    embed.add_field(name="**ID**", value=member.id, inline=True)
    embed.add_field(name="**Ngày tham gia server**", value=member.joined_at.strftime('%d/%m/%Y %I:%M %p'), inline=False)
    embed.add_field(name="**Ngày tạo tài khoản**", value=member.created_at.strftime('%d/%m/%Y %I:%M %p'), inline=False)

    # Vai trò
    embed.add_field(name="**Roles**", value=roles_text if roles else "Không có vai trò", inline=False)

    # Quyền
    embed.add_field(name="**Quyền**", value=", ".join(user_permissions) if user_permissions else "Không có quyền", inline=False)

    embed.add_field(name="**Huy hiệu**", value=badges_text, inline=False)

    # Gửi embed
    await ctx.send(embed=embed)

@bot.command(name="roleinfo", aliases=["inforole", "ri"])
@commands.cooldown(1, 10, commands.BucketType.user)
async def roleinfo(ctx, *, role_input:str):
    # Nếu không có role được đề cập, trả lỗi
    role = await get_role_from_input(ctx,role_input)
    if role is None:
        await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy role.")
        return

    # Lấy danh sách quyền
    important_permissions = {
        "administrator": "Administrator",
        "kick_members": "Kick Members",
        "ban_members": "Ban Members",
        "manage_roles": "Manage Roles",
        "manage_channels": "Manage Channels",
        "manage_nicknames": "Manage Nicknames",
        "mute_members": "Mute Members",
        "view_audit_log": "View Audit Log"
    }
    role_permissions = [
        name for perm, name in important_permissions.items() if getattr(role.permissions, perm)
    ]

    # Số lượng thành viên có vai trò này
    members_with_role = len(role.members)

    # Tạo embed
    embed = discord.Embed(
        title=f"Thông tin vai trò: {role.name}",
        color=role.color
    )
    embed.add_field(name="**Tên vai trò**", value=role.name, inline=True)
    embed.add_field(name="**ID**", value=role.id, inline=True)
    embed.add_field(name="**Màu**", value=str(role.color), inline=True)
    embed.add_field(name="**Được tạo vào**", value=role.created_at.strftime('%d/%m/%Y %I:%M %p'), inline=True)
    embed.add_field(name="**Số người có**", value=f"{members_with_role} thành viên", inline=True)
    embed.add_field(name="**Được ping**", value="Có" if role.mentionable else "Không", inline=True)

    # Quyền của vai trò
    embed.add_field(
        name="**Quyền chính**",
        value=", ".join(role_permissions) if role_permissions else "Không có",
        inline=False,
    )

    await ctx.send(embed=embed)

def load_level():
    if os.path.exists('level.json'):
        try:
            with open('level.json', 'r') as f:
                levels = json.load(f)
        except json.JSONDecodeError:
            levels = {}
    else:
        levels = {}
    return levels

def save_levels(levels):
    with open('level.json', 'w') as f:
        json.dump(levels, f, indent=4)

last_message_times = {}

levels = load_level()
data = load_econ()

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    user_id = str(message.author.id)

    current_time = time.time()
    if user_id in last_message_times:
        last_time = last_message_times[user_id]
        if current_time - last_time < 1:
            return

    last_message_times[user_id] = current_time

    if user_id not in levels:
        levels[user_id] = {
            "level": 1,
            "xp": 0,
            "xp_required": 100,
            "qua_da_nhan": 1000
        }
    
    if "qua_da_nhan" not in levels:
        levels[user_id]["qua_da_nhan"] = 1000

    levels[user_id]["xp"] += 1

    while levels[user_id]["xp"] >= levels[user_id]["xp_required"]:
        levels[user_id]["xp"] -= levels[user_id]["xp_required"]
        levels[user_id]["level"] += 1
        levels[user_id]["xp_required"] *= 3
        levels[user_id]["qua_da_nhan"] *= 3
        await message.channel.send(f"Chúc mừng {message.author.mention}, bạn đã lên cấp {levels[user_id]['level']}!")

        save_levels(levels)

        if user_id not in data:
            data[user_id] = {'cash': 0,'last_daily_claim': datetime.utcnow().isoformat(),'dailied': False}
        
        data[user_id]["cash"] += levels[user_id]["qua_da_nha"]

        save_econ(data)

    await bot.process_commands(message)  # Ensure other commands are processed

def create_level_image(member, level_data):
    width, height = 600, 200
    image = Image.new('RGBA', (width, height), (255, 255, 255, 0))

    background = Image.open("level_background.jpg").resize((width, height))
    image.paste(background, (0, 0))

    draw = ImageDraw.Draw(image)
    font_large = ImageFont.truetype("arial.ttf", 40)
    font_small = ImageFont.truetype("arial.ttf", 20)

    avatar_url = member.display_avatar.url
    response = requests.get(avatar_url)
    avatar_image = Image.open(BytesIO(response.content))
    avatar_image = avatar_image.resize((128, 128))
    image.paste(avatar_image, (20, 36))

    draw.text((160, 20), f"{member.display_name}", font=font_large, fill=(255, 255, 255))
    draw.text((160, 80), f"Cấp: {level_data['level']}", font=font_small, fill=(255, 255, 255))
    draw.text((160, 110), f"XP: {level_data['xp']} / {level_data['xp_required']}", font=font_small, fill=(255, 255, 255))

    bar_width = 300
    bar_height = 25
    bar_x = 160
    bar_y = 140
    progress = level_data['xp'] / level_data['xp_required']
    draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height], outline=(255, 255, 255), width=2)
    draw.rectangle([bar_x, bar_y, bar_x + int(bar_width * progress), bar_y + bar_height], fill=(0, 255, 0))

    file_path = f"level_{member.id}.png"
    image.save(file_path)
    return file_path

@bot.command()
async def level(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    user_id = str(member.id)

    if user_id in levels:
        file_path = create_level_image(member, levels[user_id])
        await ctx.send(file=discord.File(file_path))
        os.remove(file_path)
    else:
        await ctx.send(f"{member.mention} chưa có cấp độ nào.")

@bot.command()
async def xh(ctx):
    try:
        # Load the levels data from level.json
        with open('level.json', 'r') as file:
            levels = json.load(file)

        # Sort levels data by level and XP in descending order
        sorted_levels = sorted(levels.items(), key=lambda x: (x[1]['level'], x[1]['xp']), reverse=True)

        # Function to create the leaderboard image
        def create_leaderboard_image(page):
            img = Image.new('RGB', (600, 700), color=(30, 30, 30))
            draw = ImageDraw.Draw(img)

            # Use a default font if "arial.ttf" is unavailable
            try:
                font = ImageFont.truetype("arial.ttf", 20)
            except IOError:
                font = ImageFont.load_default()

            # Set the title
            draw.text((10, 10), "Bảng xếp hạng", fill="white", font=font)

            # Set starting y position for drawing ranks
            y_position = 50

            # Determine the range of users to display on this page
            start = (page - 1) * 10
            end = min(start + 10, len(sorted_levels))

            for rank, (user_id, data) in enumerate(sorted_levels[start:end], start=start + 1):
                # Fetch the user by their user_id
                user = bot.get_user(int(user_id))

                if user:
                    # If the user is found, get their name
                    display_name = user.name
                else:
                    # If the user is not found (e.g., they are not in the server), use a fallback
                    display_name = "Tên không tìm thấy"

                # Build the text for the leaderboard
                rank_text = f"#{rank} - {display_name} - Cấp {data['level']} , XP {data['xp']}"
                draw.text((70, y_position + 10), rank_text, fill="white", font=font)

                # Move to the next position
                y_position += 60

            # Save the image to a bytes buffer
            buffer = io.BytesIO()
            img.save(buffer, format="PNG")
            buffer.seek(0)

            return buffer

        # Function to handle the page change
        async def change_page(interaction, current_page):
            buffer = create_leaderboard_image(current_page)
            await interaction.message.delete()
            await interaction.followup.send(file=discord.File(buffer, "leaderboard.png"), view=create_view(current_page))

        # Function to create the view with buttons
        def create_view(current_page):
            prev_button = Button(label="Previous", style=discord.ButtonStyle.primary, disabled=current_page == 1)
            next_button = Button(label="Next", style=discord.ButtonStyle.primary, disabled=(current_page * 10 >= len(sorted_levels)))

            async def prev_button_callback(interaction):
                nonlocal current_page
                current_page -= 1
                await change_page(interaction, current_page)

            async def next_button_callback(interaction):
                nonlocal current_page
                current_page += 1
                await change_page(interaction, current_page)

            prev_button.callback = prev_button_callback
            next_button.callback = next_button_callback

            view = View()
            view.add_item(prev_button)
            view.add_item(next_button)
            return view

        # Initialize the current page
        current_page = 1

        # Create the initial image for page 1
        buffer = create_leaderboard_image(current_page)

        # Create the view with the buttons
        view = create_view(current_page)

        # Send the initial leaderboard image with the buttons
        await ctx.send(file=discord.File(buffer, "leaderboard.png"), view=view)

    except Exception as e:
        # Log the error message and traceback
        error_message = f"An error occurred: {str(e)}"
        traceback_message = traceback.format_exc()
        print(error_message)
        print(traceback_message)
        
        # Send the error message to the Discord channel
        await ctx.send(f"Error: {error_message}\n```{traceback_message}```")

@bot.command()
async def rank(ctx):
    sorted_levels = sorted(levels.items(), key=lambda x: x[1]['level'], reverse=True)
    leaderboard_text = ""
    for user_id, data in sorted_levels:
        member = ctx.guild.get_member(int(user_id))
        if member:
            leaderboard_text += f"{member.display_name}: Cấp {data['level']} , XP {data['xp']}\n"

    await ctx.send(f"Bảng xếp hạng:\n{leaderboard_text}")

async def update_presence():  
    while True:  
        total_guilds = len(bot.guilds)  
        total_members = sum(guild.member_count for guild in bot.guilds)  
        total_channels = sum(len(guild.channels) for guild in bot.guilds)  

        activities = [  
            discord.Activity(type=discord.ActivityType.watching, name=f"{total_members} members"),  
            discord.Activity(type=discord.ActivityType.watching, name=f"{total_guilds} servers"),  
            discord.Activity(type=discord.ActivityType.watching, name=f"{total_channels} channels"),  
            discord.Streaming(name=f"/help | mlhelp", url="https://www.twitch.tv/nocopyrightsounds")  
        ]  

        for activity in activities:  
            try:  
                await bot.change_presence(activity=activity)  
            except Exception as e:  
                print(f"Error updating presence: {e}")  
                await asyncio.sleep(5)
                continue  
            
            await asyncio.sleep(5) 

bot.start_time = datetime.now(timezone.utc)
@bot.event
async def on_command(ctx):
    user = ctx.author
    command = ctx.command
    print(f"{Fore.MAGENTA}[COMMAND]{Style.RESET_ALL} 🛠 {user} đã sử dụng lệnh: {Fore.CYAN}{command}{Style.RESET_ALL}")
def count_json_files():
    return len([f for f in os.listdir() if f.endswith(".json")])

def count_commands():
    return len(bot.commands)

def count_lines_in_main():
    try:
        with open("main.py", "r", encoding="utf-8") as f:
            return sum(1 for _ in f)
    except FileNotFoundError:
        return 0
@bot.event
async def on_ready():
    print(f"{Fore.GREEN}[SUCCESS]{Style.RESET_ALL} 🚀 Bot đang hoạt động!")
    reset_daily.start()
    bot.loop.create_task(update_presence())
    await bot.tree.sync()
    tasks = [
        ["Reset Daily", "✅ Đã bắt đầu"],
        ["Update Presence", "✅ Đã bắt đầu"],
        ["Sync Commands", "✅ Hoàn tất"],
        ["Start Time", f"⏱ {time.strftime('%d-%m-%Y %H:%M:%S', time.localtime(time.time()))}"],
    ]

    code_info = [
        ["Tổng file JSON", f"📂 {count_json_files()} file"],
        ["Số lượng lệnh", f"📜 {count_commands()} lệnh"],
        ["Số dòng", f"📝 {count_lines_in_main()} dòng"],
    ]
    table1 = Fore.CYAN + tabulate(tasks, headers=["Tác Vụ", "Trạng Thái"], tablefmt="grid") + Style.RESET_ALL
    table2 = Fore.YELLOW + tabulate(code_info, headers=["Thông Tin Code", "Giá Trị"], tablefmt="grid") + Style.RESET_ALL
    print(f"{table1}\n{table2}")


    bot.start_time = time.time()

webhook_url = 'https://discord.com/api/webhooks/1334823001597804544/8hlZA2yLS7R2NaYihdm10CN2WnAdVh_W-uMvbJ_mawm7f0WtWtwkVCZywX96lPX9n1HL'

async def send_webhook(content, embed=None):
    async with aiohttp.ClientSession() as session:
        payload = {'content': content}
        if embed:
            payload['embeds'] = [embed.to_dict()]
        async with session.post(webhook_url, json=payload) as response:
            if response.status != 204:
                print(f"Failed to send log to webhook: {response.status}, {await response.text()}")
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.errors.HTTPException) and error.status == 429:
        embed = discord.Embed(
            title="Ratelimit Error",
            description="Bot đã bị rate limited.",
            color=discord.Color.red()
        )
        embed.add_field(name="Tóm tắt lỗi", value="Bot đã bị rate limited.", inline=False)
        
        full_error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        embed.add_field(name="Đầy đủ lỗi", value=f"```{full_error}```", inline=False)
        
        await send_webhook(content="<@847341889015644171> <@1219514896778133594> Dính Rate Limited Rồi", embed=embed)
        
        retry_after = int(error.response.headers.get("Retry-After", 10))
        print(f'Rate limited. Retrying after {retry_after} seconds.')
        await asyncio.sleep(retry_after)

    else:
        embed = discord.Embed(
            title="Error Log",
            description="Bot gặp lỗi.",
            color=discord.Color.red()
        )
        embed.add_field(name="Tóm tắt lỗi", value=str(error), inline=False)
        
        full_error = ''.join(traceback.format_exception(type(error), error, error.__traceback__))
        embed.add_field(name="Đầy đủ lỗi", value=f"```{full_error}```", inline=False)
        
        await send_webhook(content="Thông tin lỗi:", embed=embed)

webhook_url2 = 'https://discord.com/api/webhooks/1328949158492766218/kHFpzn2j5VIQ03x9CBWxEQ4eACzepwuvqg0zdeWY67Y36JMNuf34DGTu-8GuhLTioLZX'
async def send_webhook2(content):
    async with aiohttp.ClientSession() as session:
        async with session.post(webhook_url2, json={'content': content}) as response:
            if response.status != 204:
                print(f"Failed to send log to webhook: {response.status}, {await response.text()}")
@bot.event
async def on_guild_join(guild):
    content = f'Bot đã gia nhập server mới: {guild.name} (ID: {guild.id})\n'
    content += f'Số lượng thành viên hiện tại: {guild.member_count}'
    await send_webhook2(content)
    print(f'Bot đã gia nhập server mới: {guild.name}')

@bot.event
async def on_guild_remove(guild):
    content = f'Bot đã bị kick khỏi server: {guild.name} (ID: {guild.id})\n'
    content += f'Số lượng thành viên hiện tại trước khi bị kick: {guild.member_count}'
    await send_webhook2(content)
    print(f'Bot đã bị kick khỏi server: {guild.name}')

webhook_commands_logs = 'https://discord.com/api/webhooks/1328641674896736298/t4TqENGcVxQf16EkaAJMoFPZqT9DpXMV-inU9hXMS-SuI9Z66PhuSQm9aoJB3GivTPUJ'

async def send_webhook_commands_logs(content, embed=None):
    async with aiohttp.ClientSession() as session:
        payload = {'content': content}
        if embed:
            payload['embeds'] = [embed.to_dict()]
        async with session.post(webhook_commands_logs, json=payload) as response:
            if response.status != 204:
                error_text = await response.text()
                print(f"Failed to send log to webhook: Status {response.status}, Error: {error_text}")

# @bot.event
# async def on_command(ctx):
#     vn_timezone = timezone(timedelta(hours=7))
#     joined_at_vn = ctx.author.joined_at.astimezone(vn_timezone)
#    created_at_vn = ctx.author.created_at.astimezone(vn_timezone)
#     current_time_vn = datetime.now(vn_timezone)

#    # Creating an embed and setting properties
#    embed = discord.Embed(title="Lệnh đã được sử dụng", color=discord.Color.blue())
#    try:
#        embed.set_thumbnail(url=ctx.author.avatar.url)  # Ensure compatibility with discord.py version
#    except AttributeError:
#        print("Could not set avatar URL for the embed.")
#    embed.add_field(name="Tên người dùng", value=f"**{ctx.author.name}**", inline=True)
#    embed.add_field(name="ID người dùng", value=f"**{ctx.author.id}**", inline=True)
#    embed.add_field(name="Ngày tạo tài khoản", value=f"<t:{int(created_at_vn.timestamp())}:f>", inline=True)
#    embed.add_field(name="Tên server", value=f"**{ctx.guild.name}**", inline=True)
#    embed.add_field(name="ID server", value=f"**{ctx.guild.id}**", inline=True)
#    embed.add_field(name="Kênh sử dụng", value=f"**{ctx.channel.name}**", inline=True)
#    embed.add_field(name="Ngày tham gia server", value=f"<t:{int(joined_at_vn.timestamp())}:f>", inline=True)
#   embed.add_field(name="Lệnh", value=f"**{ctx.command.name}**", inline=True)

#    footer_text = "Milo Commands Logs"
#    embed.set_footer(text=footer_text)
#    embed.timestamp = current_time_vn

#   await send_webhook_commands_logs(f"**{ctx.author}** đã sử dụng một lệnh.", embed=embed)

@bot.command()
async def wanted(ctx, user: discord.User = None):

    user = user or ctx.author
    
    image_url = user.avatar.url
    api_url = f'https://api.popcat.xyz/wanted?image={image_url}'
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            wanted_image_url = response.url
            
            embed = discord.Embed(title=f"`{user.name}` bị truy nã!", color=0x00ff00)
            embed.set_image(url=wanted_image_url)
            embed.set_footer(text="Nguồn: Claso API")
            
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
    
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def color(ctx):
    url = "https://api.popcat.xyz/randomcolor"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        
        hex_color = data.get('hex', 'No color found')
        name_color = data.get('name', 'No name found')
        image_url = data.get('image', None)

        embed = discord.Embed(
            title="",
            description=f"Tên: **{name_color}**\n"
                        f"Hex: **#{hex_color}**",
            color=discord.Color(int(hex_color, 16))
        )

        if image_url:
            embed.set_thumbnail(url=image_url)

        await ctx.send(content=f"🎨 | **{ctx.author.display_name}**, đây là màu ngẫu nhiên của bạn.",embed=embed)
    else:
        await ctx.send("<:cancel:1307210917594796032> | Không thể random màu.")

@bot.command()
async def lyric(ctx, *, song_name: str):
    url = f"https://api.popcat.xyz/lyrics?song={song_name.replace(' ', '+')}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                lyrics = data.get('lyrics', 'Không tìm thấy lời bài hát.')

                max_length = 2048
                if len(lyrics) > max_length:
                    for i in range(0, len(lyrics), max_length):
                        embed = discord.Embed(
                            title=song_name,
                            description=lyrics[i:i + max_length],
                            color=discord.Color.blue()
                        )
                        await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title=song_name,
                        description=lyrics,
                        color=discord.Color.blue()
                    )
                    await ctx.send(embed=embed)
            else:
                await ctx.send("<:cancel:1307210917594796032> | Không thể truy cập API.")

@bot.command()
async def weather(ctx, *, city_name: str):
    url = f"https://api.popcat.xyz/weather?q={city_name.replace(' ', '+')}"
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                if not data:  # Kiểm tra nếu không có dữ liệu
                    await ctx.send("<:cancel:1307210917594796032> | Không tìm thấy dữ liệu thời tiết.")
                    return

                location = data[0]['location']
                current_weather = data[0]['current']
                forecast = data[0]['forecast']

                # Tạo Embed cho thông tin hiện tại
                embed = discord.Embed(
                    title=f"Thời tiết tại {location['name']}",
                    description=f"**Thời tiết hiện tại**: {current_weather['skytext']}\n"
                                f"**Nhiệt độ**: {current_weather['temperature']}°C (Cảm thấy như {current_weather['feelslike']}°C)\n"
                                f"**Độ ẩm**: {current_weather['humidity']}%\n"
                                f"**Tốc độ gió**: {current_weather['windspeed']}\n"
                                f"**Thời gian quan sát**: {current_weather['observationtime']}\n",
                    color=discord.Color.blue()
                )
                embed.set_thumbnail(url=current_weather['imageUrl'])
                await ctx.send(embed=embed)

                # Dự báo thời tiết cho vài ngày tới
                forecast_description = "\n**Dự báo 5 ngày tới:**\n"
                for day in forecast:
                    forecast_description += (f"**{day['day']}**: {day['skytextday']}\n"
                                             f"Cao: {day['high']}°C, Thấp: {day['low']}°C\n"
                                             f"Sự kết tủa: {day['precip']}%\n\n")
                embed = discord.Embed(
                    title="",
                    description=forecast_description,
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)

            else:
                await ctx.send("<:cancel:1307210917594796032> | Không thể truy cập API.")

@bot.command(name="translate",aliases=["dịch",'dich'])
async def translate(ctx, lag: str, *, text: str):
    url = f"https://api.popcat.xyz/translate?to={lag}&text={text.replace(' ', '+')}"

    valid_languages = ['vi', 'en', 'fr', 'de', 'es'] 
    if lag not in valid_languages:
        await ctx.send(f"<:cancel:1307210917594796032> | Ngôn ngữ '{lag}' không hợp lệ. Vui lòng sử dụng một trong các ngôn ngữ sau: {', '.join(valid_languages)}")
        return

    
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()

                if 'translated' in data:
                    translated_text = data['translated']
                    embed=discord.Embed(description=f"Gốc: {text} \n \n Đã dịch: {translated_text}",color=discord.Color.blue())
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("<:cancel:1307210917594796032> | Không thể dịch văn bản.")
            else:
                await ctx.send("<:cancel:1307210917594796032> | Không thể truy cập API.")

@bot.command()
async def ship(ctx, user1: discord.User = None, user2: discord.User = None):
    user1 = user1 or ctx.author
    user2 = user2 or ctx.author
    

    image_url1 = user1.avatar.url
    image_url2 = user2.avatar.url
    api_url = f'https://api.popcat.xyz/ship?user1={image_url1}&user2={image_url2}'
    
    try:

        response = requests.get(api_url)
        

        if response.status_code == 200:
            ship_image_url = response.url
            
            percentage = random.randint(0, 100)
            
            green_squares = ":green_square:" * (percentage // 10)
            white_squares = ":white_large_square:" * (10 - (percentage // 10))
            squares = green_squares + white_squares
            
            embed = discord.Embed(title=f"`{user1.name}` và `{user2.name}` - Kết quả", color=0xFFFFFF)
            embed.set_image(url=ship_image_url)
            embed.add_field(name="Tỷ lệ Yêu Nhau", value=f"{squares} {percentage}%", inline=True)
            embed.set_footer(text="Nguồn: Claso API")
            
            view = discord.ui.View()
            view.add_item(discord.ui.Button(label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=1239105383801290834&permissions=8&scope=bot"))
            view.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/QxqkBWf5vr"))

            refresh_button = discord.ui.Button(label="Làm mới", style=discord.ButtonStyle.green)

            async def refresh_callback(interaction):
                if interaction.user != ctx.author:
                    await interaction.response.send_message("Có vẻ nút này không dành cho bạn!", ephemeral=True)
                else:
                    new_percentage = random.randint(0, 100)
                    new_green_squares = ":green_square:" * (new_percentage // 10)
                    new_white_squares = ":white_large_square:" * (10 - (new_percentage // 10))
                    new_squares = new_green_squares + new_white_squares
                    
                    new_embed = discord.Embed(title=f"`{user1.name}` và `{user2.name}` - Kết quả", color=0xFFFFFF)
                    new_embed.set_image(url=ship_image_url)
                    new_embed.add_field(name="Tỷ lệ Yêu Nhau", value=f"{new_squares} {new_percentage}%", inline=True)
                    new_embed.set_footer(text="Nguồn: Claso API")
                    
                    await interaction.response.edit_message(embed=new_embed, view=view)
            
            refresh_button.callback = refresh_callback
            view.add_item(refresh_button)
            
            await ctx.send(embed=embed, view=view)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
    
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")
    
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def drake(ctx, text1: str, text2: str):

    api_url = f'https://api.popcat.xyz/drake?text1={text1}&text2={text2}'
    
    try:

        response = requests.get(api_url)

        if response.status_code == 200:
            drake_image_url = response.url
            
            embed = discord.Embed(title="Drake Meme", color=0x00ff00)
            embed.set_image(url=drake_image_url)
            embed.set_footer(text="Nguồn: Claso API")
            view2 = discord.ui.View()
            view2.add_item(discord.ui.Button(label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=1239105383801290834&permissions=8&scope=bot"))
            view2.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/QxqkBWf5vr"))   
            await ctx.send(embed=embed, view=view2)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
 
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def pet(ctx, user: discord.User = None):
    user = user or ctx.author
    
    image_url = user.avatar.url
    api_url = f'https://api.popcat.xyz/pet?image={image_url}'
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            pet_gif = BytesIO(response.content)
            
            embed = discord.Embed(title=f"`{user.name}` Bạn đã được `{ctx.author.name}` chọn làm Pet!", color=0x00ff00)
            embed.set_image(url="attachment://pet_image.gif")
            embed.set_footer(text="Nguồn: Popcat API")
            view3 = discord.ui.View()
            view3.add_item(discord.ui.Button(label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=1239105383801290834&permissions=8&scope=bot"))
            view3.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/QxqkBWf5vr"))  
            await ctx.send(embed=embed, file=discord.File(pet_gif, filename="pet_image.gif"), view=view3)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
    
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def caution(ctx, *, query: str):
    api_url = f'https://api.popcat.xyz/caution?text={query}'
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            caution_image_url = response.url
            
            embed = discord.Embed(title=f"Caution", color=0x00ff00)
            embed.set_image(url=caution_image_url)
            embed.set_footer(text="Nguồn: Popcat API")
            view4 = discord.ui.View()
            view4.add_item(discord.ui.Button(label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=1239105383801290834&permissions=8&scope=bot"))
            view4.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/QxqkBWf5vr"))             
            await ctx.send(embed=embed, view=view4)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
    
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def jail(ctx, user: discord.User = None):
    user = user or ctx.author
    
    avatar_url = user.avatar.url
    api_url = f'https://api.popcat.xyz/jail?image={avatar_url}'
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            file = discord.File(image_data, filename="jail.png")
            
            embed = discord.Embed(title=f"`{user.name}` - Bạn đã bị `{ctx.author.name}` nhốt vào tù!", color=0xFFFFFF)
            embed.set_image(url="attachment://jail.png")
            view5 = discord.ui.View()
            view5.add_item(discord.ui.Button(label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=1239105383801290834&permissions=8&scope=bot"))
            view5.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/QxqkBWf5vr")) 
            await ctx.send(embed=embed, file=file, view=view5)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
    
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def fact(ctx, *, text: str):
    formatted_text = text.replace(' ', '+')
    
    api_url = f'https://api.popcat.xyz/facts?text={formatted_text}'
    
    try:
        response = requests.get(api_url)
        
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            file = discord.File(image_data, filename="fact.png")
            
            embed = discord.Embed(title="Fact", color=0x00ff00)
            embed.set_image(url="attachment://fact.png")
            view6 = discord.ui.View()
            view6.add_item(discord.ui.Button(label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=1239105383801290834&permissions=8&scope=bot"))
            view6.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/QxqkBWf5vr"))             
            await ctx.send(embed=embed, file=file, view=view6)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
    
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

class UserIDModal(Modal):
    def __init__(self, user: discord.User, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    id_input = TextInput(label="Nhập ID của bạn", placeholder="ID người dùng", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        user_id = self.id_input.value
        await self.create_ad(interaction, user_id)

    async def create_ad(self, interaction: discord.Interaction, user_id: str):
        avatar_url = self.user.avatar.url
        api_url = f'https://api.popcat.xyz/ad?image={avatar_url}'

        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                image_data = io.BytesIO(response.content)
                file = discord.File(image_data, filename="ad.png")

                embed = discord.Embed(
                    title=f"`{self.user.name}` đã được `{interaction.user.name}` đăng lên quảng cáo!",
                    description=f"**ID người dùng:** {user_id}",
                    color=0x00ff00
                )
                embed.set_image(url="attachment://ad.png")

                await interaction.response.edit_message(embed=embed, file=file)
            else:
                await interaction.response.send_message(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"Đã xảy ra lỗi: {e}", ephemeral=True)

@bot.command()
async def ad(ctx, user: discord.User = None):
    user = user or ctx.author

    view4 = discord.ui.View()
    view4.add_item(Button(label="Invite Me!", url="https://discord.com/oauth2/authorize?client_id=1239105383801290834&permissions=8&scope=bot"))
    view4.add_item(Button(label="Support Server", url="https://discord.gg/QxqkBWf5vr"))

    api_url = f'https://api.popcat.xyz/ad?image={user.avatar.url}'

    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            image_data = io.BytesIO(response.content)
            file = discord.File(image_data, filename="ad.png")

            embed = discord.Embed(
                title=f"`{user.name}` đã được `{ctx.author.name}` đăng lên quảng cáo!",
                description=f"**ID người dùng:** {user.id}",
                color=0x00ff00
            )
            embed.set_image(url="attachment://ad.png")

            await ctx.send(embed=embed, file=file, view=view4)
        else:
            await ctx.send(f"Đã xảy ra lỗi khi lấy hình ảnh từ API. Mã lỗi: {response.status_code}.")
    except Exception as e:
        await ctx.send(f"Đã xảy ra lỗi: {e}")

@bot.command()
async def nokia(ctx, member: discord.Member = None):
    if member is None:
        member = ctx.author

    avatar_url = member.avatar.url

    try:
        response = requests.get(f"https://api.popcat.xyz/nokia?image={avatar_url}")
        
        if response.status_code == 200:
            image_data = BytesIO(response.content)
            image_file = discord.File(image_data, filename="nokia_avatar.png")
            
            embed = discord.Embed(
                title=f"Ảnh đại diện với hiệu ứng 'Nokia' của {member.display_name}",
                color=discord.Color.blue()
            )
            embed.set_image(url="attachment://nokia_avatar.png")

            await ctx.send(embed=embed, file=image_file)
        else:
            await ctx.send("Có lỗi xảy ra khi xử lý hình ảnh. Vui lòng thử lại.")
    except Exception as e:
        await ctx.send(f"Có lỗi xảy ra: {str(e)}")

def discord_timestamp_cooldown(seconds):
    future_time = datetime.now() + timedelta(seconds=seconds)
    return f'<t:{int(future_time.timestamp())}:R>'

@bot.event
async def on_command_error(ctx, e):
    if isinstance(e, commands.CommandOnCooldown):
        remaining_time = e.retry_after

        a = discord_timestamp_cooldown(remaining_time)
        message = await ctx.send(f"- <:cancel:1261242787353858120> Bạn cần đợi {a} nữa")

        if remaining_time > 1:
            await asyncio.sleep(max(remaining_time - 1, 0))

        await message.delete()

    elif isinstance(e, commands.MissingPermissions):
        await ctx.send(f"<:cancel:1261242787353858120> | Bạn cần quyền `{', '.join(e.missing_permissions)}` để sử dụng lệnh này!")

    elif isinstance(e, commands.MissingRequiredArgument):
        await ctx.send(f"<:cancel:1261242787353858120> | Vui lòng nhập giá trị hợp lệ cho biến `{e.param.name}`!")

@bot.command(name="botinfo",aliases=["ib","infobot"])
async def botinfo(ctx):
    total_guilds = len(bot.guilds)
    total_users = sum(guild.member_count for guild in bot.guilds)
    total_channels = sum(len(guild.channels) for guild in bot.guilds)
    websocket_ping = round(bot.latency * 1000)
    os_info = platform.system()
    architecture = platform.machine()
    cores = psutil.cpu_count(logical=True)
    cpu_usage = f"{psutil.cpu_percent()}%"
    memory = psutil.virtual_memory()
    bot_ram_usage = psutil.Process().memory_info().rss / (1024 ** 2)
    bot_ram_available = memory.total / (1024 ** 3)
    bot_ram_percent = f"{(bot_ram_usage / (bot_ram_available * 1024)) * 100:.1f}%"
    overall_ram_used = memory.used / (1024 ** 3)
    overall_ram_available = memory.total / (1024 ** 3)
    overall_ram_percent = f"{memory.percent}%"
    python_version = platform.python_version()
    uptime = str(datetime.timedelta(seconds=int((datetime.datetime.now() - bot.start_time).total_seconds())))

    embed = discord.Embed(title="Bot Information",description =  f"❒ Total guilds: {total_guilds} \n ❒ Total users: {total_users} \n ❒ Total channels: {total_channels} \n ❒ Websocket Ping: {websocket_ping} ms \n ",color=0x00ff00)
    embed.set_thumbnail(url=bot.user.avatar.url)  # Set bot's avatar as the thumbnail
    
    embed.add_field(name="CPU", value=f"❯ **OS:** {os_info} [{architecture}]\n❯ **Cores:** {cores}\n❯ **Usage:** {cpu_usage}", inline=True)
    embed.add_field(name="Bot's RAM", value=f"❯ **Used:** {bot_ram_usage:.2f} MB\n❯ **Available:** {bot_ram_available:.2f} GB\n❯ **Usage:** {bot_ram_percent}", inline=True)
    embed.add_field(name="Overall RAM", value=f"❯ **Used:** {overall_ram_used:.2f} GB\n❯ **Available:** {overall_ram_available:.2f} GB\n❯ **Usage:** {overall_ram_percent}", inline=True)
    embed.add_field(name="Python Version", value=python_version, inline=False)
    embed.add_field(name="Uptime", value=f"```{uptime}```", inline=False)

    view = discord.ui.View()
    view.add_item(discord.ui.Button(label="Invite Link", url="https://discord.com/oauth2/authorize?client_id=1268055884987109447"))
    view.add_item(discord.ui.Button(label="Support Server", url="https://discord.gg/milosupport"))

    await ctx.send(embed=embed, view=view)

ZOO_FILE = "zoo.json"

# Danh sách thú và độ hiếm
ANIMALS = {
    "common": ["Rabbit", "Deer", "Squirrel"],
    "uncommon": ["Fox", "Hedgehog", "Raccoon"],
    "rare": ["Wolf", "Eagle", "Bear"],
    "legendary": ["Dragon", "Phoenix", "Unicorn"]
}

# Tạo file zoo.json nếu chưa tồn tại
def ensure_zoo_file():
    try:
        with open(ZOO_FILE, "r") as f:
            json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        with open(ZOO_FILE, "w") as f:
            json.dump({}, f)

# Thêm thú vào bộ sưu tập
def add_to_zoo(user_id, animal):
    ensure_zoo_file()
    with open(ZOO_FILE, "r") as f:
        data = json.load(f)
    
    if str(user_id) not in data:
        data[str(user_id)] = {}

    if animal in data[str(user_id)]:
        data[str(user_id)][animal] += 1
    else:
        data[str(user_id)][animal] = 1

    with open(ZOO_FILE, "w") as f:
        json.dump(data, f)

# Lấy bộ sưu tập của người dùng
def get_zoo(user_id):
    ensure_zoo_file()
    with open(ZOO_FILE, "r") as f:
        data = json.load(f)
    
    return data.get(str(user_id), {})

ANIMAL_EMOJIS = {
    "Rabbit": "🐇",
    "Deer": "🦌",
    "Squirrel": "🐿️",
    "Fox": "🦊",
    "Hedgehog": "🦔",
    "Raccoon": "🦝",
    "Sheep": ":sheep:",
    "Bee": ":bee:",
    "Cow": ":cow2:",
    "Rooster": ":rooster:",
    "Butterfly": ":butterfly:",
    "Wolf": "🐺",
    "Eagle": "🦅",
    "Bear": "🐻",
    "Unicorn": "🦄",
    "Tiger": "🐅",
    "Phoenix": "<a:phoenix:1333890746738151445>",
    "Panda": "🐼",
    "Bear": "🐻",
    "Unicorn": "🦄",
    "Gold Deer": "<a:gold_deer:1333892029704310865>",
    "Gold Fox": "<a:gold_fox:1333892033164607539>",
    "Gold Lion": "<a:gold_lion:1333892037136875672>",
    "Gold Owl": "<a:gold_owl:1333892040831930428>",
    "Gold Squid": "<a:gold_squid:1333892044459868242>"
}

RARITY_EMOJIS = {
    "common": "<:common:1333885176400576562>",
    "uncommon": "<:uncommon:1333885188572184640>",
    "rare": "<:rare:1333885183933419620>",
    "epic": "<:epic:1333885178510315692>",
    "mythic": "<:mythic:1333885181790261350>"
}

ANIMALS = {
    "common": ["Rabbit", "Deer", "Squirrel", "Sheep", "Bee", "Cow"],
    "uncommon": ["Fox", "Hedgehog", "Raccoon", "Rooster", "Butterfly"],
    "rare": ["Wolf", "Eagle", "Bear"],
    "epic": ["Tiger", "Panda"],
    "mythic": ["Phoenix", "Unicorn","Gold Deer", "Gold Fox", "Gold Lion", "Gold Owl", "Gold Squid"]
}

@bot.command(name="hunt",aliases=["h"])
@commands.cooldown(1, 15, commands.BucketType.user)
async def hunt(ctx):
    rarity = random.choices(["common", "uncommon", "rare", "epic", "mythic"], weights=[70, 20, 9, 1, 0.5], k=1)[0]
    animal = random.choice(ANIMALS[rarity])

    add_to_zoo(ctx.author.id, animal)

    await ctx.send(f"<a:ml_cay:1267679528193495123> **|** {ctx.author.display_name}, bạn vào rừng săn và tìm thấy {ANIMAL_EMOJIS[animal]} {animal} | {RARITY_EMOJIS[rarity]}")

@bot.command(name="zoo",aliases=["z"])
async def zoo(ctx):
    zoo = get_zoo(ctx.author.id)
    
    if not zoo:
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn chưa có thú nào trong vườn.")
        return

    # Đếm số lượng động vật theo độ hiếm
    rarity_count = {"common": 0, "uncommon": 0, "rare": 0, "epic": 0, "mythic": 0}

    # Hiển thị động vật trong bộ sưu tập
    zoo_text = ""
    for rarity, animals in ANIMALS.items():
        row = f"{RARITY_EMOJIS[rarity]} "
        for animal in animals:
            count = zoo.get(animal, 0)
            row += f"{ANIMAL_EMOJIS[animal]} {count}  " if count > 0 else "❓"
            rarity_count[rarity] += count
        zoo_text += row + "\n"

    # Tính tổng điểm Zoo Points
    zoo_points = (rarity_count["common"] * 1) + (rarity_count["uncommon"] * 3) + \
                 (rarity_count["rare"] * 7) + (rarity_count["epic"] * 12) + (rarity_count["mythic"] * 20)

    # Tạo Embed giống OwO Bot
    embed = discord.Embed(title=f"<a:ml_cay:1267679528193495123> Vườn thú của {ctx.author.name} <a:ml_cay:1267679528193495123>", color=discord.Color.green())
    embed.description = zoo_text
    embed.add_field(name=f"Zoo Points: {zoo_points}", value="", inline=False)
    embed.add_field(name=f"M-{rarity_count['mythic']}, E-{rarity_count['epic']}, R-{rarity_count['rare']}, U-{rarity_count['uncommon']}, C-{rarity_count['common']}",value="",inline=False)

    await ctx.send(embed=embed)

def update_user_cash(user_id, amount):
    data = load_econ()
    
    if str(user_id) not in data:
        data[str(user_id)] = {"cash": 0}
    
    data[str(user_id)]["cash"] += amount

    save_econ(data)

# Sell animal and update zoo and cash
@bot.command(name="sell")
async def sell(ctx, animal: str = None):
    zoo = get_zoo(ctx.author.id)
    
    if not zoo:
        await ctx.send("<:cancel:1307210917594796032> | Bạn chưa có thú nào để bán.")
        return
    
    # Sell all animals
    if animal == "all":
        total_cash = 0
        for animal in zoo:
            total_cash += sell_animal(ctx, animal, zoo[animal])
        await ctx.send(f"Bạn đã bán tất cả các thú trong vườn. Bạn đã kiếm được {total_cash} <:mlcoin:1330026986667769867>.")
        return
    
    # If a specific animal is mentioned, sell that animal
    if animal not in zoo:
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn không có {ANIMAL_EMOJIS.get(animal, '❓')} {animal} trong vườn thú.")
        return
    
    total_cash = sell_animal(ctx, animal, zoo[animal])
    await ctx.send(f"Bạn đã bán {ANIMAL_EMOJIS.get(animal, '❓')} {animal}. Bạn đã kiếm được {total_cash} <:mlcoin:1330026986667769867>.")

# Helper function to sell animal and calculate its cash value
def sell_animal(ctx, animal_name, quantity):
    rarity = get_animal_rarity(animal_name)
    cash_per_animal = calculate_animal_value(rarity)
    
    total_cash = cash_per_animal * quantity
    update_user_cash(ctx.author.id, total_cash)
    
    # Remove sold animals from zoo
    remove_from_zoo(ctx.author.id, animal_name, quantity)
    
    return total_cash

# Get the rarity of an animal
def get_animal_rarity(animal_name):
    for rarity, animals in ANIMALS.items():
        if animal_name in animals:
            return rarity
    return "common"  # Default to common if not found

# Calculate the cash value of an animal based on its rarity
def calculate_animal_value(rarity):
    value = {
        "common": 10,
        "uncommon": 30,
        "rare": 70,
        "epic": 150,
        "mythic": 300
    }
    return value.get(rarity, 10)

def remove_from_zoo(user_id, animal_name, quantity):
    ensure_zoo_file()
    with open(ZOO_FILE, "r") as f:
        data = json.load(f)
    
    if str(user_id) in data and animal_name in data[str(user_id)]:
        if data[str(user_id)][animal_name] <= quantity:
            del data[str(user_id)][animal_name]
        else:
            data[str(user_id)][animal_name] -= quantity
    
    with open(ZOO_FILE, "w") as f:
        json.dump(data, f)

def load_inv():
    with open("inv.json", "r") as f:
        inv = json.load(f)
    return inv

def save_inv(inv):
    with open('inv.json', 'w') as f:
        json.dump(inv, f, indent=4)

class PaginatorShop(discord.ui.View):
    def __init__(self, pages , ctx):
        super().__init__(timeout=180)  # View sẽ tự động hết hạn sau 180 giây
        self.pages = pages
        self.current_page = 0
        self.ctx = ctx

        self.prev_button = discord.ui.Button(emoji="<:muitentrai:1297154558384144384>", style=discord.ButtonStyle.primary)
        self.home_button = discord.ui.Button(emoji="<:home:1297154827012542609>", style=discord.ButtonStyle.primary)
        self.next_button = discord.ui.Button(emoji="<:muitenphai:1297154785610301450>", style=discord.ButtonStyle.primary)

        self.prev_button.callback = self.previous_page
        self.home_button.callback = self.home_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.home_button)
        self.add_item(self.next_button)

    async def home_page(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1261242787353858120> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        self.current_page = 0
        embed = discord.Embed(title="**Milo Hỗ Trợ**",description=f"Xin chào {interaction.user.mention},dưới đây là các danh mục shop \n \n 🛒 `:` Gian hàng chính \n <:ml_premium:1247467886457524285> `:` Gian hàng premium \n <:pet:1310148666773737472> `:` Gian hàng pet \n <a:snowflake2:1304412171895312437> `:` Gian sự kiện",color=discord.Color.orange())
        await interaction.response.edit_message(embed=embed)

    async def previous_page(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1261242787353858120> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])
        else:
            await interaction.response.defer()

    async def next_page(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1261242787353858120> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])
        else:
            await interaction.response.defer()

    async def on_timeout(self):
        # Khi hết thời gian, xóa các nút và cập nhật tin nhắn
        for child in self.children:
            child.disabled = True  # Vô hiệu hóa các nút
        await self.message.edit(view=None) 

    # Hàm tạo Embed dựa trên trang hiện tại
    def get_embed(self):
        embed = discord.Embed(
            title=f"Page {self.current_page + 1}/{len(self.pages)}",
            description=self.pages[self.current_page],
            color=discord.Color.blue()
        )
        return embed

shop_item = {"tv": 8000 , "the": 500 , "pre1m": 300 , "pre3m": 800 , "pre1y": 3000 , "10": 500 , "11": 500 , "12": 500 , "13": 2000 , "14": 2000 , "15": 2000}

@bot.command()
async def shop(ctx):
    pages = [
        discord.Embed(title="**Milo Shop**",description=f"Xin chào {ctx.author.mention},dưới đây là các danh mục shop \n \n 🛒 `:` Gian hàng chính \n <:ml_premium:1247467886457524285> `:` Gian hàng premium \n <:pet:1310148666773737472> `:` Gian hàng pet \n <a:snowflake2:1304412171895312437> `:` Gian sự kiện",color=discord.Color.orange()),
        discord.Embed(title="Gian Hàng Chính",description="TV: id tv \n > Giá: 8.000 <:ml_coin:1246279542172291163> \n \n Thẻ: id the \n > Giá: 500 <:ml_coin:1246279542172291163>" ,color=discord.Color.yellow()),
        discord.Embed(title="Gian Hàng Premium",description="Premium 1 tháng: id pre1m \n > Giá: 300 <:micoin:1307211365890654248> \n \n Premium 3 tháng: id pre3m \n > Giá: 800 <:micoin:1307211365890654248> \n \n Premium 1 năm: id pre1y \n > Giá: 3000 <:micoin:1307211365890654248>" ,color=discord.Color.yellow()),
        #discord.Embed(title="Gian Hàng Pet",description="Pet: :rooster: ID: 10 \n > Giá: 500 <:mlcoin:1307211294981492827> \n Pet: :duck: ID: 11 \n > Giá: 500 <:mlcoin:1307211294981492827> \n Pet: :rabbit2: ID: 12 \n > Giá: 500 <:mlcoin:1307211294981492827> \n Pet: :dog2: ID: 13 \n > Giá: 2000 <:mlcoin:1307211294981492827> \n Pet: :cat2: ID: 14 \n > Giá: 2000 <:mlcoin:1307211294981492827> \n Pet: :pig2: ID: 15 \n > Giá: 2000 <:mlcoin:1307211294981492827>" ,color=discord.Color.yellow()),
        discord.Embed(title="Gian Hàng Pet",description="Gian hàng chưa có gì." ,color=discord.Color.yellow()),
        discord.Embed(title="Gian Hàng Sự Kiện",description="Gian hàng chưa có gì." ,color=discord.Color.yellow())
    ]

    embed = discord.Embed(title="**Milo Shop**",description=f"Xin chào {ctx.author.mention},dưới đây là các danh mục shop \n \n 🛒 `:` Gian hàng chính \n <:ml_premium:1247467886457524285> `:` Gian hàng premium \n <:pet:1310148666773737472> `:` Gian hàng pet \n <a:snowflake2:1304412171895312437> `:` Gian sự kiện",color=discord.Color.orange())

    view = PaginatorShop(pages,ctx)
    await ctx.send(embed=embed , view=view)

@bot.command()
async def buy(ctx, item: str):
    data = load_econ()
    inv = load_inv()
    micash = load_micoin()
    pet = load_pet()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = {
                'cash': 0,
                'last_daily_claim': datetime.utcnow().isoformat(),
                'dailied': False
            }
    if user_id not in pet:
        pet[user_id] = {'inv': {} , 'data': {}}
    if pet[user_id]['inv'] == {}:
        pet[user_id]['inv'] = {
            '10': 0,
            '11': 0,
            '12': 0,
            '13': 0,
            '14': 0,
            '15': 0
            }
        save_pet(pet)
    if user_id not in inv:
        inv[user_id] = {'tv': 0 , 'the': 0}

    if item in shop_item:
        price = shop_item[item]
        
        if item == "tv":
            if data[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
        
            inv[user_id]['tv'] += 1
            item = ":tv:"
            data[user_id]['cash'] -= price
        elif item == "the":
            if data[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
            
            item = "<:vipticket:1280790359584276503>"
            inv[user_id]['the'] += 1
            data[user_id]['cash'] -= price
        elif item == 10:
            if data[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
            item = ":rooster:"
            pet[user_id]['inv']['10'] += 1
            save_pet(pet)
        elif item == 11:
            if data[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
            item = ":duck:"
            pet[user_id]['inv']['11'] += 1
            save_pet(pet)
        elif item == 12:
            if data[user_id]['inv']['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
            item = ":rabbit2:"
            pet[user_id]['inv']['12'] += 1
            save_pet(pet)
        elif item == 13:
            if data[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
            item = ":dog2:"
            pet[user_id]['inv']['13'] += 1
            save_pet(pet)
        elif item == 14:
            if data[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
            item = ":cat2:"
            pet[user_id]['inv']['14'] += 1
            save_pet(pet)
        elif item == 15:
            if data[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return
            item = ":pig2:"
            pet[user_id]['inv']['15'] += 1
            save_pet(pet)

        elif item in ["pre1m", "pre3m", "pre1y"]:
            if micash[user_id]['cash'] < price:
                await ctx.send("<:cancel:1261242787353858120> | Bạn không có đủ tiền để mua đồ.")
                return

            days_to_add = 30 if item == "pre1m" else 90 if item == "pre3m" else 360
            
            # Lấy ngày hết hạn hiện tại, hoặc đặt mặc định là hôm nay
            current_expiration = datetime.fromisoformat(premium_data['users'][user_id])
            new_expiration = current_expiration + timedelta(days=days_to_add)
            
            # Cập nhật dữ liệu
            premium_data['users'][user_id] = new_expiration.isoformat()
            micash[user_id]['cash'] -= price

            # Lưu dữ liệu
        save_premium_data()
        save_micoin(micash)
        save_econ(data)
        save_inv(inv)
        save_pet(pet)

        await ctx.send(f"<:checked:1261242796916998144> | Bạn đã mua thành công {item} với giá {price}.")
    else:
        await ctx.send("<:cancel:1261242787353858120> | Mặt hàng này không có trong cửa hàng.")

class PaginatorInv(discord.ui.View):
    def __init__(self, pages , ctx):
        super().__init__(timeout=180)  # View sẽ tự động hết hạn sau 180 giây
        self.pages = pages
        self.current_page = 0
        self.ctx = ctx

        self.prev_button = discord.ui.Button(emoji="<:muitentrai:1297154558384144384>", style=discord.ButtonStyle.primary)
        self.home_button = discord.ui.Button(emoji="<:home:1297154827012542609>", style=discord.ButtonStyle.primary)
        self.next_button = discord.ui.Button(emoji="<:muitenphai:1297154785610301450>", style=discord.ButtonStyle.primary)

        self.prev_button.callback = self.previous_page
        self.home_button.callback = self.home_page
        self.next_button.callback = self.next_page

        self.add_item(self.prev_button)
        self.add_item(self.home_button)
        self.add_item(self.next_button)

    async def home_page(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1261242787353858120> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        self.current_page = 0
        embed = discord.Embed(title=f"**Túi đồ của {interaction.user.display_name}**",description=f"Xin chào {interaction.user.mention},dưới đây là các danh mục inv \n \n <:pack:1304405024033607680> `:` Túi đồ thường \n <a:snowflake2:1304412171895312437> `:` Túi đồ sự kiện",color=discord.Color.green())
        await interaction.response.edit_message(embed=embed)

    async def previous_page(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1261242787353858120> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        if self.current_page > 0:
            self.current_page -= 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])
        else:
            await interaction.response.defer()

    async def next_page(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1261242787353858120> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            await interaction.response.edit_message(embed=self.pages[self.current_page])
        else:
            await interaction.response.defer()

    async def on_timeout(self):
        # Khi hết thời gian, xóa các nút và cập nhật tin nhắn
        for child in self.children:
            child.disabled = True  # Vô hiệu hóa các nút
        await self.message.edit(view=None) 

    # Hàm tạo Embed dựa trên trang hiện tại
    def get_embed(self):
        embed = discord.Embed(
            title=f"Page {self.current_page + 1}/{len(self.pages)}",
            description=self.pages[self.current_page],
            color=discord.Color.blue()
        )
        return embed

@bot.command()
async def inv(ctx):
    inv = load_inv()
    user_id = str(ctx.author.id)

    # Khởi tạo dữ liệu nếu chưa có
    if user_id not in inv:
        inv[user_id] = {'tv': 0, 'the': 0, 'pacK_giang_sinh': 0, 'bongtuyet': 0, 'caythong': 0}

    save_inv(inv)

    # Tạo các trang
    pages = [
        discord.Embed(
            title=f"**Túi đồ của {ctx.author.display_name}**",
            description=f"Xin chào {ctx.author.mention}, dưới đây là các danh mục inv \n\n"
                        f"<:pack:1304405024033607680> `:` Túi đồ thường \n"
                        f"<a:snowflake2:1304412171895312437> `:` Túi đồ sự kiện",
            color=discord.Color.green()
        ),
        discord.Embed(
            title="Túi đồ thường",
            description=f"<:chamxanhbien:1275686480240705546> TV: {inv[user_id]['tv']} \n"
                        f"<:chamxanhbien:1275686480240705546> Thẻ: {inv[user_id]['the']}",
            color=discord.Color.yellow()
        ),
        discord.Embed(
            title="Túi đồ sự kiện",
            description=f"Túi đồ không có gì.",
            color=discord.Color.yellow()
        )
    ]

    view = PaginatorInv(pages, ctx)
    await ctx.send(embed=pages[0], view=view)

def load_event():
    try:
        with open("event.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_event(data):
    with open("event.json", "w") as file:
        json.dump(data, file, indent=2)

@bot.command()
@commands.cooldown(1, 5, commands.BucketType.user)
async def use(ctx, item_id: int):
    inv = load_inv()
    user_id = str(ctx.author.id)
    
    if user_id not in inv:
        inv[user_id] = {'tv': 0, 'the': 0, 'pacK_giang_sinh': 0}
    if 'pacK_giang_sinh' not in inv[user_id]:
        inv[user_id]['pacK_giang_sinh'] = 0

    if item_id == 77:
        if inv[user_id]['pacK_giang_sinh'] == 0:
            await ctx.send("<:cancel:1307210917594796032> | Bạn không có `pack giáng sinh` để mở.")
            return
        
        inv[user_id]['pacK_giang_sinh'] -= 1

        save_inv(inv)
        
        giang_sinh_emoji = [
            '<a:pine:1304408486653726731>', 
            '<:gingerbread:1304407913011613748>', 
            '<:candycane:1304407914714497034>', 
            '<:snowball:1304407901766418442>', 
            '<a:snowflake2:1304412171895312437>', 
            '<a:snowflakes:1304407905893748797>'
        ]
        
        emoji_chon = random.choice(giang_sinh_emoji)

        await ctx.send(f"<a:snowflakes:1304407905893748797> | Bạn mở `pack giáng sinh` và nhận được {emoji_chon}")
    else:
        await ctx.send(f"<:cancel:1307210917594796032> | id `{item_id}` không tồn tại.")

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def hochoi(ctx):
    data = load_event()
    user_id = str(ctx.author.id)

    # Khởi tạo dữ liệu nếu chưa có
    if user_id not in data:
        data[user_id] = {'inv': {}, 'data': {}}
    if data[user_id]['inv'] == {}:
        data[user_id]['inv'] = {'bongtuyet': 0, 'caythong': 0}
    if data[user_id]['data'] == {}:
        data[user_id]['data'] = {'sucmanh': 0, 'exp': 0,'streak': 0}

    # Tăng exp cho người dùng (ngẫu nhiên từ 1 đến 5)
    exp = data[user_id]['data']['exp']
    bongtuyet = data[user_id]['inv']['bongtuyet']
    caythong = data[user_id]['inv']['caythong']

    save_event(data)

    # Xác định mức giảm dựa trên exp
    if exp >= 5:
        bong_tuyet_tru = 5
        cay_thong_tru = 3
    elif exp >= 20:
        bong_tuyet_tru = 10
        cay_thong_tru = 8
    elif exp >= 30:
        bong_tuyet_tru = 15
        cay_thong_tru = 10
    elif exp >= 50:
        bong_tuyet_tru = 30
        cay_thong_tru = 25
    elif exp >= 100:
        bong_tuyet_tru = 50
        cay_thong_tru = 45
    else:
        bong_tuyet_tru = 2
        cay_thong_tru = 1
    
    if bongtuyet < bong_tuyet_tru or caythong < cay_thong_tru:
        bong_tuyet_thieu = max(0, bong_tuyet_tru - bongtuyet)
        cay_thong_thieu = max(0, cay_thong_tru - caythong)
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn thiếu **{bong_tuyet_thieu}** <:snowball:1304407901766418442> & **{cay_thong_thieu}** <a:pine:1304408486653726731>")
        return

    exp_gain = random.randint(1, 5)

    data[user_id]['data']['exp'] += exp_gain
    data[user_id]['inv']['bongtuyet'] -= bong_tuyet_tru
    data[user_id]['inv']['caythong'] -= cay_thong_tru

    # Lưu dữ liệu
    save_event(data)

    # Thông báo cho người dùng
    await ctx.send(f"{ctx.author.display_name} | Bạn đã học hỏi và tăng **{exp_gain}** xp")

@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def luyentap(ctx):
    data = load_event()
    user_id = str(ctx.author.id)

    # Khởi tạo dữ liệu nếu chưa có
    if user_id not in data:
        data[user_id] = {'inv': {}, 'data': {}}
    if data[user_id]['inv'] == {}:
        data[user_id]['inv'] = {'bongtuyet': 0, 'caythong': 0}
    if data[user_id]['data'] == {}:
        data[user_id]['data'] = {'sucmanh': 0, 'exp': 0,'streak': 0}

    # Tăng exp cho người dùng (ngẫu nhiên từ 5 đến 10)
    exp = data[user_id]['data']['exp']
    bongtuyet = data[user_id]['inv']['bongtuyet']
    caythong = data[user_id]['inv']['caythong']

    save_event(data)

    # Xác định mức giảm dựa trên exp
    if exp >= 5:
        bong_tuyet_tru = 5
        cay_thong_tru = 3
    elif exp >= 20:
        bong_tuyet_tru = 10
        cay_thong_tru = 8
    elif exp >= 30:
        bong_tuyet_tru = 15
        cay_thong_tru = 10
    elif exp >= 50:
        bong_tuyet_tru = 30
        cay_thong_tru = 25
    elif exp >= 100:
        bong_tuyet_tru = 50
        cay_thong_tru = 45
    else:
        bong_tuyet_tru = 2
        cay_thong_tru = 1
    
    if bongtuyet < bong_tuyet_tru or caythong < cay_thong_tru:
        bong_tuyet_thieu = max(0, bong_tuyet_tru - bongtuyet)
        cay_thong_thieu = max(0, cay_thong_tru - caythong)
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn thiếu **{bong_tuyet_thieu}** <:snowball:1304407901766418442> & **{cay_thong_thieu}** <a:pine:1304408486653726731> để vào sân tập luyện.")
        return

    exp_gain = random.randint(5, 10)

    data[user_id]['data']['exp'] += exp_gain
    data[user_id]['inv']['bongtuyet'] -= bong_tuyet_tru
    data[user_id]['inv']['caythong'] -= cay_thong_tru

    # Lưu dữ liệu
    save_event(data)

    # Thông báo cho người dùng
    await ctx.send(f"{ctx.author.display_name} | Bạn vừa tập luyện và tăng **{exp_gain}** xp")

@bot.command()
#@commands.cooldown(1, 60, commands.BucketType.user)
async def tapgym(ctx):
    data = load_event()
    user_id = str(ctx.author.id)

    # Khởi tạo dữ liệu nếu chưa có
    if user_id not in data:
        data[user_id] = {'inv': {}, 'data': {}}
    if data[user_id]['inv'] == {}:
        data[user_id]['inv'] = {'bongtuyet': 0, 'caythong': 0}
    if data[user_id]['data'] == {}:
        data[user_id]['data'] = {'sucmanh': 0, 'exp': 0,'streak': 0}

    # Tăng exp cho người dùng (ngẫu nhiên từ 5 đến 10)
    power = data[user_id]['data']['sucmanh']
    bongtuyet = data[user_id]['inv']['bongtuyet']
    caythong = data[user_id]['inv']['caythong']

    save_event(data)

    # Xác định mức giảm dựa trên exp
    if power >= 5:
        bong_tuyet_tru = 5
        cay_thong_tru = 3
    elif power >= 20:
        bong_tuyet_tru = 10
        cay_thong_tru = 8
    elif power >= 30:
        bong_tuyet_tru = 15
        cay_thong_tru = 10
    elif power >= 50:
        bong_tuyet_tru = 30
        cay_thong_tru = 25
    elif power >= 100:
        bong_tuyet_tru = 50
        cay_thong_tru = 45
    else:
        bong_tuyet_tru = 2
        cay_thong_tru = 1
    
    if bongtuyet < bong_tuyet_tru or caythong < cay_thong_tru:
        bong_tuyet_thieu = max(0, bong_tuyet_tru - bongtuyet)
        cay_thong_thieu = max(0, cay_thong_tru - caythong)
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn thiếu **{bong_tuyet_thieu}** <:snowball:1304407901766418442> & **{cay_thong_thieu}** <a:pine:1304408486653726731> để vào phòng tập gym.")
        return

    power_gain = random.randint(5, 10)

    data[user_id]['data']['sucmanh'] += power_gain
    data[user_id]['inv']['bongtuyet'] -= bong_tuyet_tru
    data[user_id]['inv']['caythong'] -= cay_thong_tru

    # Lưu dữ liệu
    save_event(data)

    # Thông báo cho người dùng
    await ctx.send(f"{ctx.author.display_name} | Bạn vừa tập gym và tăng **{power_gain}** sức mạnh")

@bot.command()
async def nemtuyet(ctx):
    pass

def load_pray():
    try:
        with open("pray.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_pray(data):
    with open("pray.json", "w") as file:
        json.dump(data, file, indent=2)

@bot.command()
@commands.cooldown(1, 300, commands.BucketType.user)
async def pray(ctx, member: str = None):
    # Load existing pray data
    data = load_pray()
    user_id = str(ctx.author.id)

    # Handle the case where the member input is invalid
    if member:
        try:
            member_get = await get_user_from_input(ctx, member)
        except ValueError:  # Adjust according to your error handling in get_user_from_input
            await ctx.send("Không tìm thấy người dùng này.")
            return
        member_id = str(member_get.id)
    else:
        # If no member is provided, only show user's pray points
        await ctx.send(f"**{ctx.author.display_name}** | Bạn đang có {data.get(user_id, {'pray': 0})['pray']} điểm may mắn")
        return

    # Prevent users from praying for themselves
    if member_id == user_id:
        await ctx.send(f"**{ctx.author.display_name}** | Bạn đang có {data.get(user_id, {'pray': 0})['pray']} điểm may mắn")
        return
    
    if member_id == str(bot.user.id):
        await ctx.send(f"**{ctx.author.display_name}** cầu nguyện cho một người máy nhưng? ... tại sao? ...")
        return

    # Ensure both users exist in the data
    if user_id not in data:
        data[user_id] = {'pray': 0}
    if member_id not in data:
        data[member_id] = {'pray': 0}

    # Update pray points
    data[user_id]['pray'] -= 1
    data[member_id]['pray'] += 1

    # Save the updated data
    save_pray(data)

    # Send the result
    await ctx.send(f"**{ctx.author.display_name}** cầu nguyện cho **{member_get.display_name}** gặp nhiều may mắn")

# Tải dữ liệu từ disable.json
def load_disable():
    try:
        with open("disable.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Lưu dữ liệu vào disable.json
def save_disable(data):
    with open("disable.json", "w") as file:
        json.dump(data, file, indent=4)

disabled_commands = load_disable()

@bot.command()
@commands.has_permissions(administrator=True)
async def disable(ctx, command_name: str):
    channel_id = str(ctx.channel.id)

    # Nếu command_name là "all", vô hiệu hóa tất cả lệnh trong kênh này
    if command_name.lower() == "all":
        disabled_commands[channel_id] = [cmd.name for cmd in bot.commands if cmd.name not in ["disable", "enable"]]
        save_disable(disabled_commands)
        await ctx.send("<:checked:1261242796916998144> | Đã vô hiệu hóa tất cả các lệnh trong kênh này.")
        return

    # Kiểm tra xem lệnh có tồn tại trong bot hay không
    command = bot.get_command(command_name)
    if not command:
        await ctx.send(f"<:cancel:1261242787353858120> | Lệnh `{command_name}` không tồn tại")
        return

    # Thêm lệnh vào kênh trong disable.json
    if channel_id not in disabled_commands:
        disabled_commands[channel_id] = []
    
    if command_name not in disabled_commands[channel_id]:
        disabled_commands[channel_id].append(command_name)
        save_disable(disabled_commands)
        await ctx.send(f"<:checked:1261242796916998144> | Đã thành công vô hiệu hóa lệnh `{command_name}` trong kênh này.")
    else:
        await ctx.send(f"<:cancel:1261242787353858120> | Lệnh `{command_name}` đã bị vô hiệu hóa trong kênh này.")

@bot.command()
@commands.has_permissions(administrator=True)
async def enable(ctx, command_name: str):
    channel_id = str(ctx.channel.id)

    # Nếu command_name là "all", kích hoạt lại tất cả các lệnh trong kênh này
    if command_name.lower() == "all":
        if channel_id in disabled_commands:
            del disabled_commands[channel_id]
            save_disable(disabled_commands)
            await ctx.send("<:checked:1261242796916998144> | Thành công kích hoạt lại tất cả các lệnh trong kênh này.")
        else:
            await ctx.send("<:cancel:1261242787353858120> | Không có lệnh nào bị vô hiệu hóa trong kênh này.")
        return

    # Kiểm tra xem lệnh có tồn tại trong bot hay không
    command = bot.get_command(command_name)
    if not command:
        await ctx.send(f"<:cancel:1261242787353858120> | Lệnh `{command_name}` không tồn tại")
        return

    # Kiểm tra nếu kênh có trong disable.json và lệnh đã bị vô hiệu hóa
    if channel_id in disabled_commands and command_name in disabled_commands[channel_id]:
        disabled_commands[channel_id].remove(command_name)

        # Xóa kênh khỏi disable.json nếu không còn lệnh nào bị vô hiệu hóa
        if not disabled_commands[channel_id]:
            del disabled_commands[channel_id]

        save_disable(disabled_commands)
        await ctx.send(f"<:checked:1261242796916998144> | Thành công kích hoạt lệnh `{command_name}` trong kênh này.")
    else:
        await ctx.send(f"<:cancel:1261242787353858120> | Lệnh `{command_name}` không bị vô hiệu hóa trong kênh này.")

# Kiểm tra xem lệnh có bị vô hiệu hóa trong kênh hay không
@bot.check
async def globally_block_commands(ctx):
    channel_id = str(ctx.channel.id)
    command_name = ctx.command.name

    # Bỏ qua kiểm tra cho các lệnh enable và disable
    if command_name in ["enable", "disable"]:
        return True

    # Kiểm tra nếu tất cả lệnh bị vô hiệu hóa trong kênh
    if channel_id in disabled_commands and ("all" in disabled_commands[channel_id] or command_name in disabled_commands[channel_id]):
        await ctx.send(f"<:cancel:1261242787353858120> | Lệnh `{command_name}` đã bị vô hiệu hóa trong kênh này.")
        return False
    return True

# Tải dữ liệu từ autorole.json
def load_autoroles():
    try:
        with open("autorole.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Lưu dữ liệu vào autorole.json
def save_autoroles(data):
    with open("autorole.json", "w") as file:
        json.dump(data, file, indent=4)

autoroles = load_autoroles()

@bot.command()
@commands.has_permissions(administrator=True)
async def setautorole(ctx, role_id: int):
    guild_id = str(ctx.guild.id)

    # Lưu ID vai trò vào autorole.json
    autoroles[guild_id] = role_id
    save_autoroles(autoroles)
    await ctx.send(f"<:checked:1261242796916998144> | Đã đặt vai trò tự động cho server.")

@bot.command()
@commands.has_permissions(administrator=True)
async def removeautorole(ctx):
    guild_id = str(ctx.guild.id)

    # Xóa vai trò tự động của máy chủ
    if guild_id in autoroles:
        del autoroles[guild_id]
        save_autoroles(autoroles)
        await ctx.send("<:checked:1261242796916998144> | Đã xóa vai trò tự động cho server này.")
    else:
        await ctx.send("<:cancel:1261242787353858120> | Không có vai trò tự động nào được thiết lập cho server này.")

@bot.event
async def on_member_join(member):
    guild_id = str(member.guild.id)

    if member.bot:
        return

    if guild_id in autoroles:
        role_id = autoroles[guild_id]
        role = member.guild.get_role(int(role_id))
        if role:
            await member.add_roles(role)
        else:
            print(f"Vai trò với ID {role_id} không tồn tại trong server {member.guild.name}.")

def load_agreementsrule():
    try:
        with open("agreementsrule.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_agreementsrule(data):
    with open("agreementsrule.json", "w") as file:
        json.dump(data, file, indent=2)

class AcceptTermsView(View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        self.ctx = ctx

    @discord.ui.button(label="Tôi chấp nhận quy tắc của bot.", style=discord.ButtonStyle.green)
    async def accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.ctx.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Có vẻ như nút này không dành cho bạn.", ephemeral=True)
            return
        
        user_id = str(interaction.user.id)
        data = load_agreementsrule()

        if 'user' not in data:
            data['user'] = {}

        data['user'][user_id] = True

        save_agreementsrule(data)

        for item in self.children:
            item.disabled = True

        embed = discord.Embed(
            title="Không tuân thủ các quy định này sẽ dẫn đến bị cấm hoặc reset tài khoản",
            description="• Bất kỳ hành động nào được thực hiện để giành lợi thế không công bằng so với những người dùng khác đều vi phạm rõ ràng các quy định. Điều này bao gồm nhưng không giới hạn ở: \n └> Sử dụng macro/script cho bất kỳ lệnh nào \n └> Sử dụng nhiều tài khoản vì bất kỳ lý do gì \n \n • **Không sử dụng** bất kỳ lỗi nào của bot. \n \n • Nếu bạn có bất kỳ câu hỏi nào, hãy hỏi chúng tôi trong [server support](https://discord.gg/QxqkBWf5vr) \n \n [Chính sách bảo mật](https://discord.com/channels/1242775514951847936/1242777806035882064) - [Điều khoản dịch vụ](https://discord.com/channels/1242775514951847936/1242777735625969694)",
            color=discord.Color.green()
        )
        await interaction.response.edit_message(content="Bạn đã chấp nhận quy tắc của bot.",embed=embed,view=self)

async def check_terms(ctx):
    data = load_agreementsrule()
    user_id = str(ctx.author.id)

    if user_id not in data['user'] or data['user'][user_id] == False:
        embed = discord.Embed(
            title="Không tuân thủ các quy định này sẽ dẫn đến bị cấm hoặc reset tài khoản",
            description="• Bất kỳ hành động nào được thực hiện để giành lợi thế không công bằng so với những người dùng khác đều vi phạm rõ ràng các quy định. Điều này bao gồm nhưng không giới hạn ở: \n └> Sử dụng macro/script cho bất kỳ lệnh nào \n └> Sử dụng nhiều tài khoản vì bất kỳ lý do gì \n \n • **Không sử dụng** bất kỳ lỗi nào của bot. \n \n • Nếu bạn có bất kỳ câu hỏi nào, hãy hỏi chúng tôi trong [server support](https://discord.gg/QxqkBWf5vr) \n \n [Chính sách bảo mật](https://discord.com/channels/1242775514951847936/1242777806035882064) - [Điều khoản dịch vụ](https://discord.com/channels/1242775514951847936/1242777735625969694)",
            color=discord.Color.blue()
        )
        view = AcceptTermsView(ctx)
        await ctx.send(embed=embed, view=view)
        return False
    return True

@bot.before_invoke
async def before_command(ctx):
    if not await check_terms(ctx):
        raise commands.CommandInvokeError("Hãy chấp nhận luật của bot trước khi sử dụng lệnh.")

@bot.command()
@commands.cooldown(1, 10, commands.BucketType.user)
async def rule(ctx):
    data = load_agreementsrule()
    user_id = str(ctx.author.id)

    if user_id not in data['user'] or data['user'][user_id] == False:
        embed = discord.Embed(
            title="Không tuân thủ các quy định này sẽ dẫn đến bị cấm hoặc reset tài khoản",
            description="• Bất kỳ hành động nào được thực hiện để giành lợi thế không công bằng so với những người dùng khác đều vi phạm rõ ràng các quy định. Điều này bao gồm nhưng không giới hạn ở: \n └> Sử dụng macro/script cho bất kỳ lệnh nào \n └> Sử dụng nhiều tài khoản vì bất kỳ lý do gì \n \n • **Không sử dụng** bất kỳ lỗi nào của bot. \n \n • Nếu bạn có bất kỳ câu hỏi nào, hãy hỏi chúng tôi trong [server support](https://discord.gg/QxqkBWf5vr) \n \n [Chính sách bảo mật](https://discord.com/channels/1242775514951847936/1242777806035882064) - [Điều khoản dịch vụ](https://discord.com/channels/1242775514951847936/1242777735625969694)",
            color=discord.Color.green()
        )
        view= AcceptTermsView(ctx)
        await ctx.send(embed=embed,view=view)
    else:
        embed = discord.Embed(
            title="Không tuân thủ các quy định này sẽ dẫn đến bị cấm hoặc reset tài khoản",
            description="• Bất kỳ hành động nào được thực hiện để giành lợi thế không công bằng so với những người dùng khác đều vi phạm rõ ràng các quy định. Điều này bao gồm nhưng không giới hạn ở: \n └> Sử dụng macro/script cho bất kỳ lệnh nào \n └> Sử dụng nhiều tài khoản vì bất kỳ lý do gì \n \n • **Không sử dụng** bất kỳ lỗi nào của bot. \n \n • Nếu bạn có bất kỳ câu hỏi nào, hãy hỏi chúng tôi trong [server support](https://discord.gg/QxqkBWf5vr) \n \n [Chính sách bảo mật](https://discord.com/channels/1242775514951847936/1242777806035882064) - [Điều khoản dịch vụ](https://discord.com/channels/1242775514951847936/1242777735625969694)",
            color=discord.Color.green()
        )
        await ctx.send(content="Bạn đã chấp nhận quy tắc của bot.",embed=embed)

# Tải dữ liệu từ disable.json
def load_testcmd():
    try:
        with open("test_cmd.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

# Lưu dữ liệu vào disable.json
def save_testcmd(data):
    with open("test_cmd.json", "w") as file:
        json.dump(data, file, indent=4)

disabled_commands = load_testcmd()
tester_ids = load_manage_id()

# Add a command to the test-only list
@bot.command(aliases=["atcmd"])
async def addtestcmd(ctx, command_name: str):
    data = load_manage_id()
    user_id = str(ctx.author.id)
    if user_id not in data["owner_id"] and user_id not in data["admin_id"]:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")
        return

    if command_name.lower() == "all":
        for cmd in bot.commands:
            if cmd.name not in ["atcmd", "rtcmd", "addtestcmd", "removetestcmd"] and cmd.name not in disabled_commands:
                disabled_commands.append(cmd.name)
        save_testcmd(disabled_commands)
        await ctx.send("<:checked:1307210920082145330> | Tất cả các lệnh đã được đặt ở chế độ chỉ dành cho tester.")
        return

    command = bot.get_command(command_name)
    if not command:
        await ctx.send(f"<:cancel:1307210917594796032> | Lệnh `{command_name}` không tồn tại.")
        return

    if command_name not in disabled_commands:
        disabled_commands.append(command_name)
        save_testcmd(disabled_commands)
        await ctx.send(f"<:checked:1307210920082145330> | Đã đặt lệnh `{command_name}` ở chế độ chỉ dành cho tester.")
    else:
        await ctx.send(f"<:cancel:1307210917594796032> | Lệnh `{command_name}` đã được đặt ở chế độ chỉ dành cho tester.")

@bot.command(aliases=["rtcmd"])
async def removetestcmd(ctx, command_name: str):
    data = load_manage_id()
    user_id = str(ctx.author.id)
    if user_id not in data["owner_id"] and user_id not in data["admin_id"]:
        await ctx.send("<:cancel:1307210917594796032> | Bạn không có quyền sử dụng lệnh này.")
        return

    if command_name.lower() == "all":
        disabled_commands.clear()
        save_testcmd(disabled_commands)
        await ctx.send("<:checked:1307210920082145330> | Tất cả các lệnh đã được đặt ở chế độ mọi người.")
        return

    command = bot.get_command(command_name)
    if not command:
        await ctx.send(f"<:cancel:1307210917594796032> | Lệnh `{command_name}` không tồn tại.")
        return

    if command_name in disabled_commands:
        disabled_commands.remove(command_name)
        save_testcmd(disabled_commands)
        await ctx.send(f"<:checked:1307210920082145330> | Lệnh `{command_name}` đã được đặt ở chế độ mọi người.")
    else:
        await ctx.send(f"<:cancel:1307210917594796032> | Lệnh `{command_name}` không ở chế độ chỉ dành cho tester.")

@bot.check
async def globally_block_commands(ctx):
    data = load_manage_id()
    command_name = ctx.command.name
    user_id = str(ctx.author.id)

    # Allow control commands
    if command_name in ["atcmd", "rtcmd", "addtestcmd", "removetestcmd"]:
        return True

    if user_id in data["owner_id"] or user_id in data["admin_id"] or user_id in data["tester_id"]:
        return True

    # Restrict other users from using disabled commands
    if command_name in disabled_commands:
        await ctx.send(f"<:cancel:1307210917594796032> | Lệnh này chỉ dành cho tester.")
        return False

    return True

def load_pet():
    try:
        with open("pet.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {}
    return data

def save_pet(data):
    with open("pet.json", "w") as file:
        json.dump(data, file, indent=2)

@bot.command()
async def petadd(ctx,id):
    data = load_pet()
    user_id = str(ctx.author.id)

    if user_id not in data:
        data[user_id] = {}
    
    embed = discord.Embed()

@bot.command(name="emoji", description="Phóng to Emoji")
async def emoji(ctx, emoji: str):
    if emoji:
        if emoji.startswith("<") and emoji.endswith(">"):
            emoji_parts = emoji.split(":")
            if emoji_parts[0] == "<a" and len(emoji_parts) > 1:
                emoji_id = emoji_parts[-1].strip(">")
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.gif"
            elif emoji_parts[0] == "<" and len(emoji_parts) > 1:
                emoji_id = emoji_parts[-1].strip(">")
                emoji_url = f"https://cdn.discordapp.com/emojis/{emoji_id}.png"
            else:
                emoji_url = None
        else:
            await ctx.send("<:cancel:1307210917594796032> | Không phải là emoji hợp lệ.")
            return
        embed = discord.Embed(description=f"> `{emoji}`", color=0x00ff00)
        if emoji_url:
            embed.set_image(url=emoji_url)
        await ctx.send(embed=embed)
    else:
        await ctx.send("<:cancel:1307210917594796032> | Vui lòng cung cấp emoji.")

@bot.hybrid_command(name="copy", description="Copy Emoji Từ Server Khác")
@commands.has_permissions(manage_emojis_and_stickers=True)
async def copy(ctx, emoji: str):
    if (emoji.startswith('<:') and emoji.endswith('>')) or (emoji.startswith('<a:') and emoji.endswith('>')):   
        is_animated = emoji.startswith('<a:')
        emoji_name = emoji[2:-1].split(':')[0] if not is_animated else emoji[3:-1].split(':')[0]  
        emoji_id = emoji[2:-1].split(':')[1] if not is_animated else emoji[3:-1].split(':')[1]  

        guild = ctx.guild  
        embed = discord.Embed(color=0xFFFF00)  

        try:   
            emoji_url = f'https://cdn.discordapp.com/emojis/{emoji_id}.png' if not is_animated else f'https://cdn.discordapp.com/emojis/{emoji_id}.gif'  
            async with aiohttp.ClientSession() as session:  
                async with session.get(emoji_url) as response:  
                    if response.status == 200:  
                        image_data = await response.read()  
                        new_emoji = await guild.create_custom_emoji(name=emoji_name, image=image_data)    
                        embed.description = f'{new_emoji} Emoji **{emoji_name}** đã được thêm thành công!'  
                    else:  
                        embed.description = 'ID Emoji có vấn đề, vui lòng kiểm tra lại emoji!'  
        except discord.HTTPException as e: 
            embed.color = discord.Color.red()
            error = str(e).split(':', 2)[-1]
            embed.description = f'{error}'
            print(f'{e}')
        except Exception as e:  
            embed.color = discord.Color.red()
            error = str(e).split(':', 2)[-1]
            embed.description = f'{error}'
            print(f'{e}')

        await ctx.send(embed=embed)  
    else:  
        embed = discord.Embed(color=0xFF0000)  
        embed.description = 'Vui lòng cung cấp emoji hợp lệ theo định dạng <:name:id> hoặc <a:name:id>.'  
        await ctx.send(embed=embed)

@bot.command(name="emotes", description="Danh sách tất cả emoji trong server")
async def emotes(ctx):
    static_emojis = [str(emoji) for emoji in ctx.guild.emojis if not emoji.animated]
    animated_emojis = [str(emoji) for emoji in ctx.guild.emojis if emoji.animated]
    total_static = len(static_emojis)
    total_animated = len(animated_emojis)
    total_emojis = total_static + total_animated
    embeds = []
    main_embed = discord.Embed(title="Danh sách emoji", description=f"**Tĩnh: {total_static} \n Động: {total_animated} \n Tổng: {total_emojis}**", color=discord.Color.blue())

    embeds.append(main_embed)    
    def format_emojis(emojis):
        return " ".join(emojis)
    if static_emojis:
        static_embed = discord.Embed(title="Emoji tĩnh", description=format_emojis(static_emojis), color=discord.Color.green())
        embeds.append(static_embed)
    if animated_emojis:
        animated_embed = discord.Embed(title="Emoji động", description=format_emojis(animated_emojis), color=discord.Color.orange())
        embeds.append(animated_embed)
    for embed in embeds:
        await ctx.send(embed=embed)

@bot.command()
async def idemoji(ctx, url: str, emoji_name: str):
    match = re.search(r'/emojis/(\d+)', url)
    if match:
        emoji_id = match.group(1)
        is_animated = "animated=true" in url
        if is_animated:
            emoji_format = f"<a:{emoji_name}:{emoji_id}>"
        else:
            emoji_format = f"<:{emoji_name}:{emoji_id}>"
        embed = discord.Embed(description=f"Emoji: {emoji_format} \n Emoji id: `{emoji_format}`",color=discord.Color.yellow())
        await ctx.send(embed=embed)
    else:
        await ctx.send("<:cancel:1307210917594796032> | Url emoji không hợp lệ.")

nhacdaily = discord.Embed(title="Lời nhắc ấm áp", description="Sử dụng lệnh `daily` để nhận 500 <:mlcoin:1330026986667769867> mỗi ngày hoặc 1.000 <:mlcoin:1330026986667769867> và 10 <:micoin:1307211365890654248> nếu bạn có premium.", color=discord.Color.blue())

@bot.event
async def on_command(ctx):
    if random.random() < 0.2:
        econ = load_econ()
        user_id = str(ctx.author.id)
        today = str(ctx.message.created_at.date())

        if econ[user_id]["last_daily_claim"] != today:
            await ctx.send(embed=nhacdaily,delete_after=15)

def calculate_score(cards):
    values = []
    for card in cards:
        if card[0] in ["j", "q", "k"]:
            values.append(10)
        elif card[0] == "a":
            values.append(11)
        else:
            values.append(int(card[0]))

    score = sum(values)
    while score > 21 and 11 in values:
        values.remove(11)
        values.append(1)
        score = sum(values)
    return score

suits = ["s", "c", "h", "d"]  # s = Bích, c = Tép, h = Cơ, d = Rô
values = ["a", "2", "3", "4", "5", "6", "7", "8", "9", "10", "j", "q", "k"]

def get_card():
    value = random.choice(values)
    suit = random.choice(suits)
    return (value, suit, card_emojis[f"{value}{suit}"])

def format_cards(cards):
    return ' '.join(card[2] for card in cards)

card_emojis = {
    "as": "<:as:1279287117704597525>", "ah": "<:ah:1333977563004928031>", "ad": "<:ad:1333977953364611093>", "ac": "<:ac:1333977183789649972>",
    "2s": "<:2s:1279287186117759097>", "2h": "<:2h:1333977592772165773>", "2d": "<:2d:1333977981781278761>", "2c": "<:2c:1333977210712752148>",
    "3s": "<:3s:1279287247773896725>", "3h": "<:3h:1333977621020676209>", "3d": "<:3d:1334042592819548160>", "3c": "<:3c:1333977243730575512>",
    "4s": "<:4s:1279287404758302804>", "4h": "<:4h:1333977646874230806>", "4d": "<:4d:1333978160877928468>", "4c": "<:4c:1333977267675598888>",
    "5s": "<:5s:1279287447271772222>", "5h": "<:5h:1333977674447589406>", "5d": "<:5d:1333978183132905552>", "5c": "<:5c:1333977295785820225>",
    "6s": "<:6s:1279287497238646846>", "6h": "<:6h:1333977705363931278>", "6d": "<:6d:1333978206197514291>", "6c": "<:6c:1333977325359992863>",
    "7s": "<:7s:1279287535863992391>", "7h": "<:7h:1333977733931204680>", "7d": "<:7d:1333978232025907233>", "7c": "<:7c:1333977349179441155>",
    "8s": "<:8s:1279287578318864510>", "8h": "<:8h:1333977758724001884>", "8d": "<:8d:1333978260622671872>", "8c": "<:8c:1333977378149629974>",
    "9s": "<:9s:1333976944584163329>", "9h": "<:9h:1333977781452800071>", "9d": "<:9d:1333978286287749240>", "9c": "<:9c:1333977402514214984>",
    "10s": "<:10s:1333976982647734294>", "10h": "<:10h:1333977805431640074>", "10d": "<:10d:1333978317224808489>", "10c": "<:10c:1333977428229492787>",
    "js": "<:js:1333977017980420126>", "jh": "<:jh:1333977839070085144>", "jd": "<:jd:1333978794343661600>", "jc": "<:jc:1333977467760803960>",
    "qs": "<:qs:1333977045994176682>", "qh": "<:qh:1333977866370813983>", "qd": "<:qd:1333978813809557516>", "qc": "<:qc:1333977504246923315>",
    "ks": "<:ks:1333977074880483388>", "kh": "<:kh:1333977896192184324>", "kd": "<:kd:1333978838220144737>", "kc": "<:kc:1333977527466856469>"
}

@bot.command(name="blackjack", aliases=['bj'])
async def blackjack(ctx, bet: int = 1):
    econ = load_econ()
    user_id = str(ctx.author.id)

    if user_id not in econ:
        econ[user_id] = {'cash': 0, 'last_daily_claim': datetime.utcnow().isoformat(), 'dailied': False}

    if bet > econ[user_id]['cash']:
        await ctx.send(f"<:cancel:1307210917594796032> | Bạn không có đủ tiền để cược.")
        return

    econ[user_id]["cash"] -= bet
    save_econ(econ)

    player_cards = [get_card(), get_card()]
    dealer_cards = [get_card(), get_card()]

    embed = discord.Embed(title="", description="", color=0x7dbbeb)
    embed.set_author(name=f"{ctx.author.display_name}, bạn cược {bet} để chơi blackjack", icon_url=ctx.author.avatar.url)
    embed.add_field(name=f"Dealer ``[{dealer_cards[0][0]} + ?]``", value=f"{dealer_cards[0][2]} <:cardback:1279287073659949056>", inline=True)
    embed.add_field(name=f"{ctx.author.display_name} ``[{calculate_score([c[0] for c in player_cards])}]``", value=f"{format_cards(player_cards)}", inline=True)
    embed.set_footer(text="🎲 ~ trò chơi đang diễn ra")
    message = await ctx.send(embed=embed)

    await message.add_reaction("👊")
    await message.add_reaction("🛑")

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in ["👊", "🛑"] and reaction.message.id == message.id

    while True:
        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=60.0, check=check)

            if str(reaction.emoji) == "👊":
                player_cards.append(get_card())
                player_score = calculate_score(player_cards)
                await message.remove_reaction("👊", user)

                if player_score > 21:
                    color = 0xFF0000
                    result = f"Bạn đã thua {bet} mlcoin!"
                    break
                
                embed.set_field_at(1, name=f"{ctx.author.display_name} ``[{player_score}]``", value=f"{format_cards(player_cards)}", inline=True)
                await message.edit(embed=embed)

            elif str(reaction.emoji) == "🛑":
                while calculate_score(dealer_cards) < 17:
                    dealer_cards.append(get_card())
                
                player_score = calculate_score(player_cards)
                dealer_score = calculate_score(dealer_cards)
                
                if dealer_score > 21 or player_score > dealer_score:
                    result = f"Bạn đã thắng {bet} mlcoin!"
                    color = 0x00FF00
                    econ[user_id]["cash"] += bet * 2
                elif player_score == dealer_score:
                    result = "Bạn đã hòa!"
                    color = 0x808080
                    econ[user_id]["cash"] += bet
                else:
                    result = f"Bạn đã thua {bet} mlcoin!"
                    color = 0xFF0000
                break

        except asyncio.TimeoutError:
            result = "Trò chơi đã bị hủy do hết thời gian!"
            color = 0xFF0000
            econ[user_id]["cash"] += bet
            break
        except Exception as e:
            print(f"{str(e)}")
            break
    
    embed.set_field_at(0, name=f"Dealer ``[{calculate_score(dealer_cards)}]``", value=f"{format_cards(dealer_cards)}", inline=True)
    embed.set_field_at(1, name=f"{ctx.author.display_name} ``[{calculate_score(player_cards)}]``", value=f"{format_cards(player_cards)}", inline=True)
    embed.set_footer(text=f"🎲 ~ {result}")
    embed.color = color
    await message.edit(embed=embed)
    await message.clear_reactions()
    save_econ(econ)

class ConfirmView(View):
    def __init__(self, channel, author):
        super().__init__(timeout=30)
        self.channel = channel
        self.author = author
        self.result = None

    @discord.ui.button(label="Xác nhận", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không thể sử dụng nút này.", ephemeral=True)
            return

        self.result = True
        self.stop()
        await interaction.response.defer()

    @discord.ui.button(label="Hủy", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.author:
            await interaction.response.send_message("<:cancel:1307210917594796032> | Bạn không thể sử dụng nút này.", ephemeral=True)
            return

        self.result = False
        self.stop()
        await interaction.response.defer()

@bot.command()
@commands.has_permissions(manage_channels=True)
async def nuke(ctx, channel: discord.TextChannel = None):
    if channel is None:
        channel = ctx.channel

    view = ConfirmView(channel, ctx.author)
    embed = discord.Embed(
        title="Bạn chắc chứ?",
        description=f"Điều này sẽ xóa toàn bộ tin nhắn trong kênh {channel.mention}.",
        color=discord.Color.orange()
    )
    await ctx.send(embed=embed, view=view)

    await view.wait()

    if view.result is None:
        return
    elif view.result is False:
        await ctx.send("<:cancel:1307210917594796032> | Lệnh đã bị hủy.")
    else:
        # Lưu thông tin kênh
        guild = ctx.guild
        category = channel.category
        position = channel.position
        overwrites = channel.overwrites

        await channel.delete()
        new_channel = await guild.create_text_channel(
            name=channel.name,
            category=category,
            position=position,
            overwrites=overwrites,
            topic=channel.topic,
            nsfw=channel.is_nsfw()
        )

        # Gửi thông báo trong kênh mới
        await new_channel.send(f"Nuke bởi: **{ctx.author.name}** **-** **{ctx.author.id}** \nServer: **{ctx.guild.name}** **-** **{ctx.guild.id}**`")
REMOVE_BG_API_KEY = 'n5QAgFPeHfdDhk8kFDmy2Yag'

@bot.hybrid_command(name="removebg", description="Xóa nền ảnh từ tệp đính kèm.")
async def removebg(ctx, image: discord.Attachment):
    print(Fore.CYAN + f"Lệnh removebg được gọi bởi: {ctx.author.display_name}")

    if not image:
        await ctx.send(f'**⚠ | {ctx.author.display_name},** Hãy đính kèm một ảnh để xóa nền', delete_after=7)
        print(Fore.YELLOW + "Không có tệp hình ảnh được đính kèm." + Style.RESET_ALL)
        return

    print(Fore.GREEN + "Đã nhận tệp hình ảnh.")
    os.makedirs("images", exist_ok=True)

    original_filename = os.path.join("images", image.filename)
    await image.save(original_filename)

    try:
        with open(original_filename, 'rb') as file:
            print(Fore.YELLOW + "Đang gửi yêu cầu đến remove.bg...")
            response = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files={'image_file': file},
                data={'size': 'auto'},
                headers={'X-Api-Key': REMOVE_BG_API_KEY},
            )

        if response.status_code == requests.codes.ok and response.content:
            output_filename = os.path.join("images", f'no_bg_{image.filename}')
            with open(output_filename, 'wb') as output_file:
                output_file.write(response.content)

            print(f"{Fore.GREEN}[SUCCESS] Hình ảnh đã được xóa thành công.{Style.RESET_ALL}")
            icon1= ctx.guild.icon.url if ctx.guild.icon else "https://media.discordapp.net/attachments/1260159594349596775/1340220385248940032/image.png?ex=67b190ff&is=67b03f7f&hm=bd379b71d321fbb1ddb55b631393df1e50f12504219a9506339a8be9bac4e76f&=&format=webp&quality=lossless&width=421&height=417"
            embed = discord.Embed(title="Xóa Nền", color=0x03fcf8)
            embed.set_image(url=f"attachment://{os.path.basename(output_filename)}")
            embed.set_author(name=f"{ctx.guild.name}", icon_url=icon1)

            await ctx.send(embed=embed, file=discord.File(output_filename))

            os.remove(original_filename)
            os.remove(output_filename)
        else:
            await ctx.send('**🚫 |** Có lỗi xảy ra khi xóa nền, vui lòng thử lại!')
            print(f"{Fore.RED}[ERROR] Lỗi khi gửi đến remove.bg: {response.text}{Style.RESET_ALL}")

    except Exception as e:
        await ctx.send('**🚫 |** Đã xảy ra lỗi khi xử lý ảnh!')
        print(f"{Fore.RED}[ERROR] Lỗi: {str(e)}{Style.RESET_ALL}") 
page = 0  
per_page = 10  
bank_data = {}  
total_pages = 0  


async def load_bank_data():  
    global bank_data  
    try:  
        with open('bank.json', 'r') as f:  
            bank_data = json.load(f)  
    except FileNotFoundError:  
        bank_data = {}  
        print("Không tìm thấy file bank.json")  
    except json.JSONDecodeError:  
        bank_data = {}  
        print("File bank.json không hợp lệ.")  

async def create_bank_page(bot):  
    global page, per_page, bank_data, total_pages  
    start = page * per_page  
    end = start + per_page  
    users = list(bank_data.keys())[start:end]  
    now = datetime.now(timezone.utc) 
    embed = discord.Embed(title="Thông tin Bank", color=discord.Color.green())  
    for user_id in users:  
        data = bank_data[user_id]  
        try:  
            user = await bot.fetch_user(int(user_id))  
        except discord.NotFound:  
            user = None  
        except discord.HTTPException as e:  
            print(f"Lỗi khi fetch user {user_id}: {e}")  
            user = None     
        cash = data.get('cash', 0)  
        embed.add_field(name=user, value=f"ID: {user_id}, Cash: {cash}", inline=False)  
    embed.set_author(name=f"Ngân Hàng Đầu Tư Và Phát Triển Thương Mại Milo Bot", icon_url=bot.user.avatar.url)  
    embed.set_footer(text=f"Trang {page + 1}/{total_pages}")  
    embed.timestamp = now  
    return embed  


@bot.command(name='listbank', description="Xem tất cả người dùng trong bank (admin only)")
@command.owner_id()
async def listbank(ctx):  
    global page, per_page, bank_data, total_pages   

    await load_bank_data()  
    total_pages = (len(bank_data) + per_page - 1) // per_page  
    page = 0  

    if not bank_data:  
        return await ctx.send("Bank hiện tại trống.")  

    embed = await create_bank_page(bot)  

    first_page_button = discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="⏪", disabled=True)  
    prev_page_button = discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="⬅", disabled=True)  
    next_page_button = discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="➡", disabled=total_pages <= 1)  
    last_page_button = discord.ui.Button(style=discord.ButtonStyle.secondary, emoji="⏩", disabled=total_pages <= 1)  

    async def first_page_callback(interaction):  
        global page  
        page = 0  
        first_page_button.disabled = True  
        prev_page_button.disabled = True  
        next_page_button.disabled = False  
        last_page_button.disabled = False  
        embed = await create_bank_page(bot)  
        await interaction.response.edit_message(embed=embed, view=view)  

    async def prev_page_callback(interaction):  
        global page  
        page -= 1  
        if page == 0:  
            first_page_button.disabled = True  
            prev_page_button.disabled = True  
        next_page_button.disabled = False  
        last_page_button.disabled = False  
        embed = await create_bank_page(bot)  
        await interaction.response.edit_message(embed=embed, view=view)  

    async def next_page_callback(interaction):  
        global page  
        page += 1  
        if page == total_pages - 1:  
            next_page_button.disabled = True  
            last_page_button.disabled = True  
        first_page_button.disabled = False  
        prev_page_button.disabled = False  
        embed = await create_bank_page(bot)  
        await interaction.response.edit_message(embed=embed, view=view)  

    async def last_page_callback(interaction):  
        global page  
        page = total_pages - 1  
        first_page_button.disabled = False  
        prev_page_button.disabled = False  
        next_page_button.disabled = True  
        last_page_button.disabled = True  
        embed = await create_bank_page(bot)  
        await interaction.response.edit_message(embed=embed, view=view)  

    first_page_button.callback = first_page_callback  
    prev_page_button.callback = prev_page_callback  
    next_page_button.callback = next_page_callback  
    last_page_button.callback = last_page_callback  

    view = discord.ui.View()  
    view.add_item(first_page_button)  
    view.add_item(prev_page_button)  
    view.add_item(next_page_button)  
    view.add_item(last_page_button)  

    message = await ctx.send(embed=embed, view=view)  

bot.run("YOUR_TOKEN")
