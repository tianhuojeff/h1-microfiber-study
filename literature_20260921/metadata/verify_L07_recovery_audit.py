from pathlib import Path
import openpyxl, collections, statistics, hashlib, json
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'supplements/hamann2025_data.xlsx'
SHEET='filtration-efficiency'
BASE=['Ort','trial','analyst','inlet','FiF_length','AoA','mesh_size_µm','A0','MP_type','MP_Konz_SOLL_g','MP_Menge_IST_g','cleaning_L','C_mode']
STRICT=BASE+['Vol_total_L','Vol_filt_L']
def group(rows, cols):
 g=collections.defaultdict(list)
 for r in rows:g[tuple(r[c] for c in cols)].append(r)
 return g
def complete(v): return len(v)==3 and {r['name'] for r in v}=={'concentrate','permeate','retentate'}
def obj(k,v,cols):
    rec=sorted({r['recovery_REL'] for r in v if r['recovery_REL'] is not None},key=str)
    return {'key':dict(zip(cols,k)),'source_rows':[r['excel_row'] for r in v],'names':[r['name'] for r in v],'n_rows':len(v),'complete_three_streams':complete(v),'recovery_REL':rec[0] if len(rec)==1 else rec,'recovery_REL_values':rec,'stream_recoveries':[{'stream':r['name'],'source_row':r['excel_row'],'value':r['recovery_REL']} for r in v]}
def stats(gs,mp,conflict_policy='strict'):
    vals=[]
    for x in gs:
        if not x['complete_three_streams'] or x['key']['MP_type']!=mp: continue
        if isinstance(x['recovery_REL'],(int,float)): vals.append(x['recovery_REL'])
        elif conflict_policy=='first_concentrate':
            # The merged trial-16 group has one stored recovery_REL on the
            # concentrate/permeate rows and a conflicting value on retentate.
            # Keep the stored value; do not rewrite the workbook.
            selected=[r['value'] for r in x['stream_recoveries'] if r['stream']=='concentrate']
            assert len(selected)==1 and isinstance(selected[0],(int,float))
            vals.append(selected[0])
    return {'n':len(vals),'mean_percent':statistics.mean(vals) if vals else None,'sample_sd_percent':statistics.stdev(vals) if len(vals)>1 else None}
rows=list(openpyxl.load_workbook(SOURCE,data_only=True,read_only=True)[SHEET].values)
h=list(rows[0]); data=[dict(zip(h,r),excel_row=i) for i,r in enumerate(rows[1:],2)]
sg=group(data,STRICT); mg=group(data,BASE)
so=[obj(k,v,STRICT) for k,v in sg.items()]; mo=[obj(k,v,BASE) for k,v in mg.items()]
print(json.dumps({'sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'strict':{'groups':len(so),'complete':sum(x['complete_three_streams'] for x in so),'incomplete_or_control':sum(not x['complete_three_streams'] for x in so),'F2':stats(so,'F2'),'PA':stats(so,'PA')},'merge_volume_anomaly':{'groups':len(mo),'complete':sum(x['complete_three_streams'] for x in mo),'incomplete_or_control':sum(not x['complete_three_streams'] for x in mo),'F2':stats(mo,'F2','first_concentrate'),'PA':stats(mo,'PA','first_concentrate')},'strict_incomplete_or_control':[x for x in so if not x['complete_three_streams']], 'merged_incomplete_or_control':[x for x in mo if not x['complete_three_streams']]},ensure_ascii=False,indent=2))
