# Empacotamento

Execute na raiz do repositório, com Python 3 e sua biblioteca padrão:

```sh
python3 -B ci/package.py
python3 -B ci/package.py --plugin devbacklog
```

O script executa o validador do plugin selecionado e cria o ZIP somente se a
validação passar. Os testes são executados separadamente, conforme o `AGENTS.md`
de cada pacote.

| Seleção | Raiz do pacote | Destino padrão |
| --- | --- | --- |
| `--plugin tutor` (padrão) | `src/` | `dist/tutor.zip` |
| `--plugin devbacklog` | `DevBacklog/` | `dist/devbacklog.zip` |

Cada arquivo contém todo o conteúdo de sua raiz de pacote, incluindo arquivos
ocultos como `.codex-plugin/plugin.json`, diretamente na raiz do ZIP. Um ZIP
existente no destino é substituído. A geração é local e não publica o plugin.

Para escolher outro destino:

```sh
python3 -B ci/package.py /tmp/tutor.zip
python3 -B ci/package.py --plugin devbacklog /tmp/devbacklog.zip
```

O destino deve terminar em `.zip` e ficar fora de todas as raízes de plugins.
Caminhos relativos de saída usam o diretório atual. As raízes dos pacotes e os
destinos padrão são resolvidos a partir do script, permitindo executá-lo de
outros diretórios.

Ao adicionar um plugin, registre sua raiz e o comando de validação em `PACKAGES`
no script. Mantenha as regras estruturais no validador do próprio pacote.

## Testes do empacotamento

Na raiz do repositório:

```sh
python3 -B -m unittest discover -s ci -p 'test*.py'
```

Os testes verificam a seleção dos pacotes, os manifestos ocultos, o isolamento dos
arquivos, a validação antes da geração e os destinos recusados.
