import os
import tempfile
import unittest

import pandas as pd

from tasi.base import CollectionBase, PandasBase
from tasi.utils.base import ensure_iterable


class TestEnsureIterable(unittest.TestCase):
    def test_scalar(self):
        self.assertEqual(ensure_iterable(5), [5])

    def test_string(self):
        self.assertEqual(ensure_iterable("abc"), ["abc"])

    def test_list(self):
        self.assertEqual(ensure_iterable([1, 2, 3]), [1, 2, 3])


class TestTimestampAndIdSelection(unittest.TestCase):
    def setUp(self):
        df = pd.DataFrame(
            {
                "timestamp": ["2024-01-01T00:00:00", "2024-01-01T00:00:01"],
                "id": [1, 1],
                "position|easting": [0.0, 1.0],
                "position|northing": [0.0, 1.0],
            }
        )
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.set_index(["timestamp", "id"])
        df.columns = pd.MultiIndex.from_tuples(
            [tuple(c.split("|")) for c in df.columns], names=[None, None]
        )

        class Dummy(CollectionBase):
            @property
            def _constructor(self):
                return Dummy

            def _ensure_correct_type(self, df, key):
                return Dummy(df)

        self.Dummy = Dummy
        self.df = df

    def test_att_single_timestamp(self):
        obj = self.Dummy(self.df)
        selected = obj.att(obj.timestamps[0])
        self.assertEqual(len(selected), 1)

    def test_att_timestamp_list(self):
        obj = self.Dummy(self.df)
        selected = obj.att([obj.timestamps[0], obj.timestamps[1]])
        self.assertEqual(len(selected), 2)

    def test_atid_single(self):
        obj = self.Dummy(self.df)
        selected = obj.atid(1)
        self.assertEqual(len(selected), 2)

    def test_atid_list(self):
        obj = self.Dummy(self.df)
        selected = obj.atid([1])
        self.assertEqual(len(selected), 2)


class TestPandasBaseFromCSV(unittest.TestCase):
    def test_from_csv_no_timestamp(self):
        csv_data = "id,position|easting,position|northing\n1,0.0,0.0\n"
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".csv") as tmp:
            tmp.write(csv_data)
            path = tmp.name

        try:
            df = PandasBase.from_csv(path, indices=("id",))
            self.assertIn("id", df.index.names)
        finally:
            os.remove(path)
