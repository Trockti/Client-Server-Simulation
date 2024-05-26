from socket import *
import random


def get_header(query_type):
    final_message = ""
    for _ in range(16):
        final_message += ''.join(str(random.randint(0, 1)))
    final_message += query_type + "0000" + "1" + "0" + "0" + "0" + "0" + "000" + "000"
    final_message += "0000000000000001"
    final_message += "0000000000000000"
    final_message += "0000000000000000"
    final_message += "0000000000000000"
    # Convert each line into hexadecimal
    hexadecimal_header = ""
    for i in range(0, len(final_message), 8):
        hexadecimal_header += format(int(final_message[i:i + 8], 2), '02x') + " "
    return hexadecimal_header


def get_question(domain):
    domain = domain.lower()
    # Get the QNAME
    labels = domain.split(".")
    encoded_name = ""
    for label in labels:
        length = len(label)
        # Convert length to hexadecimal
        hex_length = format(length, '02X')
        encoded_name += hex_length + " "
        # Encode label
        label = label.encode()
        for byte in label:
            encoded_name += format(byte, '02x') + " "
    encoded_name += "00" + " "
    # Get the QTYPE
    encoded_name += "00 01" + " "
    # Get the QCLASS
    encoded_name += "00 01"
    return encoded_name


def modifiedMessage_decoded(modifiedMessage):
    message_no_spaces = modifiedMessage.split(" ")
    # Get the domain name
    domain_name = ""
    index = 12
    while message_no_spaces[index] != "00":
        int_length = int(message_no_spaces[index], 16)
        for i in range(1, int_length + 1):
            domain_name += bytes.fromhex(message_no_spaces[index + i]).decode("utf-8")
        domain_name += "."
        index += int_length + 1
    # Remove the last dot
    domain_name = domain_name[:-1]
    index += 5

    # Get the data from the Answer section
    lines = []
    while message_no_spaces[index] != "0c":
        # Get the Type
        index += 2
        qtype = message_no_spaces[index]
        index += 1
        qtype += message_no_spaces[index]
        if qtype == "0001":
            qtype = "A"
        elif qtype == "0002":
            qtype = "NS"
        elif qtype == "0003":
            qtype = "MD"
        elif qtype == "0004":
            qtype = "MF"
        # Get the Class
        index += 2
        qclass = message_no_spaces[index - 1] + message_no_spaces[index]
        if qclass == "0001":
            qclass = "IN"
        # Get the TTL
        index += 4
        ttl = message_no_spaces[index - 3] + message_no_spaces[index - 2] + message_no_spaces[index - 1] + \
              message_no_spaces[index]
        ttl = int(ttl, 16)
        # Get the RDLENGTH
        index += 2
        rdlength = message_no_spaces[index - 1] + message_no_spaces[index]
        rdlength = int(rdlength, 16)
        # Get the RDATA
        ip = ""
        for _ in range(rdlength):
            index += 1
            rdata = message_no_spaces[index]
            ip += str(int(rdata, 16)) + "."
        ip = ip[:-1]
        index += 1
        lines.append([domain_name, qtype, qclass, ttl, rdlength, ip])
        if index >= len(message_no_spaces):
            break
    return lines


def show_outputlog(parsedMessage):
    for i in range(len(parsedMessage)):
        print(">", parsedMessage[i][0], ": type",
              parsedMessage[i][1], ", class:", parsedMessage[i][2],
              ", TTL:", str(parsedMessage[i][3]), ", addr (" + str(parsedMessage[i][4])
              + ")", parsedMessage[i][5])


def main():
    serverIP = "127.0.0.1"
    serverPort = 10125
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    print("The client is ready to receive")
    while True:
        message = input('Enter Domain Name: ').lower()
        if message == "end":
            clientSocket.close()
            print("Session ended")
            break
        final_message = get_header("0")
        final_message += get_question(message)
        clientSocket.sendto(final_message.encode(), (serverIP, serverPort))
        modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
        if len(modifiedMessage) > 0:
            parsedMessage = modifiedMessage_decoded(modifiedMessage.decode())
            show_outputlog(parsedMessage)
        else:
            print("No response from server")


if __name__ == "__main__":
    main()
