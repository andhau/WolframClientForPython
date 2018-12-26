# -*- coding: utf-8 -*-

from __future__ import absolute_import, print_function, unicode_literals

try:
    import pandas
    import numpy
    pandas_available = True
except:
    pandas_available = False

import unittest
from wolframclient.utils.tests import TestCase as BaseTestCase
from wolframclient.serializers import export

@unittest.skipIf(not pandas_available, 'Pandas is not available.')
class PandasDataFrameTestCase(BaseTestCase):
    def export_compare(self, o, wl=None, wxf=None, **kwargs):
        if wl:
            res = export(o, target_format='wl', **kwargs)
            self.assertEqual(res, wl)
        if wxf:
            res = export(o, target_format='wxf', **kwargs)
            self.assertEqual(res, wxf)

    def create_numpy_data_nan(self):
        # nan-based
        arr = numpy.arange(5, dtype=float)
        index = numpy.arange(5)
        arr[1] = numpy.nan
        arr[3] = numpy.nan
        return arr, index

    def create_numpy_data_zero(self):
        # zero-based
        arr, index = create_numpy_data_nan()
        arr[np.isnan(arr)] = 0
        return arr, index

    def sparse_series_dict(self):
        d = {'b': 1, 'a': 0, 'c': 2}
        return pandas.SparseSeries(d)

    def sparse_series_dict_indexed(self):
        constructor_dict = {1: 1.}
        index = [0, 1, 2]
        # Series with index passed in
        series = pandas.Series(constructor_dict)
        return pandas.SparseSeries(series, index=index)

    def sparse_series_list_fill_zero(self):
        return pandas.SparseArray([1, 0, 3, 0], dtype=numpy.int64, fill_value=0)

    def sparse_series_date(self):
        arr, index = self.create_numpy_data_nan()
        date_index = pandas.bdate_range('1/1/2011', periods=len(index))
        return pandas.SparseSeries(arr, index=date_index, kind='block',name='bseries')

    # simple series
    def test_index_series_as_assoc(self):
        series_mixed = pandas.Series([1,2,3], index=[-1, 'a', 1])
        self.export_compare(series_mixed, 
            wl=b'<|-1 -> 1, "a" -> 2, 1 -> 3|>',
            wxf=b'8:f\x03s\x0bAssociationf\x02s\x04RuleC\xffC\x01f\x02s\x04RuleS\x01aC\x02f\x02s\x04RuleC\x01C\x03')
    
    def test_index_series_as_list(self):
        series_mixed = pandas.Series([1,2,3], index=[-1, 'a', 1])
        self.export_compare(series_mixed, 
            wl=b'{-1 -> 1, "a" -> 2, 1 -> 3}',
            wxf=b'8:f\x03s\x04Listf\x02s\x04RuleC\xffC\x01f\x02s\x04RuleS\x01aC\x02f\x02s\x04RuleC\x01C\x03',
            pandas_series_head='list')

    def test_index_series_as_dataset(self):
        series_mixed = pandas.Series([1,2,3], index=[-1, 'a', 1])
        self.export_compare(series_mixed, 
            wl=b'Dataset[<|-1 -> 1, "a" -> 2, 1 -> 3|>]',
            wxf=b'8:f\x01s\x07Datasetf\x03s\x0bAssociationf\x02s\x04RuleC\xffC\x01f\x02s\x04RuleS\x01aC\x02f\x02s\x04RuleC\x01C\x03',
            pandas_series_head='dataset')

    # nan series
    def test_index_nan_series_as_assoc(self):
        arr, index = self.create_numpy_data_nan()
        series_mixed = pandas.Series(arr, index=index)
        self.export_compare(series_mixed, 
            wl=b'<|0 -> 0., 1 -> Indeterminate, 2 -> 2., 3 -> Indeterminate, 4 -> 4.|>',
            wxf=b'8:f\x05s\x0bAssociationf\x02s\x04RuleC\x00r\x00\x00\x00\x00\x00\x00\x00\x00f\x02s\x04RuleC\x01s\rIndeterminatef\x02s\x04RuleC\x02r\x00\x00\x00\x00\x00\x00\x00@f\x02s\x04RuleC\x03s\rIndeterminatef\x02s\x04RuleC\x04r\x00\x00\x00\x00\x00\x00\x10@')
    
    def test_index_series_as_list(self):
        arr, index = self.create_numpy_data_nan()
        series_mixed = pandas.Series(arr, index=index)
        self.export_compare(series_mixed, 
            wl=b'{0 -> 0., 1 -> Indeterminate, 2 -> 2., 3 -> Indeterminate, 4 -> 4.}',
            wxf=b'8:f\x05s\x04Listf\x02s\x04RuleC\x00r\x00\x00\x00\x00\x00\x00\x00\x00f\x02s\x04RuleC\x01s\rIndeterminatef\x02s\x04RuleC\x02r\x00\x00\x00\x00\x00\x00\x00@f\x02s\x04RuleC\x03s\rIndeterminatef\x02s\x04RuleC\x04r\x00\x00\x00\x00\x00\x00\x10@',
            pandas_series_head='list')

    def test_index_series_as_dataset(self):
        arr, index = self.create_numpy_data_nan()
        series_mixed = pandas.Series(arr, index=index)
        self.export_compare(series_mixed, 
            wl=b'Dataset[<|0 -> 0., 1 -> Indeterminate, 2 -> 2., 3 -> Indeterminate, 4 -> 4.|>]',
            wxf=b'8:f\x01s\x07Datasetf\x05s\x0bAssociationf\x02s\x04RuleC\x00r\x00\x00\x00\x00\x00\x00\x00\x00f\x02s\x04RuleC\x01s\rIndeterminatef\x02s\x04RuleC\x02r\x00\x00\x00\x00\x00\x00\x00@f\x02s\x04RuleC\x03s\rIndeterminatef\x02s\x04RuleC\x04r\x00\x00\x00\x00\x00\x00\x10@',
            pandas_series_head='dataset')

    # sparse array from dict
    def test_sparse_from_dict_as_assoc(self):
        sparse_s = self.sparse_series_dict()
        self.export_compare(sparse_s,
            wl=b'<|"b" -> 1, "a" -> 0, "c" -> 2|>',
            wxf=b'8:f\x03s\x0bAssociationf\x02s\x04RuleS\x01bC\x01f\x02s\x04RuleS\x01aC\x00f\x02s\x04RuleS\x01cC\x02')

    
    def test_sparse_from_dict__as_list(self):
        sparse_s = self.sparse_series_dict()
        self.export_compare(sparse_s,
            wl=b'{"b" -> 1, "a" -> 0, "c" -> 2}',
            wxf=b'8:f\x03s\x04Listf\x02s\x04RuleS\x01bC\x01f\x02s\x04RuleS\x01aC\x00f\x02s\x04RuleS\x01cC\x02',
            pandas_series_head='list')

    def test_sparse_from_dict__as_dataset(self):
        sparse_s = self.sparse_series_dict()
        self.export_compare(sparse_s,
            wl=b'Dataset[<|"b" -> 1, "a" -> 0, "c" -> 2|>]',
            wxf=b'8:f\x01s\x07Datasetf\x03s\x0bAssociationf\x02s\x04RuleS\x01bC\x01f\x02s\x04RuleS\x01aC\x00f\x02s\x04RuleS\x01cC\x02',
            pandas_series_head='dataset')
    
    # sparse array from dict indexed
    def test_sparse_from_dict_indexed_as_assoc(self):
        sparse_s = self.sparse_series_dict_indexed()
        self.export_compare(sparse_s,
            wl=b'<|0 -> Indeterminate, 1 -> 1., 2 -> Indeterminate|>',
            wxf=b'8:f\x03s\x0bAssociationf\x02s\x04RuleC\x00s\rIndeterminatef\x02s\x04RuleC\x01r\x00\x00\x00\x00\x00\x00\xf0?f\x02s\x04RuleC\x02s\rIndeterminate')

    
    def test_sparse_from_dict_indexed_as_list(self):
        sparse_s = self.sparse_series_dict_indexed()
        self.export_compare(sparse_s,
            wl=b'{0 -> Indeterminate, 1 -> 1., 2 -> Indeterminate}',
            wxf=b'8:f\x03s\x04Listf\x02s\x04RuleC\x00s\rIndeterminatef\x02s\x04RuleC\x01r\x00\x00\x00\x00\x00\x00\xf0?f\x02s\x04RuleC\x02s\rIndeterminate',
            pandas_series_head='list')

    def test_sparse_from_dict_indexed_as_dataset(self):
        sparse_s = self.sparse_series_dict_indexed()
        self.export_compare(sparse_s,
            wl=b'Dataset[<|0 -> Indeterminate, 1 -> 1., 2 -> Indeterminate|>]',
            wxf=b'8:f\x01s\x07Datasetf\x03s\x0bAssociationf\x02s\x04RuleC\x00s\rIndeterminatef\x02s\x04RuleC\x01r\x00\x00\x00\x00\x00\x00\xf0?f\x02s\x04RuleC\x02s\rIndeterminate',
            pandas_series_head='dataset')
    
    # sparse array with zeros
    def test_sparse_array_as_numpy(self):
        sparse_s = self.sparse_series_list_fill_zero()
        self.export_compare(sparse_s,
            wl=b'BinaryDeserialize[ByteArray["ODrCAwEEAQAAAAAAAAADAAAAAAAAAA=="]]',
            wxf=b'8:\xc2\x03\x01\x04\x01\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00')

    # 
    def test_timeseries(self):
        ts = self.sparse_series_date()
        self.export_compare(ts,
            wl=b'TimeSeries[{{DateObject[{2011, 1, 3, 0, 0, 0.}, "Instant", "Gregorian", $TimeZone], 0.}, {DateObject[{2011, 1, 4, 0, 0, 0.}, "Instant", "Gregorian", $TimeZone], Indeterminate}, {DateObject[{2011, 1, 5, 0, 0, 0.}, "Instant", "Gregorian", $TimeZone], 2.}, {DateObject[{2011, 1, 6, 0, 0, 0.}, "Instant", "Gregorian", $TimeZone], Indeterminate}, {DateObject[{2011, 1, 7, 0, 0, 0.}, "Instant", "Gregorian", $TimeZone], 4.}}]',
            wxf=b'8:f\x01s\nTimeSeriesf\x05s\x04Listf\x02s\x04Listf\x04s\nDateObjectf\x06s\x04Listj\xdb\x07C\x01C\x03C\x00C\x00r\x00\x00\x00\x00\x00\x00\x00\x00S\x07InstantS\tGregorians\t$TimeZoner\x00\x00\x00\x00\x00\x00\x00\x00f\x02s\x04Listf\x04s\nDateObjectf\x06s\x04Listj\xdb\x07C\x01C\x04C\x00C\x00r\x00\x00\x00\x00\x00\x00\x00\x00S\x07InstantS\tGregorians\t$TimeZones\rIndeterminatef\x02s\x04Listf\x04s\nDateObjectf\x06s\x04Listj\xdb\x07C\x01C\x05C\x00C\x00r\x00\x00\x00\x00\x00\x00\x00\x00S\x07InstantS\tGregorians\t$TimeZoner\x00\x00\x00\x00\x00\x00\x00@f\x02s\x04Listf\x04s\nDateObjectf\x06s\x04Listj\xdb\x07C\x01C\x06C\x00C\x00r\x00\x00\x00\x00\x00\x00\x00\x00S\x07InstantS\tGregorians\t$TimeZones\rIndeterminatef\x02s\x04Listf\x04s\nDateObjectf\x06s\x04Listj\xdb\x07C\x01C\x07C\x00C\x00r\x00\x00\x00\x00\x00\x00\x00\x00S\x07InstantS\tGregorians\t$TimeZoner\x00\x00\x00\x00\x00\x00\x10@'
        )
            