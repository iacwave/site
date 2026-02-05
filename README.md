# IACWave — Blog DevOps & Cloud

Site estático para compartilhar artigos, guias e recursos sobre DevOps, Infraestrutura como Código (IaC) e Cloud.

**Live**: https://iacwave.com.br  
**GitHub Pages** habilitado no branch `master`

## Estrutura

```
.
├── index.html              # Página inicial
├── about.html              # Página Sobre
├── recursos.html           # Página de recursos (placeholder)
├── blog/
│   ├── index.html          # Índice do blog
│   ├── o-que-e-devops.html # Artigo: O que é DevOps
│   └── setup-ideal-devops-cloud-2026.html # Artigo: Setup
├── posts/                  # Posts em Markdown (fonte)
│   ├── o-que-e-devops.md
│   └── setup-ideal-devops-cloud-2026.md
├── assets/
│   ├── css/styles.css      # Estilos do site
│   ├── js/main.js          # Scripts
│   └── templates/post_template.html # Template para gerar posts
├── scripts/
│   └── md_to_html.py       # Conversor Markdown → HTML
└── README.md
```

## Como criar novo artigo

### 1. Criar arquivo Markdown

Crie um arquivo em `posts/seu-artigo.md` com esta estrutura:

```markdown
# Seu Título do Artigo
Author: Seu Nome
Tags: tag1, tag2, tag3
Description: Uma descrição curta para SEO e redes sociais.

Seu conteúdo aqui com **bold**, *itálico*, [links](url), imagens, etc.

## Seção 1

Parágrafo com conteúdo.

- Item 1
- Item 2

## Seção 2

Mais conteúdo...
```

### 2. Gerar HTML

```bash
cd /home/fabio/devops/projetos/site
python3 scripts/md_to_html.py posts/seu-artigo.md blog/seu-artigo.html --base-url https://iacwave.com.br
```

### 3. Atualizar índice do blog

Adicione um link na seção `<ul class="posts">` em `blog/index.html`:

```html
<li>
  <a href="/blog/seu-artigo.html">Seu Título</a>
  <p class="excerpt">Uma descrição curta...</p>
</li>
```

### 4. Fazer commit e push

```bash
git add -A
git commit -m "docs: add article - seu-artigo"
git push origin master
```

## Markdown suportado

- Headings: `# ## ###`
- Bold: `**texto**`
- Italic: `*texto*`
- Links: `[texto](url)`
- Imagens: `![alt](image.jpg)`
- Listas: `- item` ou `1. item`
- Blockquotes: `> citação`
- Inline code: `` `código` ``

## Testar localmente

```bash
cd projetos/site
python3 -m http.server 8000
# Abra http://localhost:8000 no navegador
```

## Metadados (Frontmatter)

Os metadados do post são extraídos da primeira linhas do arquivo:

- **Linha 1**: `# Título` — título do artigo
- **Author**: `Author: Nome` — autor (padrão: IACWave)
- **Tags**: `Tags: tag1, tag2` — tags para categorização
- **Description**: `Description: ...` — descrição para SEO

Exemplo:

```markdown
# O que é DevOps?
Author: IACWave
Tags: DevOps, Iniciante, CI/CD
Description: Guia prático sobre DevOps.
```

## SEO & Metadados

Cada artigo recebe automaticamente:

- Meta tags OG (Open Graph) para redes sociais
- JSON-LD estruturado para Google
- Canonical URL
- Reading time estimado
- Keywords das tags

## Estilo e Cores

- **Cor primária**: `#1e40af` (azul escuro)
- **Cor secundária**: `#3b82f6` (azul claro)
- **Tipografia**: Segoe UI, system fonts
- **Logo**: `logo_iacwave.png` (32px no header)

## GitHub Pages

Configurado para publicar automaticamente do branch `master`. Qualquer push ativa o deploy em poucos minutos.

## Contribuir

1. Clone o repositório
2. Crie um artigo em `posts/`
3. Gere HTML com `md_to_html.py`
4. Atualize `blog/index.html` se necessário
5. Faça commit e push
6. Aguarde 1-2 minutos para o site ser atualizado

---

**Mantido por**: IACWave  
**Licença**: MIT (ou conforme preferir)
