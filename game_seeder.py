import copy, random
from operator import itemgetter

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

class GameSeeder:
    """
    Assigns Diplomacy players to games to minimise the number of people they play again.
    The algorithms used are very much brute-force. It initially assigns players at random to games,
    then tries swapping players at random between games. A fitness measure is used to determine
    whether the old or new assignment is better.
    """
    def __init__(self, starts=1, iterations=1000):
        """
        starts is the number of initial seedings to generate.
        iterations is the number of times to modify each initial seeding in an attempt to improve it.
        """
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

    def _assign_players_to_games(self, players):
        """
        Assign all the players provided to games.
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
                res = self._assign_players_to_games(p)
                break
            except _AssignmentFailed:
                pass
        return res

    def _seed_games(self, omitting_players):
        """
        Returns a list of games, where each game is a set of 7 players, and the fitness score for the set.
        omitting_players is a set of previously-added players not to assign to games.
        Can raise InvalidPlayer if any player in omitting_players is unknown.
        Can raise InvalidPlayerCount if the resulting number of players isn't an exact multiple of 7.
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
        # Check that we have a multiple of seven players
        if len(players) % 7 != 0:
            raise InvalidPlayerCount("%d total plus %d duplicated minus %d omitted" % (len(self.games_played_matrix), len(self.duplicates), len(omitting_players)))
        res = self._assign_players_wrapper(players)
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
        seedings = []
        for i in range(self.starts):
            # This gives us a list of 2-tuples with (seeding, fitness)
            seedings.append(self._seed_games(omitting_players))
        # Sort them by fitness
        seedings.sort(key=itemgetter(1))
        print("With starts=%d and iterations=%d, best fitness score is %d" % (self.starts, self.iterations, seedings[0][1]))
        # Return the best
        return seedings[0][0]

