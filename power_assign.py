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
Assign powers to players in a Diplomacy game.
"""

import operator, random

class InvalidPower(Exception):
    """The power was not included in all_powers as passed to __init__()"""
    pass

class MissingPower(Exception):
    """One or more powers from all_powers as passed to __init__() is missing"""
    pass

class WrongPlayerCount(Exception):
    """There should be exactly one player per power"""
    pass

class PowerAssignment():
    """
    Assigns powers to the players in a Diplomacy game
    """

    def __init__(self, all_powers):
        """
        Set the list of all available powers for a game.
        """
        # Indexed by player, of powers
        self.previous_games = {}
        self.groupings = []
        self.all_powers = all_powers

    def add_grouping(self, grouping, value=100):
        """
        Specifies a way powers should be considered to be groups.
        Power assignment will try to assign powers from groups
        that have not previously been played by a player.
        Note that multiple groupings can be specified, in which case
        all of them will be considered when evaluating a possible
        assignment.

        grouping is a list of lists of powers.
        value is a measure of the weight to apply to this grouping.
            Each time a player has played a power in a group before,
            value will be added to the fitness score for that assignment.
            The default value of 100 will weight groups much higher than
            individual powers, meaning that individual powers will only
            be considered as a tie-breaker after considering groups.
        """
        # Check for unrecognised powers
        for g in grouping:
            for p in g:
                if p not in self.all_powers:
                    raise InvalidPower(p)
        # Check for missing powers
        power_set = set(self.all_powers)
        for g in grouping:
            power_set -= set(g)
        if len(power_set) > 0:
            raise MissingPower(power_set)
        self.groupings.append((grouping, value))

    def set_earlier_games(self, for_player, powers_played):
        """
        Specifies which powers have previously been played by the specified player.
        Overwrites any previous record for this player.
        Note that it makes perfect sense to include a power multiple times
        in powers_played if the player has played that power more than once.
        """
        # Check for any powers we don't know about
        for p in powers_played:
            if p not in self.all_powers:
                raise InvalidPower(p)
        self.previous_games[for_player] = powers_played

    def add_power_played(self, for_player, power):
        """
        Add to the list of powers played by the specified player.
        """
        # Check for any powers we don't know about
        if power not in self.all_powers:
            raise InvalidPower(p)
        self.previous_games[for_player].append(power)

    def _calculate_group_fitness(self, power_assignment, grouping):
        """
        Returns a fitness score for the specified power assignment and grouping.
        Score is the number of times a played in the assignment has
        previously played a power from the same group, so a lower number is better,
        and a score of zero is ideal.
        """
        score = 0
        for k,v in power_assignment.items():
            # Find the group containing this power
            for g in grouping:
                if v in g:
                    # This is the group we want
                    break
            # How many times has this player previously played a power from this group?
            try:
                for i in self.previous_games[k]:
                    if i in g:
                        score += 1
            except KeyError:
                # No previous games for this player
                pass
        return score

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
        Recursively assign powers to players, returning a list of every combination.
        Returns a list of dicts, indexed by player, of powers.
        """
        results = []
        # Assign all possible powers for the first player
        player = to_players[0]
        remaining_players = to_players[1:]
        remaining_powers = list(set(self.all_powers) - set(used_powers))
        random.shuffle(remaining_powers)
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
            score = 0
            # Score for each grouping
            for g, weight in self.groupings:
                score += weight * self._calculate_group_fitness(a, g)
            # Score for exact powers played before
            score += self._calculate_fitness(a)
            results.append((a, score))
        # Sort by fitness score
        results.sort(key=operator.itemgetter(1))
        # Return the best assignment
        #print("Best assignment has a score of %d" % results[0][1])
        return results[0][0]
