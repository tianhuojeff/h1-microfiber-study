"""Produce a review patch from manually read saved text; never write on invocation."""
from pathlib import Path
import csv
import datetime
import difflib
import hashlib
import io
import json
import sys
import subprocess
from local_source import read_anchors

RUN = Path(__file__).resolve().parents[1]
H1 = RUN.parents[1]
MASTER = RUN / 'data/analysis_master.json'
SOURCE = H1 / 'team_package_20260928/sources/CN120500565A.html'
NOW = '2026-10-01T12:42:10.7987048+08:00'
SHA = 'f47cbd39c8c21842fb5b5140377dece6b8421369bc765d6c183ff970e6a41e1d'

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def dumps(v):
    return json.dumps(v, ensure_ascii=False, indent=2) + '\n'

def check_current(m):
    ids = []
    evidence_count = 0
    literal_checks = []
    cache = {}
    for sample in m['samples']:
        assert sample['sample_role'] == 'pending'
        for field in sample['features'].values():
            for obs in field['observations']:
                ids.append(obs['observation_id'])
                for e in obs['evidence']:
                    source = Path(e['source_path'])
                    assert digest(source) == e['source_sha256']
                    if e.get('html_anchor'):
                        if str(source) not in cache:
                            cache[str(source)] = read_anchors(source)
                        assert e['evidence_excerpt'] in cache[str(source)][e['html_anchor']]
                        literal_checks.append([obs['observation_id'], e['html_anchor']])
                    else:
                        assert digest(Path(e['page_image_path'])) == e['page_image_sha256']
                    evidence_count += 1
                if obs.get('pdf_visual_crosscheck'):
                    p = obs['pdf_visual_crosscheck']
                    assert digest(Path(p['source_path'])) == p['source_sha256']
                    assert digest(Path(p['image_path'])) == p['image_sha256']
    assert len(ids) == len(set(ids))
    assert not m['formal_statistics_allowed'] and not m['final_report_ready']
    return {'observations': len(ids), 'evidence_count': evidence_count,
            'literal_checks': literal_checks, 'unique_observation_ids': True,
            'source_hash_checks': True, 'all_eligibilities_pending': True,
            'formal_statistics_allowed': False, 'final_report_ready': False}

def patch_for(path, new):
    old = path.read_text(encoding='utf-8-sig') if path.exists() else ''
    rel = path.relative_to(H1.parent).as_posix()
    if old == new:
        return ''
    if not path.exists():
        return f'*** Add File: {rel}\n' + ''.join('+' + line + '\n' for line in new.splitlines())
    diff = list(difflib.unified_diff(old.splitlines(), new.splitlines(), n=20))
    return f'*** Update File: {rel}\n' + '\n'.join('@@' if line.startswith('@@') else line for line in diff[2:]) + '\n'

if '--verify' in sys.argv:
    master = json.loads(MASTER.read_text(encoding='utf-8'))
    result = check_current(master)
    sample = next(s for s in master['samples'] if s['representative_publication'] == 'CN120500565A')
    assert sample['review_completeness']['full_text_rechecked'] is False
    assert sample['review_completeness']['saved_text_review']['anchors_read'] == 338
    assert all(f['observations'] for f in sample['features'].values())
    assert sample['scene_material']['classification'] == 'explicit_laundry_microplastics_and_microfibres'
    for basis in sample['scene_material']['basis']:
        assert basis['excerpt'] == read_anchors(SOURCE)[basis['anchor']]
        assert basis['source_sha256'] == digest(SOURCE)
    baseline = json.loads(subprocess.check_output(['git', 'show', 'ffc7470f11d5e316183c487d898e3676e02725a0:corrections/20260929_r1/data/analysis_master.json'], cwd=H1))
    assert all(a == b for a,b in zip(baseline['samples'], master['samples']) if a['representative_publication'] != 'CN120500565A')
    old_sample = next(s for s in baseline['samples'] if s['representative_publication'] == 'CN120500565A')
    assert sample['prior_working_evidence'] == old_sample['prior_working_evidence']
    assert all(sample['features'][k]['observations'][:len(v['observations'])] == v['observations'] for k,v in old_sample['features'].items())
    release = json.loads((H1 / 'current_release.json').read_text(encoding='utf-8'))
    assert release['master_sha256'] == digest(MASTER)
    assert release['current_observations'] == result['observations'] == 73
    assert not release['project_completion_accepted']
    print(dumps({'readback': True, 'observations': result['observations'],
                 'master_sha256': digest(MASTER), 'all_13_fields_addressed_in_saved_scope': True,
                 'original_pdf_still_missing': True, 'full_text_completion': False}))
    raise SystemExit(0)

