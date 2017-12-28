import unittest
from game_seeder import *

class GameSeederSetupTest(unittest.TestCase):
    """
    Validate the setup of GameSeeder - adding players, games, duplicate players, etc.
    """

    # Our players will be strings (names)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # add_player()
    def test_add_player_twice(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        self.assertRaises(InvalidPlayer, seeder.add_player, 'A')

    # duplicate_player()
    def test_duplicate_player(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.duplicate_player('A', 'A2')

    def test_duplicate_player_non_existent(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        self.assertRaises(InvalidPlayer, seeder.duplicate_player, 'B', 'A2')

    def test_duplicate_player_twice(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.duplicate_player('A', 'A2')
        self.assertRaises(InvalidKey, seeder.duplicate_player, 'A', 'A2')

    def test_duplicate_player_for_three_games(self):
        # In theory, it's ok to have one player play three (or more) games simultaneously
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.duplicate_player('A', 'A2')
        seeder.duplicate_player('A', 'A3')

    def test_duplicate_player_invalid_key(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        self.assertRaises(InvalidKey, seeder.duplicate_player, 'A', 'B')

    # add_played_game()
    def test_add_played_game(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.add_player('H')
        seeder.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))

    def test_add_played_game_invalid_player(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        self.assertRaises(InvalidPlayer, seeder.add_played_game, set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))

    def test_add_played_game_duplicate_player(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.duplicate_player('G', 'G2')
        seeder.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G2']))

    def test_add_played_game_player_and_duplicate_present(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.duplicate_player('F', 'F2')
        self.assertRaises(InvalidPlayer, seeder.add_played_game, set(['A', 'B', 'C', 'D', 'E', 'F', 'F2']))

    def test_add_played_game_two_duplicates_present(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.duplicate_player('F', 'F2')
        seeder.duplicate_player('F', 'F3')
        self.assertRaises(InvalidPlayer, seeder.add_played_game, set(['A', 'B', 'C', 'D', 'E', 'F2', 'F3']))

    def test_add_played_game_player_too_few_players(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        self.assertRaises(InvalidPlayerCount, seeder.add_played_game, set(['A', 'B', 'C', 'D', 'E', 'F']))

    def test_add_played_game_player_too_few_players(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.add_player('H')
        self.assertRaises(InvalidPlayerCount, seeder.add_played_game, set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']))

    # _fitness_score()
    def test_fitness_score_no_games(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        self.assertEqual(0, seeder._fitness_score(set(['A', 'B', 'C', 'D', 'E', 'F', 'G'])))

    def test_fitness_score_invalid_player(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        self.assertRaises(InvalidPlayer, seeder._fitness_score, set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))

    def test_fitness_score_one_pair_played(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.add_player('H')
        seeder.add_player('I')
        seeder.add_player('J')
        seeder.add_player('K')
        seeder.add_player('L')
        seeder.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))
        self.assertEqual(2, seeder._fitness_score(set(['A', 'B', 'H', 'I', 'J', 'K', 'L'])))

    def test_fitness_score_worst_case(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))
        self.assertEqual(42, seeder._fitness_score(set(['A', 'B', 'C', 'D', 'E', 'F', 'G'])))

    def test_fitness_score_worst_case_with_duplicate(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.duplicate_player('F', 'F2')
        seeder.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))
        game = set(['A', 'B', 'C', 'D', 'E', 'F2', 'G'])
        # Take a copy of game
        g2 = set(game)
        self.assertEqual(42, seeder._fitness_score(game))
        # Check that the method didn't change game
        self.assertEqual(game, g2)

    def test_fitness_score_two_pairs(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.add_player('H')
        seeder.add_player('I')
        seeder.add_player('J')
        seeder.add_player('K')
        seeder.add_player('L')
        seeder.add_player('M')
        seeder.add_player('N')
        seeder.add_player('O')
        seeder.add_player('P')
        seeder.add_player('Q')
        # Two previous non-overlapping games
        seeder.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))
        seeder.add_played_game(set(['H', 'I', 'J', 'K', 'L', 'M', 'N']))
        # Game with two pairs from each earlier game
        game = set(['A', 'B', 'M', 'N', 'O', 'P', 'Q'])
        self.assertEqual(4, seeder._fitness_score(game))

    def test_fitness_score_one_triple(self):
        seeder = GameSeeder()
        seeder.add_player('A')
        seeder.add_player('B')
        seeder.add_player('C')
        seeder.add_player('D')
        seeder.add_player('E')
        seeder.add_player('F')
        seeder.add_player('G')
        seeder.add_player('H')
        seeder.add_player('I')
        seeder.add_player('J')
        seeder.add_player('K')
        seeder.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))
        # Game with two pairs from each earlier game
        game = set(['A', 'C', 'D', 'H', 'I', 'J', 'K'])
        self.assertEqual(6, seeder._fitness_score(game))

def create_seeder():
    # As there's no way to remove players or duplicates, we'll re-create the seeder in each test
    seeder = GameSeeder()
    # 20 players to start with
    seeder.add_player('A')
    seeder.add_player('B')
    seeder.add_player('C')
    seeder.add_player('D')
    seeder.add_player('E')
    seeder.add_player('F')
    seeder.add_player('G')
    seeder.add_player('H')
    seeder.add_player('I')
    seeder.add_player('J')
    seeder.add_player('K')
    seeder.add_player('L')
    seeder.add_player('M')
    seeder.add_player('N')
    seeder.add_player('O')
    seeder.add_player('P')
    seeder.add_player('Q')
    seeder.add_player('R')
    seeder.add_player('S')
    seeder.add_player('T')
    return seeder

class GameSeederSeedingTest(unittest.TestCase):
    """
    Validate the meat of GameSeeder - actually seeding games
    """

    # Our players will be strings (names)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def check_game(self, game):
        # Game should have exactly 7 players
        self.assertEqual(len(game), 7)
        # No player should be playing with their duplicate
        # In this test, all duplicates are the playername plus '2'
        for p in game:
            if p[-1] == '2':
                self.assertFalse(p[:-1] in game)

    def check_game_set(self, game_set, players, omissions = set()):
        game_count = len(game_set)
        self.assertEqual(game_count, players / 7)
        # Every game should be valid by itself
        for g in game_set:
            self.check_game(g)
        # Each player should be present exactly once
        players = set()
        for g in game_set:
            players |= g
        self.assertEqual(len(players), 7 * game_count, "One or more players is playing multiple games")
        # No omitted players should be present
        self.assertEqual(len(players & omissions), 0, "One or more omitted players is in a game")

    # seed_games()
    def test_seed_games_initial(self):
        s = create_seeder()
        s.add_player('U')
        r = s.seed_games()
        self.check_game_set(r, 21)

    def test_seed_games_second_round(self):
        s = create_seeder()
        s.add_player('U')
        # Add some previously-played games
        s.add_played_game(set(['A', 'B', 'C', 'D', 'E', 'F', 'G']))
        s.add_played_game(set(['H', 'I', 'J', 'K', 'L', 'M', 'N']))
        s.add_played_game(set(['O', 'P', 'Q', 'R', 'S', 'T', 'U']))
        r = s.seed_games()
        self.check_game_set(r, 21)
        # Check that game_set has a "good" fitness score
        # With 21 players, we should end up with games with 2 pairs and a triplet,
        # which gives each game a fitness of 2+2+6=10, and the set a fitness of 10*3=30
        self.assertEqual(s._set_fitness(r), 30)

    def test_seed_games_bigger_tournament(self):
        # Two rounds of a 49-player tournament
        seeder = GameSeeder()
        for i in range(49):
            seeder.add_player('%dp' % i)
        r = seeder.seed_games()
        self.check_game_set(r, 49)
        # First round by definition should have a fitness of zero
        self.assertEqual(seeder._set_fitness(r), 0)
        # Add the first round games as played
        for g in r:
            seeder.add_played_game(g)
        r = seeder.seed_games()
        self.check_game_set(r, 49)
        # Check that game_set has a "good" fitness score
        # TODO What number works here?
        # With 49 players, there is a solution with a fitness of zero.
        # In practice, with 1000 iterations I see 14..22
        # In practice, with 10000 iterations I see 12..16
        self.assertTrue(seeder._set_fitness(r) < 24)
        print(seeder._set_fitness(r))

    def test_seed_games_wrong_number_of_players(self):
        # Total player count not a multiple of 7
        s = create_seeder()
        s.add_player('U')
        s.add_player('V')
        self.assertRaises(InvalidPlayerCount, s.seed_games)

    def test_seed_games_wrong_number_of_players_2(self):
        # Mutliple of 7 players, plus one duplicate
        s = create_seeder()
        s.add_player('U')
        s.duplicate_player('U', 'U2')
        self.assertRaises(InvalidPlayerCount, s.seed_games)

    def test_seed_games_wrong_number_of_players_3(self):
        # Multiple of 7 players, minus one not playing
        s = create_seeder()
        s.add_player('U')
        self.assertRaises(InvalidPlayerCount, s.seed_games, set(['U']))

    def test_seed_games_with_omission(self):
        # Multiple of 7 players plus one, minus one not playing
        s = create_seeder()
        s.add_player('U')
        s.add_player('V')
        omits = set(['U'])
        r = s.seed_games(omits)
        self.check_game_set(r, 21)

    def test_seed_games_with_duplicate(self):
        # Multiple of 7 players minus one, plus one duplicate
        s = create_seeder()
        s.duplicate_player('T', 'T2')
        r = s.seed_games()
        self.check_game_set(r, 21)

    def test_seed_games_with_omitted_duplicate(self):
        # Multiple of 7 players, plus one omitted duplicate
        s = create_seeder()
        s.add_player('U')
        s.duplicate_player('T', 'T2')
        omits = set(['T2'])
        r = s.seed_games(omits)
        self.check_game_set(r, 21)

if __name__ == '__main__':
    unittest.main()
