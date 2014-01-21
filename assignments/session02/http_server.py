import socket
import sys
import os

# http server constants
SERVER_IP = '127.0.0.1'
SERVER_PORT = 10000
BUFFER_SIZE = 1024
SERVER_ROOT = 'webroot'
CRLF = '\r\n'


def response_ok(body="this is a pretty minimal response", mimetype="text/plain"):
    """returns a basic HTTP response"""
    resp = []
    resp.append("HTTP/1.1 200 OK")
    resp.append("Content-Type: %s" % mimetype)
    resp.append("")
    resp.append(body)
    return CRLF.join(resp)


def get_mimetype(file_extension):
    """returns the appropriate mime type for a given file extensions"""
    mime_types = {
        '.html': 'text/html',
          '.py': 'text/x-python',
         '.txt': 'text/plain',
         '.jpg': 'image/jpeg',
         '.png': 'image/png',
          '.js': 'text/javascript',
         '.css': 'text/css'
    }
    return mime_types.get(file_extension, 'Unknown')


def resolve_uri(uri):
    """
    handles looking up resources on disk using the URI
    Returns (body, mimetype) or raises ValueError if not found
    
    """

    # map the pathname represented by the URI to a filesystem location    
    path = os.path.join(SERVER_ROOT, uri.lstrip('/'))

    if os.path.exists(path):
        # the requested uri does in fact exist on the file system
        
        if os.path.isdir(path):
            # uri is a directory; body should contain file listing
            body = CRLF.join(os.listdir(path))
            mimetype = get_mimetype('.txt')
            
        elif os.path.isfile(path):
            # uri is a file; body should contain file contents
            f = open(path, 'r')
            body = f.read()
            f.close() 

            # and mimetype depends on file extension
            filename = os.path.split(path)[1]
            extension = os.path.splitext(filename)[1]
            mimetype = get_mimetype(extension)
        else:
            # path exists but is neither directory nor file (Wut?)
            body = None
            mimetype = None
        return (body, mimetype)

    else:
        raise ValueError("File not found on Server") 



def response_not_found():
    """returns a 404 code - File not found """
    resp = []
    resp.append("HTTP/1.1 404 Not Found")
    resp.append("")
    return CRLF.join(resp)

    
def response_method_not_allowed():
    """returns a 405 Method Not Allowed response"""
    resp = []
    resp.append("HTTP/1.1 405 Method Not Allowed")
    resp.append("")
    return CRLF.join(resp)


def parse_request(request):
    first_line = request.split(CRLF, 1)[0]
    method, uri, protocol = first_line.split()
    if method != "GET":
        raise NotImplementedError("We only accept GET")
    print >>sys.stderr, 'request is okay'
    return uri


def server():
    address = (SERVER_IP, SERVER_PORT)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    print >>sys.stderr, "making a server on %s:%s" % address
    sock.bind(address)
    sock.listen(1)
    
    try:
        while True:
            print >>sys.stderr, 'waiting for a connection'
            conn, addr = sock.accept() # blocking
            try:
                print >>sys.stderr, 'connection - %s:%s' % addr
                request = ""
                while True:
                    data = conn.recv(BUFFER_SIZE)
                    request += data
                    if len(data) < BUFFER_SIZE or not data:
                        break
                try:
                    # parse the request to get a URI
                    uri = parse_request(request)
                    # with the URI, find the appropriate resource on disk
                    body, mimetype = resolve_uri(uri)
                except ValueError:
                        response = response_not_found()
                except NotImplementedError:
                    response = response_method_not_allowed()
                else:
                    response = response_ok(body, mimetype)

                print >>sys.stderr, 'sending response'
                conn.sendall(response)
            finally:
                conn.close()
            
    except KeyboardInterrupt:
        sock.close()
        return


if __name__ == '__main__':
    server()
    sys.exit(0)