assert digest(SOURCE) == SHA
anchors = read_anchors(SOURCE)
assert len(anchors) == 338
assert all(f'p{i:04}' in anchors for i in range(1, 320))
assert all(f'zh-cl{i:04}' in anchors for i in range(1, 20))
original = json.loads(MASTER.read_text(encoding='utf-8'))
check_current(original)
master = json.loads(dumps(original))
sample = next(s for s in master['samples'] if s['representative_publication'] == 'CN120500565A')

# Each row is a manual semantic decision, not a keyword-derived 0/1 label.
decisions = [
    ('capture', 'filter130', 'explicit', ['p0123','p0124','p0128'],
     '过滤构件131从衣物分离的洗涤水中过滤微塑料；构件及框架限定顶部敞开的过滤器腔室135。孔仅描述足够过滤小于5mm颗粒，未给出具体孔径。',
     '洗衣水中微塑料', '洗涤水', '过滤构件131及过滤器腔室135', '过滤器内部', ['水穿过过滤构件','颗粒被截留']),
    ('transfer', 'guided_surface_to_bottom', 'explicit', ['p0169','p0171'],
     '引导水从过滤器侧面上部向下扫掠，使附着颗粒脱离并收集于过滤器底部；清理与内部转移由同一水流实现，未越过模块边界。',
     '滤面颗粒', '过滤构件侧表面', '过滤器底部', '同一过滤器内部', ['水流导向侧面上部','向下扫掠','颗粒脱离','底部收集']),
    ('storage', 'filter_bottom_accumulation', 'explicit', ['p0131','p0171'],
     '颗粒自过滤器左右侧面下部向上堆积、在过滤器底部收集；这是含物过滤组件内的积存，不能写成独立密闭干渣盒或长期储存验证。',
     '脱离滤面颗粒', '左右滤面', '过滤器底部', '过滤组件内', ['颗粒脱离','底部积聚']),
    ('chamber_drainage', 'maintenance_emptying_unlocated', 'not_located_in_reviewed_scope', ['p0145','p0150','p0151','p0156'],
     '已复核保存中文说明书p0001-p0319及权1-19，未定位独立维护前排空动作。坡面、出水口及泵停虹吸截断支持排水结构；p0145反而保留取出过滤器残水污染风险，并以抽屉底面承接。不得据此写成已排空或无滴漏。',
     '维护时残留游离水', '第二腔/过滤器', '独立维护排空终点未定位', '过滤模块维护边界', ['正常水出口排水有依据','独立维护排空时序未定位']),
    ('solids_dewatering', 'collected_solids_dewatering_unlocated', 'not_located_in_reviewed_scope', ['p0145','p0171'],
     '在已复核保存中文说明书p0001-p0319及权1-19内，未定位针对收集颗粒的压滤、离心或独立脱水步骤。正常透水、降低整体水位和抽屉接残水分别处理，不自动证明收集物含水率降低。',
     '已收集颗粒夹带水', '过滤器底部积存颗粒', '专门脱水终点未定位', '收集固体与液体分离边界', ['底部积聚有依据','专门固体脱水顺序未定位']),
    ('liquid_route', 'machine_drain_case1', 'explicit', ['p0100','p0101','p0102','p0103'],
     '排放流道73的水可由排水泵61送入排水流道75，塑料过滤器100处在情况1排水路径，经75a进入、75b排出。情况2循环由循环泵62单独启动并回桶，不能把塑料过滤器的位置移到该循环分支，也不推断最终环境终点。',
     '洗涤/漂洗水', '桶30/排放流道73', '第二排水软管75b', '洗衣机排水路径及外置过滤单元', ['排水泵启动','73进入75','75a经过滤器','75b排出']),
    ('removal', 'description_drawer_then_filter', 'explicit', ['p0113','p0115','p0117','p0145'],
     '同一说明书方案明确过滤器在抽屉、抽屉在外壳：用前部手柄向前抽出抽屉，再向上移除含物过滤器。抽屉是支承/接残水界面，不另算干渣容器；该原文路径不并入每一独立项。',
     '含截留物过滤器130及支承抽屉120', '外壳内第二腔', '外壳外抽屉、继而抽屉外过滤器', '外壳边界及抽屉边界分别越过', ['向前移除抽屉','向上移除过滤器']),
    ('state_switch', 'pump_and_passive_cleaning', 'explicit', ['p0102','p0144','p0156'],
     '排水/回桶循环由排水泵61与循环泵62互斥工作描述；滤面自清洁利用经开口落下水流，无单独滤面驱动源。泵停负压时止回阀引入空气是虹吸控制，不能合成过滤—压实—自动排固状态机。',
     '水流、滤面颗粒与空气', '泵运行/开口落水/泵停负压各状态', '排水/回桶/滤面清理/压力均衡各终点', '不同流路与触发状态分别记录', ['排水状态与回桶状态分开','清理随过滤水流发生','泵停负压触发进气']),
    ('seals_connections', 'drawer_seals_and_residual_water', 'explicit', ['p0145','p0158','p0160','p0161','p0162'],
     '抽屉可拆带来密封需求；第一密封件封外壳前口，第二件封第一腔前口，第三件在过滤器接触处形成水密界面。取出时残水承接由抽屉底面描述；未提供滴漏量或密封测试。',
     '抽屉/外壳/过滤器连接与残水', '可拆抽屉接口', '三处密封座及抽屉底面承接', '前部开口及过滤腔接口', ['抽屉插入时各密封件接触','抽屉取出时底面承接残水']),
    ('performance', 'textual_claims_without_comparable_data', 'explicit', ['p0043','p0047','p0048','p0049','p0192','p0199','p0214'],
     '保存全文中降低排水阻力、延长清洁周期及实施方式水位/排水压力差异属于文本效果解释；已读范围未定位带具体条件和样本量的测量表或跨方案可比实验。图中符号/尺寸与75cm安装背景不充作性能实测。',
     '排水阻力/清洁周期/水位效果主张', '各自描述的实施方式', '文本主张而非验收性能', '文本披露与实验效果边界', ['效果解释已定位','可比实测未定位']),
    ('endpoint', 'post_removal_disposal_unlocated', 'not_located_in_reviewed_scope', ['p0115','p0145','p0171'],
     '在保存中文说明书p0001-p0319与权1-19内已定位过滤器取出和颗粒积聚，未定位取出后收集颗粒的废物处置动作。背景p0004所述河海危害不能移作本发明最终去向。',
     '取出后截留颗粒', '含物过滤器离开抽屉后', '最终处置终点未定位', '装置移出与下游处置边界', ['取出路径已定位','后续处置未定位']),
    ('carrier_conditioning', 'filter_carrier_conditioning_unlocated', 'not_located_in_reviewed_scope', ['p0123','p0124','p0145'],
     '在保存中文说明书p0001-p0319与权1-19内未定位过滤载体专门排水/干燥程序；滤面自清洁另归cleaning，衣物脱水循环p0080不属于载体干燥，残水承接不等于载体干燥。',
     '过滤构件自身残水', '过滤器130', '载体专门排水/干燥终点未定位', '载体维护边界', ['滤面清理另列','载体干燥未定位'])
]

