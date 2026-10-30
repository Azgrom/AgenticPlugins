# Plugins

Este repositório reúne os fontes de plugins independentes e a automação para
validar e preparar seus arquivos de distribuição.

| Plugin | Finalidade | Raiz do pacote |
| --- | --- | --- |
| [Tutor AZ](Tutor/README.md) | Tutoria sob demanda e verificação do entendimento | `Tutor/` |
| [DevBacklog](DevBacklog/README.md) | Planejamento, execução de projetos e revisão de testes | `DevBacklog/` |

Cada pacote contém seus manifestos, habilidades e arquivos de apoio. Consulte
[AGENTS.md](AGENTS.md) para manutenção e o README de cada plugin para uso e
validação.

## Preparar distribuição

Na raiz do repositório, com Python 3:

```sh
python3 -B ci/package.py --plugin tutor
python3 -B ci/package.py --plugin devbacklog
```

Os comandos validam o pacote selecionado e geram, respectivamente,
`dist/tutor.zip` e `dist/devbacklog.zip`. Cada ZIP contém os arquivos de um único
plugin diretamente na raiz, incluindo `.codex-plugin/plugin.json`. A geração do
arquivo é local; não publica nem instala o plugin em um serviço.

Consulte [ci/README.md](ci/README.md) para destinos alternativos e testes do
empacotamento.
