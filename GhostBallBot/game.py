#!/usr/bin/env python3
# Copyright 2022 - c0de <c0de@c0de.dev>
# Licensed under the MIT License (https://opensource.org/licenses/MIT)

import uuid

from .database.models import database, GameModel, GuessModel

class Game:
    """
        The game state class

        This represents a game that exists in a channel
    """

    def __init__(self):
        # Only one game should run at at time
        self.is_running = False

        self.commands = {
            'ghostball': self.start,
            'resolve': self.stop,
            'guess': self.guess,
            'points': self.points,
            'help': self.help,
        }

        self.game = None

        # Discord message
        self.message = None

        # Discord client instance
        self.discord = None

    async def start(self):
        if self.is_running:
            return await self.message.channel.send("A game is already running")
        
        database.connect()
        self.is_running = True

        # game.pitch_value is unknown at the start of the game
        self.game = GameModel.create(
            game_id = uuid.uuid4(),
            server_id = self.message.guild.id
        )

        database.close()

        await self.message.send("@flappy ball, pitch is in! Send me your guesses with !guess <number>")

    def __stopArgs__(self):
        pieces = self.message.content.split()

        if len(pieces) == 2:
            return pieces[1], False, None, None
        elif len(pieces) == 4:
            return pieces[1], True, pieces[2], pieces[3]

        return None, False, None, None

    async def stop(self):
        if not self.is_running:
            return await self.message.channel.send("There is no game running to resolve")

        # Determine arguments
        pitch_value, has_batter, batter_id, batter_guess = self.__stopArgs__()
        if not pitch_value:
            return await self.message.channel.send(f"Invalid command <@{ str(self.message.author.id) }>!")

        database.connect()

        if has_batter:
            player_id = batter_id[3:]
            GuessModel.create(
                game_id = self.game.game_id,
                player_id = player_id,
                player_name = self.discord.get_user(int(player_id).name),
                guess = int(batter_guess)
            )

        # Save the pitch value
        self.game.update({'pitch_value': pitch_value})

        # TODO: Determine differences

        # stop and discard game
        self.is_running = False
        self.game = None
        database.close()

    async def guess(self):
        database.connect()

        database.close()

    async def points(self):
        database.connect()

        database.close()

    async def help(self):
        # TODO: Add help message
        help_message = "help"

        recipient = await self.discord.fetch_user(self.message.author.id)
        await recipient.send(help_message)