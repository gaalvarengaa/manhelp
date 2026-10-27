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

"""Interface de linha de comando do manhelp."""

import re
import sys
from typing import List, Optional

from . import __version__
from .reader import ManPage, get_page
from .search import search

USAGE = """\
uso:
  manhelp <descrição>     busca comandos por descrição
                          ex.: manhelp listar arquivos maiores que 100MB
  manhelp <comando>       mostra o resumo de um comando
                          ex.: manhelp ls
  manhelp --versao        mostra a versão
"""

# Nomes de comandos válidos; evita passar opções ou caracteres estranhos ao man
_COMMAND_RE = re.compile(r"[\w.+-]+")


def _label(page: ManPage) -> str:
    return f"{page.name}({page.section})" if page.section else page.name


def _first_lines(text: str, count: int) -> List[str]:
    return [line.strip() for line in text.splitlines() if line.strip()][:count]


def _show_page(page: ManPage) -> None:
    print(f"{_label(page)} - {page.description}")
    if page.synopsis:
        print("\nSINOPSE")
        for line in _first_lines(page.synopsis, 6):
            print(f"  {line}")
    if page.examples:
        print("\nEXEMPLOS")
        for line in _first_lines(page.examples, 10):
            print(f"  {line}")


def _show_results(results: List[tuple]) -> None:
    for _, page in results:
        print(f"{_label(page)} - {page.description}")
        example = _first_lines(page.examples, 1) or _first_lines(page.synopsis, 1)
        if example:
            print(f"    {example[0]}")
        print()


def main(argv: Optional[List[str]] = None) -> int:
    args = sys.argv[1:] if argv is None else argv

    if not args or args[0] in ("-h", "--help"):
        print(USAGE)
        return 0
    if args[0] in ("-v", "--versao"):
        print(__version__)
        return 0

    # Um único nome de comando: mostra o resumo dele, se a página existir
    if len(args) == 1 and _COMMAND_RE.fullmatch(args[0]):
        page = get_page(args[0])
        if page:
            _show_page(page)
            return 0

    results = search(" ".join(args))
    if not results:
        print("Nenhum comando encontrado para essa descrição.")
        print("Tente palavras-chave em inglês, como 'find', 'size' ou 'compress'.")
        return 1

    _show_results(results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
