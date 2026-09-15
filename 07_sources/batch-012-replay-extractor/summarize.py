import hashlib
import json
from pathlib import Path

root = Path(__file__).parent
rows = [json.loads(line) for line in (root / 'snapshots.jsonl').open(encoding='utf-8')]
names = ['Miposhka', 'Yatoro', 'TORONTOTOKYO', 'Mira', 'Collapse', 'Ame', 'NothingToSay', 'Faith_bian', 'XinQ', 'y`']
heroes = ['寒冬飞龙', '恐怖利刃', '灰烬之灵', '祸乱之源', '马格纳斯', '小小', '昆卡', '狼人', '天怒法师', '魅惑魔女']
result = []
for row in rows:
    player_resource = next(e['state'] for e in row['entities'] if e['class'] == 'CDOTA_PlayerResource')
    by_handle = {e['index'] + (e['serial'] << 14): e for e in row['entities']}
    teams = {e['class']: e['state'] for e in row['entities'] if e['class'] in ('CDOTA_DataDire', 'CDOTA_DataRadiant')}
    real_heroes = []
    for player in range(10):
        prefix = f'm_vecPlayerTeamData.{player:04d}.'
        entity = by_handle[player_resource[prefix + 'm_hSelectedHero']]
        state = entity['state']
        assert state['m_iPlayerID'] == player
        items = []
        abilities = []
        for key, value in sorted(entity['linked'].items()):
            fields = value['state']
            if key.startswith('m_hItems.'):
                items.append({'slot': int(key.rsplit('.', 1)[1]), 'name': value['name'], 'charges': fields.get('m_iCurrentCharges'), 'cooldown_remaining': fields.get('m_fCooldown')})
            if key.startswith('m_hAbilities.') and not value['name'].startswith(('special_bonus', 'generic_', 'seasonal_', 'plus_', 'ability_', 'abyssal_underlord_portal_warp')):
                abilities.append({'slot': int(key.rsplit('.', 1)[1]), 'name': value['name'], 'level': fields.get('m_iLevel'), 'cooldown_remaining': fields.get('m_fCooldown'), 'mana_cost': fields.get('m_iManaCost')})
        team_class = 'CDOTA_DataRadiant' if player < 5 else 'CDOTA_DataDire'
        team_slot = player_resource[prefix + 'm_iTeamSlot']
        real_heroes.append({'player': names[player], 'hero_cn': heroes[player], 'entity_index': entity['index'], 'entity_serial': entity['serial'], 'team': state['m_iTeamNum'], 'level': state['m_iCurrentLevel'], 'xp': state['m_iCurrentXP'], 'hp': state['m_iHealth'], 'max_hp': state['m_iMaxHealth'], 'mana': state['m_flMana'], 'max_mana': state['m_flMaxMana'], 'net_worth': teams[team_class].get(f'm_vecDataTeam.{team_slot:04d}.m_iNetWorth'), 'kills': player_resource[prefix + 'm_iKills'], 'deaths': player_resource[prefix + 'm_iDeaths'], 'visible_team_mask_raw': state['m_iTaggedAsVisibleByTeam'], 'position_raw': {axis: {'cell': state.get('CBodyComponent.m_cell' + axis), 'vec': state.get('CBodyComponent.m_vec' + axis)} for axis in 'XYZ'}, 'items': items, 'abilities': abilities})
    towers = [{'name': e['name'], 'hp': e['state']['m_iHealth'], 'team': e['state']['m_iTeamNum']} for e in row['entities'] if e['class'] == 'CDOTA_BaseNPC_Tower']
    result.append({'target_game_seconds': row['target'], 'observed_game_seconds': row['game_time'], 'demo_tick': row['tick'], 'heroes': real_heroes, 'towers': towers})

fi = json.loads((root / '6227492909.dem.fileinfo.json').read_text(encoding='utf-8'))
summary = {'match_id': 6227492909, 'source': 'http://replay273.valve.net/570/6227492909_1934613958.dem.bz2', 'retrieved_at': '2026-09-14', 'compressed_bytes': 124472677, 'compressed_sha256': hashlib.sha256((root / '6227492909.dem.bz2').read_bytes()).hexdigest(), 'parser': 'github.com/dotabuff/manta v1.5.0', 'game_build': rows[0]['build'], 'selection_rule': 'CDOTA_PlayerResource m_hSelectedHero -> entity index AND serial; never first hero class match; replicas excluded', 'sampling_rule': 'First PacketEntities callback at/after each target; observed time is m_fGameTime minus m_flGameStartTime, no interpolation', 'coordinate_rule': 'Raw cell and vec only; no terrain geometry or full fog mask reconstructed', 'fileinfo': {'end_time': fi['game_info']['dota']['end_time'], 'playback_time': fi['playback_time'], 'playback_ticks': fi['playback_ticks']}, 'snapshots': result}
(root / 'selected-snapshots.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
assert len(result) == 39
publication = {key: value for key, value in summary.items() if key != 'snapshots'}
publication['snapshots'] = [r for r in result if r['target_game_seconds'] == 540]
publication['xinq_checkpoints'] = [dict(target_game_seconds=r['target_game_seconds'], observed_game_seconds=r['observed_game_seconds'], hero=r['heroes'][8]) for r in result if r['target_game_seconds'] in [509,542,546,550,555,559,562,615,660,720,1110,1146,2205]]
publication['score_audit'] = {'opendota_radiant_score': 29, 'replay_player_kills_sum_radiant': sum(h['kills'] for h in result[-1]['heroes'][:5]), 'replay_player_kills_sum_dire': sum(h['kills'] for h in result[-1]['heroes'][5:]), 'broadcast_final_frame_verified': False}
(root / 'publication-extract.json').write_text(json.dumps(publication, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
for row in result:
    sky = row['heroes'][8]
    if row['target_game_seconds'] in [540,542,546,550,555,559,560,562,615,660,720,2205]:
        print(row['target_game_seconds'], sky['level'], sky['xp'], sky['hp'], round(sky['mana'],2), [(a['name'], a['level'], round(a['cooldown_remaining'], 2)) for a in sky['abilities']], [(i['slot'], i['name']) for i in sky['items']])
print('VALIDATED selected heroes:', len(result) * 10)
