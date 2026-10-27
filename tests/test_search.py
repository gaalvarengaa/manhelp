import unittest

from manhelp.reader import ManPage, _description_from_name
from manhelp.search import _score, stem, suggest_command
from manhelp.synonyms import expand_terms


class DescriptionFromNameTest(unittest.TestCase):
    def test_hifen(self):
        self.assertEqual(_description_from_name("ls - list directory contents"), "list directory contents")

    def test_travessao(self):
        self.assertEqual(_description_from_name("file — determine file type"), "determine file type")

    def test_hifen_escapado(self):
        self.assertEqual(_description_from_name("tar \\- an archiving utility"), "an archiving utility")

    def test_hifen_no_nome(self):
        self.assertEqual(_description_from_name("git-log - Show commit logs"), "Show commit logs")


class StemTest(unittest.TestCase):
    def test_plurais(self):
        self.assertEqual(stem("files"), "file")
        self.assertEqual(stem("directories"), "directory")
        self.assertEqual(stem("processes"), "process")

    def test_palavras_que_terminam_em_s(self):
        self.assertEqual(stem("process"), "process")
        self.assertEqual(stem("status"), "status")
        self.assertEqual(stem("ls"), "ls")


class SuggestCommandTest(unittest.TestCase):
    def test_maiores(self):
        self.assertEqual(suggest_command("listar arquivos maiores que 100MB"), "find . -type f -size +100M")

    def test_menores_com_espaco(self):
        self.assertEqual(suggest_command("arquivos menores que 10 KB"), "find . -type f -size -10k")

    def test_acentos_e_gib(self):
        self.assertEqual(suggest_command("arquivos acima de 2GiB"), "find . -type f -size +2G")

    def test_sem_filtro(self):
        self.assertIsNone(suggest_command("listar arquivos"))


class ScoreTest(unittest.TestCase):
    def test_sinonimo_nao_ganha_bonus_de_nome(self):
        # "maiores" sugere a palavra "size", mas não o comando size(1)
        terms, commands = expand_terms(["maiores"])
        idf = {term: 1.0 for term in terms}
        size = ManPage("size", "1", "list section sizes")
        du = ManPage("du", "1", "estimate file space usage")
        self.assertGreater(_score(du, terms, commands, idf), _score(size, terms, commands, idf))

    def test_nome_digitado_ganha_bonus(self):
        terms, commands = expand_terms(["grep"])
        idf = {term: 1.0 for term in terms}
        grep = ManPage("grep", "1", "print lines that match patterns")
        dctrl = ManPage("grep-dctrl", "1", "grep Debian control files")
        self.assertGreater(_score(grep, terms, commands, idf), _score(dctrl, terms, commands, idf))


if __name__ == "__main__":
    unittest.main()
