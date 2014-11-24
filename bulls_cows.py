#!/usr/bin/env python3

# Nikita Kouevda
# 2014/11/23

import itertools
import multiprocessing
import random
import statistics


ALPHABET = tuple(range(10))
LENGTH = 4
PERMUTATIONS = tuple(itertools.permutations(ALPHABET, LENGTH))


def get_response(guess, secret):
  bulls, cows = 0, 0
  for g, s in zip(guess, secret):
    if g == s:
      bulls += 1
    elif g in secret:
      cows += 1
  return (bulls, cows)


class Solver:

  def __init__(self):
    self.possible_secrets = PERMUTATIONS

  def get_guess(self):
    raise NotImplementedError

  def update_response(self, guess, response):
    raise NotImplementedError


class RandomSolver(Solver):

  def get_guess(self):
    return random.choice(self.possible_secrets)

  def update_response(self, guess, response):
    self.possible_secrets = [s for s in self.possible_secrets
                             if get_response(guess, s) == response]


def solve(solver_class, secret):
  solver = solver_class()
  for move_count in itertools.count(1):
    guess = solver.get_guess()
    response = get_response(guess, secret)
    if response[0] == LENGTH:
      return move_count
    else:
      solver.update_response(guess, response)


def batch_solve(solver_class, secrets):
  return [solve(solver_class, secret) for secret in secrets]


def main():
  solver_class = RandomSolver
  secrets = PERMUTATIONS

  num_threads = multiprocessing.cpu_count()
  batch_size = (len(secrets) + num_threads - 1) // num_threads
  pool = multiprocessing.Pool()
  results = []
  for i in range(num_threads):
    batch = secrets[i * batch_size:(i + 1) * batch_size]
    results.append(pool.apply_async(batch_solve, args=(solver_class, batch)))
  pool.close()
  pool.join()

  move_counts = [x for result in results for x in result.get()]
  print('µ = {:f}'.format(statistics.mean(move_counts)))
  print('s = {:f}'.format(statistics.stdev(move_counts)))


if __name__ == '__main__':
  main()
