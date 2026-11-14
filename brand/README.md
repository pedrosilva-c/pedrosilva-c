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
py brand\components.py   # topo: assets/hero (painel e botões)
py brand\sections.py     # seções: assets/sections (Tech Stack, projetos, certificações, experiência, rodapé)
py brand\stats.py        # assets/sections/analytics(-mobile).svg e o bloco <!-- stats --> do README
```

Todas as seções seguem a moldura do painel do topo: barra de título com três pontos e um comando (`ls stack/`, `gh api`, `history`), barra petróleo à esquerda, raio 20. Cada peça larga tem versão de desktop (1280 de referência) e de celular (720), servida por `<picture>` abaixo de 600 px, porque a área útil do GitHub a 390 px é de 293 px.

- **Tech Stack:** uma linha por categoria; o nível fica no canto de cada bloco (verde = uso profissional, ciano = projetos próprios, cinza = fundamentos/curso concluído, âmbar tracejado = em estudo), mesmo critério do portfólio. Os dados estão em `DATA["stack"]` de `components.py`.
- **Projetos:** cartão horizontal com a capa do repositório embutida (PNG reduzido em `data:`, permitido pela CSP do GitHub para SVG em `<img>`). Barra e selo de status: verde com visto = pronto para uso; âmbar com meio círculo = em desenvolvimento; âmbar com documento = em documentação (âmbar segue a regra de cores das capas). Requer Pillow.
- **GitHub Analytics:** destaque para projetos, contribuições e tempo de conta; commits em linha secundária; linguagens contadas por projeto ("4 de 6"), sem porcentagem de bytes. A Action [`stats.yml`](../.github/workflows/stats.yml) roda toda segunda-feira, só com a API do GitHub, e só faz commit quando algo mudou.
- **Logotipos** oficiais em [`_source/icons/`](_source/icons/) (Devicon e Simple Icons, ver `LICENSES.md`). Sem logotipo próprio (AD, GPO, DNS, DHCP, TCP/IP, Tkinter, VLibras), usa-se monograma ou texto, nunca um logotipo inventado.
- **Texto** monoespaçado com `textLength`, para manter a largura com qualquer fonte de fallback.
- **Acessibilidade:** cada imagem tem `alt` com o conteúdo completo; o README mantém em texto as estatísticas, "Sobre mim" e as atividades.
- **Cache da CDN:** ao redesenhar uma peça, use um caminho novo. O GitHub chegou a servir por mais de 10 minutos a versão antiga de um arquivo regravado no mesmo caminho.
