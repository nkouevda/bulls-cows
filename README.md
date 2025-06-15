# bulls-cows

[Bulls and cows](https://en.wikipedia.org/wiki/Bulls_and_cows) solver.

## Usage

```
usage: bulls-cows [<options>]

Bulls and cows solver

options:
  -h, --help            show this help message and exit
  -a, --alen <len>      alphabet length (default: 10)
  -c, --class {FirstPossibleSecretSolver,LastPossibleSecretSolver,LeastCommonGuessedDigitSolver,MiddlePossibleSecretSolver,MostCommonRemainingDigitSolver,RandomSolver}
                        solver class name (default: RandomSolver)
  -m, --multiprocess    parallelize computation via multiprocessing (default: False)
  -n, --num <num>       number of secrets (default: all)
  -s, --slen <len>      secret length (default: 4)
  -v, --verbose         verbose output (default: False)
```

## Examples

To run with the default configuration (alphabet length `10`, secret length `4`,
all possible secrets, `RandomSolver`, single process):

    python -m bulls_cows

To run with a different configuration (e.g. alphabet length `20`, secret length
`3`, `10` secrets, `MiddleSolver`, multiprocessing, verbose output):

    python -m bulls_cows -a 20 -s 3 -n 10 -c MiddleSolver -m -v

## License

[MIT License](LICENSE.txt)
