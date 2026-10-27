# manhelp

Busca comandos do Linux por descrição em linguagem natural, usando as páginas do `man` instaladas no seu sistema. Funciona offline e sem dependências externas.

```
$ manhelp listar arquivos maiores que 100MB
du(1) - estimate file space usage
    du -h --threshold=100M ...
find(1) - search for files in a directory hierarchy
    find . -size +100M
```

```
$ manhelp ls
ls(1) - list directory contents
...
```

## Requisitos

- Python 3.8 ou superior
- `man` instalado (e as páginas de manual dos programas que você quer consultar)

## Instalação

```
pip install .
```

## Como funciona

1. A descrição é separada em palavras, sem stopwords (`de`, `que`, `the`...).
2. As palavras são expandidas com sinônimos em português e inglês (`listar` → `list`, `ls`).
3. Cada página é pontuada pelo nome, pela descrição curta (`man -k`), e depois pela SINOPSE e pelos EXEMPLOS dos melhores candidatos.

## Limitações atuais

- A busca só usa palavras-chave. Não entende números nem comparações: "maiores que 100MB" é tratado como a palavra "maiores", sem o limite de 100 MB.
- Páginas que só mencionam o termo nos exemplos, e não na descrição, podem não entrar entre os candidatos.
- O dicionário de sinônimos é pequeno e precisa crescer.

## Roadmap

- Testes automatizados
- Filtros numéricos (tamanho, data)
- Cache do índice em `~/.cache/manhelp`
- Backend opcional com modelo de linguagem, para buscas mais precisas

## Licença

GPL-3.0-or-later
