from pathlib import Path
import hashlib,json
BASE=Path(__file__).resolve().parent
ROOT=BASE.parent.parent
PDF=ROOT/'h1-study/patents/WO2024199585A1.pdf'
sha=hashlib.sha256(PDF.read_bytes()).hexdigest()
TRANS=BASE/'evidence/WO2024199585A1_原页人工回读.md'

def evidence(quote,loc,page,typ):
    image=BASE/'evidence/wo2024199585_pages'/page
    return {'source_path':str(PDF),'source_sha256':sha,'locator':loc,'quote':quote,'evidence_type':typ,
            'verification_method':'root_visual_readback_of_rendered_original_pdf','transcription_path':str(TRANS),
            'page_image_path':str(image),'page_image_sha256':hashlib.sha256(image.read_bytes()).hexdigest()}
def field(summary,ev):
    return dict(judgment='explicit',summary=summary,evidence=ev,unknown_reason='',review_scope='原PDF物理14、15、26、27页主代理完整目视回读；其余页不据此作否定。')

fields={
'solids_dewatering':field('可选下游离心分离截留物附着液，或由压机压缩并去除残余液；这是收集物含水量降低，不是过滤腔排空。',[
    evidence('beispielsweise einer Zentrifuge, um am Retentat anhaftendes Fluid abzutrennen','物理14页/印刷12页第3—5行','description-14.png','description'),
    evidence('Ferner und zusätzlich kann das Retentat in eine Presse münden, die das Retentat zusammendrücken und verbliebenes Fluid aus dem Retentat entfernen kann.','物理14页/印刷12页第6—8行','description-14.png','description')]),
'removal':field('权1/8明示截留物在容器收集并从容器取出；权5另述滤元可单独取出/清洗。未据此认定收集容器本身可拆卸。',[
    evidence('dass das Retentat in einem Behälter (7) auffangbar und aus dem Behälter (7) entnehmbar ist.','物理27页/印刷25页权8','claims-27.png','claim'),
    evidence('dass das Filterelement (3) mit der maschen- oder porenförmige Filterstruktur (5) einzeln aus der bionischen Vorrichtung (1) entnehm- und/oder waschbar ist.','物理27页/印刷25页权5','claims-27.png','claim')]),
'liquid_route':field('主过滤液经网状/多孔滤结构侧向进入滤液出口13；截留物流经出口14导出或抽吸并容器收集。外部离心/压机脱出液终点在所读页未说明。',[
    evidence('das Fluid lateral durch die maschen- oder porenförmige Filterstruktur (5) des Filterelements (3) und den Filtratablauf (13) austritt,','物理26页/印刷24页权1','claims-26.png','claim'),
    evidence('zentral im Bereich des Filterelements (3) über einen Retentatablauf (14) ableitbar oder absaugbar und in einem Behälter (7) auffangbar und entnehmbar ist,','物理26页/印刷24页权1','claims-26.png','claim')]),
'state_switch':field('实施例滤液出口阀关闭、截留物出口阀打开可加强抽吸以收集颗粒；阀控制也支持压力脉冲清理，但具体周期/时长未知。',[
    evidence('Dieser wird stärker, wenn beispielsweise ein Ventil im Bereich des Filtratablaufs schließt, während im Bereich des Retentatablaufs beispielsweise ein Ventil öffnet.','物理15页/印刷13页第7—10行','description-15.png','description')])}
# Use the visually verified grammatical form from the source, verbatim.
fields['removal']['evidence'][1]['quote']='dass das Filterelement (3) mit der maschen- oder porenförmigen Filterstruktur (5) einzeln aus der bionischen Vorrichtung (1) entnehm- und/oder waschbar ist.'
fields['removal'].update(removal_object=['loose_or_compacted_solids','filter_element'],integrated_or_separate='截留物从容器取出；滤元单独取出是另一特征，容器可拆未据此证明',text_disclosed_only=True)
record={'publication':'WO2024199585A1','fields':fields,'additional_sources':[{'source_path':str(PDF),'source_sha256':sha,'url':'https://patents.google.com/patent/WO2024199585A1/en','source_kind':'original_WO_publication_PDF'},{'source_path':str(TRANS),'source_sha256':hashlib.sha256(TRANS.read_bytes()).hexdigest(),'source_kind':'root_visual_transcription'}],
        'sequence':[{'variant':'容器收集取出','steps':['截留物经出口14导出/抽吸','容器收集','从容器取出截留物'],'evidence_locators':['原PDF物理15页/印刷13页第4—15行；权1/8'],'ordering_certainty':'explicit'},{'variant':'可选直接进一步处理','steps':['截留物流直接导向进一步处理','离心分离附着液，或追加压机压缩去液'],'evidence_locators':['原PDF物理14页/印刷12页第1—8行'],'ordering_certainty':'explicit'}],
        'additional_boundary_notes':['主代理已目视核原PDF：权8取出主体为截留物，不是“可拆收集容器”；外部离心/压机是可选路线，不能强拼为必要序列。']}
(BASE/'pdf_root_overrides.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding='utf-8')
print('PDF override saved',sha)
