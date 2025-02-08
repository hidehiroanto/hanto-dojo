#!/usr/bin/exec-suid -- /usr/local/bin/scapy -c

author_note = '''
Note from the author:

This challenge was originally about some other vulnerable scapy features.
However, designing the scenario for this challenge was so awkward that I procrastinated finishing this for a long time.
Until suddenly, I found an even cooler vulnerability, so I discarded most of my other unoriginal ideas.
Anyway, this is an interactive Build-A-Packet-Bear program where you can craft and send bear-themed packets.
It's currently broken btw, it often hangs when you try to add a part, and occasionally the other commands hang too.
Even though it should not affect your ability to get the flag, please contact me if you have any suggestions to fix this.
If you are clever, you should already be able to read the flag by the time you see this message.
'''

global bear_parts_dir, bear_parts
bear_parts_dir = os.path.join('/challenge', 'bear_parts')
bear_parts = {f: open(os.path.join(bear_parts_dir, f), 'rb').read() for f in os.listdir(bear_parts_dir)}

def bear_handler(p):
    from scapy.sendrecv import sendp
    from scapy.layers.l2 import Ether
    from scapy.layers.inet import IP, TCP
    from scapy.packet import Raw

    if 'IP' in p and 'TCP' in p:
        if p['TCP'].dport == 80:
            if p['TCP'].flags == 'S':
                sendp(
                    Ether() /
                    IP(src=p['IP'].dst, dst=p['IP'].src) /
                    TCP(sport=p['TCP'].dport, dport=p['TCP'].sport, flags='SA', seq=0, ack=p['TCP'].seq + 1 & (1 << 32) - 1)
                )
            elif p[TCP].flags == 'A':
                sendp(
                    Ether() /
                    IP(src=p['IP'].dst, dst=p['IP'].src) /
                    TCP(sport=p['TCP'].dport, dport=p['TCP'].sport, flags='PA', seq=p['TCP'].ack, ack=p['TCP'].seq + 1 & (1 << 32) - 1) /
                    Raw(load=b'START')
                )
            elif p['TCP'].flags == 'PA':
                lines = p['Raw'].load.splitlines()
                payload = b'NONE'
                if lines[0] == b'ADD':
                    bear.append(bear_parts[lines[1].decode()])
                    payload = b'CONTINUE'
                elif lines[0] == b'CLEAR':
                    bear.clear()
                    payload = b'CLEARED'
                elif lines[0] == b'PRINT':
                    payload = b'BEAR\n' + b'\n'.join(bear)
                sendp(
                    Ether() /
                    IP(src=p['IP'].dst, dst=p['IP'].src) /
                    TCP(sport=p['TCP'].dport, dport=p['TCP'].sport, flags='PA', seq=p['TCP'].ack, ack=p['TCP'].seq + 1 & (1 << 32) - 1) /
                    Raw(load=payload)
                )
        elif p['TCP'].dport == 1337:
            if p['TCP'].flags == 'SA':
                sendp(
                    Ether() /
                    IP(src=p['IP'].dst, dst=p['IP'].src) /
                    TCP(sport=p['TCP'].dport, dport=p['TCP'].sport, flags='A', seq=p.ack, ack=p.seq + 1 & (1 << 32) - 1)
                )
            elif p[TCP].flags == 'PA':
                lines = p['Raw'].load.splitlines()
                print(lines[0].decode())
                if lines[0] == b'BEAR':
                    print(b'\n'.join(lines[1:]).decode())
                print(f'Bear parts: {list(bear_parts.keys())}')
                choice = input('Enter choice [(A)dd <part_name>/(C)lear/(P)rint/(Q)uit]: ').strip().lower()
                payload = b'NONE'
                if choice.startswith('a'):
                    payload = b'ADD\n' + input('Enter part: ').strip().encode()
                elif choice.startswith('c'):
                    payload = b'CLEAR'
                elif choice.startswith('p'):
                    payload = b'PRINT'
                elif choice.startswith('q'):
                    payload = b'QUIT'
                else:
                    print('Invalid choice')
                sendp(
                    Ether() /
                    IP(src=p['IP'].dst, dst=p['IP'].src) /
                    TCP(sport=p['TCP'].dport, dport=p['TCP'].sport, flags='PA', seq=p.ack, ack=p.seq + 1 & (1 << 32) - 1) /
                    Raw(load=payload)
                )

if __name__ == '__main__':
    import os
    print(f'Please run this program with the shell command `{os.path.realpath(__file__)}`, not as an argument to Python.')

elif __name__ == 'scapy.main':
    assert os.path.basename(sys.argv[0]) == 'scapy'
    print(author_note)
    global bear
    bear = []
    pid = os.fork()
    if pid == 0:
        sniff(prn=bear_handler, stop_filter=lambda p: 'Raw' in p and p['Raw'].load == b'QUIT')
        os._exit(0)
    sendp(Ether() / IP(src='127.0.0.1', dst='127.0.0.1') / TCP(sport=1337, dport=80, flags='S', seq=0))
    os.wait()
    exit()
