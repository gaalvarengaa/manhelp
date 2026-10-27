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
Os valores são termos em inglês, que aparecem nas descrições e exemplos do man.
"""

import unicodedata
from typing import Dict, Iterable

SYNONYMS: Dict[str, list] = {
    # arquivos e diretórios
    "listar": ["list", "ls"],
    "lista": ["list", "ls"],
    "arquivo": ["file", "files"],
    "arquivos": ["file", "files"],
    "pasta": ["directory", "folder", "dir"],
    "pastas": ["directory", "folder", "dir"],
    "diretorio": ["directory", "dir"],
    "diretorios": ["directory", "dir"],
    "copiar": ["copy", "cp"],
    "mover": ["move", "mv"],
    "renomear": ["rename", "mv"],
    "remover": ["remove", "delete", "rm"],
    "apagar": ["delete", "remove", "rm"],
    "excluir": ["delete", "remove", "rm"],
    "link": ["link", "symbolic"],
    "simbolico": ["symbolic", "link"],
    # tamanho e disco
    "maior": ["size", "largest", "big"],
    "maiores": ["size", "largest", "big"],
    "menor": ["smallest", "size"],
    "menores": ["smallest", "size"],
    "tamanho": ["size", "du"],
    "espaco": ["space", "disk", "usage"],
    "disco": ["disk", "filesystem"],
    # busca e texto
    "buscar": ["search", "find", "grep"],
    "procurar": ["search", "find", "grep"],
    "texto": ["text", "grep"],
    "linhas": ["lines", "line"],
    "contar": ["count", "wc"],
    "ordenar": ["sort"],
    # compactação
    "compactar": ["compress", "archive", "tar"],
    "comprimir": ["compress", "gzip"],
    "descompactar": ["extract", "decompress", "untar"],
    "extrair": ["extract", "decompress"],
    # permissões e usuários
    "permissao": ["permission", "permissions", "mode", "chmod"],
    "permissoes": ["permission", "permissions", "mode", "chmod"],
    "dono": ["owner", "chown"],
    "usuario": ["user", "users"],
    "usuarios": ["user", "users"],
    "senha": ["password", "passwd"],
    # processos, sistema e rede
    "processo": ["process", "processes", "ps"],
    "processos": ["process", "processes", "ps"],
    "matar": ["kill", "signal"],
    "memoria": ["memory", "free"],
    "rede": ["network", "ip", "interface"],
    "data": ["date"],
    "hora": ["time", "date"],
    "agendar": ["schedule", "cron"],
    # pacotes e edição
    "instalar": ["install"],
    "pacote": ["package", "packages"],
    "pacotes": ["package", "packages"],
    "editar": ["edit", "editor"],
    "imprimir": ["print", "echo"],
    "mostrar": ["show", "print", "display"],
}

# Peso de um termo que veio do dicionário, em relação ao termo original da busca
SYNONYM_WEIGHT = 0.7


def strip_accents(text: str) -> str:
    """Remove acentos: 'permissão' vira 'permissao'."""
    decomposed = unicodedata.normalize("NFKD", text)
    return decomposed.encode("ascii", "ignore").decode("ascii")


def expand_terms(tokens: Iterable[str]) -> Dict[str, float]:
    """Gera o conjunto de termos da busca, com o peso de cada um."""
    terms: Dict[str, float] = {}
    for token in tokens:
        terms[token] = max(terms.get(token, 0.0), 1.0)
        for synonym in SYNONYMS.get(strip_accents(token), []):
            terms[synonym] = max(terms.get(synonym, 0.0), SYNONYM_WEIGHT)
    return terms
