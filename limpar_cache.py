import os
import shutil

print("🧹 Limpando cache do sistema...")

# Lista de pastas de cache para limpar
pastas_cache = ['cache', 'temp', '__pycache__']

for pasta in pastas_cache:
    if os.path.exists(pasta):
        try:
            # Remove todos os arquivos da pasta
            for arquivo in os.listdir(pasta):
                caminho_arquivo = os.path.join(pasta, arquivo)
                try:
                    if os.path.isfile(caminho_arquivo):
                        os.remove(caminho_arquivo)
                        print(f"  ✅ Removido: {caminho_arquivo}")
                except Exception as e:
                    print(f"  ❌ Erro ao remover {caminho_arquivo}: {e}")
            print(f"✅ Pasta {pasta} limpa!")
        except Exception as e:
            print(f"❌ Erro ao limpar pasta {pasta}: {e}")
    else:
        print(f"ℹ️ Pasta {pasta} não existe")

print("\n✨ Cache limpo com sucesso!")
print("🚀 Agora você pode executar o app.py normalmente")