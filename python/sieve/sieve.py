"""
Implements the Sieve of Eratosthenes for the purpose of calculating the
nth-prime.

Indexing is 0-based: nth_prime(0) == 2, nth_prime(1) == 3, and so on.
"""

from math import log


class Sieve:
    """
    Computes prime numbers using the Sieve of Eratosthenes and exposes
    a 0-based lookup of the nth prime (nth_prime(0) == 2).
    """

    def __init__(self) -> None:
        """
        Initialization method - currently unneeded, will retain until I'm sure
        I won't need it.
        """
        pass

    def rossers_bounds(self, n: int) -> dict:
        """
        Rosser's bounds apply to the n-th prime for n >= 6. We use
        0-based indexing here, so feed k = n + 1 into the formula and
        special-case the small values it can't cover.

        :param int n: the ordinal position of prime number being looked for
        :return: a dict containing the lower bound and the upper bound
        """

        if n < 5:
            return {"lower": 2, "upper": 13}

        k = n + 1
        return {
            "lower": int(k * (log(k) + log(log(k)) - 1)),
            "upper": int(k * (log(k) + log(log(k)))),
        }

    def nth_prime(self, n: int) -> int:
        """
        Given n, calculate the nth prime number

        :param int n: the oridinal position of the prime number being looked for
        :return: the nth prime
        :rtype: int
        """

        # safeguards (reject bool explicitly — bool is a subclass of int)
        if isinstance(n, bool) or not isinstance(n, int) or n < 0:
            raise ValueError("n must be a non-negative integer")

        bounds = self.rossers_bounds(n)
        upper = bounds["upper"]
        sqrt_upper = int(upper**0.5) + 1

        window = 1 << 18  # this is 256KB, this _should_ fit inside L2 cache

        base_primes = []
        primes_seen = 0
        low = 2
        while low <= upper:
            high = min(low + window - 1, upper)
            segment_primes = self.sieve(low, high, base_primes)
            base_primes.extend(p for p in segment_primes if p <= sqrt_upper)
            if primes_seen + len(segment_primes) > n:
                return segment_primes[n - primes_seen]
            primes_seen += len(segment_primes)
            low = high + 1

        raise IndexError("Something went terribly wrong")

    def sieve(
        self, low: int, high: int, base_primes: list[int] | None = None
    ) -> list[int]:
        """
        Given the bounds "low" and "high", calculate which positive integers
        are prime utilizing the Sieve of Eratosthenes

        :param int low: the lower bound of primes to calculate using the sieve
        :param int high: the upper bound of primes to calculate using the sieve
        :param list[int]|None base_primes: a list of primes from lower segments
        :return: a tuple of all prime numbers less than the given limit
        :rtype: tuple
        """

        # Base case - the original, simple sieve algorithm
        if low <= 2:
            nums = bytearray(b"\x01" * (high + 1))
            nums[0] = 0
            nums[1] = 0
            p = 2

            while p**2 <= high:
                if nums[p]:
                    # mark all multiples of p as not prime
                    nums[p**2::p] = b"\x00" * (
                        ((high - p**2) // p) + 1
                    )  # fancy math to ensure the byte slice is the correct size

                p += 1

            return [i for i, v in enumerate(nums) if v]

        # safeguard
        if base_primes is None:
            raise ValueError("base_primes required when low > 2")

        # extended segment algorithm - due to the properties of prime number
        #    math, you really only need to iterate through `base_primes` to
        #    eliminate composites in the current segment.
        nums = bytearray(b"\x01" * (high - low + 1))
        for p in base_primes:
            if p**2 > high:
                break
            start = max(p**2, ((low + p - 1) // p) * p)
            nums[start - low::p] = b"\x00" * (
                ((high - start) // p) + 1
            )  # fancy math to ensure the byte slice is the correct size

        return [low + i for i, v in enumerate(nums) if v]
