"""
Teste de geração de PDFs com centro_custo=true
Com suporte para GCS (download via URL)
"""
import requests
import time

url = "https://ize-relatorios-api-1052359947797.southamerica-east1.run.app/v1/relatorios/pdf"
headers = {"X-API-Key": "tj8DbJ0bDYDwqLKhF4rEDKaoOW6KxIC6ofeDtc44aA_0XlOEZcu49zAQKYylodOZ"}

# Payload com centro_custo = true
payload = {
    "id_cliente": [378],
    "mes": 9,
    "ano": 2025,
    "relatorios": [1, 2, 3, 4, 5],
    "centro_custo": True
}

print("🔄 Enviando requisição com centro_custo=true...")
print(f"📦 Payload: {payload}")
print("⏱️  Aguardando resposta (pode demorar alguns minutos)...\n")

start_time = time.time()

try:
    response = requests.post(url, json=payload, headers=headers, timeout=900)  # 15 minutos
    
    elapsed = time.time() - start_time
    
    print(f"\n⏱️  Tempo de processamento: {elapsed:.2f}s ({elapsed/60:.1f} min)")
    print(f"📊 Status Code: {response.status_code}")
    
    if response.status_code == 200:
        content_type = response.headers.get('content-type', '')
        
        # Verificar se é JSON (GCS) ou binário (streaming direto)
        if 'application/json' in content_type:
            # Resposta JSON com URL do GCS
            data = response.json()
            print(f"\n✅ Relatórios gerados com sucesso!")
            print(f"📄 Arquivo: {data['filename']}")
            print(f"📏 Tamanho: {data['size_mb']} MB ({data['num_pdfs']} PDFs)")
            print(f"⏰ URL válida por: {data['expires_in']}")
            print(f"\n🔗 URL de download:")
            print(data['download_url'])
            
            # Baixar o arquivo do GCS
            print(f"\n📥 Baixando ZIP do GCS...")
            download_start = time.time()
            
            download_response = requests.get(data['download_url'], stream=True, timeout=300)
            
            if download_response.status_code == 200:
                filename = data['filename']
                with open(filename, "wb") as f:
                    for chunk in download_response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                download_time = time.time() - download_start
                print(f"✅ ZIP baixado com sucesso: {filename}")
                print(f"⏱️  Tempo de download: {download_time:.2f}s")
            else:
                print(f"❌ Erro ao baixar do GCS: {download_response.status_code}")
        
        else:
            # Resposta binária direta (streaming)
            print(f"📏 Tamanho: {len(response.content):,} bytes ({len(response.content)/1024/1024:.2f} MB)")
            filename = "relatorios_centros_custo.zip"
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"✅ ZIP salvo com sucesso: {filename}")
    else:
        print(f"❌ Erro {response.status_code}")
        print(f"Resposta: {response.text[:500]}")
        
except requests.Timeout:
    print("❌ TIMEOUT - A requisição excedeu 15 minutos")
except Exception as e:
    print(f"❌ Erro: {str(e)}")
