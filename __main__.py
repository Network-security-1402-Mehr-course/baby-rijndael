from numpy import arange, ndarray, uint8, uint16

from baby_rijndael import BabyRijndael

if __name__ == "__main__":
    br = BabyRijndael(ndarray((2,), uint8, bytes((6 * 16 + 11, 5 * 16 + 13))))

    block_count = 2**16
    inp = ndarray(
        (
            block_count,
            2,
        ),
        uint8,
    )

    for i in range(block_count):
        inp[i] = (i // 256, i % 256)

    print(br.encrypt(inp))
    print(inp)
    print(inp[(2 * 16 + 12) * 256 + 10 * 16 + 5])