added = []
for field, embodiment, status, keys, interpretation, obj, start, end, boundary, order in decisions:
    oid = f'CN120500565A-{field}-{embodiment}-20261001'
    assert not any(o['observation_id'] == oid for o in sample['features'][field]['observations']), 'Already applied; use --verify for readback'
    evidence = [{
        'locator': '保存HTML #' + key, 'html_anchor': key,
        'evidence_excerpt': anchors[key], 'source_role': 'description',
        'subject_role': 'this_invention_or_optional_embodiment',
        'source_path': str(SOURCE), 'source_url': 'https://patents.google.com/patent/CN120500565A/zh',
        'source_sha256': SHA, 'verified_at': NOW,
        'extraction_note': 'Saved patent-publication mirror; anchor is not an official paragraph number; PDF unavailable.'
    } for key in keys]
    observation = {
        'observation_id': oid, 'publication_id': 'CN120500565A', 'grant_publication_id': None,
        'sample_role': 'pending', 'embodiment_id': embodiment, 'stage': field,
        'technical_feature': interpretation, 'object': obj, 'start': start, 'end': end,
        'boundary': boundary, 'operation_order': order, 'support_status': status,
        'review_status': 'complete_in_stated_scope', 'claim_dependency': '说明书方案；不据此增添独立项限定',
        'evidence': evidence, 'interpretation': interpretation,
        'performance_status': 'text_claim_only' if field == 'performance' else 'not_verified',
        'verified_at': NOW, 'old_value': sample['features'][field]['support_status'],
        'new_value': interpretation, 'change_reason': '2026-10-01保存全文复核补充；原PDF和资格缺口独立保留',
        'removal_kind': 'target_bearing_filter_component' if field == 'removal' else None,
        'review_scope': '保存中文HTML p0001-p0319及zh-cl0001-zh-cl0019；未核原PDF/附图'
    }
    sample['features'][field]['observations'].append(observation)
    sample['features'][field]['support_status'] = status
    sample['features'][field]['review_status'] = 'partial'
    sample['review_completeness']['current_scope'].append({'publication': 'CN120500565A', 'anchors': keys, 'field': field, 'at': NOW})
    added.append(observation)

