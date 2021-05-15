import hashlib
import json


def crypto_hash(*args):
    """
    Return a SHA-256 hash of the given arguments
    """
    stringified_args = sorted(map(lambda x: json.dumps(x), args))

    joined_data = "".join(stringified_args)

    return hashlib.sha256(joined_data.encode("utf-8")).hexdigest()


def main():
    # print(f"crypto_hash('foo'): {crypto_hash('foo')}")
    # print(f"crypto_hash(1): {crypto_hash(1)}")
    # print(f"crypto_hash([2]]): {crypto_hash([2])}")
    print(
        f"crypto_hash('one', 2, [3]): {crypto_hash('one', 2, [3])}")
    print(
        f"crypto_hash('one', [3], 2): {crypto_hash('one', [3], 2)}")


if __name__ == "__main__":
    main()
