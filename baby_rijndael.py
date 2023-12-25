from functools import cache

from numpy import array, flip, fromiter, ndarray, packbits, uint8, unpackbits
from numpy.typing import NDArray


class BabyRijndael:
    "https://citeseerx.ist.psu.edu/document?repid=rep1&type=pdf&doi=f7adc1d021ade59b4cb8d68d45a82b07e8ad737b"

    BLOCK_BYTES = 2
    KEY_BYTES = BLOCK_BYTES

    @staticmethod
    def reverse_column(column: uint8) -> uint8:
        return uint8((column % 16 << 4) + (column // 16))

    @staticmethod
    def y(i: int):
        return 2 ** (i + 3)

    s_box_table = [10, 4, 3, 11, 8, 14, 2, 12, 5, 7, 6, 15, 0, 1, 9, 13]
    t = array(
        [
            [1, 1, 1, 0, 0, 0, 1, 0],
            [0, 1, 1, 1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1, 0, 0, 1],
            [0, 1, 0, 1, 1, 1, 0, 1],
            [0, 0, 1, 0, 1, 1, 1, 0],
            [0, 0, 0, 1, 0, 1, 1, 1],
            [1, 0, 0, 1, 1, 0, 1, 0],
            [1, 1, 0, 1, 0, 1, 0, 1],
        ],
        dtype=uint8,
    )

    @classmethod
    @cache
    def s(cls, column: uint8) -> uint8:
        return uint8(
            (cls.s_box_table[int(column) // 16] << 4)
            + cls.s_box_table[int(column) % 16]
        )

    def __init__(self, key: NDArray[uint8]) -> None:
        assert key.shape == (self.KEY_BYTES,)

        self.key = key

    def w(self, i: int) -> uint8:
        if i < 2:
            return self.key[i]

        if i % 2:
            return self.w(i - 2) ^ self.w(i - 1)

        return (
            self.w(i - 2) ^ self.s(self.reverse_column(self.w(i - 1))) ^ self.y(i // 2)
        )

    def k(self, i: int) -> NDArray[uint8]:
        return ndarray(
            (self.BLOCK_BYTES,),
            uint8,
            bytes(self.w(2 * i + j) for j in range(self.BLOCK_BYTES)),
        )

    def apply_sbox(self, blocks: NDArray[uint8]):
        for i in range(len(blocks)):
            blocks[i] = fromiter((self.s(j) for j in blocks[i]), uint8)

    def shift_rows(self, blocks: NDArray[uint8]):
        second_rows = ndarray(blocks.shape, uint8, blocks % 16)
        blocks -= second_rows
        blocks += flip(second_rows, 1)

    def mix_columns(self, blocks: NDArray[uint8]):
        temp = unpackbits(blocks.reshape(-1, 2, 1), axis=2)
        temp @= self.t
        temp %= 2
        temp = packbits(temp, axis=2)
        temp = temp.reshape(-1, 2)
        for i, col in enumerate(temp):
            blocks[i] = col

    def apply_round(
        self, blocks: NDArray[uint8], i: int, omit_column_mix: bool = False
    ):
        self.apply_sbox(blocks)
        self.shift_rows(blocks)
        if not omit_column_mix:
            self.mix_columns(blocks)

        blocks ^= self.k(i)

    def encrypt(self, blocks: NDArray[uint8]):
        assert blocks.ndim == 2 and blocks.shape[1] == self.BLOCK_BYTES

        blocks ^= self.k(0)

        for i in range(1, 4):
            self.apply_round(blocks, i)

        self.apply_round(blocks, 4, True)
