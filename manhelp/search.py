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

"""Busca de comandos por descrição em linguagem natural.

A busca acontece em duas etapas:
1. Pontua todas as páginas usando só o nome e a descrição curta (rápido, via man -k).
2. Carrega a página completa apenas dos melhores candidatos e pontua também
   SYNOPSIS e EXAMPLES.
"""

import re
from typing import Dict, List, Set, Tuple

from .reader import ManPage, get_page, list_pages
from .synonyms import expand_terms

STOPWORDS = {
    # português
    "a", "o", "as", "os", "de", "do", "da", "dos", "das", "em", "no", "na",
    "um", "uma", "e", "ou", "que", "para", "por", "com", "meu", "minha",
    # inglês
    "the", "an", "of", "to", "in", "for", "and", "or", "with",
}

# Quantas páginas completas carregar na segunda etapa
DEEP_CANDIDATES = 30


def tokenize(text: str) -> List[str]:
    """Separa o texto em palavras minúsculas, sem stopwords."""
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def _score(page: ManPage, terms: Dict[str, float]) -> float:
    """Pontua uma página: nome vale mais que descrição, que vale mais que exemplos."""
    name = page.name.lower()
    fields: List[Tuple[Set[str], float]] = [
        (set(tokenize(page.description)), 2.0),
        (set(tokenize(page.synopsis)), 1.0),
        (set(tokenize(page.examples)), 1.0),
    ]

    score = 0.0
    for term, weight in terms.items():
        if term == name:
            score += 5.0 * weight
        for words, factor in fields:
            if term in words:
                score += factor * weight
    return score


def search(query: str, limit: int = 5) -> List[Tuple[float, ManPage]]:
    """Retorna as páginas mais relevantes para a descrição dada, da melhor para a pior."""
    terms = expand_terms(tokenize(query))
    if not terms:
        return []

    # Etapa 1: pontuação rápida, só com nome e descrição
    candidates: List[Tuple[float, ManPage]] = []
    for page in list_pages():
        score = _score(page, terms)
        if score > 0:
            candidates.append((score, page))
    candidates.sort(key=lambda item: item[0], reverse=True)

    # Etapa 2: página completa só para os melhores candidatos
    results: List[Tuple[float, ManPage]] = []
    for _, page in candidates[:DEEP_CANDIDATES]:
        full = get_page(page.name, page.section) or page
        score = _score(full, terms)
        if score > 0:
            results.append((score, full))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:limit]
