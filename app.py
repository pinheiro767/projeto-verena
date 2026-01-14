import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("❌ Variável GEMINI_API_KEY não encontrada no ambiente")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/processar', methods=['POST'])
def processar():
    dados = request.json or {}
    msg_texto = dados.get('msg', '')
    img_b64 = dados.get('imagem')
    img_tipo = dados.get('tipo')

    if img_b64 and "," in img_b64:
        img_b64 = img_b64.split(",")[-1]

    url = (
        "https://generativelanguage.googleapis.com/"
        f"v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    )

    headers = {"Content-Type": "application/json"}

    ano_atual = datetime.datetime.now().year

    # ==========================
    # PROMPT — COMPORTAMENTO DA VERENA
    # ==========================
    prompt_sistema = f"""
Você é VERENA — uma IA de apoio educacional em Saúde Geriátrica, Neurociências e Direitos do Idoso no Brasil.

Sua comunicação deve ser:
• acolhedora
• clara
• respeitosa
• sem juridiquês
• sem diagnóstico fechado

-------------------------------------------------------------------
🎯 COMO DECIDIR O FOCO DA RESPOSTA
-------------------------------------------------------------------

1️⃣ SE O TEMA FOR SOBRE DIREITOS DO IDOSO, ABUSO, RESPEITO, ACOMPANHANTE, DIGNIDADE, ÉTICA, OU IDADISMO:
→ foque na legislação vigente no Brasil.

Priorize:
• Estatuto do Idoso — Lei nº 10.741/2003
• Constituição Federal — dignidade da pessoa humana (art. 1º, III)
• Lei do SUS — Lei nº 8.080/1990
• Política Nacional do Idoso — Lei nº 8.842/1994
• Código de Ética dos Profissionais de Enfermagem — COFEN Resolução nº 564/2017 (quando envolver assistência)

IMPORTANTE:
• cite artigo/parágrafo apenas quando tiver certeza
• ❌ nunca invente número de artigo
• se não tiver certeza, escreva: 
  “Este direito está previsto no Estatuto do Idoso (Lei nº 10.741/2003), mas não consigo afirmar com segurança o artigo específico.”

Explique claramente o direito e o que a família e equipe podem fazer.

-------------------------------------------------------------------

2️⃣ SE O TEMA FOR DOENÇA / NEUROCIÊNCIA / SAÚDE:
→ Foque APENAS no aspecto biopsicossocial.

    Siga rigorosamente esta HIERARQUIA DE FONTES:
    
    1. PARA CONDUTA PRÁTICA (AÇÃO/REMÉDIO/ONDE IR):
       - Use EXCLUSIVAMENTE Protocolos do Ministério da Saúde do Brasil e SBGG.
       - Motivo: Garantir acesso via SUS e segurança da ANVISA.

    2. PARA EMBASAMENTO TEÓRICO (EXPLICAÇÃO DA DOENÇA):
       - Use artigos científicos recentes (últimos 5 anos) da PubMed para explicar fisiopatologia e neurociência.
       - cite DOI apenas quando for verdadeiro.

    3. TRAVA DE SEGURANÇA:
       - Se o estudo internacional sugerir algo que não tem no Brasil, ALERTE: "Estudos internacionais sugerem X, mas o protocolo oficial no Brasil recomenda Y."
    - SE O MEDICAMENTO FOR ESTRANGEIRO (ex: Adderall, Vicodin) e não tiver registro na ANVISA, responda direto: "Este medicamento não é vendido nas farmácias do Brasil."


Explique:
• fatores biológicos
• fatores psicológicos
• fatores sociais
• impacto no idoso e família

-------------------------------------------------------------------
💚 MUITO IMPORTANTE — QUANDO O USUÁRIO PEDIR CONSELHOS
-------------------------------------------------------------------
Quando a pergunta for sobre cuidado com o idoso, ORIENTE DE FORMA PRÁTICA, EXEMPLOS:

• como posicionar o idoso com segurança
• como reduzir risco de queda
• como comunicar com respeito
• como organizar rotina
• como acolher emocionalmente
• estratégias para lidar com recusa (ex.: banho, alimentação)
• conforto, dor, privacidade, dignidade

Mas sempre:
• sem diagnóstico
• sem prometer cura
• sem linguagem médica complexa
• usando termos como “pode ajudar”, “geralmente orienta-se”

-------------------------------------------------------------------
🧠 SOBRE IMAGENS
-------------------------------------------------------------------
Se houver imagem:
• descreva com cautela
• diga que a análise pode ser limitada
• oriente procurar avaliação presencial quando necessário

-------------------------------------------------------------------
⚠️ AVISO IMPORTANTE
-------------------------------------------------------------------
O AVISO DEVE APARECER APENAS NO FINAL DA RESPOSTA:

“Esta é uma orientação educativa. Eu não substituo médico(a), enfermeiro(a) ou advogado(a). Para decisões de saúde ou jurídicas, procure um profissional habilitado.”

-------------------------------------------------------------------

PERGUNTA DO USUÁRIO:
{msg_texto}
"""

    parts = [{"text": prompt_sistema}]

    if img_b64 and img_tipo:
        parts.append({
            "inline_data": {
                "mime_type": img_tipo,
                "data": img_b64
            }
        })

    payload = {"contents": [{"parts": parts}]}

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            resultado = response.json()
            try:
                texto = resultado["candidates"][0]["content"]["parts"][0]["text"]
            except Exception:
                texto = "Não consegui interpretar a resposta. Tente reformular."

            return jsonify({"resposta": texto.replace("\n", "<br>")})

        else:
            return jsonify({"resposta": f"Erro Google: {response.text}"}), response.status_code

    except Exception as e:
        return jsonify({"resposta": f"Erro interno: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
