#initialized data
#----------------------
import discord
import os
import asyncio
import youtube_dl
prefix = '-'
helpMessage = """
```
{0}add [playlist name] [song name] - Adds a song to the playlist
{0}remove [playlistname] [song name] - Removes a song from the playlist
{0}create [playlist name] - Creates a playlist
{0}delete [playlist name] - Deletes a playlist
{0}play [playlist name] - Plays a playlist
{0}dc - Leaves voice channel
{0}prefix [newPrefix] - Change prefix
```
""".format(prefix)

nizbotDataFolder = "dirlocationhere"

commands = ["help", "create", "add", "delete", "remove", "play", "dc", "skip", "queue", "prefix"]
voice = None
songs = []
channel = None
currentlyPlaying = ""
class Error(Exception):
    pass

#functions
#---------------
def mapSongNames():
    songNames

def validateCommand(message, commandIndex):
    global commands
    global prefix
    commandLength = len(commands[commandIndex]) + len(prefix) + 1 #command + prefix + space
    if(commandLength - 1 >= len(message)):
        raise Error("Invalid command.")
    if(message[commandLength - 1] != ' '):
        raise Error("Invalid command.")

def play_song(song, playlistFolder):
    global voice
    if(voice != None and voice.is_connected()):
        player = discord.FFmpegPCMAudio(song)
        def after_playing(err):
            if(voice != None):
                global songs
                if(len(songs) > 1):
                    songs.pop(0)
                    next_song = songs[0]
                    play_song(next_song, playlistFolder)
                else:
                    #loops
                    songs = []
                    import glob
                    for song in glob.glob(playlistFolder + '/*.mp3'):
                        songs.append(song)
                    play_song(songs[0], playlistFolder)
        if(voice.is_connected()):
            voice.play(player, after = after_playing)
            voice.volume = 100


def fetchSong(song, playlistFolder):
    ydl_opts = {
            'outtmpl': playlistFolder + '/%(id)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'default_search': 'auto',
            'quiet' : True,
        }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(song, download=False)
        if 'entries' in info_dict:
            info_dict = info_dict['entries'][0]
        songId = info_dict['id']
        songFile = playlistFolder + '/' + songId +'.mp3'
        if not os.path.isfile(songFile):
            ydl.download([song])

async def playPlaylist(message, serverId):
    try:
        global nizbotDataFolder
        global prefix
        global voice
        global channel
        channel = message.channel
        
        validateCommand(message.content, 5)

        #validate that playlist name doesnt have any spaces
        if(message.content.count(' ') != 1):
            raise Error("Invalid playlist name.")

        playlistName = message.content.split()[1]

        #validate playlist name (between 1 and 16)
        if(len(playlistName) < 1 or len(playlistName) > 16):
            raise Error("Invalid playlist name. Length must be between 1 and 16.")

        #Check if playlist exists
        serverFolder = "{0}/{1}/{2}".format(nizbotDataFolder, serverId, playlistName)
        playlistFile = "{0}/{1}".format(serverFolder, playlistName) + '.txt'
        if not os.path.exists(playlistFile):
            raise Error("Playlist doesn't exist.")

        #Check if playlist is empty
        if(os.stat(playlistFile).st_size == 0):
            raise Error("Playlist is empty.")

        #connect to voice channel
        if(message.author.voice != None and message.author.voice.channel != None):
            voice = await message.author.voice.channel.connect()
        else:
            raise Error("Must be in a voice channel to play music")
        
        global songs
        import glob
        for song in glob.glob(serverFolder + '/*.mp3'):
            songs.append(song)
        if(voice != None and channel != None):
            play_song(songs[0], serverFolder)
            
        return """ ``` Playing playlist.. ``` """
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)
    

