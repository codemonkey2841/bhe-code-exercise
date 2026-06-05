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
         100      31.1us       7.8KB              y
      10,000       6.2ms       1.3MB              y
   1,000,000       1.61s     162.7MB              y
  10,000,000      21.40s       1.8GB              y
 100,000,000    2145.91s      19.7GB              y
```

The key takeaway here is that as n increases, peak mem and time increase
expontentially. I need to find ways to shave that down... Significantly

Another consideration I need to be aware of is that python integers are int64.
This isn't a huge concern for the given test values, but for larger prime
numbers we may need to account for that limitation.

## Phase 1 - bytearray optimization

Between the 2 metrics I am trying to optimize for, peak mem is the more
significant of the two. The optional 100M case required close to 20GB of RAM
and even the 10M case required nearly 2GB. Testing these is not feasible unless
you have enough resources. In a real life situation you'd likely be automating
unit tests somewhere in your CI/CD pipeline and having that kind of resource
drain gets expensive.

The main contributor to the memory issue is the list used in the sieve function.
Each element in a boolean list in python is an 8-byte pointer, plus the size of
2 boolean objects.

The simplest solution to this is to implement a `bytearray` sized to the `n`
value given. Each "element" in a bytearray is only 1 byte, meaning that I
should see a 7/8 cost reduction from memory and, depending on how much swapping
is going on under the hood, I could also see a significant reduction in time
from this as well.

### Test Results

Skipping n=100,000,000 test:
```
$ python -m unittest test_sieve.py
.s........
----------------------------------------------------------------------
Ran 10 tests in 6.016s

OK (skipped=1)                                                           [6.3s]
```

Full test suite:
```
$ python -m unittest test_sieve.py
..........
----------------------------------------------------------------------
Ran 10 tests in 71.067s

OK                                                                    [1m11.4s]
```

### Performance

```
Label:     bytearray-optimization
Timestamp: 2026-06-05T16:38:06+00:00
Prev:      simple-sieve (2026-06-05T14:01:38+00:00)

           n        time    peak mem     vs prev  ok
         100      18.8us       3.5KB        -40%  y
      10,000       2.9ms     499.8KB        -54%  y
   1,000,000     426.7ms      53.0MB        -74%  y
  10,000,000       5.26s     545.6MB        -75%  y
 100,000,000      62.71s       5.8GB        -97%  y
```

As expected, I saw a significant improvement in both memory usage and execution
time. I still need to squeeze more out of this to get results into a production
feasible range...

## References

- https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes
- https://en.wikipedia.org/wiki/Prime_number_theorem
- https://www.geeksforgeeks.org/dsa/how-is-the-time-complexity-of-sieve-of-eratosthenes-is-nloglogn/
