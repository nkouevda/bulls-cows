import collections
import itertools
import logging
import random

solver_classes = set()


class Solver(object):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        solver_classes.add(cls)

    def __init__(self, possible_secrets):
        self.guesses = []
        self.possible_secrets = possible_secrets

    def get_guess(self):
        raise NotImplementedError

    def update_response(self, guess, response):
        """Filter out all secrets that would not have yielded the given response."""
        self.guesses.append(guess)
        self.possible_secrets = [
            secret for secret in self.possible_secrets if _get_response(guess, secret) == response
        ]


# --num 25200: mean 5.560317, stdev 1.053684
class FirstPossibleSecretSolver(Solver):
    def get_guess(self):
        """Return the first possible secret."""
        return self.possible_secrets[0]


# --num 25200: mean 5.472222, stdev 0.978551
class MiddlePossibleSecretSolver(Solver):
    def get_guess(self):
        """Return the middle possible secret."""
        return self.possible_secrets[len(self.possible_secrets) >> 1]


# --num 25200: mean 5.560317, stdev 1.053684
class LastPossibleSecretSolver(Solver):
    def get_guess(self):
        """Return the last possible secret."""
        return self.possible_secrets[-1]


# --num 25200: mean 5.551468, stdev 1.045763
class LeastCommonGuessedDigitSolver(Solver):
    def get_guess(self):
        # Random first guess
        if not self.guesses:
            return random.choice(self.possible_secrets)

        counter = collections.Counter(itertools.chain.from_iterable(self.guesses))

        best_secret = None
        lowest_score = float("inf")

        for secret in self.possible_secrets:
            score = sum(s * counter[s] for s in secret)
            if score < lowest_score:
                best_secret = secret
                lowest_score = score

        return best_secret


# --num 25200: mean 5.445952, stdev 0.959092
class MostCommonRemainingDigitSolver(Solver):
    def get_guess(self):
        # Random first guess
        if not self.guesses:
            return random.choice(self.possible_secrets)

        counter = collections.Counter(itertools.chain.from_iterable(self.possible_secrets))

        best_secret = None
        highest_score = 0

        for secret in self.possible_secrets:
            score = sum(s * counter[s] for s in secret)
            if score > highest_score:
                best_secret = secret
                highest_score = score

        return best_secret


# --num 25200: mean 5.470000, stdev 0.978810
class RandomSolver(Solver):
    def get_guess(self):
        """Return a random possible secret."""
        return random.choice(self.possible_secrets)


def solve(solver_class, possible_secrets, secret):
    solver = solver_class(possible_secrets)
    for move_count in itertools.count(1):
        guess = solver.get_guess()
        if guess == secret:
            logging.debug("solved %s in %s moves", secret, move_count)
            return move_count
        else:
            solver.update_response(guess, _get_response(guess, secret))


def batch_solve(solver_class, possible_secrets, secrets):
    return [solve(solver_class, possible_secrets, secret) for secret in secrets]


def _get_response(guess, secret):
    bulls, cows = 0, 0
    for g, s in zip(guess, secret):
        if g == s:
            bulls += 1
        elif g in secret:
            cows += 1
    return (bulls, cows)
