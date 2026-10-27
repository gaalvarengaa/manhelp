# Copyright (C) 2026 Gabriel de Alvarenga
#
# Este programa é software livre: você pode redistribuí-lo e/ou modificá-lo
# sob os termos da GNU General Public License, versão 3 ou (a seu critério)
# qualquer versão posterior, publicada pela Free Software Foundation.
#
# Este programa é distribuído na esperança de que seja útil, mas SEM
# NENHUMA GARANTIA; veja a GNU General Public License para mais detalhes.
# Você deve ter recebido uma cópia da licença junto com este programa.
# Caso contrário, veja <https://www.gnu.org/licenses/>.

"""Termos em português que apontam para comandos do Linux.

As chaves são palavras em português sem acento e em minúsculas.
Os valores de SYNONYMS são palavras em inglês, que aparecem nas descrições e
exemplos do man. Os valores de COMMANDS são nomes de comandos: só eles ganham
o bônus de nome na busca, para que uma palavra como "size" não puxe o comando
size(1) quando a busca é sobre tamanho de arquivos.
"""

import unicodedata
from typing import Dict, Iterable, Tuple

SYNONYMS: Dict[str, list] = {
    # arquivos e diretórios
    "listar": ["list"],
    "lista": ["list"],
    "arquivo": ["file"],
    "arquivos": ["file"],
    "pasta": ["directory", "folder"],
    "pastas": ["directory", "folder"],
    "diretorio": ["directory"],
    "diretorios": ["directory"],
    "copiar": ["copy"],
    "mover": ["move"],
    "renomear": ["rename"],
    "remover": ["remove", "delete"],
    "apagar": ["delete", "remove"],
    "excluir": ["delete", "remove"],
    "link": ["link", "symbolic"],
    "simbolico": ["symbolic", "link"],
    # tamanho e disco
    "maior": ["size", "largest", "big", "space"],
    "maiores": ["size", "largest", "big", "space"],
    "menor": ["smallest", "size", "space"],
    "menores": ["smallest", "size", "space"],
    "tamanho": ["size", "space"],
    "espaco": ["space", "disk", "usage"],
    "disco": ["disk", "filesystem"],
    # busca e texto
    "buscar": ["search", "find"],
    "procurar": ["search", "find"],
    "texto": ["text"],
    "linhas": ["line"],
    "contar": ["count"],
    "ordenar": ["sort"],
    # compactação
    "compactar": ["compress", "archive"],
    "comprimir": ["compress"],
    "descompactar": ["extract", "decompress"],
    "extrair": ["extract", "decompress"],
    # permissões e usuários
    "permissao": ["permission", "mode"],
    "permissoes": ["permission", "mode"],
    "dono": ["owner"],
    "usuario": ["user"],
    "usuarios": ["user"],
    "senha": ["password"],
    # processos, sistema e rede
    "processo": ["process"],
    "processos": ["process"],
    "matar": ["kill", "signal"],
    "memoria": ["memory"],
    "rede": ["network", "interface"],
    "data": ["date"],
    "hora": ["time", "date"],
    "agendar": ["schedule"],
    # pacotes e edição
    "instalar": ["install"],
    "pacote": ["package"],
    "pacotes": ["package"],
    "editar": ["edit", "editor"],
    "imprimir": ["print"],
    "mostrar": ["show", "print", "display"],
}

COMMANDS: Dict[str, list] = {
    "listar": ["ls"],
    "lista": ["ls"],
    "copiar": ["cp"],
    "mover": ["mv"],
    "renomear": ["mv"],
    "remover": ["rm"],
    "apagar": ["rm"],
    "excluir": ["rm"],
    "link": ["ln"],
    "maior": ["du", "find"],
    "maiores": ["du", "find"],
    "menor": ["du", "find"],
    "menores": ["du", "find"],
    "tamanho": ["du"],
    "espaco": ["df", "du"],
    "disco": ["df"],
    "buscar": ["find", "grep"],
    "procurar": ["find", "grep"],
    "texto": ["grep"],
    "contar": ["wc"],
    "ordenar": ["sort"],
    "compactar": ["tar", "zip"],
    "comprimir": ["gzip"],
    "descompactar": ["tar", "unzip"],
    "permissao": ["chmod"],
    "permissoes": ["chmod"],
    "dono": ["chown"],
    "senha": ["passwd"],
    "processo": ["ps"],
    "processos": ["ps"],
    "matar": ["kill", "pkill"],
    "memoria": ["free"],
    "rede": ["ip"],
    "data": ["date"],
    "hora": ["date"],
    "agendar": ["cron", "crontab"],
    "imprimir": ["echo"],
}

# Peso de um termo que veio do dicionário, em relação ao termo original da busca
SYNONYM_WEIGHT = 0.7

# Peso de um comando que veio do dicionário, em relação a um nome digitado na busca
COMMAND_WEIGHT = 0.5


def strip_accents(text: str) -> str:
    """Remove acentos: 'permissão' vira 'permissao'."""
    decomposed = unicodedata.normalize("NFKD", text)
    return decomposed.encode("ascii", "ignore").decode("ascii")


def expand_terms(tokens: Iterable[str]) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Gera os termos da busca e os nomes de comando procurados, com o peso de cada um.

    Os termos digitados entram nos dois: o usuário pode ter escrito o nome
    de um comando, como "grep". O peso de um comando soma quando várias
    palavras apontam para ele ("procurar texto" reforça o grep).
    """
    terms: Dict[str, float] = {}
    commands: Dict[str, float] = {}
    for token in dict.fromkeys(tokens):
        key = strip_accents(token)
        terms[token] = max(terms.get(token, 0.0), 1.0)
        commands[token] = max(commands.get(token, 0.0), 1.0)
        for synonym in SYNONYMS.get(key, []):
            terms[synonym] = max(terms.get(synonym, 0.0), SYNONYM_WEIGHT)
        for command in COMMANDS.get(key, []):
            commands[command] = commands.get(command, 0.0) + COMMAND_WEIGHT
    return terms, commands
