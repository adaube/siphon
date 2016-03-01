# Copyright (c) 2013-2015 Unidata.
# Distributed under the terms of the MIT License.
# SPDX-License-Identifier: MIT

from io import BytesIO
from siphon.testing import get_recorder
from siphon.cdmr.ncstream import read_ncstream_messages, read_var_int
from siphon.cdmr.ncStream_pb2 import Header

recorder = get_recorder(__file__)


@recorder.use_cassette('latest_rap_catalog')
def get_test_latest_url(query=None):
    from siphon.catalog import TDSCatalog
    cat = TDSCatalog('http://thredds-test.unidata.ucar.edu/thredds/catalog/'
                     'grib/NCEP/RAP/CONUS_13km/latest.xml')
    url = list(cat.datasets.values())[0].access_urls['CdmRemote']
    if query:
        url += '?' + query
    return url


@recorder.use_cassette('latest_rap_ncstream_header')
def get_header_remote():
    from siphon.http_util import urlopen
    return urlopen(get_test_latest_url('req=header'))


def test_var_int():
    for src, truth in [(b'\xb6\xe0\x02', 45110), (b'\x17\n\x0b', 23)]:
        yield check_var_int, src, truth


def check_var_int(src, result):
    read_var_int(BytesIO(src)) == result


def test_header_message_def():
    'Test parsing of Header message'
    f = get_header_remote()
    messages = read_ncstream_messages(f)
    assert len(messages) == 1
    assert isinstance(messages[0], Header)
    head = messages[0]
    assert head.location == ('http://thredds-test.unidata.ucar.edu/thredds/cdmremote/grib/'
                             'NCEP/RAP/CONUS_13km/RR_CONUS_13km_20150519_0300.grib2')
    assert head.title == ''
    assert head.id == ''
    assert head.version == 1


def test_local_data():
    f = BytesIO(b'\xab\xec\xce\xba\x17\n\x0breftime_ISO\x10\x07\x1a\x04\n'
                b'\x02\x10\x01(\x02\x01\x142014-10-28T21:00:00Z')
    messages = read_ncstream_messages(f)
    assert len(messages) == 1
    assert messages[0][0] == '2014-10-28T21:00:00Z'
