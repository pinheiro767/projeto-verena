import os

print("\n" + "="*40)
print("🩺 DIAGNÓSTICO DO SISTEMA VERENA 2.0")
print("="*40)

if os.path.exists('app.py'):
    print("✅ Arquivo 'app.py' encontrado.")
    with open('app.py', 'r', encoding='utf-8') as f:
        codigo = f.read()
        
        print("\n--- 🧠 CÉREBRO (MODELO) ---")
        if "gemini-2.0-flash" in codigo:
            print("✅ VERENA 2.0 ATIVA! (Modelo 'gemini-2.0-flash' detectado)")
        elif "gemini-1.5" in codigo:
            print("⚠️ AINDA NA VERSÃO 1.5. (Atualize para 'gemini-2.0-flash-exp')")
        else:
            print("❌ Modelo não identificado claramente.")

        print("\n--- 🛠️ CAPACIDADES ---")
        if "PIL" in codigo or "Image" in codigo:
            print("👁️ VISÃO COMPUTACIONAL: [ON]")
        else:
            print("👁️ VISÃO COMPUTACIONAL: [OFF]")
            
        if "system_instruction" in codigo:
            print("🛡️ PROTOCOLOS DE SEGURANÇA: [ON]")
        else:
            print("🛡️ PROTOCOLOS DE SEGURANÇA: [OFF]")
else:
    print("❌ ERRO: Não encontrei o arquivo 'app.py'.")

print("\n" + "="*40 + "\n")