"""Small helpers for reading framed data from TCP byte streams."""


def recv_exact(sock, size):
    """Read exactly size bytes from a socket.

    TCP does not preserve application message boundaries, so one recv call
    is not guaranteed to return a complete packet. An empty result means the
    peer closed the connection before sending any bytes; a partial packet
    raises ConnectionError rather than being passed to a parser.
    """
    if not isinstance(size, int):
        raise TypeError("size must be an integer")
    if size < 0:
        raise ValueError("size must be non-negative")
    if size == 0:
        return b""

    chunks = []
    received = 0

    while received < size:
        chunk = sock.recv(size - received)
        if not chunk:
            if received == 0:
                return b""
            raise ConnectionError(
                f"Connection closed after {received} of {size} expected bytes"
            )

        chunks.append(chunk)
        received += len(chunk)

    return b"".join(chunks)
