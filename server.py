from socket import *


# Dictionary of domain names
DOMAIN_NAMES = {
    "google.com": ["A", "IN", "260", ["192.165.1.1", "192.165.1.10"]],
    "youtube.com": ["A", "IN", "160", ["192.165.1.2"]],
    "uwaterloo.ca": ["A", "IN", "160", ["192.165.1.3"]],
    "wikipedia.org": ["A", "IN", "160", ["192.165.1.4"]],
    "amazon.ca": ["A", "IN", "160", ["192.165.1.5"]]
}

def get_header_server(DNSrequest, domain_name):
    """Function to get the header of the DNS response"""
    # Flags
    final_message = "1" + "0000" + "1" + "0" + "0" + "0" + "0" + "000" + "000"
    # QDCOUNT
    final_message += "0000000000000001"
    # ANCOUNT
    final_message += bin(len(DOMAIN_NAMES[domain_name][3]))[2:].zfill(16)
    # NSCOUNT
    final_message += "0000000000000000"
    # ARCOUNT
    final_message += "0000000000000000"
    # Convert into hexadecimal
    hexadecimal_header = ""
    for i in range(0, len(final_message), 8):
        hexadecimal_header += format(int(final_message[i:i + 8], 2), '02x') + " "
    # ID
    hexadecimal_header = DNSrequest[:2] + " " + DNSrequest[2:4] + " " + hexadecimal_header
    return hexadecimal_header


def get_query(DNSrequest):
    # QNAME
    Qname = DNSrequest[24:-8]
    i = 2
    label_length = int(Qname[:2])
    domain = ""
    #
    while i < len(Qname):
        for j in range(i, i + (2 * label_length), 2):
            # Obtain the letters of the domain name
            domain += bytes.fromhex(Qname[j:j + 2]).decode('utf-8')

        # Obtain the length of the next label
        i += 2 * label_length
        label_length = int(Qname[i:i + 2])
        if label_length != 0:
            domain += "."
        i += 2
    Qtype = DNSrequest[-8:-4]
    Qclass = DNSrequest[-4:]
    return domain, Qtype, Qclass


def get_answer_section(Qtype, Qclass, TTL, IP):
    final_message = ""
    # NAME
    final_message += "c0 0c "
    # TYPE and CLASS
    binary_type = bin(int(Qtype))[2:].zfill(16)
    final_message += format(int(binary_type[:8], 2), '02x') + " " + format(int(binary_type[8:], 2), '02x') + " "
    binary_class = bin(int(Qclass))[2:].zfill(16) 
    final_message += format(int(binary_class[:8], 2), '02x') + " " + format(int(binary_class[8:], 2), '02x') + " "
    # TTL
    binary_TTL = bin(int(TTL))[2:].zfill(32)
    final_message += format(int(binary_TTL[:8], 2), '02x') + " " + format(int(binary_TTL[8:16], 2), '02x') + " " + format(int(binary_TTL[16:24], 2), '02x') + " " + format(int(binary_TTL[24:], 2), '02x') + " "
    # RDLENGTH
    final_message += "00 04 "
    # RDATA
    numbers = IP.split(".")
    for number in numbers:
        final_message += format(int(bin(int(number))[2:].zfill(4), 2), '02x') + " "
    return final_message


def main():
    serverIP = "127.0.0.1"
    serverPort = 10125
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    serverSocket.bind((serverIP, serverPort))
    print("The server is ready to receive")
    while True:
        message, clientAddress = serverSocket.recvfrom(2048)
        DNSrequest = message.decode()
        print("Request:")
        print(DNSrequest)
        DNSrequest = DNSrequest.replace(" ", "")
        domain, type, Qclass = get_query(DNSrequest)
        found = False
        IP = []
        TTL = ""
        # Search for the domain name in the dictionary
        for key in DOMAIN_NAMES:
            if key == domain:
                found = True
                # Obtain the information of the domain name
                TTL = DOMAIN_NAMES[key][2]
                if len(DOMAIN_NAMES[key][3]) <= 1:
                    # Obtain the IP addresses of the domain name
                    IP.append(DOMAIN_NAMES[key][3][0])
                else:
                    for i in range(len(DOMAIN_NAMES[key][3])):
                        IP.append(DOMAIN_NAMES[key][3][i])
                break
        if found == False:
            DNSresponse = ""
            serverSocket.sendto(DNSresponse.encode(), clientAddress)
        else:
            # Send a response to the client for every IP address
            # Get the header of the DNS request
            DNSresponse = get_header_server(DNSrequest, domain)
            # Get the previous question section of the DNS request
            for i in range(0, (len(DNSrequest) - len(DNSresponse.replace(" ", ""))), 2):
                DNSresponse += DNSrequest[24 + i: 26 + i] + " "
            # Add the answer section
            for element in IP:
                DNSresponse += get_answer_section(type, Qclass, TTL, element)
            # Send the response to the client
            serverSocket.sendto(DNSresponse[:-1].encode(), clientAddress)
            print("Response:")
            print(DNSresponse)


if __name__ == "__main__":
    main()