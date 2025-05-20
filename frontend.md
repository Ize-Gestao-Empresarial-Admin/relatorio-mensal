
## Estrutura Proposta (Foco no frontend e renderização)


v2_relatorio_mensal/
├── src/
│   ├── core/                  # Lógica de negócio (já existe)
│   ├── database/              # Acesso a dados (já existe) 
│   ├── interfaces/            # Interfaces de usuário (já existe)
│   └── rendering/             # Motor de renderização
│       ├── __init__.py
│       ├── engine.py          # Motor central de renderização
│       └── renderers/         # Conversor de dados para templates
│           ├── __init__.py
│           ├── base_renderer.py
│           └── relatorios_renderer(1-8).py
├── templates/
│   ├── base/                  # Apenas elementos comuns a todos relatórios
│   │   ├── base.html          # Template base com estrutura HTML
│   │   ├── header.html        # Cabeçalho padrão 
│   │   └── footer.html        # Rodapé padrão
│   ├── relatorio1/            # TUDO do relatório 1 fica aqui
│   │   ├── template.html      # Template específico do relatório 1
│   │   ├── style.css          # CSS específico do relatório 1
│   │   ├── components/        # Componentes específicos, logicas de visualização (se necessario)
│   ├── relatorio2/            # TUDO do relatório 2 fica aqui
│   │   ├── template.html
│   │   ├── style.css
│   │   ├── components/
│   └── ...                    # Outros relatórios seguem o mesmo padrão
├── assets/                    # Apenas ativos globais compartilhados
│   ├── images/                # Imagens globais (logo da empresa)
│   └── fonts/                 # Fontes utilizadas
└── outputs/                   # PDFs gerados

Se necessario posso criar uma pasta assets pra cada relatorio, mas o ideal é que os assets sejam globais e compartilhados entre todos os relatórios.
