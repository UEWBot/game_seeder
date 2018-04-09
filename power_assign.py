import operator

class InvalidPower(Exception):
    pass

class WrongPlayerCount(Exception):
    pass

class PowerAssignment():
    """
    Assigns powers to the players in a Diplomacy game
    """

    def __init__(self, all_powers):
        """
        Set the list of all available powers for a game.
        """
        self.previous_games = {}
        self.all_powers = all_powers

    def set_earlier_games(self, for_player, powers_played):
        """
        Specifies which powers have previously been played by the specified player.
        """
        # Check for any powers we don't know about
        for p in powers_played:
            if p not in self.all_powers:
                raise InvalidPower(p)
        self.previous_games[for_player] = powers_played

    def _calculate_fitness(self, power_assignment):
        """
        Returns a fitness score for the specified power assignment.
        Score is the number of times a played in the assignment has
        previously played their assigned power, so a lower number is better,
        and a score of zero is ideal.
        """
        score = 0
        for k,v in power_assignment.items():
            # How many times has this player previously played this power?
            try:
                for i in self.previous_games[k]:
                    if i == v:
                        score += 1
            except KeyError:
                # No previous games for this player
                pass
        return score

    def _assign_remaining_powers(self, used_powers, to_players):
        """
        Recursively assign powers to players, returning a list of every combo.
        Returns a list of dicts, indexed by player, of powers.
        """
        results = []
        # Assign all possible powers for the first player
        player = to_players[0]
        remaining_players = to_players[1:]
        remaining_powers = list(set(self.all_powers) - set(used_powers))
        for power in remaining_powers:
            assignment = {}
            assignment[player] = power
            if len(remaining_players) == 0:
                results += [assignment]
            else:
                for a in self._assign_remaining_powers(used_powers + [power], remaining_players):
                    # Merge in our power assignment
                    a.update(assignment)
                    results += [a]
        return results

    def best_power_assignment(self, for_players):
        """
        Returns the best power assignment found.
        If it finds multiple 'best' options, returns one of them.
        """
        if len(for_players) != len(self.all_powers):
            raise WrongPlayerCount(len(for_players))
        # With 7 players, we can exhaustively test every possible (5040) power assignment
        # in a reasonable time
        assignments = self._assign_remaining_powers([], for_players)
        # Calculate a fitness score for each possible assignment
        results = []
        for a in assignments:
            results.append((a, self._calculate_fitness(a)))
        # Sort by fitness score
        results.sort(key=operator.itemgetter(1))
        # Return the best assignment
        return results[0][0]
