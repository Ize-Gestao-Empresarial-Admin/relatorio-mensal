# Roda a API

import os
import uvicorn

if __name__ == "__main__":
    # Usar a porta da variável de ambiente ou 8080 como padrão
    port = int(os.getenv("PORT", 8080))
    
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=port,
        reload=False  # Desabilitar reload em produção
    )