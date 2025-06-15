import argparse
import itertools
import logging
import multiprocessing
import random

from . import solvers


def main():
    all_solvers = {solver.__name__: solver for solver in solvers.solver_classes}

    parser = argparse.ArgumentParser(
        prog="bulls-cows",
        usage="%(prog)s [<options>]",
        description="Bulls and cows solver",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-a",
        "--alen",
        type=int,
        default=10,
        help="alphabet length",
        metavar="<len>",
    )
    parser.add_argument(
        "-c",
        "--class",
        dest="solver_class",
        choices=all_solvers.keys(),
        default="RandomSolver",
        help="solver class name",
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
        help="number of secrets",
        metavar="<num>",
    )
    parser.add_argument(
        "-s",
        "--slen",
        type=int,
        default=4,
        help="secret length",
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
    solver_class = all_solvers[args.solver_class]
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
    logging.info("alphabet length: %s", len(alphabet))
    logging.info("secret length: %s", secret_length)
    logging.info("possible secrets: %s", len(possible_secrets))
    logging.info("secrets to solve: %s", num_secrets)
    logging.info("solver class: %s", solver_class.__name__)

    if multiprocess:
        num_threads = multiprocessing.cpu_count()
        batch_size = (num_secrets + num_threads - 1) // num_threads
        pool = multiprocessing.Pool()
        results = []
        for i in range(num_threads):
            batch = list(itertools.islice(secrets_cycle, batch_size))
            results.append(
                pool.apply_async(solvers.batch_solve, args=(solver_class, possible_secrets, batch))
            )
        pool.close()
        pool.join()
        move_counts = [x for result in results for x in result.get()]
    else:
        batch = list(itertools.islice(secrets_cycle, num_secrets))
        move_counts = solvers.batch_solve(solver_class, possible_secrets, batch)

    mean = 1.0 * sum(move_counts) / len(move_counts)
    print("mean: %.6f" % mean)
    stdev = (sum((c - mean) ** 2 for c in move_counts) / len(move_counts)) ** 0.5
    print("stdev: %.6f" % stdev)


if __name__ == "__main__":
    main()
