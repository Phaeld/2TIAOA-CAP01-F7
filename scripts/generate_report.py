"""Rebuild the four-page FIAP report. Update delivery.json after real deployment."""
from pathlib import Path
import json
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Flowable

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/relatorio-tecnico.pdf'
status_path = ROOT / 'docs/delivery.json'
status = json.loads(status_path.read_text()) if status_path.exists() else {}
ink = colors.HexColor('#173f38')
teal = colors.HexColor('#087c6b')
muted = colors.HexColor('#657d73')
styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='TitleC',fontName='Helvetica-Bold',fontSize=27,leading=31,textColor=ink,spaceAfter=16))
styles.add(ParagraphStyle(name='SectionC',fontName='Helvetica-Bold',fontSize=14,leading=18,textColor=ink,spaceBefore=17,spaceAfter=9))
styles.add(ParagraphStyle(name='BodyC',fontName='Helvetica',fontSize=10,leading=15,textColor=ink,spaceAfter=9))
styles.add(ParagraphStyle(name='SmallC',fontName='Helvetica',fontSize=8,leading=11,textColor=muted,spaceAfter=7))
styles.add(ParagraphStyle(name='TagC',fontName='Helvetica-Bold',fontSize=8,leading=12,textColor=teal,spaceAfter=12))
story=[]
def p(text,style='BodyC'):
    story.append(Paragraph(text,styles[style]))
def title(number,name):
    p('FIAP / CARDIOIA / FASE 7 / '+number,'TagC');p(name,'TitleC')
def table(rows,widths):
    cells=[[Paragraph(str(c),styles['SmallC']) for c in row] for row in rows]
    t=Table(cells,colWidths=widths,hAlign='LEFT')
    t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#e5eee7')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),8),('BOTTOMPADDING',(0,0),(-1,-1),7),('LINEBELOW',(0,0),(-1,-1),.4,colors.HexColor('#dce5df'))]))
    story.append(t)

class Architecture(Flowable):
    def __init__(self):
        Flowable.__init__(self);self.width=490;self.height=280
    def draw(self):
        c=self.canv
        def box(x,y,w,h,lines,fill='#edf3ed'):
            c.setFillColor(colors.HexColor(fill));c.setStrokeColor(colors.HexColor('#c9dcd0'));c.roundRect(x,y,w,h,8,fill=1,stroke=1)
            c.setFillColor(ink)
            for i,line in enumerate(lines):
                c.setFont('Helvetica-Bold' if i==0 else 'Helvetica',9 if i==0 else 8)
                c.drawCentredString(x+w/2,y+h-19-i*14,line)
        def arrow(x1,y1,x2,y2,label=None):
            c.setStrokeColor(teal);c.setLineWidth(1.3);c.line(x1,y1,x2,y2)
            if x2>x1:c.line(x2,y2,x2-5,y2-3);c.line(x2,y2,x2-5,y2+3)
            elif y2<y1:c.line(x2,y2,x2-3,y2+5);c.line(x2,y2,x2+3,y2+5)
            if label:c.setFont('Helvetica',7);c.setFillColor(muted);c.drawCentredString((x1+x2)/2,(y1+y2)/2+6,label)
        box(0,209,125,64,['Sensor + MicroPython','Wokwi / Raphael','Temperatura, BPM, botão'])
        box(182,209,130,64,['Backend Python','FastAPI / Render','Validação + orquestração'])
        box(367,209,123,64,['Interfaces','React/Vite - Vercel','Expo / APK - Android'])
        arrow(125,240,182,240,'HTTPS');arrow(312,240,367,240,'JWT / 5 s')
        box(367,113,123,55,['SQLite','Leituras + resultados'])
        arrow(247,140,367,140,'Gravar / consultar')
        box(0,12,145,66,['Modelos locais','F2: TF-IDF; F6: Random Forest','F4: ResNet50 + Grad-CAM'])
        box(173,12,145,66,['Regras / protocolos','Alertas do sensor: F3','ProtocolAgent: F6'])
        box(346,12,144,66,['APIs de IA','Gemini: F5','Corpus textual: F1'])
        c.setStrokeColor(teal);c.line(247,209,247,96);c.line(73,96,418,96)
        for x in [73,247,418]:arrow(x,96,x,78)
        c.setFont('Helvetica',7);c.setFillColor(muted);c.drawString(0,190,'Retorno ao Wokwi: feedback.led + label')

