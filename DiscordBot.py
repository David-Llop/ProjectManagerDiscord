# bot.py

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from os.path import exists
import random

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()  # Allow the use of custom intents
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

class Projecte:
    def __init__(self, nom, coordinador):
        self.nom=nom
        self.coordinador=coordinador

    
    def toString(self):
        return "\n**Projecte:\t"+self.nom+"**\nCoordinador:\t"+self.coordinador+"\n"
    
    def save(self):
        return self.nom+','+self.coordinador

projects=[]
if exists("save.csv"):
    with open("save.csv", "r") as f:
        for line in f:
            line=line.split(',')
            if len(line) == 2:
                projects.append(Projecte(line[0], line[1]))


"""
- dm llista projectes

- xat text:
    - general
    - edició
    - càsting
    - traducció
- xat veu:
    - general
"""

def isBot(m):
    return m.author.bot

@bot.command(name='crear-projecte', help="Crea l'estructura de canals i rols per a un nou projecte")
@commands.guild_only()
async def crear_projete(ctx, projecte, trello=None):
    if isBot(ctx.message):
        return
    # creem un color random per l'embeded i els rols
    color_coordinador = random.randint(0,16777215)
    color_projecte = random.randint(0,16777215)
    color_embed = random.randint(0,16777215)
    guild=ctx.guild
    isProjecte=discord.utils.get(guild.categories, name=projecte)
    if not isProjecte:
        if not trello:
            user=ctx.message.author
            await user.send("Per tal de poder crear un projecte, primer n'has de crear el trello.")
            await user.send("Aquí tens l'enllaç del trello de Fandubbers, si us plau, crea-hi un tauler pel projecte")
            link=discord.Embed(title="Trello", type="link", url="https://trello.com/creadorsfandubbers1/boards")
            await user.send(embed=link)
            f=discord.File(open("Captura.PNG", 'rb'), filename="Captura.PNG")
            await user.send("Aquí tens un exemple de com hauria de ser el trello del projecte", file=f)
            f=discord.File(open("Captura2.PNG", 'rb'), filename="Captura2.PNG")
            await user.send("Quan l'hagis creat, copia l'enllaç d'invitació i torna a crear el projecte amb l'enllaç del trello")
            await user.send("Aquí en tens les instruccions", file=f)
            await ctx.send("Quan hagis creat el trello, executa la comanda ``!crear-projecte "+projecte+" [enllaç d'invitació del trello]``")
            return
        new_project = await guild.create_category(projecte)
        print("Categoria creada\n")
        coordinador=ctx.message.author
        # el fem invisible
        new_role = await guild.create_role(name=projecte, color=color_projecte)
        print("Rol "+projecte+" creat\n")
        perms = new_project.overwrites_for(guild.default_role)
        perms.view_channel=False
        await new_project.set_permissions(guild.default_role, overwrite=perms)
        coor_role = await guild.create_role(name='coordinador '+projecte, color=color_coordinador)
        print("Rol coordinador creat\n")
        # afegim permisos rol projecte
        perms = new_project.overwrites_for(new_role)
        perms.view_channel=True
        await new_project.set_permissions(new_role, overwrite=perms)
        # afegim permisos admin
        admin=discord.utils.get(ctx.guild.roles, name='admin')
        perms = new_project.overwrites_for(admin)
        perms.view_channel=True
        await new_project.set_permissions(admin, overwrite=perms)
        # afegim permisos rol coordinador
        perms = new_project.overwrites_for(coor_role)
        perms.view_channel=True
        await new_project.set_permissions(coor_role, overwrite=perms)
        # afegim canals text
        print("Rols i permisos creats\n")
        await new_project.create_text_channel("General")
        await new_project.create_text_channel("Edició")
        await new_project.create_text_channel("Càsting")
        await new_project.create_text_channel("Traducció")
        # afegim canal trello i eliminem permisos escriptura
        trello_C = await new_project.create_text_channel("Enllaços")
        # afegim permisos rol projecte
        perms = trello_C.overwrites_for(new_role)
        perms.send_messages=False
        await trello_C.set_permissions(new_role, overwrite=perms)
        link=discord.Embed(title="Trello", description="Enllaç al trello del projecte",type="link", url=trello, color=color_embed)
        link.set_author(name=coordinador.name, icon_url=coordinador.avatar_url)
        await trello_C.send(embed=link)
        # afegim canals veu
        await new_project.create_voice_channel("General")
        # afegim el coordinador al projecte
        #await coordinador.add_roles(new_role)
        await coordinador.add_roles(coor_role)
        projects.append(Projecte(projecte, coordinador.name))
        with open("save.csv", "w") as csv:
            for p in projects:
                csv.write(p.save())
        await ctx.send ("S'ha creat el projecte "+new_role.mention+", el coordinador en serà "+coordinador.mention)
    else:
        await ctx.send ("Aquest projecte ja existeix")

