# Notes

## Testes de CSS para PDF
Para testar o CSS, pois não estou conseguindo emitir o PDF com estilização:

1. Baixar localmente os arquivos do Bootstrap em `static/css/`
2. Garantir que o PDFKit tenha acesso aos meus arquivos locais

## Adicionando Novos Relatórios
Para adicionar um novo tipo de relatório, basta:

1. Criar um arquivo de renderizador correspondente
2. Adicionar à fábrica de renderizadores no `__init__.py`
3. Criar um diretório de template com `template.html` e `style.css`

**Nota:** Quando você implementar as outras classes de renderização (Relatorio1Renderer a Relatorio6Renderer), você seguirá a mesma estrutura, com cada renderer responsável por formatar e estilizar seu respectivo tipo de relatório.