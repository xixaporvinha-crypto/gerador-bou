import os
import re
import sys
import unicodedata
from datetime import datetime
import streamlit as st
import io

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.utils import ImageReader, simpleSplit
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.pdfgen import canvas
except ImportError:
    st.error("ERRO: A biblioteca 'reportlab' nao esta instalada.")
    sys.exit(1)

st.set_page_config(
    page_title="Gerador BOU - Painel Web",
    page_icon="🛡️",
    layout="centered"
)

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .titulo { text-align: center; font-size: 2.2rem; font-weight: bold; color: #ffffff; margin-bottom: 0px; }
    .subtitulo { text-align: center; color: #8a99ad; margin-bottom: 30px; }
    .divisor { border-bottom: 1px solid #262730; margin-bottom: 20px; padding-bottom: 10px; font-size: 1.2rem; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

PASTA = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(PASTA, "assets")
PASTA_LOGOS_BANCO = os.path.join(ASSETS, "logo_banco")
PASTA_LOGOS_ESTADOS = os.path.join(ASSETS, "logo_estados")
PASTA_DADOS = os.path.join(ASSETS, "dados")

LARGURA, ALTURA = A4
LINHA_X0 = 30.75
LINHA_X1 = 565.50

ESTADOS = {
    "AC": {"nome": "Acre", "governo": "GOVERNO DO ESTADO DO ACRE", "policia": "POLÍCIA CIVIL DO ESTADO DO ACRE", "endereco": "Rua Quintino Bocaiúva, 1490 - Bosque, Rio Branco - AC, 69900-640, TEL.: (68) 3212-4000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "CARLOS EDUARDO MENDES OLIVEIRA", "investigador_cargo": "Investigador Policial - 112.045-1"},
    "AL": {"nome": "Alagoas", "governo": "GOVERNO DO ESTADO DE ALAGOAS", "policia": "POLÍCIA CIVIL DO ESTADO DE ALAGOAS", "endereco": "Av. Fernandes Lima, 2345 - Farol, Maceió - AL, 57050-000, TEL.: (82) 3315-2400", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "ROBERTO ALVES COSTA NETO", "investigador_cargo": "Investigador Policial - 223.118-4"},
    "AP": {"nome": "Amapá", "governo": "GOVERNO DO ESTADO DO AMAPÁ", "policia": "POLÍCIA CIVIL DO ESTADO DO AMAPÁ", "endereco": "Av. FAB, 1685 - Central, Macapá - AP, 68900-074, TEL.: (96) 3212-5800", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "PAULO HENRIQUE SILVA RAMOS", "investigador_cargo": "Investigador Policial - 089.334-2"},
    "AM": {"nome": "Amazonas", "governo": "GOVERNO DO ESTADO DO AMAZONAS", "policia": "POLÍCIA CIVIL DO ESTADO DO AMAZONAS", "endereco": "Av. André Araújo, 1923 - Aleixo, Manaus - AM, 69060-000, TEL.: (92) 3648-1000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "MARCOS VINICIUS FERREIRA LIMA", "investigador_cargo": "Investigador Policial - 445.201-8"},
    "BA": {"nome": "Bahia", "governo": "GOVERNO DO ESTADO DA BAHIA", "policia": "POLÍCIA CIVIL DO ESTADO DA BAHIA", "endereco": "Av. Centenário, 2883 - Chame-Chame, Salvador - BA, 40155-150, TEL.: (71) 3116-6000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "JULIO CESAR SANTOS BARBOSA", "investigador_cargo": "Investigador Policial - 567.890-3"},
    "CE": {"nome": "Ceará", "governo": "GOVERNO DO ESTADO DO CEARÁ", "policia": "POLÍCIA CIVIL DO ESTADO DO CEARÁ", "endereco": "Av. Bezerra de Menezes, 581 - São Gerardo, Fortaleza - CE, 60325-000, TEL.: (85) 3101-2000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "FRANCISCO DAS CHAGAS MOURA", "investigador_cargo": "Investigador Policial - 334.672-1"},
    "DF": {"nome": "Distrito Federal", "governo": "GOVERNO DO DISTRITO FEDERAL", "policia": "POLÍCIA CIVIL DO DISTRITO FEDERAL", "endereco": "SAF Sul Quadra 6 - Zona Cívico-Administrativa, Brasília - DF, 70040-912, TEL.: (61) 3207-4000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "RICARDO ALMEIDA PINTO JUNIOR", "investigador_cargo": "Investigador Policial - 901.245-6"},
    "ES": {"nome": "Espírito Santo", "governo": "GOVERNO DO ESTADO DO ESPÍRITO SANTO", "policia": "POLÍCIA CIVIL DO ESTADO DO ESPÍRITO SANTO", "endereco": "Av. Governador Bley, 236 - Centro, Vitória - ES, 29010-150, TEL.: (27) 3636-1100", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "ANDERSON LUIZ PEREIRA GOMES", "investigador_cargo": "Investigador Policial - 178.456-9"},
    "GO": {"nome": "Goiás", "governo": "GOVERNO DO ESTADO DE GOIÁS", "policia": "POLÍCIA CIVIL DO ESTADO DE GOIÁS", "endereco": "Av. Anhanguera, 7171 - St. Oeste, Goiânia - GO, 74110-010, TEL.: (62) 3201-1500", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "DIEGO FERNANDES CASTRO SILVA", "investigador_cargo": "Investigador Policial - 612.903-5"},
    "MA": {"nome": "Maranhão", "governo": "GOVERNO DO ESTADO DO MARANHÃO", "policia": "POLÍCIA CIVIL DO ESTADO DO MARANHÃO", "endereco": "Av. dos Holandeses, s/n - Calhau, São Luís - MA, 65071-380, TEL.: (98) 3214-8000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "RAFAEL SOUSA NASCIMENTO", "investigador_cargo": "Investigador Policial - 256.781-0"},
    "MT": {"nome": "Mato Grosso", "governo": "GOVERNO DO ESTADO DE MATO GROSSO", "policia": "POLÍCIA CIVIL DO ESTADO DE MATO GROSSO", "endereco": "Av. Escolástico, 346 - Bandeirantes, Cuiabá - MT, 78010-200, TEL.: (65) 3613-5630", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "023ª Delegacia", "investigador": "ANDRE RELVA SANTANA GANANÇA", "investigador_cargo": "Investigador Policial - 968.961-3"},
    "MS": {"nome": "Mato Grosso do Sul", "governo": "GOVERNO DO ESTADO DE MATO GROSSO DO SUL", "policia": "POLÍCIA CIVIL DO ESTADO DE MATO GROSSO DO SUL", "endereco": "Rua Rui Barbosa, 3500 - Monte Castelo, Campo Grande - MS, 79010-220, TEL.: (67) 3318-4000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "LUCIANO ROBERTO DIAS MELO", "investigador_cargo": "Investigador Policial - 401.556-7"},
    "MG": {"nome": "Minas Gerais", "governo": "GOVERNO DO ESTADO DE MINAS GERAIS", "policia": "POLÍCIA CIVIL DO ESTADO DE MINAS GERAIS", "endereco": "Av. Presidente Carlos Luz, 1275 - Caiçaras, Belo Horizonte - MG, 31230-000, TEL.: (31) 3330-7000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "GUSTAVO HENRIQUE CAMPOS REIS", "investigador_cargo": "Investigador Policial - 789.012-4"},
    "PA": {"nome": "Pará", "governo": "GOVERNO DO ESTADO DO PARÁ", "policia": "POLÍCIA CIVIL DO ESTADO DO PARÁ", "endereco": "Av. Magalhães Barata, 651 - São Brás, Belém - PA, 66063-240, TEL.: (91) 3201-2000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "EDUARDO BRITO FIGUEIREDO", "investigador_cargo": "Investigador Policial - 345.678-2"},
    "PB": {"nome": "Paraíba", "governo": "GOVERNO DO ESTADO DA PARAÍBA", "policia": "POLÍCIA CIVIL DO ESTADO DA PARAÍBA", "endereco": "Av. Duarte da Silveira, 600 - Centro, João Pessoa - PB, 58013-280, TEL.: (83) 3218-5000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "THIAGO LACERDA FREITAS", "investigador_cargo": "Investigador Policial - 512.349-8"},
    "PR": {"nome": "Paraná", "governo": "GOVERNO DO ESTADO DO PARANÁ", "policia": "POLÍCIA CIVIL DO ESTADO DO PARANÁ", "endereco": "Rua Desembargador Westphalen, 35 - Centro, Curitiba - PR, 80010-110, TEL.: (41) 3313-1000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "FELIPE AUGUSTO RODRIGUES", "investigador_cargo": "Investigador Policial - 678.901-3"},
    "PE": {"nome": "Pernambuco", "governo": "GOVERNO DO ESTADO DE PERNAMBUCO", "policia": "POLÍCIA CIVIL DO ESTADO DE PERNAMBUCO", "endereco": "Rua da Aurora, 485 - Boa Vista, Recife - PE, 50050-000, TEL.: (81) 3181-2000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "BRUNO CESAR ALBUQUERQUE", "investigador_cargo": "Investigador Policial - 234.567-1"},
    "PI": {"nome": "Piauí", "governo": "GOVERNO DO ESTADO DO PIAUÍ", "policia": "POLÍCIA CIVIL DO ESTADO DO PIAUÍ", "endereco": "Av. Frei Serafim, 2352 - Centro/Sul, Teresina - PI, 64001-020, TEL.: (86) 3216-1000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "LEONARDO MATOS VIEIRA", "investigador_cargo": "Investigador Policial - 890.123-5"},
    "RJ": {"nome": "Rio de Janeiro", "governo": "GOVERNO DO ESTADO DO RIO DE JANEIRO", "policia": "POLÍCIA CIVIL DO ESTADO DO RIO DE JANEIRO", "endereco": "Rua da Relação, 42 - Centro, Rio de Janeiro - RJ, 20231-110, TEL.: (21) 2332-8000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "MARCELO ANDRADE TEIXEIRA", "investigador_cargo": "Investigador Policial - 456.789-0"},
    "RN": {"nome": "Rio Grande do Norte", "governo": "GOVERNO DO ESTADO DO RIO GRANDE DO NORTE", "policia": "POLÍCIA CIVIL DO ESTADO DO RIO GRANDE DO NORTE", "endereco": "Av. Coronel Estevam, 1959 - Alecrim, Natal - RN, 59020-000, TEL.: (84) 3232-2000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "PEDRO HENRIQUE DANTAS", "investigador_cargo": "Investigador Policial - 123.456-7"},
    "RS": {"nome": "Rio Grande do Sul", "governo": "GOVERNO DO ESTADO DO RIO GRANDE DO SUL", "policia": "POLÍCIA CIVIL DO ESTADO DO RIO GRANDE DO SUL", "endereco": "Av. João Pessoa, 2050 - Cidade Baixa, Porto Alegre - RS, 90040-000, TEL.: (51) 3288-1000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "ALEXANDRE SCHMIDT OLIVEIRA", "investigador_cargo": "Investigador Policial - 567.234-8"},
    "RO": {"nome": "Rondônia", "governo": "GOVERNO DO ESTADO DE RONDÔNIA", "policia": "POLÍCIA CIVIL DO ESTADO DE RONDÔNIA", "endereco": "Av. Presidente Dutra, 2986 - Centro, Porto Velho - RO, 76801-086, TEL.: (69) 3216-5000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "WELLINGTON SOUZA CARVALHO", "investigador_cargo": "Investigador Policial - 678.345-9"},
    "RR": {"nome": "Roraima", "governo": "GOVERNO DO ESTADO DE RORAIMA", "policia": "POLÍCIA CIVIL DO ESTADO DE RORAIMA", "endereco": "Av. Ville Roy, 5245 - São Vicente, Boa Vista - RR, 69303-340, TEL.: (95) 3621-1000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "JOSÉ ROBERTO ALMEIDA", "investigador_cargo": "Investigador Policial - 089.012-3"},
    "SC": {"nome": "Santa Catarina", "governo": "GOVERNO DO ESTADO DE SANTA CATARINA", "policia": "POLÍCIA CIVIL DO ESTADO DE SANTA CATARINA", "endereco": "Rua Paschoal Apóstolo Pítsica, 4840 - Agronômica, Florianópolis - SC, 88025-255, TEL.: (48) 3665-6000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "RODRIGO MACHADO BORGES", "investigador_cargo": "Investigador Policial - 345.901-2"},
    "SP": {"nome": "São Paulo", "governo": "GOVERNO DO ESTADO DE SÃO PAULO", "policia": "POLÍCIA CIVIL DO ESTADO DE SÃO PAULO", "endereco": "Av. São Luís, 99 - República, São Paulo - SP, 01046-001, TEL.: (11) 3311-3000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "RENATO APARECIDO SILVA", "investigador_cargo": "Investigador Policial - 812.345-6"},
    "SE": {"nome": "Sergipe", "governo": "GOVERNO DO ESTADO DE SERGIPE", "policia": "POLÍCIA CIVIL DO ESTADO DE SERGIPE", "endereco": "Av. Ministro Geraldo Barreto Sobral, 215 - Capucho, Aracaju - SE, 49080-470, TEL.: (79) 3226-1000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "DANIEL SANTOS MENEZES", "investigador_cargo": "Investigador Policial - 456.012-7"},
    "TO": {"nome": "Tocantins", "governo": "GOVERNO DO ESTADO DO TOCANTINS", "policia": "POLÍCIA CIVIL DO ESTADO DO TOCANTINS", "endereco": "Av. Teotônio Segurado, 102 Sul - Plano Diretor Sul, Palmas - TO, 77016-002, TEL.: (63) 3218-4000", "delegacia": "Delegacia Especializada de Repressão a Crimes Cibernéticos", "origem": "Delegacia de Polícia Digital", "circunscricao": "01ª Delegacia", "investigador": "FABIANO COSTA LIMA", "investigador_cargo": "Investigador Policial - 567.890-1"},
}
UFS_ORDENADAS = sorted(ESTADOS.keys())

def _registrar_fontes():
    candidatos = [r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\ARIAL.TTF"]
    bold_cand = [r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\ARIALBD.TTF"]
    fonte, fonte_b = "Helvetica", "Helvetica-Bold"
    for path in candidatos:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("ArialDoc", path))
            fonte = "ArialDoc"
            break
    for path in bold_cand:
        if os.path.exists(path):
            pdfmetrics.registerFont(TTFont("ArialDoc-Bold", path))
            fonte_b = "ArialDoc-Bold"
            break
    return fonte, fonte_b

FONTE, FONTE_B = _registrar_fontes()
MESES = {1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril", 5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto", 9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"}
DIAS = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"]

def data_extenso(dt=None):
    dt = dt or datetime.now()
    return f"{dt.day:02d} de {MESES[dt.month]} de {dt.year} - {DIAS[dt.weekday()]} às {dt.hour:02d}:{dt.minute:02d}"

def formatar_cpf(texto):
    numeros = "".join(filter(str.isdigit, str(texto)))
    if len(numeros) == 11:
        return f"{numeros[:3]}.{numeros[3:6]}.{numeros[6:9]}-{numeros[9:]}"
    return str(texto)

def formatar_celular(texto):
    numeros = "".join(filter(str.isdigit, str(texto)))
    if len(numeros) == 11:
        return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
    elif len(numeros) == 10:
        return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
    return str(texto)

def caminho_asset(uf, nome):
    if not nome: return None
    nome_base, ext_original = os.path.splitext(nome)
    extensoes = [ext_original, ".png", ".jpg", ".jpeg", ""]
    locais_busca = [PASTA_LOGOS_BANCO, os.path.join(PASTA_LOGOS_ESTADOS, uf.upper()), os.path.join(ASSETS, uf.upper()), ASSETS]
    for local in locais_busca:
        if not os.path.exists(local): continue
        for arq in os.listdir(local):
            for ext in extensoes:
                if arq.lower() == f"{nome_base}{ext}".lower():
                    return os.path.join(local, arq)
    return None

def carregar_texto_externo():
    candidatos_txt = [os.path.join(PASTA_DADOS, "dados.txt"), os.path.join(PASTA_DADOS, "dados"), os.path.join(PASTA, "dados.txt")]
    dados_txt = {
        "capitulacao": "Art. 154-A do Código Penal . Motivo Presumido Crime Cibernético - Invasão de Dispositivo Informático",
        "despacho": "Considerando a natureza da ocorrência, encaminhe-se este registro para o Departamento de Investigação de Crimes Cibernéticos para as devidas apurações e providências legais cabíveis."
    }
    for caminho in candidatos_txt:
        if os.path.exists(caminho):
            try:
                with open(caminho, "r", encoding="utf-8") as f:
                    conteudo = f.read()
                fato_match = re.search(r"FATO\s*AT[ÍI]PICO:?\s*(.*?)(?=\n\s*[A-Z\s]+:?|\Z)", conteudo, re.DOTALL | re.IGNORECASE)
                despacho_match = re.search(r"DESPACHO\s*DA\s*AUTORIDADE:?\s*(.*?)(?=\n\s*[A-Z\s]+:?|\Z)", conteudo, re.DOTALL | re.IGNORECASE)
                if fato_match: dados_txt["capitulacao"] = fato_match.group(1).strip()
                if despacho_match: dados_txt["despacho"] = despacho_match.group(1).strip()
                break
            except Exception:
                continue
    return dados_txt

def y_from_top(top_y): return ALTURA - top_y

def linha(c, top_y, grossa=False):
    altura_linha = 1.5 if grossa else 0.75
    c.setFillColorRGB(0, 0, 0)
    c.rect(LINHA_X0, y_from_top(top_y) - altura_linha, LINHA_X1 - LINHA_X0, altura_linha, stroke=0, fill=1)

def draw_img_fit(c, path, max_x, top_y, max_w, max_h, align="right"):
    if not path or not os.path.exists(path): return
    img = ImageReader(path)
    orig_w, orig_h = img.getSize()
    if orig_w <= 0 or orig_h <= 0: return
    scale = min(max_w / float(orig_w), max_h / float(orig_h))
    final_w, final_h = orig_w * scale, orig_h * scale
    x = max_x - final_w if align == "right" else max_x
    c.drawImage(img, x, y_from_top(top_y + max_h) + ((max_h - final_h) / 2.0), width=final_w, height=final_h, preserveAspectRatio=True, mask="auto")

def gerar_pdf_bytes(dados):
    dados = {**dados, "inicio": data_extenso(datetime.now())}
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    M = 30.5
    uf = dados["uf"]
    est = ESTADOS[uf]
    
    # Pagina 1
    logo_pc = caminho_asset(uf, "logo_policia.png")
    if logo_pc: c.drawImage(ImageReader(logo_pc), 20.7, y_from_top(26.3) - 127.2, width=108, height=127.2, preserveAspectRatio=True, mask="auto")
    
    cx = 350
    c.setFont(FONTE_B, 9)
    c.drawCentredString(cx, y_from_top(31.8 + 9), est["governo"])
    c.drawCentredString(cx, y_from_top(49.8 + 9), "SECRETARIA DE ESTADO DA SEGURANÇA PÚBLICA")
    c.setFont(FONTE, 9)
    c.drawCentredString(cx, y_from_top(67.8 + 9), est["policia"])
    c.drawCentredString(cx, y_from_top(85.1 + 9), dados["endereco"])
    c.setFont(FONTE_B, 9)
    c.drawCentredString(cx, y_from_top(101.6 + 9), dados["delegacia"])

    linha(c, 160.3, grossa=True)
    linha(c, 184.3, grossa=True)
    c.setFont(FONTE_B, 11)
    c.drawString(M, y_from_top(196.8 + 11), "REGISTRO DE OCORRÊNCIA")
    c.setFont(FONTE_B, 10)
    c.drawRightString(LARGURA - 30.5, y_from_top(196.8 + 10), f"No. {dados['numero']}")
    linha(c, 218.8, grossa=True)

    c.setFont(FONTE, 10)
    c.drawString(M, y_from_top(246.3 + 10), f"Início do Registro: {dados['inicio']}")
    c.drawString(M, y_from_top(268.1 + 10), f"Origem: {dados['origem']} . Circunscrição: {dados['circunscricao']}")
    linha(c, 299.1, grossa=False)

    # Fato Atípico
    c.setFont(FONTE_B, 10)
    c.drawString(M, y_from_top(322.1 + 10), "Fato Atípico")
    linha(c, 338.1, grossa=False)
    c.setFont(FONTE, 10)
    c.drawString(M, y_from_top(357.3 + 10), f"Capitulação: {dados['capitulacao']}")

    # Despacho da Autoridade
    y_desp = 403.8
    c.setFont(FONTE_B, 10)
    c.drawString(M, y_from_top(y_desp + 10), "Despacho da Autoridade")
    linha(c, y_desp + 16, grossa=False)
    c.setFont(FONTE, 10)
    y_texto = y_desp + 35.3
    for ln in simpleSplit(dados["despacho"], FONTE, 10, LINHA_X1 - M):
        c.drawString(M, y_from_top(y_texto), ln)
        y_texto += 12

    # Envolvido / Vítima
    y_env_fixo = 517.1
    c.setFont(FONTE_B, 10)
    c.drawString(M, y_from_top(y_env_fixo + 10), "Envolvido(s) na Ocorrência - Vítima")
    linha(c, y_env_fixo + 16, grossa=False)

    y_nome, y_cpf, y_cel = y_env_fixo + 35.2, y_env_fixo + 57.7, y_env_fixo + 79.5
    c.setFont(FONTE_B, 10)
    c.drawString(30.5, y_from_top(y_nome + 10), "Nome")
    c.drawString(30.5, y_from_top(y_cpf + 10), "CPF:")
    c.drawString(30.5, y_from_top(y_cel + 10), "CELULAR:")

    c.setFont(FONTE, 10)
    c.drawString(90.0, y_from_top(y_nome + 10), str(dados["vitima_nome"]).upper())
    c.drawString(90.0, y_from_top(y_cpf + 10), formatar_cpf(dados["vitima_cpf"]))
    c.drawString(90.0, y_from_top(y_cel + 10), formatar_celular(dados["vitima_celular"]))

    logo_banco = caminho_asset(uf, dados.get("logo_banco_nome"))
    if logo_banco: draw_img_fit(c, logo_banco, max_x=LINHA_X1, top_y=y_nome - 2, max_w=140, max_h=40, align="right")

    linha(c, y_cel + 52, grossa=False)

    # Dinâmica do fato
    y_din = y_cel + 68
    c.setFont(FONTE_B, 10)
    c.drawString(M, y_from_top(y_din), "Dinâmica do fato")
    linha(c, y_din + 6, grossa=True)
    
    c.setFont(FONTE, 10)
    y_txt_din = y_din + 20
    for ln in simpleSplit(dados["dinamica"], FONTE, 10, LINHA_X1 - M):
        c.drawString(M, y_from_top(y_txt_din), ln)
        y_txt_din += 12

    # Procedimento
    y_proc = y_txt_din + 15
    c.setFont(FONTE_B, 10)
    c.drawString(M, y_from_top(y_proc), "PROCEDIMENTO DE CANCELAMENTO IMEDIATO ATRAVÉS DE VALIDAÇÃO BIOMETRIA FACIAL")
    linha(c, y_proc + 6, grossa=True)
    c.showPage()

    # Pagina 2
    c.setFont(FONTE, 10)
    c.drawString(40, y_from_top(22), "Protocolo Administrativo nº: 048640-1023/2026")
    assinatura = caminho_asset(uf, "assinatura.png")
    if assinatura: c.drawImage(ImageReader(assinatura), (LARGURA - 180)/2, y_from_top(75)-35, width=180, height=35, preserveAspectRatio=True, mask="auto")
    
    c.setLineWidth(0.8)
    c.line(LARGURA / 2 - 110, y_from_top(120), LARGURA / 2 + 110, y_from_top(120))
    c.setFont(FONTE_B, 10)
    c.drawCentredString(LARGURA / 2, y_from_top(140), dados["investigador"])
    c.setFont(FONTE, 8)
    c.drawCentredString(LARGURA / 2, y_from_top(155), dados["investigador_cargo"])
    
    c.save()
    buffer.seek(0)
    return buffer.getvalue()

# Interface Web Streamlit
st.markdown('<p class="titulo">Gerador de Boletim Web</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitulo">Preencha os dados abaixo para gerar e baixar o PDF oficial</p>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    uf_escolhida = st.selectbox("Selecione o Estado (UF):", UFS_ORDENADAS, format_func=lambda x: f"{x} - {ESTADOS[x]['nome']}")

bancos_opcoes = {
    "Bradesco": "logo_bradesco.png",
    "Itaú": "logo_itau.png",
    "Caixa Econômica Federal": "logo_caixa.png",
    "Banco do Brasil": "logo_bb.png",
    "Santander": "logo_santander.png",
    "Nubank": "logo_nubank.png",
    "Banco Inter": "logo_inter.png",
    "C6 Bank": "logo_c6.png",
    "BTG Pactual": "logo_btg.png",
    "PagBank": "logo_pagbank.png",
    "PagSeguro": "logo_pagseguro.png",
    "Mercado Pago": "logo_mercadopago.png",
    "Banco SICOOB": "logo_sicoob.png",
    "Banco SICREDI": "logo_sicredi.png",
    "Banco Safra": "logo_safra.png",
    "Banrisul": "logo_banrisul.png",
    "Banco BMG": "logo_bmg.png",
    "Banco Pan": "logo_pan.png",
    "Banco Original": "logo_original.png",
    "Neon": "logo_neon.png",
    "XP Investimentos": "logo_xp.png",
    "Ame Digital": "logo_ame.png",
    "PicPay": "logo_picpay.png",
    "Banco Nordeste (BNB)": "logo_bnb.png",
    "Banco da Amazônia (BASA)": "logo_basa.png",
    "BRB - Banco de Brasília": "logo_brb.png",
    "Sem Logo": None
}

with col2:
    banco_escolhido_nome = st.selectbox("Selecione a Logo do Banco:", list(bancos_opcoes.keys()))
    logo_banco_nome = bancos_opcoes[banco_escolhido_nome]

tipos_ocorrencia = [
    "Acesso Indevido à Conta",
    "Acesso Indevido ao Aplicativo",
    "Cancelamento de Empréstimo",
    "Dispositivo Clonado",
    "Fraude na Agência",
    "Operações Não Autorizadas",
    "Transferência Indevida"
]
tipo_ocorrencia_escolhida = st.selectbox("Selecione o Tipo de Ocorrência (Dinâmica):", tipos_ocorrencia)

st.markdown('<div class="divisor">DADOS DA VÍTIMA</div>', unsafe_allow_html=True)

dados_txt_externos = carregar_texto_externo()

with st.form(key="form_bou"):
    vitima_nome = st.text_input("Nome Completo:", placeholder="Ex: Carlos Eduardo")
    
    col_a, col_b = st.columns(2)
    with col_a:
        vitima_cpf = st.text_input("CPF:", placeholder="000.000.000-00")
    with col_b:
        vitima_celular = st.text_input("Celular:", placeholder="(00) 00000-0000")
        
    submit_button = st.form_submit_button(label="📄 Processar e Gerar PDF", type="primary")

if submit_button:
    if not vitima_nome:
        st.error("⚠️ Por favor, preencha o nome da vítima.")
    else:
        est = ESTADOS[uf_escolhida]
        
        banco_texto = "" if banco_escolhido_nome == "Sem Logo" else f" APP {banco_escolhido_nome.upper()},"
        
        if tipo_ocorrencia_escolhida == "Acesso Indevido à Conta":
            dinamica_personalizada = f"ACESSO INDEVIDO (INVASÃO){banco_texto} ACESSO INDEVIDO À CONTA E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
        elif tipo_ocorrencia_escolhida == "Acesso Indevido ao Aplicativo":
            dinamica_personalizada = f"ACESSO INDEVIDO (INVASÃO){banco_texto} ACESSO INDEVIDO AO APLICATIVO E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
        elif tipo_ocorrencia_escolhida == "Cancelamento de Empréstimo":
            dinamica_personalizada = f"ACESSO INDEVIDO (INVASÃO){banco_texto} CANCELAMENTO DE EMPRÉSTIMO E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
        elif tipo_ocorrencia_escolhida == "Dispositivo Clonado":
            dinamica_personalizada = f"ACESSO INDEVIDO (INVASÃO){banco_texto} DISPOSITIVO CLONADO E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
        elif tipo_ocorrencia_escolhida == "Fraude na Agência":
            dinamica_personalizada = f"ACESSO INDEVIDO (INVASÃO){banco_texto} FRAUDE NA AGÊNCIA E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
        elif tipo_ocorrencia_escolhida == "Operações Não Autorizadas":
            dinamica_personalizada = f"ACESSO INDEVIDO (INVASÃO){banco_texto} OPERAÇÕES NÃO AUTORIZADAS E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
        elif tipo_ocorrencia_escolhida == "Transferência Indevida":
            dinamick_personalizada = f"ACESSO INDEVIDO (INVASÃO){banco_texto} TRANSFERÊNCIA INDEVIDA E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
            dinamica_personalizada = dinamick_personalizada
        else:
            dinamica_personalizada = "ACESSO INDEVIDO (INVASÃO) À CONTA E REMOÇÃO DO DISPOSITIVO NÃO AUTORIZADO"
        
        dados_finais = {
            "uf": uf_escolhida,
            "numero": "025-06119/2026",
            "origem": est["origem"],
            "circunscricao": est["circunscricao"],
            "delegacia": est["delegacia"],
            "endereco": est["endereco"],
            "investigador": est["investigador"],
            "investigador_cargo": est["investigador_cargo"],
            "logo_banco_nome": logo_banco_nome,
            "vitima_nome": vitima_nome,
            "vitima_cpf": vitima_cpf if vitima_cpf else "000.000.000-00",
            "vitima_celular": vitima_celular if vitima_celular else "(00) 00000-0000",
            "capitulacao": dados_txt_externos.get("capitulacao", ""),
            "despacho": dados_txt_externos.get("despacho", ""),
            "dinamica": dinamica_personalizada
        }
        
        try:
            pdf_bytes = gerar_pdf_bytes(dados_finais)
            st.success("✅ PDF gerado com sucesso!")
            
            # Ajuste para salvar com o nome "Boletim [BANCO].pdf"
            nome_banco_arquivo = banco_escolhido_nome if banco_escolhido_nome != "Sem Logo" else "Geral"
            nome_arquivo_pdf = f"Boletim {nome_banco_arquivo}.pdf"
            
            st.download_button(
                label="📥 Clique aqui para baixar o PDF",
                data=pdf_bytes,
                file_name=nome_arquivo_pdf,
                mime="application/pdf"
            )
        except Exception as e:
            st.error(f"Erro ao gerar o PDF: {e}")