@bot.command(name='entrar-projecte', help="T'afegeix al projecte que haguis triat")
async def entrar_projecte(ctx, projecte):
    if isBot(ctx.message):
        return
    user=ctx.message.author
    role=discord.utils.get(ctx.guild.roles, name=projecte)
    if len(role.members) == 0:
        for admin in (discord.utils.get(ctx.guild.roles, name='admin')).members:
            dm = await admin.create_dm()
            await dm.send("S'ha afegit algú al projecte "+projecte+ ", que s'havia quedat sense membres")
    await user.add_roles(role)
    await ctx.send ("Enhorabona "+user.mention+" , t'has afegit al projecte "+role.mention)

@bot.command(name='sortir-projecte', help="T'elimina del projecte que haguis triat si ja en formaves part")
async def sortir_projecte(ctx, projecte):
    if isBot(ctx.message):
        return
    user=ctx.message.author
    role=discord.utils.get(ctx.guild.roles, name=projecte)
    if discord.utils.get(user.roles, name='coordinador '+projecte):
        await ctx.send("Ets el coordinador del projecte, mira si algú et pot substituir o tanca el projecte")
        return
    await user.remove_roles(role)
    await ctx.send ("Ens sap greu saber que abandones el projecte "+role.mention +", " +user.mention)
    if len(role.members) == 0:
        admins=discord.utils.get(ctx.guild.roles, name='admin')
        for admin in admins.members:
            await admin.send("El projecte "+projecte+ " s'ha quedat sense membres i només hi queda el coordinador")
        admins=discord.utils.get(ctx.guild.roles, name='coordinador '+projecte)
        for admin in admins.members:
            await admin.send("El projecte "+projecte+ ", del que ets coordinador, s'ha quedat sense membres i només hi quedes tu")

@bot.command(name="projectes", help="Llista els projectes actius")
async def projectes(ctx):
    """
    s=""
    for p in projects:
        s+=p.toString()
    if not s:
        s="Actualment no hi ha cap projecte en marxa, però pots buscar material que t'agradaria que dobléssim"
    await ctx.send(s)
    """
    if isBot(ctx.message):
        return
    await ctx.send(embed=embedProjectes())

@bot.command(name="eliminar-projecte", help="Elimina un projecte de la llista de projectes actius, només disponible pels admins i el coordinador del projecte")
async def eliminar_projecte(ctx, projecte):
    if isBot(ctx.message):
        return
    perm = discord.utils.get(ctx.message.author.roles, name='admin')
    if not perm:
        perm = discord.utils.get(ctx.message.author.roles, name='coordinador '+projecte)
    if not perm:
        await ctx.send("No tens permís per executar aquesta comanda")
    role = discord.utils.get(ctx.guild.roles, name=projecte)
    if role:
        try:
            await role.delete()
            project=discord.utils.get(ctx.guild.categories, name=projecte)
            if project:
                for c in project.channels:
                    await c.delete()
                await project.delete()
                for p in projects:
                    if p.nom == projecte:
                        projects.remove(p)
                        break
                role = discord.utils.get(ctx.guild.roles, name='coordinador '+projecte)
                if role:
                    try:
                        await role.delete()
                    except discord.Forbidden:
                        pass
            with open("save.csv", "w") as csv:
                for p in projects:
                    csv.write(p.save())
            await ctx.send("Projecte "+projecte+" eliminat")
        except discord.Forbidden:
            pass

@bot.event
async def on_command_error(ctx, error):
    if isBot(ctx.message):
        return
    if isinstance(error, commands.errors.CheckFailure):
        await ctx.send("No tens permís per executar aquesta comanda")
    else:
        await ctx.send(error)

def embedProjectes():
    embed=discord.Embed(type='rich', title="Projectes en curs")
    for p in projects:
        embed.add_field(name="Projecte", value="Coordinador", inline=True)
        embed.add_field(name=p.nom, value=p.coordinador, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=False)
    return embed


@bot.event
async def on_member_join(member):
    await member.send(embed=embedProjectes())


bot.run(TOKEN)
