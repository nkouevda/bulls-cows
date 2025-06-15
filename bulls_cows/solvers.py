import itertools
import logging
import random


solver_classes = set()


class Solver(object):
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        solver_classes.add(cls)

    def __init__(self, possible_secrets):
        self.possible_secrets = possible_secrets

    def get_guess(self):
        raise NotImplementedError

    def update_response(self, guess, response):
        """Filter out all secrets that would not have yielded the given response."""
        self.possible_secrets = [
            secret for secret in self.possible_secrets if _get_response(guess, secret) == response
        ]


class MiddleSolver(Solver):
    def get_guess(self):
        """Return the middle possible secret."""
        return self.possible_secrets[len(self.possible_secrets) >> 1]


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
