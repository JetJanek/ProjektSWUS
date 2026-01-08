import json
import os

host_config_path = 'configs'
container_config_path = '/etc/quagga'
edges = [('PC1', 'R1'), ('PC2', 'R1'), ('PC3', 'R4'), ('PC4', 'R6'), ('R1', 'R2'), ('R2', 'R3'), ('R2', 'R5'), ('R3', 'R5'), ('R3', 'R4'), ('R5', 'R6')]

connections = {'R1': [], 'R2': [], 'R3': [], 'R4': [], 'R5': [], 'R6': [], 'PC1': [], 'PC2': [], 'PC3': [], 'PC4': []}
for a, b in edges:
    connections[a].append(b)
    connections[b].append(a)


class Network:
    def __init__(self, a: str, b: str):
        self.name = f'net_{a.lower()}_{b.lower()}'
        num_a = int(a[-1])
        num_b = int(b[-1])
        self.a = a
        self.b = b
        self.address = f'10.0.{num_a}.0' if a.startswith('PC') else f'10.{num_a}{num_b}.0.0'
        self.mask = '24' if a.startswith('PC') else '28'

    def __str__(self):
        return self.address + '/' + self.mask

    def __repr__(self):
        return '"' + str(self) + '"'


class Interface:
    def __init__(self, a: str, b: str, i: int):
        self.name = f'eth{i}'
        num_a = int(a[-1])
        num_b = int(b[-1])
        c, d = (a, b) if a.startswith('PC') else (b, a) if b.startswith('PC') else (a, b) if num_a < num_b else (b, a)
        self.network_name = f'net_{c.lower()}_{d.lower()}'
        self.a = a
        self.b = b
        if a.startswith('PC'):
            self.address = f'10.0.{num_a}.100'
        elif b.startswith('PC'):
            self.address = f'10.0.{num_b}.2'
        else:
            self.address = f'10.{c[-1]}{d[-1]}.0.{ 2 if num_a < num_b else 3 }'
        self.mask = '24' if a.startswith('PC') or b.startswith('PC') else '28'

    def __str__(self):
        return self.address

    def __repr__(self):
        return '"' + str(self) + '"'

    def network(self):
        return self.address[:self.address.rfind('.')] + '.0/' + self.mask


print(connections)

networks = [Network(a, b) for a, b in edges]
interfaces = {a: [Interface(a, b, i+1) for i, b in enumerate(value)] for a, value in connections.items()}

print(json.dumps(json.loads(repr(networks)), indent=4))
print(json.dumps(json.loads(repr(interfaces).replace('\'', '\"')), indent=4))


# Generate zebra and ospf files:
for i, r in enumerate(('r1', 'r2', 'r3', 'r4', 'r5', 'r6')):
    i += 1
    interface_list = interfaces[r.upper()]
    os.makedirs(f'{host_config_path}/{r}', exist_ok=True)
    with open(f'{host_config_path}/{r}/zebra.conf', 'w', encoding='UTF-8') as file:
        file.write(f'''hostname zebra
password zebra
log file {container_config_path}/log/zebra.log
''')
        for interface in interface_list:
            file.write(f'''!
interface {interface.name}
 ip address {interface.address + "/" + interface.mask}
''')

    # Create empty log files
    os.makedirs(f'{host_config_path}/{r}/log', exist_ok=True)
    open(f'{host_config_path}/{r}/log/zebra.log', 'a').close()
    open(f'{host_config_path}/{r}/log/ospfd.log', 'a').close()

    bs = '\n'
    with open(f'{host_config_path}/{r}/ospfd.conf', 'w', encoding='UTF-8') as file:
        file.write(f'''!
router ospf
 ospf router-id {i}.{i}.{i}.{i}
{bs.join([f' network {interface.network()} area 0' for interface in interface_list])}
!
log file {container_config_path}/log/ospfd.log
!''')

# Generate docker-compose.yml
with open(f'docker-compose.yml', 'w', encoding='UTF-8') as file:
    file.write('services:\n')
    for node, interface_list in interfaces.items():
        node_name = node.lower()
        if node.startswith('R'):
            file.write(f'''  {node_name}:
    build: ./quagga
    container_name: {node_name}
    privileged: true
    cap_add:
      - NET_ADMIN
      - NET_RAW
    networks:''')
            for interface in interface_list:
                file.write(f'''
      {interface.network_name}:
        ipv4_address: {interface.address}
        interface_name: {interface.name}''')
            file.write(f'''
    volumes:
      - ./configs/{node_name}:{container_config_path}
    command: bash -c "zebra -d && ospfd -d && vtysh && tail -f /dev/null"

''')
        else:
            interface = interface_list[0]
            file.write(f'''  {node_name}:
    build: ./pc  # Zmień na swój obraz PC
    container_name: {node_name}
    networks:
      {interface.network_name}:
        ipv4_address: {interface.address}
    command: tail -f /dev/null  # Idle, instaluj co chcesz via exec
    
''')
    file.write('networks:')
    for network in networks:
        file.write(f'''
  {network.name}:
    driver: bridge
    ipam:
      config:
        - subnet: {network}''')
