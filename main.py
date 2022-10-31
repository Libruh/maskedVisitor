from cmath import log
from io import BytesIO
from optparse import Option
import random
from webbrowser import get
from discord.ext import commands
import discord
import mysql.connector
from lackeyCostumes import *
from config import *
from pprint import pprint
import collections

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents, debug_guilds=[481904955016478743])
knownUsers = {}

class mySqlConnection:

    def __init__(self):
        self.connection = None
        self.init_db()

    def init_db(self):
        self.connection = mysql.connector.connect(user=mysqlUser, password=mysqlPass, host=mysqlHost, database=mysqlDB)
        return 

    def get_cursor(self):
        try:
            self.connection.ping(reconnect=True, attempts=3, delay=5)
        except mysql.connector.Error as err:
            self.init_db()
        return self.connection.cursor(buffered=True)

    def commit(self):
        self.connection.commit()

hwDatabase = mySqlConnection()

closetDict = getClosetDict()

def updateKnownUsers():
    query = (f"SELECT userId, teamId FROM {mysqlTable}")

    cursor = hwDatabase.get_cursor()
    cursor.execute(query)
    hwDatabase.commit()

    for (userId, team) in cursor:
        knownUsers[userId] = team

def addUser(userId, teamId):
    query = (f"INSERT INTO {mysqlTable} (userId, teamId, points, abilityPoints) VALUES ({userId}, {teamId}, 0, 0)")
    
    cursor = hwDatabase.get_cursor()
    cursor.execute(query)
    hwDatabase.commit()

    knownUsers[str(userId)] = str(teamId)

def updateUserTeam(userId, teamId):
    query = (f"UPDATE {mysqlTable} SET teamId = {teamId} WHERE userId = {userId}")

    cursor = hwDatabase.get_cursor()
    cursor.execute(query)
    hwDatabase.commit()

    knownUsers[str(userId)] = str(teamId)

def editCandies(userId, num, rainbow=False, ghost=False):
    query = (f"UPDATE {mysqlTable} SET points = points + {num} WHERE userId = {userId}")
    if rainbow:
        query = (f"UPDATE {mysqlTable} SET abilityPoints = abilityPoints + {num} WHERE userId = {userId}")
    if ghost:
        query = (f"UPDATE {mysqlTable} SET ghostPoints = ghostPoints + {num} WHERE userId = {userId}")

    cursor = hwDatabase.get_cursor()
    cursor.execute(query)
    hwDatabase.commit()

def getBag(userId):
    query = (f"SELECT points, abilityPoints, ghostPoints FROM {mysqlTable} WHERE userId = {userId}")
    
    cursor = hwDatabase.get_cursor()
    cursor.execute(query)

    result = cursor.fetchone()
    if result == None:
        result = (0,0)

    return result

def getTeamLeaderboard():
    query=f"(SELECT teamId, SUM(points)+SUM(ghostPoints) FROM halloweenEvent WHERE teamId = '{list(teams.keys())[0]}') UNION (SELECT teamId, SUM(points)+SUM(ghostPoints) FROM halloweenEvent WHERE teamId = '{list(teams.keys())[1]}');"
    
    cursor = hwDatabase.get_cursor()
    cursor.execute(query)

    teamLeaderboard = []

    for (teamId, points) in cursor:
        if len(teamLeaderboard) == 0:
            teamLeaderboard.append((str(teamId), str(points)))
        elif points > int(teamLeaderboard[0][1]):
            teamLeaderboard.insert(0, (str(teamId), str(points)))
        else:
            teamLeaderboard.append((str(teamId), str(points)))

    return teamLeaderboard

def getTeamRole(user):
    teamRole = None

    for role in user.roles:
        if str(role.id) in teams.keys():
            teamRole = role
            break

    if teamRole != None:
        if str(user.id) in knownUsers.keys():
            if str(teamRole.id) != knownUsers[str(user.id)]:
                updateUserTeam(user.id, teamRole.id)
                print(f"Corrected team record for {user.display_name}")
        else:
            addUser(user.id, teamRole.id)
            print(f"Created team record for {user.display_name}")

    return teamRole

