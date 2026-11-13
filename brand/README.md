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

O script abre [`_source/render.html`](_source/render.html) no Microsoft Edge em modo headless, uma vez por peça, e grava `assets/banner.png` (1280×320) e `assets/covers/<repositório>.png` (1280×640, tamanho recomendado pelo GitHub para *social preview*), todos em resolução 2×. Se o Python com Pillow estiver instalado, os PNG são otimizados (cerca de 50 KB cada).

Para mudar textos ou diagramas, edite o objeto `DATA` no HTML.
