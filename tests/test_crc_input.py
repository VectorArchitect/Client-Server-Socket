import unittest

from crc_input import append_crc, encode_request_data, verify_packet


class EncodeRequestDataTests(unittest.TestCase):
    def test_encodes_six_unsigned_bytes(self):
        self.assertEqual(
            encode_request_data([0, 1, 2, 127, 254, 255]),
            bytes([0, 1, 2, 127, 254, 255]),
        )

    def test_rejects_wrong_number_of_fields(self):
        for values in ([0] * 5, [0] * 7):
            with self.subTest(length=len(values)):
                with self.assertRaisesRegex(ValueError, "exactly six"):
                    encode_request_data(values)

    def test_rejects_values_below_byte_range(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 255"):
            encode_request_data([0, 1, 2, 3, 4, -1])

    def test_rejects_values_above_byte_range(self):
        with self.assertRaisesRegex(ValueError, "between 0 and 255"):
            encode_request_data([0, 1, 2, 3, 4, 256])

    def test_rejects_non_integer_values(self):
        for value in (1.5, "2", True):
            with self.subTest(value=value):
                with self.assertRaisesRegex(TypeError, "must be an integer"):
                    encode_request_data([0, 1, 2, 3, 4, value])

    def test_encoded_request_can_be_crc_verified(self):
        data = encode_request_data([0xA1, 0x03, 0x00, 0x0F, 0x00, 0x0F])
        packet = append_crc(data)

        _, _, valid = verify_packet(packet)

        self.assertTrue(valid)
        self.assertEqual(len(packet), 8)


if __name__ == "__main__":
    unittest.main()
