# bulls-cows

[Bulls and cows](https://en.wikipedia.org/wiki/Bulls_and_cows) solver.

## Usage

```
usage: bulls_cows.py [-h] [-a len] [-c class] [-m] [-n num] [-s len] [-v]

Bulls and cows solver

optional arguments:
  -h, --help            show this help message and exit
  -a len, --alen len    alphabet length (default: 10)
  -c class, --class class
                        solver class name (default: RandomSolver)
  -m, --multiprocess    parallelize computation via multiprocessing
  -n num, --num num     number of secrets (default: all possible secrets)
  -s len, --slen len    secret length (default: 4)
  -v, --verbose         verbose output
```

## Examples

To run with the default configuration (alphabet length `10`, secret length `4`,
all possible secrets, `RandomSolver`, single process):

    python -m bulls_cows.bulls_cows

To run with a different configuration (e.g. alphabet length `20`, secret length
`3`, `10` secrets, `MiddleSolver`, multiprocessing, verbose output):

    python -m bulls_cows.bulls_cows -a 20 -s 3 -n 10 -c MiddleSolver -m -v

## License

[MIT License](LICENSE.txt)
