import discord
import json
import sys

from kbhit import KBHit

kb = KBHit()


class TermCord(discord.Client):
    def __init__(self):
        super().__init__()
        self.messages = Queue()
        self.current_channel = None
        with open('config.json') as f:
            conf = json.load(f)
        self.token = conf['token']
        self.pause_input = False

    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.token, bot=False, reconnect=True))
        finally:
            self.loop.close()

    async def initialize_chat(self, channel):
        messages = await channel.history(limit=20).flatten()
        list(map(print, reversed([f"{message.author.display_name}#{message.author.discriminator}: {message.content}"
                        for message in messages])))

    async def menu(self):
        self.current_channel = None
        print("1. Guilds (Servers)\n2. Recent DM Conversations (Groups included)\n3. Start a new DM conversation")
        choice = input()
        #print("choice", choice)
        if choice == "1":
            print('\n'.join([f"{num}. {name}" for num, name in enumerate([g.name for g in self.guilds], 1)]))
            server_choice = input()
            if server_choice.isdigit():
                guild = self.guilds[int(server_choice)-1]
            else:
                self.pause_input = False
                return
            print('\n'.join([f"{num}. {name}" for num, name in enumerate([c.name for c in guild.channels if
                                                                          isinstance(c, discord.TextChannel)], 1)]))
            channel_choice = input()
            if channel_choice.isdigit():
                channel = [x for x in guild.channels if isinstance(x, discord.TextChannel)][int(channel_choice)-1]
            else:
                self.pause_input = False
                return
            await self.initialize_chat(channel)
            self.current_channel = channel
            self.pause_input = False

    def handle_message(self, message):
        if message == ">menu":
            self.pause_input = True
            self.loop.create_task(self.menu())
        elif self.current_channel:
            self.loop.create_task(self.current_channel.send(message))

    def input_loop(self):
        message = []
        sys.stdout.write("inside inputloop")
        sys.stdout.flush()
        while 1:
            while not self.pause_input:
                if kb.kbhit():
                    ch = kb.getch()
                    #print(int(ord(ch)))
                    if ch not in ["\n", ""]:
                        message.append(ch)
                    elif ch == "":
                        message.remove(message[-1])
                    else:
                        self.handle_message(''.join(message))
                        message.clear()

    async def on_ready(self):
        sys.stdout.write("Logged in")
        await self.loop.run_in_executor(None, self.input_loop)

    async def on_message(self, message):
        if message.channel == self.current_channel:
            print(f"{message.author.display_name}#{message.author.discriminator}: {message.content}")