from functools import reduce
from typing import Callable, Self


class BabyRijndael:
    "https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=f7adc1d021ade59b4cb8d68d45a82b07e8ad737b"

    Col = list[int]
    State = list[Col]
    Key = State

    block_size = 2

    s_table = [10, 4, 3, 11, 8, 14, 2, 12, 5, 7, 6, 15, 0, 1, 9, 13]

    t = [
        [1, 1, 1, 0, 0, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1, 0, 0, 1],
        [0, 1, 0, 1, 1, 1, 0, 1],
        [0, 0, 1, 0, 1, 1, 1, 0],
        [0, 0, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 1, 1, 0, 1, 0],
        [1, 1, 0, 1, 0, 1, 0, 1],
    ]

    ti = [
        [0, 1, 1, 0, 0, 1, 1, 1],
        [0, 0, 1, 1, 1, 0, 1, 0],
        [1, 0, 0, 0, 0, 1, 0, 1],
        [0, 1, 0, 0, 1, 0, 1, 1],
        [0, 1, 1, 1, 0, 1, 1, 0],
        [1, 0, 1, 0, 0, 0, 1, 1],
        [0, 1, 0, 1, 1, 0, 0, 0],
        [1, 0, 1, 1, 0, 1, 0, 0],
    ]

    @classmethod
    def xor(cls, *cols: Col) -> Col:
        return reduce(lambda x, y: [i ^ j for i, j in zip(x, y)], cols, [0, 0])

    @classmethod
    def reverse(cls, col: Col) -> Col:
        return list(reversed(col))

    @classmethod
    def mat_mult(cls, a: list[list[int]], b: list[list[int]]):
        ars = len(a[0])

        bcs = len(b)
        brs = len(b[0])

        ans = [[0 for _ in range(ars)] for _ in range(bcs)]

        for arow in range(ars):
            for bcol in range(bcs):
                for i in range(brs):
                    ans[bcol][arow] += a[i][arow] * b[bcol][i]

        return ans

    @classmethod
    def mat_mod(cls, a: list[list[int]], base: int):
        return [[i % base for i in j] for j in a]

    @classmethod
    def s(cls, col: Col) -> Col:
        return [cls.s_table[i] for i in col]

    @classmethod
    def y(cls, i: int) -> Col:
        return [2 ** (i - 1), 0]

    @classmethod
    def r(
        cls, i: int
    ) -> Callable[[Self,], None]:
        def round(br: BabyRijndael):
            br.sub_bytes()
            br.shift_rows()
            if i < 4:
                br.mix_columns()

            br.apply_round_key(i)

        return round

    @classmethod
    def ri(
        cls, i: int
    ) -> Callable[[Self,], None]:
        def round_inverse(br: BabyRijndael):
            br.apply_round_key(i)
            if i < 4:
                br.mix_columns_inverse()

            br.shift_rows()
            br.sub_bytes_inverse()

        return round_inverse

    def __init__(self, state: State, key: Key):
        assert len(state) == len(key) == self.block_size
        self.state = state
        self.key = key

    def w(self, i: int) -> Col:
        if i < 2:
            return self.key[i]

        if i % 2:
            return self.xor(self.w(i - 2), self.w(i - 1))

        return self.xor(
            self.w(i - 2),
            self.s(self.reverse(self.w(i - 1))),
            self.y(i // 2),
        )

    def k(self, i: int) -> Key:
        return [self.w(2 * i), self.w(2 * i + 1)]

    def sub_bytes(self):
        self.state = [[self.s_table[i] for i in j] for j in self.state]

    def sub_bytes_inverse(self):
        self.state = [[self.s_table.index(i) for i in j] for j in self.state]

    def shift_rows(self):
        self.state[0][1], self.state[1][1] = self.state[1][1], self.state[0][1]

    def state_bit_column(self, col: Col) -> list[int]:
        return [1 if 2**j & i else 0 for i in col for j in reversed(range(4))]

    def state_bit_matrix(self) -> list[list[int]]:
        return [self.state_bit_column(col) for col in self.state]

    def set_state_from_bit_matrix(self, bit_matrix: list[list[int]]):
        self.state = [[0 for _ in range(2)] for _ in range(2)]
        for i in range(2):
            for j in range(8):
                self.state[i][j // 4] += bit_matrix[i][j] * 2 ** ((7 - j) % 4)

    def mix_columns(self):
        self.set_state_from_bit_matrix(
            self.mat_mod(
                self.mat_mult(self.t, self.state_bit_matrix()),
                2,
            )
        )

    def mix_columns_inverse(self):
        self.set_state_from_bit_matrix(
            self.mat_mod(
                self.mat_mult(self.ti, self.state_bit_matrix()),
                2,
            )
        )

    def apply_round_key(self, i: int):
        self.state = [self.xor(self.state[j], self.k(i)[j]) for j in range(2)]

    def encrypt(self):
        self.apply_round_key(0)
        for i in range(1, 5):
            self.r(i)(self)

    def decrypt(self):
        for i in reversed(range(1, 5)):
            self.ri(i)(self)

        self.apply_round_key(0)