sample['scene_material'] = {
    'classification': 'explicit_laundry_microplastics_and_microfibres',
    'review_status': 'complete_in_saved_text_scope', 'verified_at': NOW,
    'basis': [{'anchor': k, 'excerpt': anchors[k], 'source_sha256': SHA} for k in ['p0004','p0123']],
    'boundary': 'p0004背景定义包含合成衣物微塑料/微纤维；p0123本方案过滤从衣物分离的微塑料，不宣称所有绒毛皆塑料。'
}
sample['review_completeness']['saved_text_review'] = {
    'verified_at': NOW, 'source_path': str(SOURCE), 'source_sha256': SHA,
    'anchors_read': 338, 'description_anchors': 'p0001-p0319',
    'claim_anchors': 'zh-cl0001-zh-cl0019', 'figures_visually_reviewed': False,
    'original_pdf_acquired': False, 'all_fields_addressed_in_this_scope': True
}
sample['review_completeness']['full_text_rechecked'] = False
sample['publications'][0]['review_status'] = 'complete_saved_text_review_original_pdf_and_figures_pending'
master['updated_at'] = NOW
master_text = dumps(master)
result = check_current(master)
assert result['observations'] == 73
assert all(f['observations'] for f in sample['features'].values())
assert all(json.dumps(s['prior_working_evidence'], sort_keys=True, ensure_ascii=False) ==
           json.dumps(o['prior_working_evidence'], sort_keys=True, ensure_ascii=False)
           for s,o in zip(master['samples'], original['samples']))
master_newline = '\r\n' if b'\r\n' in MASTER.read_bytes() else '\n'
master_sha = hashlib.sha256(master_text.replace('\n', master_newline).encode()).hexdigest()
release_path = H1 / 'current_release.json'
release = json.loads(release_path.read_text(encoding='utf-8'))
release.update(updated_at=NOW, current_observations=73, master_sha256=master_sha,
               weekly_used_percent=9, weekly_remaining_percent=91)

rows = list(csv.DictReader((RUN/'data/review_coverage.csv').read_text(encoding='utf-8-sig').splitlines()))
for row in rows:
    if row['publication'] == 'CN120500565A':
        f = sample['features'][row['field']]
        row.update(review_status=f['review_status'], support_status=f['support_status'], observation_count=str(len(f['observations'])))
out = io.StringIO(newline='')
writer = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator='\n')
writer.writeheader(); writer.writerows(rows)

