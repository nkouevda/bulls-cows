#!/usr/bin/env python3

from argparse import ArgumentParser
import itertools
import multiprocessing
import random
import statistics

def get_response(guess, secret):
  bulls, cows = 0, 0
  for g, s in zip(guess, secret):
    if g == s:
      bulls += 1
    elif g in secret:
      cows += 1
  return (bulls, cows)

class Solver:

  def __init__(self, possible_secrets):
    self.possible_secrets = possible_secrets

  def get_guess(self):
    raise NotImplementedError

  def update_response(self, guess, response):
    """Filter out all secrets that would not have yielded the given response.
    """
    self.possible_secrets = [s for s in self.possible_secrets
                             if get_response(guess, s) == response]

class MiddleSolver(Solver):

  def get_guess(self):
    """Return the middle possible secret.
    """
    return self.possible_secrets[len(self.possible_secrets) >> 1]

class RandomSolver(Solver):

  def get_guess(self):
    """Return a random possible secret.
    """
    return random.choice(self.possible_secrets)

def solve(solver_class, possible_secrets, secret, verbose=False):
  solver = solver_class(possible_secrets)
  for move_count in itertools.count(1):
    guess = solver.get_guess()
    if guess == secret:
      if verbose:
        print('{} in {:d} moves'.format(secret, move_count))
      return move_count
    else:
      solver.update_response(guess, get_response(guess, secret))

def batch_solve(solver_class, possible_secrets, secrets, verbose=False):
  return [solve(solver_class, possible_secrets, s, verbose) for s in secrets]

def main():
  valid_solvers = {s.__name__: s for s in (MiddleSolver, RandomSolver)}

  parser = ArgumentParser(description='Bulls and cows solver')
  parser.add_argument('-a', '--alen', metavar='len', default=10, type=int,
                      help='alphabet length (default: %(default)s)')
  parser.add_argument('-c', '--class', metavar='class', dest='solver_class',
                      default='RandomSolver', choices=valid_solvers.keys(),
                      help='solver class name (default: %(default)s)')
  parser.add_argument('-m', '--multiprocess', action='store_true',
                      help='parallelize computation via multiprocessing')
  parser.add_argument('-n', '--num', metavar='num', type=int,
                      help='number of secrets (default: all possible secrets)')
  parser.add_argument('-s', '--slen', metavar='len', default=4, type=int,
                      help='secret length (default: %(default)s)')
  parser.add_argument('-v', '--verbose', action='count', default=0,
                      help='verbose output (-vv for very verbose)')

  args = parser.parse_args()
  alphabet = tuple(range(args.alen))
  secret_length = args.slen
  num_secrets = args.num
  solver_class = valid_solvers[args.solver_class]
  multiprocess = args.multiprocess
  verbose = args.verbose
  very_verbose = verbose > 1

  possible_secrets = tuple(itertools.permutations(alphabet, secret_length))
  shuffled_secrets = list(possible_secrets)
  random.shuffle(shuffled_secrets)
  secrets_cycle = itertools.cycle(shuffled_secrets)
  if num_secrets is None:
    num_secrets = len(possible_secrets)
  if verbose:
    print('alphabet length: {:d}'.format(len(alphabet)))
    print('secret length: {:d}'.format(secret_length))
    print('possible secrets: {:d}'.format(len(possible_secrets)))
    print('secrets to solve: {:d}'.format(num_secrets))
    print('solver class: {}'.format(solver_class.__name__))

  if multiprocess:
    num_threads = multiprocessing.cpu_count()
    batch_size = (num_secrets + num_threads - 1) // num_threads
    pool = multiprocessing.Pool()
    results = []
    for i in range(num_threads):
      batch = [next(secrets_cycle) for _ in range(batch_size)]
      results.append(pool.apply_async(batch_solve, args=(
          solver_class, possible_secrets, batch, very_verbose)))
    pool.close()
    pool.join()
    move_counts = [x for result in results for x in result.get()]
  else:
    batch = [next(secrets_cycle) for _ in range(num_secrets)]
    move_counts = batch_solve(
        solver_class, possible_secrets, batch, very_verbose)

  print('µ = {:f}'.format(statistics.mean(move_counts)))
  print('s = {:f}'.format(statistics.stdev(move_counts)))

if __name__ == '__main__':
  main()
