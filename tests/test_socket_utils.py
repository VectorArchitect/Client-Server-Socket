import unittest

from socket_utils import recv_exact


class ChunkedSocket:
    """Minimal socket test double that returns predefined chunks."""

    def __init__(self, chunks):
        self.chunks = list(chunks)
        self.requested_sizes = []

    def recv(self, size):
        self.requested_sizes.append(size)
        if not self.chunks:
            return b""

        chunk = self.chunks.pop(0)
        if len(chunk) > size:
            self.chunks.insert(0, chunk[size:])
            return chunk[:size]
        return chunk


class RecvExactTests(unittest.TestCase):
    def test_combines_fragmented_tcp_reads(self):
        sock = ChunkedSocket([b"ab", b"cde", b"fgh"])

        self.assertEqual(recv_exact(sock, 6), b"abcdef")
        self.assertEqual(sock.requested_sizes, [6, 4, 1])
        self.assertEqual(sock.chunks, [b"gh"])

    def test_returns_empty_bytes_when_peer_closes_before_packet(self):
        self.assertEqual(recv_exact(ChunkedSocket([]), 4), b"")

    def test_rejects_a_truncated_packet(self):
        sock = ChunkedSocket([b"ab"])

        with self.assertRaisesRegex(ConnectionError, "2 of 4"):
            recv_exact(sock, 4)

    def test_zero_length_read_does_not_touch_socket(self):
        sock = ChunkedSocket([b"data"])

        self.assertEqual(recv_exact(sock, 0), b"")
        self.assertEqual(sock.requested_sizes, [])
        self.assertEqual(sock.chunks, [b"data"])

    def test_negative_length_is_rejected(self):
        with self.assertRaises(ValueError):
            recv_exact(ChunkedSocket([]), -1)

    def test_non_integer_length_is_rejected(self):
        with self.assertRaises(TypeError):
            recv_exact(ChunkedSocket([]), "4")


if __name__ == "__main__":
    unittest.main()
