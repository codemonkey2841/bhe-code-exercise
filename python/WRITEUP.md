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

## Phase 2: Segmentation Optimization

Memory usage is still our biggest issue. If I can work through the list in
segments instead of running the whole list at once that will limit the amount
of memory needed to a nearly static rate for all large values of n.  The value
to use is for segment size is pretty arbitrary and the optimal value can vary
greatly depending on the hardware the function is being run on. Using a value
of 256k is small enough that it will fit in most modern L2 caches (which can
potentially speed up calculations), but big enough that I'm not causing too
much overhead with segment management.

### Test Results

Skipping n=100,000,000 test:
```
$ python -m unittest test_sieve.py
.s........
----------------------------------------------------------------------
Ran 10 tests in 5.606s

OK (skipped=1)                                                           [5.8s]
```

Full test suite:
```
$ python -m unittest test_sieve.py
..........
----------------------------------------------------------------------
Ran 10 tests in 69.960s

OK                                                                    [1m10.2s]
```

### Performance

```
Label:     segmentation-optimization
Timestamp: 2026-06-05T20:21:25+00:00
Prev:      bytearray-optimization (2026-06-05T16:38:06+00:00)

           n        time    peak mem     vs prev  ok
         100      21.3us       3.6KB        +14%  y
      10,000       3.0ms     499.9KB         +3%  y
   1,000,000     424.2ms       1.8MB         -1%  y
  10,000,000       4.99s       1.9MB         -5%  y
 100,000,000      64.27s       2.0MB         +2%  y
 ```

There is no neglible reduction in time, but for lower values that makes sense
since this optimization does nothing for n<128k (the segment window size). For
the larger values I _could've_ seen a potential reduction by forcing the
operations to occur in the L2 cache but there are a lot of external factors
that could affect this. The important part is that it didn't _add_ time. But
the key improvement here is **huge**. We've gone from GB memory usage on the
extreme end (with the expectation that it would increase exponentially with
`n`) to 2MB at the extreme end with a trending pattern of not getting much
larger.

## Phase N: lucy_hedgehog

During my research into bounding formulae for right-sizing the sieve list
during Phase 0 I discovered a shortcut for this calculation, commonly referred
to as the lucy_hedgehog algorithm. The methodology for this is calculating the
bounds as I already have (using Rosser's bounds), then use some arithmetic to
accurately count the number of primes that exist from 2 to the lower bounds.
Then run the sieve up to the square root of your ultimate `n`. This gives you
a significantly smaller calculation to perform in order to get a list of
primes to eliminate multiples of. Then you run the sieve starting at the lower
bound, going to the upper bound.

As you may suspect, this will cause a _significant_ reduction in time and, if I
hadn't already implemented the segmentation optimization, would reduce memory
usage. However, these reductions would only actually be significant for
extremely large numbers (I'm guessing you'd really start to see the reduction
at n>10^9).

Considering the edge case on the large side is 10^8 per the assessment brief
in the README, this isn't a worthwhile pursuit. If I was expecting to use this
on larger numbers, this would be my next step.

## References

- https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes
- https://en.wikipedia.org/wiki/Prime_number_theorem
- https://www.geeksforgeeks.org/dsa/how-is-the-time-complexity-of-sieve-of-eratosthenes-is-nloglogn/
- https://math.berkeley.edu/~elafandi/euler/p10/
