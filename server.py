import socket

SERVER_NAME = "AppuServer/1.0"
STATUS_CODES = {
    200: "OK",
    301: "Moved Permanently",
    400: "Bad Request",
    404: "Not Found",
    405: "Method Not Allowed",
    500: "Internal Server Error",
    501: "Not Implemented",
}


def run(addr, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((addr, port))
    s.listen()
    print(f"Listening on {addr}:{port}")

    while True:
        try:
            conn, remote = s.accept()
            remote_host, remote_port = remote
            print(f"Connection from {remote_host}:{remote_port}")

            response = reply(conn)

            if response == b"":
                response = craft_response(
                    200, {}, "<center><h1>Closing connection...</h1></center>"
                )
                conn.sendall(response)
                conn.close()
                break

            conn.sendall(response)
            conn.close()

        except KeyboardInterrupt:
            conn.close()
            break

        except OSError as e:
            print(e)
            conn.close()

        except Exception as e:
            print(e)
            response = raise_error(500)
            conn.sendall(response)
            conn.close()


def reply(conn):
    raw_request = conn.recv(1024).decode("utf-8")
    method, path, version, headers = parse_request(raw_request)

    if path == "/close":
        return b""

    if method not in ["GET", "HEAD"]:
        return raise_error(405)

    # Redirect to index.html if the path is /
    if path == "/":
        return craft_response(301, {"Location": "index.html"}, "")

    # Return only the headers if the method is HEAD
    head = method == "HEAD"

    # Check if the file exists
    file_path = "/" + path[1:]
    # if not os.path.isfile(file_path):
    #     return raise_error(404)
    try:
        with open(file_path, "rb") as f:
            pass
    except OSError:
        return raise_error(404)

    # Set MIME type
    extension = path.split(".")[-1]
    mime = "text/html" if extension == "html" else "other"

    # Read file (text or binary)
    if mime.split("/")[0] == "text":
        with open(file_path, "r") as f:
            message = f.read()
    else:
        with open(file_path, "rb") as f:
            message = f.read()

    # Create response headers
    response_headers = {
        "Content-Type": mime,
        # "Content-Length": str(os.path.getsize(file_path)),
        "Content-Length": str(len(message)),
        # "Last-Modified": datetime.fromtimestamp(
        #     os.path.getmtime(file_path)
        # ).strftime("%a, %d %b %Y %H:%M:%S %Z"),
    }

    return craft_response(200, response_headers, message if not head else "")


def parse_request(raw_request):
    """Parses the request and returns it as a Request object."""

    try:
        request_line, *headers = raw_request.splitlines()
        method, path, version = request_line.split()
    except ValueError:
        method, path, version = "ERROR", "Method not supported", "HTTP/1.0"
        headers = []

    # headers = {
    #     k.strip(): v.strip() for k, v in (header.split(":", 1) for header in headers)
    # }

    # for header in headers:
    #     # To get away with the colon in the value of Host header
    #     key, value = header.split(":")[0], ":".join(header.split(":")[1:])
    #     headers[key] = value

    return (method, path, version, headers)


def raise_error(status):
    """Processes an error and returns the response."""

    message = f"<h1>Error {status}</h1><p>{STATUS_CODES[status]}</p>"

    return craft_response(
        status,
        {
            "Content-Type": "text/html",
            "Content-Length": str(len(message)),
        },
        message,
    )


def craft_response(status, headers, body):
    """Creates a response from a status code and a body."""

    # Add default headers
    headers["Connection"] = "close"
    # headers["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S %Z")
    headers["Server"] = SERVER_NAME

    # Add status line and headers to response
    response = f"HTTP/1.0 {status} {STATUS_CODES[status]}\r\n"
    response += "\r\n".join([f"{key}: {value}" for key, value in headers.items()])

    # Add an empty line to separate headers from body
    response += "\r\n\r\n"

    # Add body to response. Body can be a string if it is a text file or bytes if it is a binary file.
    if isinstance(body, str):
        response += body
        response = response.encode("UTF-8")
    else:
        response = response.encode("UTF-8") + body

    return response
