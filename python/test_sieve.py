import random
import unittest
from sieve import Sieve


def _is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0:
        return False
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


class SieveTest(unittest.TestCase):

    def setUp(self):
        self.sieve = Sieve()

    def _assert_fuzz(self, low: int, high: int, sample_size: int, seed: int) -> None:
        rng = random.Random(seed)
        indices = sorted(rng.sample(range(low, high), sample_size))
        primes = [self.sieve.nth_prime(i) for i in indices]
        for idx, p in zip(indices, primes):
            self.assertTrue(_is_prime(p), f"nth_prime({idx}) = {p} is not prime")
        for a, b in zip(primes, primes[1:]):
            self.assertLess(a, b, "nth_prime must be strictly increasing")

    def test_sieve_base_case(self) -> None:
        self.assertEqual(2, self.sieve.nth_prime(0))

    def test_sieve_small_n_sequence(self) -> None:
        # Covers the Rosser boundary at n=5, where rossers_bounds switches
        # from the n<5 special case to the formula.
        self.assertEqual(
            [2, 3, 5, 7, 11, 13, 17],
            [self.sieve.nth_prime(n) for n in range(7)],
        )

    def test_sieve_happy_path_small(self) -> None:
        self._assert_fuzz(low=0, high=1_000, sample_size=10, seed=1)

    def test_sieve_happy_path_medium(self) -> None:
        self._assert_fuzz(low=1_000, high=10_000, sample_size=10, seed=2)

    def test_sieve_happy_path_large(self) -> None:
        self._assert_fuzz(low=10_000, high=100_000, sample_size=10, seed=3)

    def test_sieve_one_millionth_prime(self) -> None:
        self.assertEqual(15_485_867, self.sieve.nth_prime(1_000_000))

    def test_sieve_ten_millionth_prime(self) -> None:
        self.assertEqual(179_424_691, self.sieve.nth_prime(10_000_000))

    def test_sieve_invalid_n(self) -> None:
        for bad in ("noodle", None, 3.0, True, False, -1):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    self.sieve.nth_prime(bad)

    def test_sieve_helper_small_cases(self) -> None:
        self.assertEqual(
            [],
            self.sieve.sieve(1)
        )
        self.assertEqual(
            [2],
            self.sieve.sieve(2)
        )
        self.assertEqual(
            [2, 3, 5, 7],
            self.sieve.sieve(10)
        )
        self.assertEqual(
            [2, 3, 5, 7, 11, 13, 17, 19, 23, 29],
            self.sieve.sieve(30),
        )

    def test_sieve_extreme_case(self) -> None:
        """
        not required, just a fun challenge
        """

        self.assertEqual(2_038_074_751, self.sieve.nth_prime(100_000_000))
