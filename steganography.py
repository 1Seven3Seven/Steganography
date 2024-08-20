from typing import Generator
import io

ZERO_WIDTH_SPACE = "​"


def can_encode(text: bool, hidden_text: str, encoding: str = "utf-8") -> bool:
    """
    Returns true if the hidden text can be encoded in the text.
    """

    hidden_text_bytes = hidden_text.encode(encoding)
    required_chars = len(hidden_text_bytes) * 8 + 1

    return len(text) >= required_chars


def iter_bits_of_str(str_: str, encoding: str = "utf-8") -> Generator[bool, None, None]:
    for byte in str_.encode(encoding):
        bits = f"{byte:08b}"
        for bit in bits:
            yield bool(int(bit))


def write_steganography(text: str, hidden_text: str, encoding: str = "utf-8",
                        hidden_char: str = ZERO_WIDTH_SPACE) -> str:
    """
    Hides the hidden text within text by encoding as utf-8 and dispersing the bits as zero width spaces inbetween letters.
    """

    if not can_encode(text, hidden_text):
        raise ValueError("Given text is not long enough to contain hidden text")

    string_buffer = io.StringIO()

    text_chars = iter(text)
    hidden_text_bits = iter_bits_of_str(hidden_text, encoding=encoding)

    for char in text_chars:
        string_buffer.write(char)

        try:
            bit = next(hidden_text_bits)
        except StopIteration:
            break

        if bit:
            string_buffer.write(hidden_char)

    try:
        next(hidden_text_bits)
    except StopIteration:
        pass
    else:
        raise ValueError("Given text is not long enough to contain hidden text")

    string_buffer.write("".join(text_chars))

    return string_buffer.getvalue()


def read_steganography(text: str, encoding: str = "utf-8", hidden_char: str = ZERO_WIDTH_SPACE) -> str:
    """
    Reads the hidden text from the text by decoding the hidden char stored between chars.
    """

    hidden_bytes = bytes()
    current_byte = ""

    text_chars = enumerate(text)
    for index, char in text_chars:  # Consumes a normal char
        if index + 1 >= len(text):
            break

        if text[index + 1] == hidden_char:
            current_byte += "1"
            next(text_chars)  # Consume the hidden char
        else:
            current_byte += "0"

        # Exit if a null byte is received
        if current_byte == "00000000":
            break

        if len(current_byte) == 8:
            hidden_bytes += int(current_byte, 2).to_bytes(1)
            current_byte = ""

    return hidden_bytes.decode(encoding)


def test():
    text = "This is some long text to allow for encoding"
    secret = "abcd"

    text_with_secret = write_steganography(text, secret, hidden_char="_")
    print(text_with_secret)

    extracted_secret = read_steganography(text_with_secret, hidden_char="_")
    print(extracted_secret)


def main():
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument()

    args = parser.parse_args()


if __name__ == "__main__":
    main()
