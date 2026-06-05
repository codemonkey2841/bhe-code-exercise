Given the goal of finding the `n`th prime number the most naive way to do this
would be to create a function that determines whether a given number is a prime
number then iterate over every number and increment a counter for every prime
encountered and stop once `n` primes have been encountered, returning the last
number encountered. This is inefficient (O(n)) and can be improved upon using
the Sieve of Eratosthenes, as hinted by the brief for this assessment.

## Phase 0 - Basic Sieve

Phase 0 is implementing the Sieve of Eratosthenes. There is nothing more to
explain beyond that. There will be more in further phases.

### Test Results

Skipping n=100,000,000 test:
```
$ python -m unittest test_sieve.py
.s........
----------------------------------------------------------------------
Ran 10 tests in 23.789s

OK (skipped=1)                                                          [24.1s]
```

Full test run:
```
$ python -m unittest test_sieve.py
..........
----------------------------------------------------------------------
Ran 10 tests in 2146.589s

OK                                                                   [35m46.9s]
```

### Performance

```
Label:     simple-sieve
Timestamp: 2026-06-05T14:01:38+00:00

           n        time    peak mem     vs prev  ok
         100      31.1us       7.8KB              ?
      10,000       6.2ms       1.3MB              ?
   1,000,000       1.61s     162.7MB              y
  10,000,000      21.40s       1.8GB              y
 100,000,000    2145.91s      19.7GB              y
```

The key takeaway here is that as n increases, peak mem and time increase
expontentially. I need to find ways to shave that down... Significantly

Another consideration I need to be aware of is that python integers are int64.
This isn't a huge concern for the given test values, but for larger prime
numbers we may need to account for that limitation.

## References

- https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes
- https://en.wikipedia.org/wiki/Prime_number_theorem
