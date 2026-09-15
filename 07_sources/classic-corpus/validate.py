"""Validate the actual collected corpus against cached source responses."""
import argparse
import collections
import datetime as dt
import hashlib
import json
import pathlib
import re
from urllib.parse import unquote

from collect import OUT, ROOT, SERIES, START, END, TOP_KEYS, PLAYER_KEYS


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--cache',required=True,type=pathlib.Path)
    args=ap.parse_args()
    errors=[]
    checks=collections.Counter()

    def check(ok,label,context):
        checks[label]+=1
        if not ok:
            errors.append({'check':label,'context':context})

    selected=[mid for *_,ids in SERIES for mid in ids]
    index=read(OUT/'match-inventory.json')
    inventory_ids={r['match_id'] for r in index}
    check(len(inventory_ids)==len(index),'unique_inventory',len(index))
    check(len(set(selected))==len(selected),'unique_selection',len(selected))
    check(set(selected)<=inventory_ids,'selection_in_inventory',list(set(selected)-inventory_ids))
    check({int(f.stem) for f in (OUT/'data').glob('*.json')}==set(selected),'export_file_set',len(selected))
    all_data={}
    for mid in selected:
        data=read(OUT/f'data/{mid}.json'); all_data[mid]=data
        raw_path=args.cache/f'match-{mid}.json'
        raw_bytes=raw_path.read_bytes(); raw=json.loads(raw_bytes.decode('utf-8-sig'))
        m=data['match']; ps=data['players']
        check(m['match_id']==raw['match_id']==mid,'identity',mid)
        check(hashlib.sha256(raw_bytes).hexdigest()==data['source']['raw_sha256'],'source_hash',mid)
        check(START<=m['start_time']<END,'time_window',mid)
        check(len(ps)==10 and {p['player_slot'] for p in ps}=={0,1,2,3,4,128,129,130,131,132},'ten_distinct_slots',mid)
        check(all(m.get(k)==raw.get(k) and (k in m)==(k in raw) for k in TOP_KEYS),'match_fields_preserved',mid)
        by_slot={p['player_slot']:p for p in raw['players']}
        for p in ps:
            source=by_slot[p['player_slot']]
            for k in PLAYER_KEYS:
                renamed={'name':'api_name','personaname':'api_personaname'}.get(k,k)
                check(p.get(renamed)==source.get(k),'player_fields_preserved',f'{mid}:{p["player_slot"]}:{k}')
            check(not any(k in p for k in ['last_login','rank_tier','benchmarks','is_subscriber']),'unrelated_profile_fields_excluded',f'{mid}:{p["player_slot"]}')
            check('待译' not in p['hero_name_zh'],'hero_translated',f'{mid}:{p["hero_id"]}')
        picks=[p['hero_id'] for p in m['picks_bans'] if p['is_pick']]
        check(collections.Counter(picks)==collections.Counter(p['hero_id'] for p in ps),'draft_matches_players',mid)
        for field in ['radiant_gold_adv','radiant_xp_adv']:
            check(len(m[field]) in [m['duration']//60+1,m['duration']//60+2],'minute_curve_length',f'{mid}:{field}')
        check(all(v is False for v in data['observation'].values()),'no_false_vod_claim',mid)
        check(data['patch_precision']['event_patch_verified'] is False,'patch_precision_honest',mid)
    for slug,_,_,_,ids in SERIES:
        check(len({frozenset((all_data[mid]['match']['radiant_team_id'],all_data[mid]['match']['dire_team_id'])) for mid in ids})==1,'same_series_opponents',slug)
        check(len({all_data[mid]['match']['leagueid'] for mid in ids})==1,'same_series_league',slug)
        times=[all_data[mid]['match']['start_time'] for mid in ids]
        check(times==sorted(times),'series_game_order',slug)
    # Cross-check selected numerical claims used in manual research cards.
    expected={6707633683:(4507,48,-22406),6819203954:(3059,46,12951),7259126761:(3601,60,9227),6832287527:(2673,30,-899),6632414079:(1748,20,-6577),7404763579:(4592,60,-20389)}
    for mid,(duration,minute,adv) in expected.items():
        m=all_data[mid]['match']
        check(m['duration']==duration and m['radiant_gold_adv'][minute]==adv,'manual_card_numeric_anchor',mid)
    # Supplemental pages are explicit field-level extracts, not substitute replays.
    cnq=read(OUT/'supplements/ti11-cn-spectral-index.json')['rows']
    cnq_api=read(args.cache/'league-14572.json')
    check({r['match_id'] for r in cnq}=={r['match_id'] for r in cnq_api},'cnq_cross_source_ids',len(cnq))
    cnq_groups=collections.defaultdict(set)
    score_differences=[]
    for r in cnq:
        mid=r['match_id'];m=all_data[mid]['match']
        seconds=0
        for part in r['duration_display'].split(':'):
            seconds=seconds*60+int(part)
        check(seconds==m['duration'],'cnq_cross_source_duration',mid)
        cnq_groups[r['spectral_series']].add(mid)
        api_total=m['radiant_score']+m['dire_score']
        if api_total!=r['combined_kills']:
            score_differences.append({'match_id':mid,'spectral_combined_kills':r['combined_kills'],'opendota_combined_score':api_total})
    check({frozenset(v) for v in cnq_groups.values()}=={frozenset(ids) for slug,_,_,_,ids in SERIES if slug.startswith('cnq-')},'cnq_cross_source_series',len(cnq_groups))
    ry=read(OUT/'supplements/riyadh23-spectral-index.json')['rows']
    ry_ids={r['match_id'] for r in ry}
    ry_api_ids={r['match_id'] for r in read(args.cache/'league-15475.json')}
    recovered=read(OUT/'supplements/riyadh23-recovered.json')
    recovered_ids={r['match_id'] for r in recovered['index']}
    check(len(ry_ids)==len(ry)==235,'riyadh_spectral_unique',len(ry))
    check(recovered_ids==ry_ids-ry_api_ids and len(recovered_ids)==15,'riyadh_exact_supplement_difference',sorted(recovered_ids))
    check(recovered_ids.isdisjoint(inventory_ids),'supplement_not_mislabeled_as_api_inventory',sorted(recovered_ids&inventory_ids))
    check({r['match_id'] for r in recovered['api_checks']}==recovered_ids and all(r.get('http_status')==404 for r in recovered['api_checks']),'supplement_api_404_recorded',len(recovered['api_checks']))
    check(recovered['api_checks']==read(args.cache/'riyadh23-late-api-check.json'),'supplement_api_check_cache',len(recovered['api_checks']))
    finals=recovered['grand_final_lineups']
    check([r['game_number'] for r in finals]==[1,2,3,4] and [r['winner'] for r in finals]==['Team Liquid','Team Spirit','Team Spirit','Team Spirit'],'riyadh_final_result',len(finals))
    indexed={r['match_id']:r for r in recovered['index']}
    for g in finals:
        check(len(g['players'])==10 and collections.Counter(p['side'] for p in g['players'])=={'radiant':5,'dire':5} and len({p['hero_zh'] for p in g['players']})==10,'riyadh_final_ten_heroes',g['match_id'])
        check(g['radiant_kills_displayed']+g['dire_kills_displayed']==indexed[g['match_id']]['combined_kills'],'riyadh_final_card_list_score',g['match_id'])
    check(not recovered['full_vod_watched'] and not recovered['scene_vod_watched'] and not recovered['api_detail_available'],'supplement_evidence_limits',15)
    for mid,hero,kda in [(6753967144,39,(21,2,14)),(6753967144,70,(19,2,3)),(6753917157,13,(20,2,16))]:
        p=next(p for p in all_data[mid]['players'] if p['hero_id']==hero)
        check((p['kills'],p['deaths'],p['assists'])==kda,'second_pass_kda_anchor',f'{mid}:{hero}')
    check(all_data[6751948451]['match']['radiant_gold_adv'][38]==-1561 and all_data[6751948451]['match']['radiant_win'],'aries_win_while_sample_behind',6751948451)
    for path in OUT.rglob('*.md'):
        content=path.read_text(encoding='utf-8')
        for link in re.findall(r'\]\(([^)]+)\)',content):
            if '://' in link or link.startswith('#'):
                continue
            target=unquote(link.strip('<>').split('#')[0])
            check((path.parent/target).resolve().exists(),'local_markdown_link',f'{path.relative_to(ROOT)}:{target}')
    check(read(ROOT/'00_meta/coverage.json')['coverage']['post_ti10_classic_corpus']['detailed_matches']==len(selected),'coverage_count',len(selected))
    status=read(OUT/'collection-status.json')
    check(status['exported_matches']==len(selected) and status['failures']==[],'collection_finished',status)
    cross_source={'cnq_score_disagreements':score_differences,'cnq_score_disagreement_note':'来源间差异，不在没有转播证据时挑选一个充作真实记分牌','riyadh_common_matches':len(ry_ids&ry_api_ids),'riyadh_spectral_only':len(ry_ids-ry_api_ids),'riyadh_api_only':len(ry_api_ids-ry_ids),'riyadh_supplement_detail_status':'15局均为已核404；决赛4局仅另存基础阵容'}
    report={'checked_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),'result':'passed' if not errors else 'failed','scope':'实际数据完整性、原响应保真及文档数值锚点；不是视频内容/战术因果/小说质量验证','selected_matches':len(selected),'selected_series':len(SERIES),'cross_source_findings':cross_source,'checks':dict(checks),'errors':errors}
    (OUT/'validation-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if errors:
        raise SystemExit(1)


if __name__=='__main__':
    main()