title('01','Coração Sob Controle')
p('Relatório técnico do MVP integrado','SectionC')
p('Grupo São Paulo e Interior | Tecnologia em Inteligência Artificial | 31/10/2026','SmallC')
p('A fase 7 transforma as entregas anteriores em uma aplicação com login, leitura de sinais, inferência e visualização Web/Android. O escopo prioriza um único backend Python, duas interfaces e um contrato simples de integração com MicroPython, sem infraestrutura distribuída adicional.')
p('Objetivo e escopo','SectionC')
p('Demonstrar o fluxo Sensor → MicroPython → Backend → IA → UI com dados simulados, disponibilizar a Web na Vercel e gerar APK via Expo EAS. O núcleo já conecta modelos de risco e linguagem, visão computacional e histórico de leituras. A captura física/simulada no Wokwi é responsabilidade de Raphael.')
table([['Fase','Componente consolidado'],['1','Corpus textual recuperado para contexto do assistente.'],['2','Extração de sintomas e TF-IDF + regressão logística; portal agora consome API real.'],['3','Regras de alertas preservadas; contrato HTTP autenticado para sensores.'],['4','ResNet50 treinada e Grad-CAM; fluxo de upload migrado para Web/Expo.'],['5','Assistência Gemini, mantendo credenciais somente no backend.'],['6','Random Forest original e ProtocolAgent, executados em sequência pelo Python.']],[45,445])
p('Equipe e colaboração','SectionC')
p('Jonas Tadeu V. Fernandes (RM563027); Levi Passos Silveira Marques (RM56557); Raphael da Silva (RM561452); Raphael Dinelli Neto (RM562892); Yan Pimental Cotta (RM562836).','SmallC')
p('Yan: backend, interfaces, deploy e documentação. Raphael: MicroPython/Wokwi e feedback visual. Grupo: revisão, teste físico e vídeo. Tutor: Caique Nonato da Silva Bezerra. Coordenador: André Godoi.','SmallC')
story.append(PageBreak())
title('02','Arquitetura e fluxo')
story.append(Architecture());story.append(Spacer(1,10))
p('Comunicação fim-a-fim','SectionC')
p('O dispositivo envia JSON a POST /api/v1/readings usando X-Device-Key. A API valida identidade, tipos, faixas e horário, calcula alertas e previsão, grava o evento e devolve a cor do LED. Web e APK consultam /dashboard a cada cinco segundos; após 30 segundos sem amostra recente, indicam dados antigos.')
p('Cada leitura possui event_id. Reenvio idêntico é idempotente; repetir ID com conteúdo diferente retorna 409. O histórico é ordenado pelo horário da captura, impedindo que uma amostra atrasada substitua a mais recente.')
p('Interpretação das previsões','SectionC')
p('O modelo F6 prevê risco <b>operacional hospitalar sintético</b>. BPM/temperatura vêm da simulação; os demais indicadores usam contexto sintético explícito, salvo SpO2/pressão quando fornecidos. A origem de cada feature é retornada pela API. Uma amostra de sensor não equivale à média de uma população: a integração é didática, sem validação clínica.')
p('Os alertas e o LED seguem as regras F3 e são independentes da probabilidade F6. Protocolos F6 são apresentados como simulações. O Python executa os agentes de forma determinística; o chat Gemini explica a saída calculada, sem ser responsável por inventar valores ou executar ações.','SmallC')
story.append(PageBreak())
title('03','Implementação e validação')
table([['Camada','Implementação'],['Backend','FastAPI/Python 3.12; JWT com 2 h; chave IoT restrita; SQLite; OpenAPI; limites de corpo/chamadas e CORS explícito.'],['Web','React + Vite. Login, painel, histórico, análise textual, imagem e chat. vercel.json com rotas SPA.'],['Mobile','React Native + Expo. Login, sinais, histórico, chat e imagem. android.package=br.com.cardioia.fiap; eas.json preview/APK.'],['IA','scikit-learn 1.9.1 compatível com joblib original. TensorFlow/Keras legado opcional para imagem. Gemini via HTTPS.'],['Entrega','Workflow GitHub Actions para testes e builds. Vercel publica após testes no push de main; Render publica o mesmo SHA via API e aguarda status live. Fluxo publicado e validado.']],[72,418])
p('Verificações executadas','SectionC')
p('27 testes de integração passaram: login, token expirado, acesso negado, chave/dispositivo, validação, idempotência, conflito, persistência, ordenação e dados antigos, modelo original, NLP, fallback/provedor, indisponibilidade de visão, limite de corpo e CORS.')
p('O caso original da F6 retornou probabilidade 0,99, classe HIGH e protocolos P02/P05/P08/P10. Build Web, bundle Android e APK assinado no EAS concluíram. ResNet50 e Grad-CAM executaram em uma imagem sintética, verificando o runtime, sem medir acurácia.')
p('Na Web pública: login e cenário de alerta atualizaram 132 bpm e 39,1 °C. O painel separou alerta do sensor HIGH e risco operacional LOW (18,5%). Gemini respondeu pela Web. Na API pública, 16 verificações passaram, incluindo sensores, modelos, chat e CORS.')
p('O que ainda precisa ser comprovado','SectionC')
p('O APK foi gerado e seu arquivo verificado, mas a instalação em Android físico será validada por Raphael/grupo. Wokwi e vídeo fim-a-fim permanecem pendentes. O helper de transporte MicroPython não é uma simulação concluída. Evidências de deploy e testes estão em docs/evidence/.','SmallC')
story.append(PageBreak())
title('04','Entrega e limitações')
p('Hospedagem adequada ao MVP','SectionC')
p('O perfil gratuito Render publicou o núcleo leve, desativa a visão e usa disco efêmero. Pode suspender por inatividade; abrir /health antes da demonstração. A hospedagem de visão foi adiada por Yan. Para todos os módulos, preparar instância com pelo menos 2 GB, TensorFlow e disco persistente. O smoke local de visão atingiu cerca de 836 MB no macOS; isso não é medição Linux. Custos precisam ser aprovados antes da contratação.')
p('Segurança e limites de uso','SectionC')
p('A aplicação tem um único usuário/paciente de demonstração e não deve receber dados reais de saúde. Tokens ficam em sessionStorage (Web) e SecureStore (mobile). Credenciais não são versionadas. Chave IoT só permite envio ao dispositivo/paciente configurado. O sistema não envia mensagens nem aciona serviços de emergência.')
p('Modelos e base textual são educacionais. O classificador textual usa somente 50 exemplos; pode falhar com negação/contexto. O modelo F6 foi treinado em dados sintéticos e há diferença de distribuição. Os resultados não constituem diagnóstico nem indicação de tratamento.')
p('Registro dos links','SectionC')
table([['Entregável','Registro'],['Repositório','https://github.com/Phaeld/2TIAOA-CAP01-F7'],['Web Vercel',(status.get('web_url') or 'Pendente de deploy verificado')],['Backend',(status.get('api_url') or 'Pendente de deploy verificado')],['Expo / APK',('Build EAS concluído: 01b49027-ce04-4310-8c76-30e3ada07c04. Link/QR e APK no README; teste físico pendente.' if status.get('expo_build_status') == 'finished' else 'Pendente de build EAS e teste físico')],['Wokwi / vídeo','Responsáveis: Raphael / grupo. Links pendentes.']],[80,410])
p('Fechamento até 10/11/2026','SectionC')
p('Phaeld deve tornar o repositório privado e compartilhar com o tutor. Concluir Wokwi, instalar APK, coletar prints e gravar vídeo de até cinco minutos. Web, API, APK e CI/CD já possuem links/evidências no README. Fechar este relatório com Wokwi e teste físico, sem declarar conclusão antes da validação.','SmallC')
p('Referências: vercel.com/docs/project-configuration/vercel-json; docs.expo.dev/build-reference/apk; render.com/docs/compute-plans; render.com/docs/disks; ai.google.dev/api/generate-content; docs.wokwi.com/guides/esp32-wifi. Fontes, commits e checksums: docs/migration-manifest.json.','SmallC')

def footer(canvas,doc):
    canvas.setStrokeColor(colors.HexColor('#dce5df'));canvas.line(52,44,543,44)
    canvas.setFont('Helvetica',8);canvas.setFillColor(muted)
    canvas.drawString(52,30,'CardioIA | Fase 7 | Relatório técnico - revisão de 31/10/2026')
    canvas.drawRightString(543,30,str(doc.page)+' / 4')

SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=52,leftMargin=52,topMargin=42,bottomMargin=60,title='CardioIA - Relatório técnico Fase 7',author='Grupo São Paulo e Interior').build(story,onFirstPage=footer,onLaterPages=footer)
print(OUT)
