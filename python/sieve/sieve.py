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
        numbers = self.sieve(bounds["upper"])

        if len(numbers) < n:
            raise IndexError("sieve didn't generate enough primes")

        return numbers[n]

    def sieve(self, n: int) -> tuple:
        """
        Given a limit n, calculate which positive integers are prime utilizing
        the Sieve of Eratosthenes

        :param int n: the upper bound of primes to calculate using the sieve
        :return: a tuple of all prime numbers less than the given limit
        :rtype: tuple
        """

        nums = bytearray(b"\x01" * (n + 1))
        nums[0] = 0
        nums[1] = 0
        p = 2

        while p ** 2 <= n:
            if nums[p]:
                # mark all multiples of p as not prime
                nums[p ** 2 :: p] = b"\x00" * (((n - p ** 2) // p) + 1) # fancy math to ensure the byte slice is the correct size

            p += 1

        return [i for i, v in enumerate(nums) if v]
