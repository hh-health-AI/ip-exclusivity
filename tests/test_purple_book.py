import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import purple_book as pb

HEADER = "Proprietary Name,Proper Name,BLA Number,BLA Type,Ref Product Proper Name\n"
DATA = ["HUMIRA,adalimumab,125057,351(a),\n",
        "AMJEVITA,adalimumab-atto,761024,351(k),adalimumab\n"]


class PurpleBookTests(unittest.TestCase):
    def test_reference_brand_finds_biosimilar(self):
        result = pb.select_family(pb.read_rows([HEADER, *DATA]), product="HUMIRA")
        self.assertEqual(result["biosimilar_count_licensed"], 1)

    def test_biosimilar_resolves_reference_family(self):
        result = pb.select_family(pb.read_rows([HEADER, *DATA]), product="AMJEVITA")
        self.assertEqual(result["reference_products"][0]["bla_number"], "125057")

    def test_bla_is_exact_not_substring(self):
        rows = pb.read_rows([HEADER, *DATA])
        with self.assertRaises(ValueError):
            pb.select_family(rows, bla="125")
        self.assertEqual(pb.select_family(rows, bla="00125057")["biosimilar_count_licensed"], 1)

    def test_repeat_headers_use_full_database_and_deduplicate_blas(self):
        rows = pb.read_rows(["Monthly changes\n", HEADER, DATA[1], "Full database\n", HEADER, *DATA, DATA[1]])
        self.assertEqual(len(rows), 3)
        self.assertEqual(pb.select_family(rows, product="HUMIRA")["biosimilar_count_licensed"], 1)

    def test_missing_link_is_unknown_not_zero(self):
        rows = pb.read_rows([HEADER, DATA[0], "AMJEVITA,adalimumab-atto,761024,351(k),\n"])
        self.assertIsNone(pb.select_family(rows, product="HUMIRA")["biosimilar_count_licensed"])

    def test_bad_header_fails(self):
        with self.assertRaises(ValueError):
            pb.read_rows(["unknown,columns\n", "1,2\n"])

    def test_ambiguous_reference_name_is_not_a_confirmed_join(self):
        rows = pb.read_rows([HEADER, *DATA, "OTHER,adalimumab,999999,351(a),\n"])
        result = pb.select_family(rows, product="HUMIRA")
        self.assertIsNone(result["biosimilar_count_licensed"])
        self.assertEqual(result["matched_biosimilar_bla_count"], 0)


if __name__ == "__main__":
    unittest.main()
