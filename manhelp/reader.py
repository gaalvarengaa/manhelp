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

"""Leitura das páginas do man instaladas no sistema."""

import os
import re
import subprocess
from dataclasses import dataclass, field
from typing import Dict, List, Optional

# Linhas de "man -k", por exemplo: "ls (1)      - list directory contents"
_APROPOS_RE = re.compile(r"^(?P<name>\S+)\s+\((?P<section>[^)]+)\)\s+-\s+(?P<desc>.*)$")

# Títulos de seção no man aparecem sem indentação e em maiúsculas: NAME, SYNOPSIS, EXAMPLES...
_HEADER_RE = re.compile(r"^[A-Z][A-Z0-9 _-]*$")

# Sequências de negrito/sublinhado (backspace) que alguns sistemas deixam no texto
_BACKSPACE_RE = re.compile(r".\x08")


@dataclass
class ManPage:
    name: str
    section: str
    description: str = ""
    sections: Dict[str, str] = field(default_factory=dict)

    @property
    def synopsis(self) -> str:
        return self.sections.get("SYNOPSIS", "")

    @property
    def examples(self) -> str:
        return self.sections.get("EXAMPLES", "")


def _run_man(args: List[str]) -> Optional[str]:
    """Executa o man sem paginador e devolve o texto, ou None se falhar."""
    env = dict(os.environ, MANPAGER="cat", PAGER="cat", MANWIDTH="200", TERM="dumb")
    try:
        result = subprocess.run(
            ["man"] + args,
            capture_output=True,
            text=True,
            errors="replace",
            env=env,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0 or not result.stdout:
        return None
    return _BACKSPACE_RE.sub("", result.stdout)


def _split_sections(text: str) -> Dict[str, str]:
    """Separa o texto de uma página do man em seções, indexadas pelo título."""
    chunks: Dict[str, List[str]] = {}
    current = None
    for line in text.splitlines():
        if _HEADER_RE.match(line):
            current = line.strip()
            chunks[current] = []
        elif current is not None:
            chunks[current].append(line.rstrip())
    return {title: "\n".join(lines).strip() for title, lines in chunks.items()}


def _description_from_name(name_section: str) -> str:
    """Extrai a descrição curta da seção NAME (formato 'comando - descrição')."""
    for line in name_section.splitlines():
        if " - " in line:
            return line.split(" - ", 1)[1].strip()
    return ""


def list_pages() -> List[ManPage]:
    """Lista as páginas instaladas com a descrição curta de cada uma (via man -k)."""
    output = _run_man(["-k", "."])
    if not output:
        return []

    pages: List[ManPage] = []
    seen = set()
    for line in output.splitlines():
        match = _APROPOS_RE.match(line.strip())
        if not match:
            continue
        key = (match["name"], match["section"])
        if key in seen:
            continue
        seen.add(key)
        pages.append(ManPage(match["name"], match["section"], match["desc"].strip()))
    return pages


def get_page(name: str, section: Optional[str] = None) -> Optional[ManPage]:
    """Carrega uma página completa do man. Devolve None se ela não existir."""
    args = [section, name] if section else [name]
    text = _run_man(args)
    if not text:
        return None

    sections = _split_sections(text)
    # Sem a seção NAME, o texto não é uma página de manual (ex.: mensagem de erro)
    if "NAME" not in sections:
        return None
    return ManPage(
        name=name,
        section=section or "",
        description=_description_from_name(sections.get("NAME", "")),
        sections=sections,
    )