def createPlaylist(message, serverId):
    try:
        global nizbotDataFolder
        global prefix

        validateCommand(message, 1)
        
        #validate playlist name doesnt have any spaces
        if(message.count(' ') != 1):
           raise Error("Invalid playlist name.")

        playlistName = message.split()[1]
        
        #validate playlist name length
        if(len(playlistName) < 1 or len(playlistName) > 16):
            raise Error("Invalid playlist name. Length must be between 1 and 16.")

        #create a folder with the server id and a playlist folder
        serverFolder = "{0}/{1}/{2}".format(nizbotDataFolder, serverId, playlistName)
        if not os.path.exists(serverFolder):
            os.makedirs(serverFolder)
            print("Server folder created:", serverFolder)
            
        #create a playlist file
        playlistFile = "{0}/{1}".format(serverFolder, playlistName) + '.txt'
        if not os.path.exists(playlistFile):
            open(playlistFile, 'w').close()
            print("Playlist file created:", playlistFile)
        else:
            raise Error("Playlist already exists.")
        
        return """ ``` Playlist created.\n Use {0}play {1} to play it.``` """.format(prefix, playlistName)
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)
    
async def addSong(message, serverId, channel):
    try:
        global nizbotDataFolder
        global prefix

        validateCommand(message, 2)

        message = message.split(' ', 1)
        print(message)
        playlistName = message[1].split(' ')[0]
        songName = message[1].split(' ', 1)[1]
        print(playlistName)
        print(songName)
        #validate song name (between 1 and 16)
        if(len(songName) < 1 or len(songName) > 50):
            raise Error("Invalid song name. Length must be between 1 and 50.")

        #Check if playlist exists
        serverFolder = "{0}/{1}/{2}".format(nizbotDataFolder, serverId, playlistName)
        playlistFile = "{0}/{1}".format(serverFolder, playlistName) + '.txt'
        if not os.path.exists(playlistFile):
            raise Error("Playlist doesn't exist.")

        #Check if playlist is empty
        if(os.stat(playlistFile).st_size == 0): #write song name
            playlist = open(playlistFile, 'w')
            playlist.write(songName)
            playlist.close()
        else: #check if song already in playlist and if it isnt append it
            playlist = open(playlistFile, 'r')
            if songName in playlist.read():
                playlist.close()
                raise Error("Song already in playlist.")
            playlist.close()
            
            playlist = open(playlistFile, 'a')
            playlist.write('\n' + songName)
            playlist.close()
        
        #read songs
        with open(playlistFile) as f:
            urls = f.read().splitlines()

        async with channel.typing():
            #download songs to directory
            for song in urls:
                fetchSong(song, serverFolder)
            
        return """ ``` Song added. ``` """
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)


async def dc(message):
    global voice
    global songs
    try:
        if voice and voice.channel:
            await voice.disconnect()
            songs = []
            songNames = dict()
            voice = None
            return """ ``` Disconnected. ``` """
        else:
            return """ ``` Im not even connected ``` """
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)

def deletePlaylist(message, serverId):
    try:
        global nizbotDataFolder
        global prefix

        validateCommand(message, 3)
        
        #validate playlist name doesnt have any spaces
        if(message.count(' ') != 1):
           raise Error("Invalid playlist name.")

        playlistName = message.split()[1]
        
        #validate playlist name length
        if(len(playlistName) < 1 or len(playlistName) > 16):
            raise Error("Invalid playlist name. Length must be between 1 and 16.")

        #Check if playlist exists
        serverFolder = "{0}/{1}/{2}".format(nizbotDataFolder, serverId, playlistName)
        playlistFile = "{0}/{1}".format(serverFolder, playlistName) + '.txt'
            
        #delete playlist
        if os.path.exists(playlistFile):
            import shutil
            shutil.rmtree(serverFolder)
            print("Playlist file deleted:", playlistFile)
            return """ ``` Playlist deleted.``` """
        else:
            return """ ``` Playlist doesn't exist.``` """
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)   

def removeSong():
    try:
        return """ ``` Delete playlist or contact niz for manual deletion.``` """
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)   
    
def mentionProtocol(x):
    try:
        return {
            1: """ ``` message here``` """,
            2: """ ``` message here``` """,
            3: """ ``` message here``` """,
            4: """ ``` message here``` """,
            5: """ ``` message here``` """,
        }[x]
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)

