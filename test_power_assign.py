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

from power_assign import *

powers = ['A', 'E', 'F', 'G', 'I', 'R', 'T']
# East versus west
grouping_1 = [['E', 'F', 'G'], ['A', 'I', 'R', 'T']]
# Centre versus west versus east
grouping_2 = [['A', 'G', 'I'], ['E', 'F'], ['R', 'T']]
# Centre versus witches versus the rest
grouping_3 = [['A', 'G', 'I'], ['E', 'T'], ['F', 'R']]
# Pairs
grouping_4 = [['A', 'I'], ['E', 'F'], ['R', 'T'], ['G']]

powers_played = {}

def note_played_powers(assigner, assignment):
    for p, power in assignment.items():
        try:
            powers_played[p].append(power)
        except KeyError:
            powers_played[p] = [power]

def one_round(assigner, players):
    for p in players:
        assigner.set_earlier_games(p, powers_played[p])
    r = assigner.best_power_assignment(players)
    print(r)
    return r

def run_test(rounds):
    round = 1
    # Create a list of players
    players = []
    for i in range(1, 8):
        players.append('Player %d' % i)
    # Create the class to test
    assigner = PowerAssignment(powers)
    # Add groupings
    assigner.add_grouping(grouping_1)
    assigner.add_grouping(grouping_2)
    assigner.add_grouping(grouping_3)
    assigner.add_grouping(grouping_4)
    # Try with no earlier games
    print("Testing with no earlier games")
    r = assigner.best_power_assignment(players)
    print(r)
    while round < rounds:
        # Add the last round to power_played
        note_played_powers(assigner, r)
        # Now do another round
        round += 1
        print("Testing round %d" % round)
        r = one_round(assigner, players)

if __name__ == '__main__':
    run_test(4)
