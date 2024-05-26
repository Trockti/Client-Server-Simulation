import os
from datetime import datetime
from socket import *


def get_formated_response(lines):
    HTTPresponse = lines[0] + " " + lines[1] + "\r\n"
    current_datetime = datetime.utcnow()  # Get the current UTC date and time
    formatted_datetime = current_datetime.strftime('%a, %d %b %Y %H:%M:%S GMT')
    HTTPresponse += "Date: " + formatted_datetime + "\r\n"
    HTTPresponse += "Server: " + lines[2] + "\r\n"
    # Only include the Last Modified header if the file exists
    if lines[1] != "404 Not Found":
        HTTPresponse += "Last Modified: " + lines[3] + "\r\n"
    HTTPresponse += "Content-Length: " + lines[4] + "\r\n"
    HTTPresponse += "Content-Type: " + lines[5] + "; charset=" + lines[6] + "\r\n"
    HTTPresponse += "Connection: " + lines[7] + "\r\n"
    if lines[8] != "":
        HTTPresponse += "Content-Language: " + lines[8] + "\r\n"
    HTTPresponse += "\r\n" + lines[9] + "\r\n"
    return HTTPresponse

def get_file_type(file_path):
    # Get the file extension
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lstrip('.')  # Remove leading dot (if present)
    # Define a dictionary mapping common file extensions to file types
    file_type_mapping = {
        'txt': 'Text',
        'csv': 'CSV',
        'json': 'JSON',
        'xml': 'XML',
        'jpg': 'JPEG Image',
        'png': 'PNG Image',
        'pdf': 'PDF Document',
        'ico': 'Icon',
        'html': 'text/html'
    }
    # Determine the file type based on the extension
    file_type = file_type_mapping.get(file_extension.lower(), 'Unknown')
    return file_type


serverIP = "127.0.0.1"
serverPort = 10126
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(1)
print("The server is ready to receive")
while True:
    connectionSocket, addr = serverSocket.accept()
    HTTPrequest = connectionSocket.recv(2048).decode()
    lines = HTTPrequest.split("\n")
    i = 0
    while i < len(lines):
        if lines[i].startswith("GET") \
                or lines[i].startswith("HEAD"):
            index_of_whitespace = lines[i].find(' ')
            filename = ""
            j = index_of_whitespace + 2
            while lines[i][j] != ' ':
                filename += lines[i][j]
                j += 1
            j += 1
            http_version = ""
            while j < len(lines[i]) - 1:
                http_version += lines[i][j]
                j += 1
        if lines[i].startswith("Connection"):
            index_of_whitespace = lines[i].find(' ')
            j = index_of_whitespace + 1
            connection_type = ""
            while j < len(lines[i]) - 1:
                connection_type += lines[i][j]
                j += 1
        i += 1

    cwd = os.getcwd()
    path = ""
    for root, dirs, files in os.walk(cwd):
        if filename in files:
            path = os.path.join(root, filename)

    try:
        with open(path, "r") as file:
            # Read the entire contents of the file
            file_contents = file.read()
            message_code = "200 OK"
            modify_time = os.path.getmtime(path)
    except:
        with open("404Notfound.html", "r") as file:
            path = "404Notfound.html"
            file_contents = file.read()
            message_code = "404 Not Found"
            #The modify time is not included
            modify_time = ""
    charset = ""
    index_charset = file_contents.find("charset=")
    i = index_charset + 9
    while file_contents[i] != '"':
        charset += file_contents[i]
        i += 1
    accepted_language = ""
    if message_code != "404 Not Found":
        index_language = file_contents.find("lang=")
        i = index_language + 6
        while file_contents[i] != '"':
            accepted_language += file_contents[i]
            i += 1
    if lines[0].startswith("GET"):
        body = file_contents
    else:
        body = ""
    if isinstance(modify_time, float):
        original_time = str(datetime.fromtimestamp(modify_time))
        parsed_time = datetime.strptime(original_time, '%Y-%m-%d %H:%M:%S.%f')
        modify_time = parsed_time.strftime('%a, %d %b %Y %H:%M:%S GMT')
    lines = (http_version,
             message_code,
             "webserver",
             modify_time,
             str(len(file_contents)),
             get_file_type(path),
             charset,
             connection_type,
             accepted_language,
             body)
    HTTPresponse = get_formated_response(lines)
    print(HTTPresponse)
    connectionSocket.send(HTTPresponse.encode())
