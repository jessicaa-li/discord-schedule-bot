import discord
import os
import schedule
import datetime
from dotenv import load_dotenv
project_folder = os.path.expanduser('./')  # adjust as appropriate
load_dotenv(os.path.join(project_folder, '.env'))

# intents = discord.Intents.default()
# intents.members = True
# client = discord.Client(intents=intents)
client = discord.Client()
meetings = []


async def dm_missing(message):
    author = message.author    
    testing = client.users
    
    if (author.voice is None):
        await message.channel.send('Sorry, you are not currently in a voice channel.')
    else:
        channel = author.voice.channel
        now = datetime.datetime.now()
        current_time = now.strftime('%H:%M')
        current_date = now.strftime('%B %d, %Y')

        for meeting in meetings:
            if meeting.getDate().day == now.day and meeting.getDate().month == now.month and meeting.getDate().year == now.year:
                if (now.minute >= meeting.getTime().minute and now.minute <= meeting.getTime().minute + 5) and meeting.getTime().hour == now.hour :
                    missing = meeting
                    await message.channel.send(meeting.getName())
        for person in missing.getParticipants():
            await message.channel.send(person)
            if person.voice is None or person.voice.channel != channel:
                await person.send('why u no in meeting :( ')

            else:
                await person.send('u in meeting :)')
    
async def parse_meeting_info(parameters):
    meeting_time = None
    meeting_date = None
    participants = []
    desc = ''
    auto_remind = None
    copy_desc = False

    #Loop through the remaining parameters
    for param in parameters:

        #Time parameter HH:MM (24HR)
        if (len(param) == 5 and param[2] == ':'):
            meeting_time = datetime.time(int(param[:2]), int(param[3:]))

        #Date parameter DD/MM/YYYY (if year is omitted, assumed the current)
        if (len(param) == 5 and param[2] == '/'):
            meeting_date = datetime.date(datetime.datetime.now().year, int(param[3:]), int(param[:2]))
        elif (len(param) == 10 and param[2] == '/' and param[5] == '/'):
            meeting_date = datetime.date(int(param[6:]), int(param[3:5]), int(param[:2]))

        #Participants parameter - all the @ users
        if (param[:3] == '<@!'):
            participants.append(await client.guilds[0].fetch_member(int(param[3:-1]))) #Add the user as a 'member' object

        #Desc parameter start - string (in quotes)
        if (param.startswith("'")):
            copy_desc = True
            param = param[1:] #Remove the quotation
            desc = ""
        
        #End of desc
        if (param[-1] == "'"):
            copy_desc = False
            desc += param[:-1] #Remove the quotation

        #Add part of the desc
        if (copy_desc):
            desc += param + ' '

        #Autoremind parameter - TRUE or FALSE
        if (param.lower() == "true"):
            auto_remind = True
        elif (param.lower() == 'false'):
            auto_remind = False
    
    return meeting_time, meeting_date, participants, desc, auto_remind

async def make_meeting(parameters):
    #Name parameter
    name = "Undefined"
    if (len(parameters) >= 1):
        for meet in meetings:
            if (meet.getName() == parameters[0]):
                return "A meeting already uses that name!"
        name = parameters[0]
    else:
        return "No parameters given!"

    meeting_time, meeting_date, participants, desc, auto_remind = await parse_meeting_info(parameters[1:])
    meeting_duration = datetime.timedelta(hours=1)

    if (meeting_time == None):
        meeting_time = datetime.datetime.now().time() #Default time is now
    if (meeting_date == None):
        meeting_date = datetime.date.today() #If the date is omitted, assume today
    if (auto_remind == None):
        auto_remind = False #Default is no auto_remind

    meetings.append(schedule.Meeting(name, meeting_time, meeting_duration, meeting_date, participants, desc, auto_remind))
    
    return None

#Updates the parameters for the given meetings
async def update_meeting(message, parameters):
    found = -1
    for i in range(len(meetings)):
        if (meetings[i].getName() == parameters[0]):
            found = i
    
    if (found == -1):
        await message.channel.send("No meeting of name '{}' found.".format(parameters[0]))
        return False

    meeting_time, meeting_date, participants, desc, auto_remind = await parse_meeting_info(parameters[1:])

    #Set any changed values
    if (meeting_time != None):
        meetings[found].setTime(meeting_time)
    if (meeting_date != None):
        meetings[found].setDate(meeting_date)
    if (participants != []): #Not NONE
        for person in participants:
            if (not(meetings[found].addParticipant(person))):
                try:
                    await message.channel.send("{} has already signed up for {}".format(person, meetings[found].getName()))
                except:
                    print("Error, likelyl no message given (meeting creation issue).")
    if (desc != ''):
        meetings[found].setDesc(desc)
    if (auto_remind != None):
        meetings[found].setAutoRemind(auto_remind)

async def show_meetings(message):
    for meeting in meetings:
        await message.channel.send(embed=meeting.getEmbed())

async def delete_meeting(message):
    for meeting in meetings:
      if (meeting.getName() == message[0]):
        meetings.remove(meeting)

async def my_meetings(message):
    user_meetings = []
    
    for meeting in meetings:
      participants = meeting.getParticipants()
      if message.author in participants:
        user_meetings.append(meeting)

    user = await client.fetch_user(message.author.id)
    await DMChannel.send(user, "Upcoming Meetings:")
    for meeting in user_meetings:
      await DMChannel.send(user, meeting)
        
async def process_command(message):
    parameters = message.content.split(' ')

    if (len(parameters) > 0):
        if (parameters[0] == 'hello'):
            await message.channel.send('Hello!')
        elif (parameters[0] == 'stop'):
            await message.channel.send('Buy-bye!')
            await client.logout()
        elif (parameters[0] == 'meeting'):
            error = await make_meeting(parameters[1:])
            if (error != None):
                await message.channel.send(error)
            else:
                message = await message.channel.send('React with \N{THUMBS UP SIGN} to enrol in {}'.format(parameters[1]))
                await message.add_reaction('\N{THUMBS UP SIGN}')
            meetings[-1].setMessage(message)
        elif (parameters[0] == 'show_meetings'):
            await show_meetings(message)
        elif (parameters[0] == 'edit'):
            await update_meeting(message, parameters[1:])
        elif (parameters[0] == 'missing'):
            await dm_missing(message)
            # await message.channel.send(message.author)
        elif (parameters[0] == 'delete_meeting'):
            await delete_meeting(parameters[1:])
        elif (parameters[0] == 'my_meetings'):
            await my_meetings(message)

@client.event
async def on_reaction_add(reaction, user):
    channel = reaction.message.channel
    if(user != client.user and reaction.emoji == '\N{THUMBS UP SIGN}'):
        for meeting in meetings:
            if (reaction.message == meeting.getMessage()):
                if (meeting.addParticipant(user)):
                    await channel.send("{} has successfully signed up for {}".format(user.name, meeting.name))
                else:
                    await channel.send("{} has already signed up for {}".format(user.name, meeting.name))

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.content.startswith('$'):
        message.content = message.content[1:]
        await process_command(message)
        
client.run(os.getenv('TOKEN'))
