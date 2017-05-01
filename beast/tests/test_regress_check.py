import os.path
import filecmp

from astropy.utils.data import download_file
from astropy.tests.helper import remote_data
from astropy.table import Table

from beast.physicsmodel.stars import isochrone

@remote_data
def test_padova_isochrone_download():
    # download the cached version
    filename = download_file('http://www.stsci.edu/~kgordon/beast/padova_iso.csv', cache=True)
    table_cache = Table.read(filename, format='ascii.basic', comment='#',
                             delimiter=',')
    
    # initialize isochrone
    oiso = isochrone.PadovaWeb()

    # download from the padova website
    t = oiso._get_t_isochrones(6.0, 10.13, 1.0, [0.03, 0.019, 0.008, 0.004])
    t.header['NAME'] = 'Test of Cached Isochrones'

    # save
    savename = '/tmp/padova_iso.csv'
    t.write(savename)

    # get the new table
    table_new = Table.read(savename)
    
    # compare
    assert len(table_new) == len(table_cache)
                       