card_path = RUN/'evidence/technical_cards/CN120500565A.md'
card = card_path.read_text(encoding='utf-8').split('## 未完成')[0]
card += '## 2026-10-01 保存全文复核补充\n\n'
card += '保存中文说明书319个anchor及19项已逐段复核；原PDF及20幅附图原页未取得，全文原页验收仍未完成。全部资格pending。\n\n'
for obs in added:
    card += f'### {obs["stage"]} / {obs["embodiment_id"]}\n\n{obs["interpretation"]}\n\n'
    card += f'支持：{obs["support_status"]}；对象：{obs["object"]}。路径：{obs["start"]} → {obs["end"]}。边界：{obs["boundary"]}。\n\n'
    card += '\n'.join('- ' + e['locator'] + '：' + e['evidence_excerpt'] for e in obs['evidence']) + '\n\n'
card += '## 仍未完成\n\n原PDF和附图原页、CN/WO权17连接词原件对照及法律资格待核。未定位字段只针对已保存文本范围，不能写成行业不存在或图文全文穷尽否定。\n'

index_path = RUN/'evidence/技术复核入口.md'
index = index_path.read_text(encoding='utf-8')
index = index.replace('本轮61条定点判断', '本轮73条定点判断')
index = index.replace('|[CN120500565A](technical_cards/CN120500565A.md)|6|全文、资格及未填字段|',
                      '|[CN120500565A](technical_cards/CN120500565A.md)|18|保存全文各字段已处理；原PDF/附图与资格待核|')

search = {
    'run_id': '20260929_r1', 'date': '2026-10-01', 'timezone': 'Asia/Shanghai',
    'purpose': 'CN120500565A缺失原PDF定向补证',
    'actual_queries': ['"CN120500565A" filetype:pdf','"CN120500565" pdf 专利','"CN120500565A" "PDF"','site:cnipa.gov.cn 专利 公布公告 全文 下载'],
    'exact_page': 'https://patents.google.com/patent/CN120500565A/zh',
    'official_entry': 'https://epub.cnipa.gov.cn/',
    'observations': ['Google页仍未提供可下载CN PDF链接；搜索只定位公开页/其他同族页',
                     'web.open官方入口返回Timeout fetching',
                     'IAB createBrowserTab官方入口：Timed out running CDP command Page.navigate for tab 1',
                     '一次getState：IAB目标URL但about:blank；Chrome通道nodeRepl.fetch request failed'],
    'original_pdf_saved': False, 'saved_result_count': 0, 'hit_count': None,
    'export_complete': False, 'genuine_search_screenshot_saved': False,
    'limitations': '结果数量不可作母集；无真实可审查截图；无登录/权限/网络设置改动；不重试失效通道。',
    'retrieval_window': '2026-10-01T12:39:00+08:00/2026-10-01T12:42:10+08:00',
    'time_precision': '工具调用所在窗口；未记录每个请求的精确毫秒，不伪造逐请求时点'
}
qa = dict(result, checked_at=NOW, master_sha256=master_sha, new_observations=12,
          saved_text_anchor_count=338, original_pdf_missing=True,
          full_text_complete_count=0, prior_evidence_unchanged=True,
          source_html_sha256=SHA, raw_source_unchanged=True,
          does_not_prove='原PDF图文全文穷尽、法律有效状态、正式统计或最终报告完成')
handoff_path = RUN/'handoff.md'
handoff = handoff_path.read_text(encoding='utf-8')
handoff += '\n## 2026-10-01 CN120500565A 保存全文技术补查\n\n'
handoff += '中文保存全文319说明书anchor与19项已逐段复核，补12条判断，当前合计73条。场景明确洗衣微塑料/微纤维；补截留、内部水流转移、底部积存、泵状态及密封/抽屉残水承接；独立维护排空、固体脱水、载体干燥和最终处置只在已读保存文本内未定位。p0145不能被写成已无残水，第一/二流路及七种导流实施方式不拼接。原PDF/附图缺口仍存在，14资格仍pending，全文完成数0，P4-P7未放行。见QA/CN120500565A_saved_text_review_20261001.json及search/CN120500565A_source_gap_20261001.json。\n'
outputs = {
    MASTER: master_text, release_path: dumps(release), RUN/'data/review_coverage.csv': out.getvalue(),
    card_path: card, index_path: index,
    RUN/'search/CN120500565A_source_gap_20261001.json': dumps(search),
    RUN/'QA/CN120500565A_saved_text_review_20261001.json': dumps(qa), handoff_path: handoff
}
print('*** Begin Patch\n' + ''.join(patch_for(p,t) for p,t in outputs.items()) + '*** End Patch')
