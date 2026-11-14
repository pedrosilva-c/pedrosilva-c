# Identidade visual

Referência única para o perfil, os repositórios e o [portfólio](https://pedro-osaka.github.io/portfolio/).

## Cores

| Token | Hex | Uso |
|---|---|---|
| Grafite | `#0F1419` | Fundo das capas e do tema escuro |
| Superfície | `#151C23` | Caixas dos diagramas, chips |
| Borda | `#2A3540` | Contornos |
| Texto | `#E8ECF0` | Títulos |
| Texto secundário | `#9AA7B4` | Descrições e rótulos |
| Ciano | `#5FB6C8` | Destaques de texto sobre fundo escuro |
| Petróleo | `#2B8A9E` | Barra lateral, linhas dos diagramas, nó principal |
| Verde | `#6CC79A` | Status *funcional* e *concluído* |
| Âmbar | `#E0A030` | Status *WIP* e *em documentação* |

No tema claro do portfólio, o petróleo de texto é escurecido para `#1F6F80` (contraste 5,76:1).

## Tipografia

- **Inter** 600–700 para títulos, 400–500 para texto.
- **JetBrains Mono** para rótulos técnicos, nomes de repositório, chips e status.

## Elementos

- **Barra vertical petróleo** à esquerda: assinatura de todas as peças.
- **Diagramas em linha fina** com a arquitetura real de cada projeto. Linha contínua para o que existe e tracejada para o que é planejado, opcional ou ainda não instalado.
- **Status** sempre declarado, com a mesma cor em todos os lugares.
- Nada de capturas de interfaces que não existem, gráficos de porcentagem ou contadores sem comprovação.

## Gerar as imagens

```powershell
powershell -NoProfile -File .\brand\render.ps1
```

O script abre [`_source/render.html`](_source/render.html) no Microsoft Edge em modo headless, uma vez por peça, e grava `assets/hero/banner.png` (1280×300) e `assets/hero/banner-mobile.png` (720×400, servido no celular) e `assets/covers/<repositório>.png` (1280×640, tamanho recomendado pelo GitHub para *social preview*), todos em resolução 2×. Se o Python com Pillow estiver instalado, os PNG são otimizados (cerca de 50 KB cada).

Para mudar textos ou diagramas, edite o objeto `DATA` no HTML.

## Componentes do README

```powershell
py brand\components.py   # assets/hero, assets/ui, assets/stack e assets/certs
```

Painel do topo em estilo terminal (`perfil.svg` 2 x 2 e `perfil-mobile.svg` empilhado, servido por `<picture>` abaixo de 600 px), botões de contato de largura igual, legenda e divisores do Tech Stack, um bloco por tecnologia, cartões de certificação e linha do tempo. Tudo em SVG, gerado a partir do objeto `DATA` no script; nada é desenhado à mão nem carregado de serviço externo.

- **Níveis no Tech Stack** (ponto no canto do bloco): verde = uso profissional, ciano = projetos próprios, cinza = fundamentos (curso concluído), âmbar tracejado = em estudo. Mesmo critério do portfólio.
- **Logotipos** oficiais em [`_source/icons/`](_source/icons/) (Devicon e Simple Icons, ver `LICENSES.md`). Tecnologias sem logotipo próprio (AD, GPO, DNS, DHCP, TCP/IP) usam monograma, nunca um logotipo inventado.
- **Texto** monoespaçado com `textLength`, para manter a largura com qualquer fonte de fallback.
- Cada imagem tem `alt` com o conteúdo completo; o README traz o mesmo conteúdo em texto (blocos recolhíveis e estatísticas).

## Estatísticas e selos

```powershell
py brand\stats.py    # assets/stats.svg e o bloco <!-- stats --> do README
py brand\status.py   # assets/status/*.svg (selos da grade de projetos)
```

`stats.py` usa só a biblioteca padrão e a API do GitHub (token de `GITHUB_TOKEN` ou de `gh auth token`). Os números vêm da API: projetos públicos (sem o repositório de perfil), commits nos repositórios públicos, contribuições dos últimos 12 meses (o calendário fica a cargo do gráfico nativo do GitHub) e linguagens contadas por repositório, sem porcentagens. A Action [`stats.yml`](../.github/workflows/stats.yml) roda toda segunda-feira e só faz commit quando algo mudou. Os mesmos números ficam em texto no README, para quem não carrega imagens.
