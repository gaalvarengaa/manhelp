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

import math
import re
from collections import Counter
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .reader import ManPage, get_page, list_pages
from .synonyms import expand_terms, strip_accents

STOPWORDS = {
    # português
    "a", "o", "as", "os", "de", "do", "da", "dos", "das", "em", "no", "na",
    "um", "uma", "e", "ou", "que", "para", "por", "com", "meu", "minha",
    # inglês
    "the", "an", "of", "to", "in", "for", "and", "or", "with",
}

# Quantas páginas completas carregar na segunda etapa
DEEP_CANDIDATES = 30

# Peso de um termo que é exatamente o nome do comando
NAME_WEIGHT = 30.0

# Filtros de tamanho, como "maiores que 100MB" ou "menos de 2 GB"
_SIZE_FILTER_RE = re.compile(
    r"\b(?P<cmp>maior(?:es)?|menor(?:es)?|acima|abaixo|mais|menos)"
    r"(?:\s+(?:do\s+)?(?:que|de))?\s+(?P<num>\d+)\s*(?P<unit>[kmgt])i?b?\b"
)
_SIZE_SIGN = {"maior": "+", "maiores": "+", "acima": "+", "mais": "+"}


def tokenize(text: str) -> List[str]:
    """Separa o texto em palavras minúsculas, sem stopwords."""
    words = re.findall(r"\w+", text.lower())
    return [w for w in words if w not in STOPWORDS and len(w) > 1]


def stem(word: str) -> str:
    """Reduz plurais do inglês ao singular: 'files' vira 'file', 'directories' vira 'directory'."""
    if len(word) <= 3:
        return word
    if word.endswith("ies"):
        return word[:-3] + "y"
    if word.endswith("sses"):
        return word[:-2]
    if word.endswith(("ss", "us", "is")):
        return word
    if word.endswith("s"):
        return word[:-1]
    return word


def _stems(text: str) -> Set[str]:
    return {stem(w) for w in tokenize(text)}


def _stem_terms(terms: Dict[str, float]) -> Dict[str, float]:
    """Aplica stem aos termos da busca, mantendo o maior peso quando dois se juntam."""
    stemmed: Dict[str, float] = {}
    for term, weight in terms.items():
        key = stem(term)
        stemmed[key] = max(stemmed.get(key, 0.0), weight)
    return stemmed


def _idf(pages: Iterable[ManPage], terms: Dict[str, float]) -> Dict[str, float]:
    """Raridade de cada termo nas descrições: palavras comuns como 'file' valem menos."""
    df: Counter = Counter()
    total = 0
    for page in pages:
        total += 1
        words = _stems(page.description)
        df.update(term for term in terms if term in words)
    return {term: math.log((total + 1) / (df[term] + 1)) for term in terms}


def _score(
    page: ManPage, terms: Dict[str, float], commands: Dict[str, float], idf: Dict[str, float]
) -> float:
    """Pontua uma página: nome vale mais que descrição, que vale mais que exemplos."""
    fields: List[Tuple[Set[str], float]] = [
        (_stems(page.description), 2.0),
        (_stems(page.synopsis), 1.0),
        (_stems(page.examples), 1.0),
    ]

    score = NAME_WEIGHT * commands.get(page.name.lower(), 0.0)
    for term, weight in terms.items():
        for words, factor in fields:
            if term in words:
                score += factor * weight * idf.get(term, 1.0)
    return score


def suggest_command(query: str) -> Optional[str]:
    """Traduz filtros de tamanho da busca para o find: 'maiores que 100MB' vira '-size +100M'."""
    match = _SIZE_FILTER_RE.search(strip_accents(query.lower()))
    if not match:
        return None
    sign = _SIZE_SIGN.get(match["cmp"], "-")
    unit = "k" if match["unit"] == "k" else match["unit"].upper()
    return f"find . -type f -size {sign}{match['num']}{unit}"


def search(query: str, limit: int = 5) -> List[Tuple[float, ManPage]]:
    """Retorna as páginas mais relevantes para a descrição dada, da melhor para a pior."""
    terms, commands = expand_terms(tokenize(query))
    terms = _stem_terms(terms)
    if not terms:
        return []

    pages = list_pages()
    idf = _idf(pages, terms)

    # Etapa 1: pontuação rápida, só com nome e descrição
    candidates: List[Tuple[float, ManPage]] = []
    for page in pages:
        score = _score(page, terms, commands, idf)
        if score > 0:
            candidates.append((score, page))
    candidates.sort(key=lambda item: item[0], reverse=True)

    # Etapa 2: página completa só para os melhores candidatos, mais os comandos
    # procurados pelo nome (que não podem ficar de fora por falta de vaga)
    deep = candidates[:DEEP_CANDIDATES]
    deep += [item for item in candidates[DEEP_CANDIDATES:] if item[1].name.lower() in commands]
    results: List[Tuple[float, ManPage]] = []
    for _, page in deep:
        full = get_page(page.name, page.section) or page
        # Se a seção NAME não pôde ser lida, fica a descrição do man -k
        full.description = full.description or page.description
        score = _score(full, terms, commands, idf)
        if score > 0:
            results.append((score, full))

    results.sort(key=lambda item: item[0], reverse=True)
    return results[:limit]
