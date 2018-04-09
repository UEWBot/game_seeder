# Diplomacy Tournament Game Seeder
# Copyright (C) 2018 Chris Brand
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Assign players to Diplomacy games in a tournament setting.
"""

import copy, random, itertools
from operator import itemgetter
from enum import Enum, auto

class InvalidPlayer(Exception):
    """A player is invalid in some way (unknown, already present, etc)."""
    pass

class InvalidKey(Exception):
    """A key is invalid in some way (duplicated, duplicates a player, etc)."""
    pass

class InvalidPlayerCount(Exception):
    """An invalid number of players. Diplomacy is a seven-player game."""
    pass

class _AssignmentFailed(Exception):
    """Internal exception used when we end up with an invalid assignment of players to games."""
    pass

class SeedMethod(Enum):
    RANDOM = auto()
    EXHAUSTIVE = auto()

class GameSeeder:
    """
    Assigns Diplomacy players to games to minimise the number of people they play again.
    Two algorithms are supported:
    EXHAUSTIVE
        Try every possible seeding. This will take a long time with many players.
        It may also exhaust memory. Definitely not recommended for 28 players, and may well
        not work with 21.
    RANDOM
        Initially assigns players at random to games, then tries swapping players at random between games.
        The number of candidate seedings and the number of iterations can both be specified.
    In both cases, a fitness measure is used to determine the best candidate seeding.
    """
    def __init__(self, starts=1, iterations=1000, seed_method=SeedMethod.RANDOM):
        """
        seed_method specifies the algorithm used to find a candidate seeding:
            RANDOM - pick sets of players at random
            EXHAUSTIVE - try every possible seeding
        starts is the number of initial seedings to generate. Not used with EXHAUSTIVE seed_method.
        iterations is the number of times to modify each initial seeding in an attempt to improve it. Not used with EXHAUSTIVE seed_method.
        """
        self.games_played = 0
        self.seed_method = seed_method
        if seed_method == SeedMethod.RANDOM:
            self.starts = starts
            self.iterations = iterations
        # Dict, keyed by player, of dicts, keyed by (other) player, of integer counts of shared games
        self.games_played_matrix = {}
        # Dict, keyed by player, of players
        # Used to track players playing in multiple games
        self.duplicates = {}

    def add_player(self, player):
        """
        Add a player to take into account.
        Player is assumed to have played no games.
        Can raise InvalidPlayer if the player is already present.
        """
        if player in self.games_played_matrix:
            raise InvalidPlayer(str(player))
        self.games_played_matrix[player] = {}

    def duplicate_player(self, player, new_key):
        """
        Create a duplicate of a player.
        This is useful if you have a player playing multiple games.
        Can raise InvalidPlayer if player is unknown.
        Can raise InvalidKey if new_key is a player.
        """
        # player must be a known player
        if player not in self.games_played_matrix:
            raise InvalidPlayer(str(player))
        # new_key must not be a known player
        if new_key in self.games_played_matrix:
            raise InvalidKey("%s is a player" % str(new_key))
        # new_key must not already exist
        if new_key in self.duplicates:
            raise InvalidKey("%s already recorded as a duplicate" % str(new_key))
        # Note the duplication
        self.duplicates[new_key] = player

    def _check_for_playing_self(self, game):
        """
        Raises InvalidPlayer if a given player is included in game multiple times,
        including checking for duplicates.
        """
        orig_len = len(game)
        new_game = game.copy()
        self._replace_duplicates_with_mains(new_game)
        if len(new_game) == orig_len:
            return
        # At this point, we know we're going to raise the exception
        removals = game - new_game
        changes = game ^ new_game
        # If game had a player and their duplicate, changes will only have the duplicate
        for p in removals:
            changes.add(self.duplicates[p])
        raise InvalidPlayer("Duplicate players: %s" % ", ".join(changes))

    def _duplicate_in_game(self, game, player):
        """
        Returns True if player, or a duplicate thereof, is in game.
        """
        new_game = game.copy()
        new_game.add(player)
        try:
            self._check_for_playing_self(new_game)
        except InvalidPlayer:
            return True
        return False

    def _replace_duplicates_with_mains(self, game):
        """
        Replace every duplicate player in game with the actual player.
        """
        # Can't change the set we're iterating through
        new_game = game.copy()
        for p in new_game:
            if p in self.duplicates:
                game.remove(p)
                game.add(self.duplicates[p])

    def add_played_game(self, game):
        """
        Add a previously-played game to take into account.
        game is a set of 7 players (player can be any type as long as it's the same in all calls to this object).
        Can raise InvalidPlayer if any player is unknown.
        """
        if len(game) != 7:
            raise InvalidPlayerCount(str(len(game)))
        self._check_for_playing_self(game)
        # First, replace any duplicate players with the primaries
        # because we track "played games" by the primaries only
        self._replace_duplicates_with_mains(game)
        for p in game:
            if p not in self.games_played_matrix:
                raise InvalidPlayer(str(p))
            for q in game:
                if p != q:
                    try:
                        self.games_played_matrix[p][q] += 1
                    except KeyError:
                        if q not in self.games_played_matrix:
                            raise InvalidPlayer(str(q))
                        self.games_played_matrix[p][q] = 1
        self.games_played += 1

    def _fitness_score(self, game):
        """
        Returns a fitness score (0-42) for a game. Lower is better.
        The value returned is twice the number of times each pair of players has played together already.
        game is a set of 7 players (player can be any type as long as it's the same in all calls to this object).
        Can raise InvalidPlayer if any player is unknown or duplicated.
        """
        # Algorithm doesn't work if a player is present more than once
        self._check_for_playing_self(game)
        # Take a copy of game, because we want to replace duplicates
        g = set(game)
        # First, replace any duplicate players with the primaries
        # because we track "games played" for mains only
        self._replace_duplicates_with_mains(g)
        f = 0
        # Sum the number of times each pair of players has played together already
        for p in g:
            if p not in self.games_played_matrix:
                raise InvalidPlayer(str(p))
            for q in g:
                if p != q:
                    try:
                        f += self.games_played_matrix[p][q]
                    except KeyError:
                        # These players have not played each other
                        pass
        return f

    def _assign_players_to_games_randomly(self, players):
        """
        Assign all the players provided to games completely at random, with no weighting.
        Returns a list of sets of 7 players.
        len(players) must be a multiple of 7.
        Raises _AssignmentFailed if the algorithm messes up.
        """
        res = []
        discards = set()
        game = set()
        while len(players) > 0:
            # Pick a random player to add to the current game
            p = random.choice(list(players))
            players.remove(p)
            if self._duplicate_in_game(game, p):
                # This player is no good
                discards.add(p)
                continue
            game.add(p)
            if len(game) == 7:
                # Done with this game. Start a new one
                res.append(game)
                game = set()
                # Move discards back into the main list
                players |= discards
                discards = set()
        # We may end up with a duplicate pairing in the last 7 players
        if len(discards) != 0:
            raise _AssignmentFailed
        return res

    def _set_fitness(self, games):
        """
        Calculate a total fitness score for this list of games.
        Range is 0-(42 * len(games)). Lower is better.
        Can raise InvalidPlayer if any player is unknown or duplicated.
        """
        fitness = 0
        for g in games:
            fitness += self._fitness_score(g)
        return fitness

    def _improve_fitness(self, games):
        """
        Try swapping random players between games to see if we can improve the overall fitness score.
        Returns the best set of games it finds and the fitness score for that set.
        """
        best_set = copy.deepcopy(games)
        best_fitness = self._set_fitness(games)
        # The more iterations, the better the result, but the longer it takes
        for t in range(self.iterations):
           # Try swapping a random player between two random games
           g1 = random.choice(games)
           g2 = random.choice(games)
           p1 = g1.pop()
           p2 = g2.pop()
           g1.add(p2)
           g2.add(p1)
           try:
               fitness = self._set_fitness(games)
           except InvalidPlayer:
               # We happened to swap in a duplicate
               # Swap them back
               g1.remove(p2)
               g2.remove(p1)
               g1.add(p1)
               g2.add(p2)
           else:
               if fitness < best_fitness:
                   #print("Improving fitness from %d to %d" % (best_fitness, fitness))
                   #print(games)
                   best_fitness = fitness
                   best_set = copy.deepcopy(games)
        return best_set, best_fitness

    def _assign_players_wrapper(self, players):
        """
        Wrapper that just keeps calling __assign_players_to_game() until it succeeds.
        """
        while True:
            # _assign_players_to_game() will empty the set of players we pass it
            p = players.copy()
            try:
                res = self._assign_players_to_games_randomly(p)
                break
            except _AssignmentFailed:
                pass
        return res

    def _all_possible_seedings(self, players):
        """
        Returns a list of all possible seedings (each being a list of sets of 7 players).
        This will include seedings with players playing their duplicates.
        It will also include seedings with the same games in different orders.
        Note that this will take a long time for large numbers of players.
        """
        if len(players) % 7 != 0:
            raise InvalidPlayerCount("%d is not an exact multiple of 7" % len(players))
        if len(players) == 7:
            # With 7 players, there is exactly one possible game,
            # and therefore exactly one possible seeding
            return [[players]]
        res = []
        # Go through all possible combinations for the first game:
        for t in itertools.combinations(list(players), 7):
            game = set(t)
            # Make a copy of players, and remove the players in game
            p2 = players.copy()
            for p in game:
                p2.remove(p)
            # Now we can create each possible set that includes this game
            for s in self._all_possible_seedings(p2):
                s.append(game)
                res.append(s)
        return res

    def _player_pool(self, omitting_players):
        """
        Returns a set of players containing every known player and every duplicate,
        but excluding any players in omitting_players.
        """
        # Come up with a list of players to draw from
        players = set(self.games_played_matrix.keys())
        # Add in any duplicate players
        players |= set(self.duplicates.keys())
        # And omit any who aren't playing this round
        for p in omitting_players:
            if p not in players:
                raise InvalidPlayer(str(p))
            players.remove(p)
        return players

    def _seed_games(self, omitting_players):
        """
        Returns a list of games, where each game is a set of 7 players, and the fitness score for the set.
        omitting_players is a set of previously-added players not to assign to games.
        Can raise InvalidPlayer if any player in omitting_players is unknown.
        Can raise InvalidPlayerCount if the resulting number of players isn't an exact multiple of 7.
        """
        players = self._player_pool(omitting_players)
        # Check that we have a multiple of seven players
        if len(players) % 7 != 0:
            raise InvalidPlayerCount("%d total plus %d duplicated minus %d omitted" % (len(self.games_played_matrix), len(self.duplicates), len(omitting_players)))
        res = self._assign_players_wrapper(players)
        # There's no point iterating if all solutions have a fitness of zero
        if self.games_played == 0:
            fitness = 0
        else:
            res, fitness = self._improve_fitness(res)
        # Return the resulting list of games
        return res, fitness

    def seed_games(self, omitting_players=set()):
        """
        Returns a list of games, where each game is a set of 7 players.
        omitting_players is an optional set of previously-added players not to assign to games.
        Internally, this will generate the number of sets specified when the class was instantiated,
        and return the best one.
        Can raise InvalidPlayer if any player in omitting_players is unknown.
        Can raise InvalidPlayerCount if the resulting number of players isn't an exact multiple of 7.
        """
        # Generate the specified number of seedings
        # Use the random method if no games have been played yet, because any seeding is fine
        if (self.games_played == 0) or (self.seed_method == SeedMethod.RANDOM):
            seedings = []
            # No point generating multiples if they're all equally good
            starts = 1
            if self.games_played > 0:
                starts = self.starts
            for i in range(starts):
                # This gives us a list of 2-tuples with (seeding, fitness)
                seedings.append(self._seed_games(omitting_players))
        elif self.seed_method == SeedMethod.EXHAUSTIVE:
            players = self._player_pool(omitting_players)
            seedings = []
            for s in self._all_possible_seedings(players):
                try:
                    fitness = self._set_fitness(s)
                except InvalidPlayer:
                    continue
                seedings.append((s, fitness))
        # Sort them by fitness
        seedings.sort(key=itemgetter(1))
        if self.seed_method == SeedMethod.RANDOM:
            bg_str = "With starts=%d and iterations=%d" % (self.starts, self.iterations)
        else:
            bg_str = "With Exhaustive seeding"
        print("%s, best fitness score is %d in %d seedings" % (bg_str, seedings[0][1], len(seedings)))
        # Return the best (we don't care if multiple seedings are equally good)
        return seedings[0][0]

