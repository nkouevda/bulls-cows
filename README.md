<!-- Nikita Kouevda -->
<!-- 2014/12/01 -->

# bulls-cows

[Bulls and cows](https://en.wikipedia.org/wiki/Bulls_and_cows) solver.

## Usage

```bash
./bulls_cows.py [-h] [-a len] [-c class] [-m] [-n num] [-s len] [-v]
```

## Examples

To run with the default configuration (alphabet length `10`, secret length `4`,
all possible secrets, `RandomSolver`, single process):

```bash
./bulls_cows.py
```

To run with a different configuration (e.g. alphabet length `20`, secret length
`3`, `10` secrets, `MiddleSolver`, multiprocessing, very verbose output):

```bash
./bulls_cows.py -a 20 -s 3 -n 10 -c MiddleSolver -m -vv
```

## License

Licensed under the [MIT License](http://www.opensource.org/licenses/MIT).
