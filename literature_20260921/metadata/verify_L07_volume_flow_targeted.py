from pathlib import Path
import openpyxl, statistics, json
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"supplements/hamann2025_data.xlsx"
ws=openpyxl.load_workbook(SRC,data_only=True,read_only=True)["volume-flow"]
rows=list(ws.values); h=list(rows[0]); data=[dict(zip(h,r),excel_row=i) for i,r in enumerate(rows[1:],2)]
def pick(**kw): return [r for r in data if all(r[k]==v for k,v in kw.items())]
def summary(rs):
 v=[r["messung"] for r in rs if isinstance(r["messung"],(int,float))]
 return {"rows":[r["excel_row"] for r in rs],"n_15L_records":len(v),"values_s":v,"mean_s":statistics.mean(v),"sample_sd_s":statistics.stdev(v) if len(v)>1 else None,"independent_trial_n":"not verifiable: source has no run identifier"}
no=pick(inlet="snail",element="none",mixer=0,microplastic="none",total_volume=25,filt_volume=20,p_conc="NA",siphon="no",ventile="no",time=15)
sy=pick(inlet="snail",element="none",mixer=0,microplastic="none",total_volume=25,filt_volume=20,p_conc="NA",siphon="yes",ventile="no",time=15)
clean=pick(inlet="snail",element="Small-11",mixer=5,microplastic="cotton",menge_g=2.5,total_volume=25,filt_volume=20,p_conc=0.1,siphon="no",ventile="no",time=15)
valves=pick(inlet="snail",element="Small-11",mixer=5,microplastic="cotton",menge_g=2.5,total_volume=25,filt_volume=20,p_conc=0.1,siphon="no",ventile="yes",time=15)
clean_all=clean
for_group=summary(no); for_siphon=summary(sy); for_clean=summary(clean_all); for_valves=summary(valves)
print(json.dumps({"filters":{"siphon_baseline":{"inlet":"snail","element":"none","mixer":0,"microplastic":"none","total_volume":25,"filt_volume":20,"p_conc":"NA","siphon":"no","ventile":"no","time":15},"siphon":{"inlet":"snail","element":"none","mixer":0,"microplastic":"none","total_volume":25,"filt_volume":20,"p_conc":"NA","siphon":"yes","ventile":"no","time":15},"cleaning_no_valves":{"inlet":"snail","element":"Small-11","mixer":5,"microplastic":"cotton","menge_g":2.5,"total_volume":25,"filt_volume":20,"p_conc":0.1,"siphon":"no","ventile":"no","time":15},"cleaning_valves":{"inlet":"snail","element":"Small-11","mixer":5,"microplastic":"cotton","menge_g":2.5,"total_volume":25,"filt_volume":20,"p_conc":0.1,"siphon":"no","ventile":"yes","time":15}},"results":{"no_siphon":for_group,"siphon":for_siphon,"no_valves_cleaning":for_clean,"valves":for_valves},"ratios":{"siphon_time_percent_of_baseline":100*for_siphon["mean_s"]/for_group["mean_s"],"cleaning_time_percent_of_baseline":100*for_valves["mean_s"]/for_clean["mean_s"]},"note":"messung rows are 15 L records; independent trial n is not verifiable without a run identifier."},ensure_ascii=False,indent=2))
