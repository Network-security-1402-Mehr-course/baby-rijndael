from baby_rijndael import BabyRijndael

if __name__ == "__main__":
    br = BabyRijndael([[2, 12], [10, 5]], [[6, 11], [5, 13]])

    br.encrypt()
    print(br.state)

    br.decrypt()
    print(br.state)
