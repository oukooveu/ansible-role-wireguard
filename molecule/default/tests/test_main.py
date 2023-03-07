import pytest

network_map = {
    'node1': {
        'ip': '10.101.0.1',
        'remotes': ['node2', 'node3']
    },
    'node2': {
        'ip': '10.102.0.1',
        'remotes': ['node1']
    },
    'node3': {
        'ip': '10.103.0.1',
        'remotes': ['node1']
    }
}


def test_service(host):
    service = host.service('wg-quick@wg0')
    assert service.is_running
    assert service.is_enabled


def test_port(host):
    socket = host.socket("udp://0.0.0.0:51820")
    assert socket.is_listening


@pytest.mark.parametrize("remote", ('10.101.0.1', '10.102.0.1', '10.103.0.1'))
def test_wireguard_network(host, remote, map=network_map):
    hostname = host.backend.get_hostname()

    if remote == map[hostname]['ip']:
        pytest.skip("localhost")

    command = host.run('ping -c1 -W1 ' + remote)
    if remote in [map[x]['ip'] for x in map[hostname]['remotes']]:
        assert command.rc == 0
        assert '1 packets transmitted, 1 received' in command.stdout
    else:
        assert command.rc == 1
        assert '1 packets transmitted, 0 received' in command.stdout