def noTeamWarning():
    return "You must pick a team to participate"

class maskSelectView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji=teamEmoji['treat'])
    async def treat_callback(self, button, interaction):
        teamRole = getTeamRole(interaction.user)

        if str(interaction.user.id) in knownUsers.keys() and teamRole != None:
            embed = discord.Embed(title='You try to take off your mask', description="You feel for seams at the edge of your face but find there's nothing there. Guess that's not coming off! Sure hope this mask suits you and doesn't alter your life in any conceivable way!", color=spookyGreen)

            print(f"{interaction.user.display_name} tried to take off their mask!")

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title='You pick up the orange mask', description="The mask floats into your outstretched hand. Intrigued, you put it on. It feels as comfortable as a second skin. Are you even wearing a mask? You can't tell anymore. \n\nYou feel a warmth wash over you and the smell of candy under your nose.", color=spookyGreen)
        embed.set_thumbnail(url="https://i.imgur.com/l9TOn97.png")

        guildRoles = await interaction.message.guild.fetch_roles()

        for roleId in teams:
            if teams[roleId] == "treat":
                break

        for role in guildRoles:
            if str(role.id) == roleId:
                await interaction.user.add_roles(role)
                break

        print(f"{interaction.user.display_name} picked up a Treat mask!")

        if str(interaction.user.id) not in knownUsers.keys():
            addUser(interaction.user.id, roleId)
        else:
            updateUserTeam(interaction.user.id, roleId)
            print(f"Changed team record for {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @discord.ui.button(style=discord.ButtonStyle.secondary, emoji=teamEmoji['trick'])
    async def trick_callback(self, button, interaction):
        teamRole = getTeamRole(interaction.user)

        if str(interaction.user.id) in knownUsers.keys() and teamRole != None:
            embed = discord.Embed(title='You try to take off your mask', description="You feel for seams at the edge of your face but find there's nothing there. Guess that's not coming off! Sure hope this mask suits you and doesn't alter your life in any conceivable way!", color=spookyGreen)

            print(f"{interaction.user.display_name} tried to take off their mask!")

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(title='You pick up the purple mask', description="The mask floats into your outstretched hand. Intrigued, you put it on. It feels as comfortable as a second skin. Are you even wearing a mask? You can't tell anymore. \n\nYou feel an impish urge crawl into your fingertips.", color=spookyGreen)
        embed.set_thumbnail(url="https://i.imgur.com/YNo00so.png")

        guildRoles = await interaction.message.guild.fetch_roles()

        for roleId in teams:
            if teams[roleId] == "trick":
                break

        for role in guildRoles:
            if str(role.id) == roleId:
                await interaction.user.add_roles(role)
                break

        print(f"{interaction.user.display_name} picked up a Trick mask!")
        if str(interaction.user.id) not in knownUsers.keys():
            addUser(interaction.user.id, roleId)
        else:
            updateUserTeam(interaction.user.id, roleId)
            print(f"Changed team record for {interaction.user.display_name}")

        await interaction.response.send_message(embed=embed, ephemeral=True) # Send a message when the button is clicked

    @bot.event
    async def on_application_command_error(ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.respond(error, ephemeral=True)
        else:
            raise error

class continueSelectView(discord.ui.View):
    @discord.ui.button(style=discord.ButtonStyle.secondary, label="> Listen to the voice...")
    async def continue_callback(self, button, interaction):
        teamRole = getTeamRole(interaction.user)
    
        for role in interaction.user.roles:
            if str(role.id) == "1025171994112696441":
                slimeGreen = 0xbbff00

                embed = discord.Embed(description="The time for you to wear this mask has come to an end.\n Don another mask and lead your team to victory.", color=slimeGreen)
                embed.set_author(name="Your mask melts away", icon_url="https://i.imgur.com/zaKinxK.png")

                await interaction.user.remove_roles(role)

                await interaction.response.send_message(embed=embed, ephemeral=True)
                return

        if teamRole == None:
            await interaction.response.send_message("Wait a second... you never put on a mask in the first place!", ephemeral=True)
            return

        embed = None

        if teams[str(teamRole.id)] == "treat":
            embed = discord.Embed(description=treatContinue, color=teamRole.color)
            embed.set_author(name="Your mask calls out to you...", icon_url="https://i.imgur.com/l9TOn97.png")

        elif teams[str(teamRole.id)] == "trick":
            embed = discord.Embed(description=trickContinue, color=teamRole.color)
            embed.set_author(name="Your mask calls out to you...", icon_url="https://i.imgur.com/YNo00so.png")

        await interaction.response.send_message(embed=embed, ephemeral=True)

@bot.event
async def on_ready():
    updateKnownUsers()
    print(f'We have logged in as {bot.user}')

    guild = await bot.fetch_guild(curGuild)
    channel = await guild.fetch_channel(alleyChannel)
    testChannelRef = await guild.fetch_channel(testChannel)
    messageView = maskSelectView(timeout=None)
    continueView = continueSelectView(timeout=None)
    teamMsg = None
    continueMsg = None

    if teamSelectMessage == None:
        embed = embed=discord.Embed(color=spookyGreen)
        embed.set_image(url="https://i.imgur.com/X0TUMtO.gif")
        teamMsg = await channel.send(embed=embed)
    else:
        teamMsg = await channel.fetch_message(teamSelectMessage)

    if continueStoryMessage == None:
        embed = embed=discord.Embed(title="Your mask calls out to you...", description="You recall the feeling you got when you put it on for the first time.", color=spookyGreen)
        continueMsg = await channel.send(embed=embed)
    else:
        continueMsg = await channel.fetch_message(continueStoryMessage)

    # Generate/Update Store

    storeEmbed = embed=discord.Embed(title="Masked Visitor's Cart", description="An assortment of wares sit in front of Lack- er, *the Masked Visitor* - beaming with pride. They beckon to you to take a look and spend some of that hard earned candy… It is burning a hole through your pocket after all!\n\n Use `/buy` to purchase items from the shop", color=spookyGreen)
    storeEmbed = embed=discord.Embed(title="Mysterious Cart", description="You notice out of the corner of your eye what looks like the Masked Visitor lugging a great wheeled cart into the mouth of the alley. Clunk, clunk, creeeeak... \n\n You turn to slink away before they notice you, it would probably be best not to let them see you snooping around. You catch a glimpse of what looks like a stock list with prices beside before running back to the main street, better get saving for tomorrow!", color=spookyGreen)

    listingDict = {}
    for key in closetDict:
        item = closetDict[key]
    
        if item["type"] not in listingDict.keys():
            listingDict[item["type"]] = {}

        listingDict[item["type"]][item["name"]] = item

    sorted_listingDict = {}
    for key in listingDict.keys():
        sorted_listingDict[key] = {}
        tempDict = listingDict[key]
        for k, v in sorted(tempDict.items(), key=lambda e: e[1]["price"]):
            sorted_listingDict[key][k] = v

    for itemType in sorted_listingDict:
        fieldString = ""
        for itemName in sorted_listingDict[itemType]:
            item = sorted_listingDict[itemType][itemName]

            fieldString += f"{item['emoji']} {item['name']} - {item['price']} candies\n"
        
        embed.add_field(name=itemType, value=fieldString, inline=False)

    fieldString = ""
    for saleKey in saleFiles.keys():
        saleItem = saleFiles[saleKey]
        fieldString += f"{saleItem['emoji']} {saleItem['name']} - {saleItem['price']} candies\n"
    embed.add_field(name="Other", value=fieldString, inline=False)

    if storeMessage == None:
        await channel.send("<@&1023772368742645792> <@&1023772280595153018>", embed=embed)
    else:
        storeMsg = await channel.fetch_message(storeMessage)
        await storeMsg.edit(embed=storeEmbed)

    await teamMsg.edit(view=messageView)
    await continueMsg.edit(view=continueView)
    print("Interactions updated!")

@bot.event
async def on_message(message):

    if channelWhitelist != []:
        if str(message.channel.id) not in channelWhitelist:
            return

    if message.author == bot.user:
        return

    if random.random() < candyChance:

        numCandies = random.choices(dropPool, dropWeights, k=1)
        candiesToDrop = random.sample(candyDraws, numCandies[0])

        for candy in candiesToDrop:
            await message.add_reaction(candy)

        if random.random() < rainbowChance:
            await message.add_reaction(rainbowCandy)
        

@bot.event
async def on_reaction_add(reaction, user):

    if user == bot.user:
        return

    teamRole = getTeamRole(user)

    if teamRole == None:
        return

    if str(reaction.emoji) in candyDraws:
        # print(str(user)+" +1")
        await reaction.message.clear_reaction(reaction.emoji)
        editCandies(user.id, 3)

    elif str(reaction.emoji) == rainbowCandy:
        print(str(user)+" +1 RAINBOW")
        await reaction.message.clear_reaction(reaction.emoji)
        editCandies(user.id, 1, rainbow=True)

@bot.command(description="See what team has the most candy") 
async def scareboard(ctx):
    teamLeaderboard = getTeamLeaderboard()

    guild = await bot.fetch_guild(curGuild)
    roles = await guild.fetch_roles()

    winningTeam = None
    losingTeam = None

    for role in roles:
        if str(role.id) == teamLeaderboard[0][0]:
            winningTeam = role
        elif str(role.id) == teamLeaderboard[1][0]:
            losingTeam = role
        if winningTeam != None and losingTeam != None:
            break

    embed=discord.Embed(title="Team Scareboard", description="The current amount of candy in each team's pumpkin", color=winningTeam.color)

    if teams[str(winningTeam.id)] == "trick":
        embed.set_thumbnail(url="https://i.imgur.com/YNo00so.png")
        embed.set_footer(text="The night takes on a deep purple hue")
    elif teams[str(winningTeam.id)] == "treat":
        embed.set_thumbnail(url="https://i.imgur.com/l9TOn97.png")
        embed.set_footer(text="The cloudy sky shines a deep, comforting orange")

    embed.add_field(name=winningTeam.name, value=f"{teamLeaderboard[0][1]} Candies", inline=False)
    embed.add_field(name=losingTeam.name, value=f"{teamLeaderboard[1][1]} Candies", inline=False)

    await ctx.respond(embed=embed, ephemeral=True)

@bot.command(description="Look at the contents of your candy bag") 
async def candybag(ctx): 
    userId = str(ctx.author.id)
    userBag = getBag(userId)

    teamRole = getTeamRole(ctx.author)
    if teamRole == None:
        await ctx.respond(noTeamWarning(), ephemeral=True)
        return

    embed=discord.Embed(title="Your Candy Bag", description="Inside your candy bag, you have...", color=teamRole.color)
    if userBag[0] == 0 and userBag[1] == 0 and userBag[2] == 0:
        embed=discord.Embed(title="Your Candy Bag", description="Your candy bag is currently empty! Get some by clicking on the candy as it appears on messages.", color=teamRole.color)
    else:
        if userBag[0] > 0:
            embed.add_field(name=f"{userBag[0]} Normal Candy", value="These candies counts toward your team score!", inline=False)
        if userBag[1] > 0:
            embed.add_field(name=f"{userBag[1]} Rainbow Candy", value=f"A special candy that allows you to use your *team ability* with `/{teams[str(teamRole.id)]}`", inline=False)
        if userBag[2] > 0:
            embed.add_field(name=f"{userBag[2]} Ghost Candy", value=f"These candies count towards your team score, but can't be taken out of your bag.", inline=False)
        if userBag[0] > 0:
            embed.add_field(name=f"1 Egg", value="Small cracks begin to appear on the surface of the egg", inline=False)
    await ctx.respond(embed=embed, ephemeral=True)

@bot.command(description="Play a devious trick on another user")
@commands.cooldown(1, 5, commands.BucketType.user)
async def trick(ctx, target: discord.Option(discord.SlashCommandOptionType.user, description="The user you'd like to trick")):
    teamRole = getTeamRole(ctx.author)
    targetTeamRole = getTeamRole(target)

    if teamRole == None:
        await ctx.respond(noTeamWarning(), ephemeral=True)
        return

    if str(ctx.channel.id) not in commandChannels:
        embed=discord.Embed(title=f"You can't use that command here!", description="Please try again in <#848758281416867850>", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YNo00so.png")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    userBag = getBag(ctx.author.id)
    if userBag[1] < 1:
        embed=discord.Embed(title=f"You rifle through your candy bag", description="But... don't seem to have any rainbow candies!", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if teams[str(teamRole.id)] != "trick":
        embed=discord.Embed(title=f"You try to trick {target.display_name}", description="But... you can't get yourself to be so mean! \nYou place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if str(target.id) == "1023480670393225256":
        embed=discord.Embed(title=f"You try to trick... the Masked Visitor?!?!", description="You put your rainbow candy away, vowing to never try something so foolish again", color=teamRole.color)
        embed.set_thumbnail(url=target.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if targetTeamRole == None:
        embed=discord.Embed(title=f"You try to trick {target.display_name}", description="But... that user isn't wearing a mask! \nYou place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if target.id == ctx.author.id:
        embed=discord.Embed(title=f"You can't play a trick on yourself!", description="That wouldn't make much sense. \nYou place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    # If this point is reached, the ability can be used

    affectedCandies = random.choices(trickPool, trickWeights, k=1)[0]
    targetsCandies = getBag(target.id)[0]

    if str(ctx.author.id) in tagBlacklist:
        affectedCandies=15

    if affectedCandies > targetsCandies:
        affectedCandies = targetsCandies

    if targetsCandies == 0:
        embed=discord.Embed(title=f"You try to trick {target.display_name}", description="But they don't have any candies! \nYou place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    editCandies(target.id, 0-affectedCandies)
    editCandies(ctx.author.id, -1, rainbow=True)
    if stealingEnabled:
        editCandies(ctx.author.id, affectedCandies)

    print(f"{ctx.author.display_name} caused {target.display_name} to lose -{affectedCandies}")
    print(f"{ctx.author.display_name} -1 RAINBOW")

    quip = random.choice(trickQuips).replace("NAME", ctx.author.display_name).replace("TARGET",target.display_name)

    embed=discord.Embed(title=f"{ctx.author.display_name} played a trick on {target.display_name}!", description=f"They lost {affectedCandies} candies! \n{quip}", color=teamRole.color)
    if stealingEnabled:
         embed=discord.Embed(title=f"{ctx.author.display_name} stole candy from {target.display_name}!", description=f"They had {affectedCandies} candies stolen! \n{quip}", color=teamRole.color)

    embed.set_thumbnail(url=target.avatar.url)
    if str(target.id) in tagBlacklist:
        await ctx.respond(embed=embed)
    else:
         await ctx.respond(f"<@{target.id}>", embed=embed)

@bot.command(description="Give a delicious treat to another user")
@commands.cooldown(1, 5, commands.BucketType.user)
async def treat(ctx, target: discord.Option(discord.SlashCommandOptionType.user, description="The user you'd like to treat")):
    teamRole = getTeamRole(ctx.author)
    targetTeamRole = getTeamRole(target)

    if teamRole == None:
        await ctx.respond(noTeamWarning(), ephemeral=True)
        return

    if str(ctx.channel.id) not in commandChannels:
        embed=discord.Embed(title=f"You can't use that command here!", description="Please try again in <#848758281416867850>", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/l9TOn97.png")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    userBag = getBag(ctx.author.id)
    if userBag[1] < 1:
        embed=discord.Embed(title=f"You rifle through your candy bag", description="But... don't seem to have any rainbow candies!", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if teams[str(teamRole.id)] != "treat":
        embed=discord.Embed(title=f"You try to treat {target.display_name}", description="But... the idea of being so nice makes you feel queasy. \nYou place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if str(target.id) == "1023480670393225256":
        embed=discord.Embed(title=f"You try to treat... the Masked Visitor?!?!", description="You get the feeling that they have enough candy already, and place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url=target.avatar.url)
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if targetTeamRole == None:
        embed=discord.Embed(title=f"You try to trick {target.display_name}", description="But... that user isn't wearing a mask! \nYou place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    if target.id == ctx.author.id:
        embed=discord.Embed(title=f"You can't give a treat to yourself!", description="But you appreciate the act of self-care \nYou place your rainbow candy back into your bag.", color=teamRole.color)
        embed.set_thumbnail(url="https://i.imgur.com/YJciMNA.gif")
        await ctx.respond(embed=embed, ephemeral=True)
        return

    # If this point is reached, the ability can be used

    affectedCandies = random.choices(treatPool, treatWeights, k=1)[0]
    if str(ctx.author.id) in tagBlacklist:
        affectedCandies=15

    editCandies(target.id, affectedCandies)
    editCandies(ctx.author.id, -1, rainbow=True)

    print(f"{ctx.author.display_name} gave {target.display_name} +{affectedCandies}")
    print(f"{ctx.author.display_name} -1 RAINBOW")
    
    quip = random.choice(treatQuips).replace("NAME", ctx.author.display_name).replace("TARGET",target.display_name)

    embed=discord.Embed(title=f"{ctx.author.display_name} gave a treat to {target.display_name}!", description=f"They gained {affectedCandies} candies!\n{quip}", color=teamRole.color)
    embed.set_thumbnail(url=target.avatar.url)

    if str(target.id) in tagBlacklist:
        await ctx.respond(embed=embed)
    else:
         await ctx.respond(f"<@{target.id}>", embed=embed)

@bot.command(description="Give candy to a player (only Libra can use this, nice try.)")
async def gift(ctx, target: discord.Option(discord.SlashCommandOptionType.user, description="The user to have candies added"), amount: discord.Option(discord.SlashCommandOptionType.integer , description="The amount of candies to be added")):

    targetTeamRole = getTeamRole(target)

    if str(ctx.author.id) in canGift:
        editCandies(target.id, amount)
        embed=discord.Embed(title=f"You've received a gift!", description=f"You got {amount} candies!", color=targetTeamRole.color)
        if teams[str(targetTeamRole.id)] == "treat":
            embed.set_thumbnail(url="https://i.imgur.com/l9TOn97.png")
        elif teams[str(targetTeamRole.id)] == "trick":
            embed.set_thumbnail(url="https://i.imgur.com/YNo00so.png")
        await ctx.respond(f"<@{target.id}>", embed=embed)
        return

    else:
        embed=discord.Embed(title=f"You can't do that...", description="Nice try, though.", color=targetTeamRole.color)
        print(f"{ctx.author.display_name} tried to use gift")
        await ctx.respond(embed=embed, ephemeral=True)
        return

# ---- Lackey Dress Up stuff ----

class costumeSelect(discord.ui.Select):

    def __init__(self, itemType, user_closet, lackeyParams):
        super().__init__()

        self.itemType = itemType
        self.user_closet = user_closet
        self.lackeyParams = lackeyParams
        self.placeholder = typeConfig[itemType]['placeholder']

        if typeConfig[itemType]['max'] > 1:
            self.max_values=min(len(self.user_closet[itemType]), typeConfig[itemType]['max'])

        for itemName in self.user_closet[itemType]:
            itemData = closetDict[itemName]

            # Not using a variable here doesnt work, no idea why.
            itemLabel = itemData["name"]

            self.add_option(
                value = itemName, 
                label = itemLabel,
                emoji = itemData["emoji"],
            )

        self.callback = self.selectCallback

    async def selectCallback(self, interaction):
        await interaction.response.defer()
        self.lackeyParams[self.itemType] = interaction.data['values']

class costumeView(discord.ui.View):

    def __init__(self, user_closet=None):
        super().__init__(timeout=30)

        self.lackeyParams = {}
        self.user_closet = user_closet

        for index, itemType in enumerate(self.user_closet.keys()):
            if index == 4:
                break

            if len(self.user_closet[itemType]) == 0:
                continue

            selectMenu = costumeSelect(itemType, self.user_closet, self.lackeyParams)
            self.add_item(selectMenu)

    @discord.ui.button(label="Done", style=discord.ButtonStyle.primary, row = 4)
    async def done_callback(self, button, interaction):
        with BytesIO() as image_binary:
            generateLackey(interaction.user.id, self.lackeyParams).save(image_binary, 'PNG')
            image_binary.seek(0)
            self.clear_items()
            await interaction.response.defer()
            await interaction.edit_original_response(content="", file=discord.File(fp=image_binary, filename=f'{interaction.user.id}s_lackey.png'), view=None)

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(content="Your Lackey got impatient, try the command again!", view=None)

# Buy View
class buyView(discord.ui.View):

    def __init__(self, user_bag, user_closet):
        super().__init__(timeout=30)

        self.itemChoice = None
        self.currentCategory = None

        self.categorySelect = discord.ui.Select(
            placeholder="Choose a Category",
            min_values=1,
            max_values=1
        )

        self.buySelects = {}

        listingDict = {}
        for key in closetDict:
            item = closetDict[key]
        
            if item["type"] not in listingDict.keys():
                listingDict[item["type"]] = {}

            listingDict[item["type"]][key] = item

        for itemCategory in listingDict:

            # Called when the category is changed
            async def category_callback(interaction):
                categoryChoice = interaction.data['values'][0]
                
                self.clear_items()
                self.add_item(self.categorySelect)
                if categoryChoice == "other":
                    self.add_item(self.otherSelect)
                else:
                    self.add_item(self.buySelects[categoryChoice])

                for option in self.categorySelect.options:
                    if option.value == interaction.data['values'][0]:
                        option.default = True
                    else:
                        option.default = False

                if categoryChoice == "other":
                    for option in self.otherSelect.options:
                        option.default = False
                else:
                    for option in self.buySelects[interaction.data['values'][0]].options:
                            option.default = False

                await self.message.edit(view=self)
                await interaction.response.defer()

            self.categorySelect.add_option(
                label = itemCategory,
                value = itemCategory
            )
            self.categorySelect.callback = category_callback

            self.buySelects[itemCategory] = discord.ui.Select(
                min_values=1,
                max_values=1
            )

            sorted_listingDict = {}
            for key in listingDict.keys():
                sorted_listingDict[key] = {}
                tempDict = listingDict[key]
                for k, v in sorted(tempDict.items(), key=lambda e: e[1]["price"]):
                    sorted_listingDict[key][k] = v

            for key in sorted_listingDict[itemCategory]:
                item = closetDict[key]

                self.buySelects[itemCategory].add_option(
                    label = item['name'],
                    value = key+"_category:"+itemCategory,
                    emoji = item['emoji'],
                    description = f"{item['price']} candies",
                )

                async def item_callback(interaction):
                    
                    userBag = getBag(interaction.user.id)
                    itemId = interaction.data["values"][0].split("_category:")[0]
                    itemCategory = interaction.data["values"][0].split("_category:")[1]
                    itemData = closetDict[itemId]

                    if userBag[0] < itemData['price']:
                        self.buyButton.label="Can't afford"
                        self.buyButton.disabled=True
                        self.buyButton.style=discord.ButtonStyle.danger
                    else:
                        self.buyButton.label=f"Buy for {itemData['price']} candies"
                        self.buyButton.disabled=False
                        self.buyButton.style=discord.ButtonStyle.primary

                    userCloset = getUserCloset(str(interaction.user.id))
                    for category in userCloset:
                        for itemName in userCloset[category]:
                            if itemName == itemId:
                                self.buyButton.label="Already Owned"
                                self.buyButton.disabled=True
                                self.buyButton.style=discord.ButtonStyle.secondary

                    for option in self.buySelects[itemCategory].options:
                        if option.value == interaction.data["values"][0]:
                            option.default = True
                        else:
                            option.default = False

                    self.buyItem = itemId
                    self.buyData = itemData
                    self.buyType = "normal"

                    self.remove_item(self.buyButton)
                    self.add_item(self.buyButton)
                    await self.message.edit(view=self)
                    await interaction.response.defer()
                    
                self.buySelects[itemCategory].callback = item_callback

        self.categorySelect.add_option(
            label="Other",
            value="other"
        )

        async def other_callback(interaction):
            
            userBag = getBag(interaction.user.id)
            itemId = interaction.data["values"][0]
            itemData = saleFiles[itemId]

            if userBag[0] < itemData['price']:
                self.buyButton.label="Can't afford"
                self.buyButton.disabled=True
                self.buyButton.style=discord.ButtonStyle.danger
            else:
                self.buyButton.label=f"Buy for {itemData['price']} candies"
                self.buyButton.disabled=False
                self.buyButton.style=discord.ButtonStyle.primary

            for option in self.otherSelect.options:
                if option.value == interaction.data["values"][0]:
                    option.default = True
                else:
                    option.default = False

            self.buyItem = itemId
            self.buyData = itemData
            self.buyType = "other"

            self.remove_item(self.buyButton)
            self.add_item(self.buyButton)
            await self.message.edit(view=self)
            await interaction.response.defer()
            
        self.otherSelect = discord.ui.Select(
            min_values=1,
            max_values=1
        )
        self.otherSelect.callback = other_callback

        for key in saleFiles:
            item = saleFiles[key]
            self.otherSelect.add_option(
                label = item['name'],
                value = key,
                emoji = item['emoji'],
                description = f"{item['price']} candies",
            )

        self.add_item(self.categorySelect)

        self.buyButton = discord.ui.Button(
            label="Buy",
            style=discord.ButtonStyle.primary,
            row = 4
        )
        
        async def buy_callback(interaction):
            editCandies(interaction.user.id, 0-self.buyData['price'])

            if self.buyType == "other":
                itemName = self.buyData["name"]

                self.clear_items()

                userBag = getBag(interaction.user.id)

                await interaction.response.defer()
                await interaction.edit_original_response(content="Here is your purchased file. Make sure you save it!", file=discord.File(self.buyData['file']), view=None)
                print(interaction.user.display_name + " bought "+itemName)

            else:
                realCategory = self.buyData["type"].lower()
                if realCategory == "styles":
                    realCategory = "paints"

                addToCloset(str(interaction.user.id), realCategory, self.buyItem)
                self.clear_items()

                itemName = self.buyData["name"]
            
                self.clear_items()

                userBag = getBag(interaction.user.id)
                embed=discord.Embed(title=f"You bought {self.buyData['name']}{self.buyData['emoji']} ", description=f"You now have {userBag[0]} candies", color=spookyGreen)

                await interaction.response.defer()
                await interaction.edit_original_response(content="", embed=embed, view=None)
                print(interaction.user.display_name + " bought "+itemName)

        self.buyButton.callback = buy_callback

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(content="You took too long, and the Masked Visitor has lost interest. Try again.", view=None)

# Costume command
@bot.command(description="???") 
async def costume(ctx):
    if str(ctx.channel.id) != '934987318627041300':
        await ctx.respond("You can't use this yet!", ephemeral=True)
        return

    user_closet = getUserCloset(str(ctx.author.id))

    emptyCloset = {
            'masks': [],
            'accessories': [],
            'backgrounds': [],
            'paints': []
        }
    if user_closet == emptyCloset:
        await ctx.respond(content=f"You have nothing to equip! Visit the shop in <#{alleyChannel}> to buy some!", ephemeral=True)
        return

    userCostumeView = costumeView(user_closet)
    await ctx.respond(content="Pick your Lackey's costume!", view=userCostumeView, ephemeral=True)

# Buy Command
@bot.command(description="???") 
async def buy(ctx):
    if str(ctx.channel.id) != '934987318627041300':
        await ctx.respond("You can't use this yet!", ephemeral=True)
        return

    user_bag = getBag(ctx.author.id)
    user_closet = getUserCloset(str(ctx.author.id))

    userbuyView = buyView(user_bag, user_closet)
    await ctx.respond(content="Select the item you'd like to buy", view=userbuyView, ephemeral=True)


bot.run(passkey)