def skipSong():
    try:
        global voice
        global songs
        if(voice.is_connected()):
            voice.stop()
            return """ ``` Song Skipped ``` """
        else:
            raise Error("No song is playing")
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)


def queue():
    global voice
    songDict = {}
    try:
        if(voice == None):
            raise Error("Not connected to a channel")
        if(not voice.is_connected()):
            raise Error("Not connected to a channel")
        if(songNames):
            ydl_opts = {
                'outtmpl': playlistFolder + '/%(id)s.%(ext)s',
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'default_search': 'auto',
                'quiet' : True,
            }
            for song in songs:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(song, download=False)
                    if 'entries' in info_dict:
                        info_dict = info_dict['entries'][0]
                    songId = info_dict['id']
                    songTitle = info_dict['title']
                    songDict[songId] = songTitle
                    for item in songDict.items():
                        print(item)
        else:
            raise Error("Queue is empty")
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)

def skipSong():
    try:
        global voice
        global songs
        if(voice.is_connected()):
            voice.stop()
        return """ ``` Song Skipped ``` """
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)


def changePrefix(message):
    try:
        global prefix
        validateCommand(message, 9)
        if(message.count(' ') != 1):
            raise Error("Invalid prefix")
        newPrefix = message.split(' ')[1]
        if(len(newPrefix) > 1):
            raise Error("Prefix too long")
        prefix = newPrefix
        return """ ``` Prefix changed to {0} ``` """.format(prefix)
    except Exception as error:
        print("error occured:", error)
        return """ ``` {0} ``` """.format(error)


    #send apu pics every now and then
async def sendApu(general):
    import random
    global nizbotDataFolder
    pics = []
    for root, dirs, files in os.walk(nizbotDataFolder + "/APU"):
        for file in files:
            if file.endswith((".jpg", ".png", ".jpeg")):
                pics.append(os.path.join(root, file))
    while True:
        await asyncio.sleep(1800)
        from discord import File
        chosenFile = File(random.choice(pics), spoiler = True)
        await general.send("APU TIME", file = chosenFile)
    
#events
#---------------------
client = discord.Client()
loop = asyncio.get_event_loop()
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="handshake guides at twitch.tv/trainwreckstv"))
    generals = list()
    for guild in client.guilds:
        for channel in guild.text_channels:
            if channel.name == 'neezbot-channel': 
                generals.append(channel)

    for general in generals:
        loop.create_task(await sendApu(general))
    loop.run_forever()
    
@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(prefix + commands[0]): #help command
        await message.channel.send(helpMessage)
        
    if message.content.startswith(prefix + commands[1]):
        await message.channel.send(createPlaylist(message.content, message.guild.id)) #create command

    if message.content.startswith(prefix + commands[3]):
        await message.channel.send(deletePlaylist(message.content, message.guild.id)) #delete command        

    if message.content.startswith(prefix + commands[2]):
        await message.channel.send(await addSong(message.content, message.guild.id, message.channel)) #add command

    if message.content.startswith(prefix + commands[4]):
        await message.channel.send(removeSong()) #remove command

    if message.content.startswith(prefix + commands[7]):
        await message.channel.send(skipSong()) #skip command

    if message.content.startswith(prefix + commands[8]):
        await message.channel.send(queue()) #queue command

    if message.content.startswith(prefix + commands[9]):
        await message.channel.send(changePrefix(message.content)) #prefix command

    if message.content.startswith(prefix + commands[5]):
        await message.channel.send(await playPlaylist(message, message.guild.id)) #play command

    if message.content == (prefix + commands[6]):
        await message.channel.send(await dc(message)) #dc command

    import re
    if (re.search('^(neez)|(niz)', message.content) != None):
        await message.channel.send('You asked for me?') #mention reply

    niz = client.get_user(userid)
    if niz.mentioned_in(message):
        await message.channel.send(mentionProtocol(1)) 

client.run('tokenhere')
