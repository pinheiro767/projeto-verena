import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("MINHA_KEY")

url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"

try:
    response = requests.get(url)
    if response.status_code == 200:
        dados = response.json()
        print("=== MODELOS DISPONÍVEIS PARA SUA CHAVE ===")
        if 'models' in dados:
            for m in dados['models']:
                # Mostra apenas os que geram texto
                if 'generateContent' in m['supportedGenerationMethods']:
                    print(f"✅ {m['name']}")
        else:
            print("Nenhum modelo encontrado (estranho!).")
    else:
        print(f"❌ Erro ao listar: {response.text}")
except Exception as e:
    print(f"Erro no código: {e}")