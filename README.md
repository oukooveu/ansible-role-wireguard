# wireguard ansible role
[![Molecule](https://github.com/oukooveu/ansible-role-wireguard/actions/workflows/molecule.yml/badge.svg)](https://github.com/oukooveu/ansible-role-wireguard/actions/workflows/molecule.yml)

This is a simple role to install wireguard and configure full-mesh connectivity (by default) between all play hosts.

The role was inspired by [this](https://github.com/mawalu/wireguard-private-networking) implementation but because it's in unmaintained state and PRs are not accepted it was decided to rewrite it from scratch.

## Requirements

There are no special requirements. There is no default for `wireguard_vpn_ip`, this variable must be defined for each host.

## Role Variables

| Variable | Description | Default value |
|----------|-------------|---------------|
| wireguard_port | port to listen | `51820` |
| wireguard_path | path to configuration files | `/etc/wireguard` |
| wireguard_vpn_ip | private address | N/A, must be provided through host vars |
| wireguard_public_ip | public address| `{{ ansible_default_ipv4.address }}` |
| wireguard_post_up | post up script | N/A |
| wireguard_post_down | post down script | N/A |
| wireguard_network | network topology, see samples below | `{}` |
| wireguard_network_name | interface name | `wg0` |
| wireguard_additional_peers | additional peers | `[]` |
| wireguard_mtu_enabled | manage `MTU` option | `false` |
| wireguard_mtu | `MTU` option value | N/A |
| wireguard_fw_mark_enabled | manage `FwMark` option | `false` |
| wireguard_fw_mark | `FwMark` option value | `{{ wireguard_port }}` |

`FwMark` wireguard option can be useful when you need to filter out all unencrypted traffic, for example:
```
PostUp = iptables -I OUTPUT ! -o %i -m mark ! --mark $(wg show %i fwmark) -m addrtype ! --dst-type LOCAL -j REJECT
PreDown = iptables -D OUTPUT ! -o %i -m mark ! --mark $(wg show %i fwmark) -m addrtype ! --dst-type LOCAL -j REJECT
```

## Example Playbooks

### full-mesh network
```
- name: setup wireguard full-mesh network
  hosts: cluster
  roles:
    - role: oukooveu.wireguard
```

### custom network topology with additional peer
```
- name: setup wireguard custom network
  hosts: cluster
  vars:
    wireguard_network:
        node1:
            - node2
            - node3
            - node4
        node2:
            - node1
            - node4
        node3:
            - node1
            - node4
        node4:
            - node1
            - node2
            - node3
    wireguard_additional_peers:
        - ip: 192.168.100.1
          key: s3cr3t
          endpoint: 10.0.100.1
          keepalive: 15
          comment: 'comment'
  roles:
    - role: oukooveu.wireguard
```

In the sample above hosts `node1` and `node4` have access to all hosts and hosts `node2` and `node3` don't have access to each other. Configuration should be symmetric (if connectivity for one node is defined it should be defined for an another node too) and there are no additional checks for this, be careful.

## Molecule tests

To run tests locally:
```
python -m venv .venv
. .venv/bin/activate
pip install -r molecule/default/requirements.txt
molecule test
```

To run tests for non-default image (`debian:10`) set `MOLECULE_IMAGE` environment variable to an appropriate value, for example:
```
export MOLECULE_IMAGE=rockylinux:9
```

To cleanup test environment run `molecule destroy`.

## License

Apache 2.0
