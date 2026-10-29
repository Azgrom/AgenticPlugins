# Empacotamento

Execute na raiz do repositório, com Python 3 e sua biblioteca padrão:

```sh
python3 -B ci/package.py
```

O script executa o validador do pacote e, se a validação passar, cria
`dist/tutor.zip`. O arquivo contém todo o conteúdo de `src/`, incluindo arquivos
ocultos como `.codex-plugin/plugin.json`, diretamente na raiz do ZIP.
Um ZIP existente no destino é substituído.

Para escolher outro destino:

```sh
python3 -B ci/package.py /tmp/tutor.zip
```

O destino deve terminar em `.zip` e ficar fora de `src/`. Caminhos relativos de
saída usam o diretório atual. A localização de `src/` e o destino padrão são
resolvidos a partir do script, permitindo executá-lo de outros diretórios.
