import argparse
import itertools
import logging
import multiprocessing
import random


def get_response(guess, secret):
    bulls, cows = 0, 0
    for g, s in zip(guess, secret):
        if g == s:
            bulls += 1
        elif g in secret:
            cows += 1
    return (bulls, cows)


_solver_classes = set()


class SolverRegistry(type):
    def __init__(cls, name, bases, namespace):
        super(SolverRegistry, cls).__init__(name, bases, namespace)
        _solver_classes.add(cls)
        _solver_classes.difference_update(bases)


class Solver(object):
    __metaclass__ = SolverRegistry

    def __init__(self, possible_secrets):
        self.possible_secrets = possible_secrets

    def get_guess(self):
        raise NotImplementedError

    def update_response(self, guess, response):
        """Filter out all secrets that would not have yielded the given response."""
        self.possible_secrets = [
            secret for secret in self.possible_secrets if get_response(guess, secret) == response
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
            logging.debug("%s in %s moves", secret, move_count)
            return move_count
        else:
            solver.update_response(guess, get_response(guess, secret))


def batch_solve(solver_class, possible_secrets, secrets):
    return [solve(solver_class, possible_secrets, secret) for secret in secrets]


def main():
    solvers = {solver.__name__: solver for solver in _solver_classes}

    parser = argparse.ArgumentParser(
        usage="%(prog)s [<options>]",
        description="Bulls and cows solver",
    )
    parser.add_argument(
        "-a",
        "--alen",
        type=int,
        default=10,
        help="alphabet length; default: %(default)s",
        metavar="<len>",
    )
    parser.add_argument(
        "-c",
        "--class",
        dest="solver_class",
        choices=solvers.keys(),
        default="RandomSolver",
        help="solver class name; default: %(default)s",
        metavar="<class>",
    )
    parser.add_argument(
        "-m",
        "--multiprocess",
        action="store_true",
        help="parallelize computation via multiprocessing",
    )
    parser.add_argument(
        "-n",
        "--num",
        type=int,
        help="number of secrets; default: all possible secrets",
        metavar="<num>",
    )
    parser.add_argument(
        "-s",
        "--slen",
        type=int,
        default=4,
        help="secret length; default: %(default)s",
        metavar="<len>",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="verbose output",
    )

    args = parser.parse_args()
    alphabet = tuple(range(args.alen))
    secret_length = args.slen
    num_secrets = args.num
    solver_class = solvers[args.solver_class]
    multiprocess = args.multiprocess
    verbose = args.verbose

    logging.basicConfig(
        format="%(asctime)s: %(levelname)s: %(message)s",
        level=logging.DEBUG if verbose else logging.INFO,
    )

    possible_secrets = tuple(itertools.permutations(alphabet, secret_length))
    shuffled_secrets = list(possible_secrets)
    random.shuffle(shuffled_secrets)
    secrets_cycle = itertools.cycle(shuffled_secrets)
    if num_secrets is None:
        num_secrets = len(possible_secrets)
    logging.debug("alphabet length: %s", len(alphabet))
    logging.debug("secret length: %s", secret_length)
    logging.debug("possible secrets: %s", len(possible_secrets))
    logging.debug("secrets to solve: %s", num_secrets)
    logging.debug("solver class: %s", solver_class.__name__)

    if multiprocess:
        num_threads = multiprocessing.cpu_count()
        batch_size = (num_secrets + num_threads - 1) // num_threads
        pool = multiprocessing.Pool()
        results = []
        for i in range(num_threads):
            batch = list(itertools.islice(secrets_cycle, batch_size))
            results.append(
                pool.apply_async(batch_solve, args=(solver_class, possible_secrets, batch))
            )
        pool.close()
        pool.join()
        move_counts = [x for result in results for x in result.get()]
    else:
        batch = list(itertools.islice(secrets_cycle, num_secrets))
        move_counts = batch_solve(solver_class, possible_secrets, batch)

    mean = 1.0 * sum(move_counts) / len(move_counts)
    print("mean: %.6f" % mean)
    stdev = (sum((c - mean) ** 2 for c in move_counts) / len(move_counts)) ** 0.5
    print("stdev: %.6f" % stdev)


if __name__ == "__main__":
    main()
