# -*- coding: utf-8 -*-
""" Tests for VTM GO EPG API """

# pylint: disable=missing-docstring

from __future__ import absolute_import, division, print_function, unicode_literals

import unittest
import warnings

from urllib3.exceptions import InsecureRequestWarning

from resources.lib import plugin
from resources.lib.kodiwrapper import KodiWrapper
from resources.lib.vtmgo import vtmgoepg

kodi = KodiWrapper()
routing = plugin.routing


class TestVtmGoEpg(unittest.TestCase):
    """ Tests for VTM GO EPG API """

    def __init__(self, *args, **kwargs):
        super(TestVtmGoEpg, self).__init__(*args, **kwargs)

        self._vtmgoepg = vtmgoepg.VtmGoEpg(kodi)

    def setUp(self):
        # Don't warn that we don't close our HTTPS connections, this is on purpose.
        # warnings.simplefilter("ignore", ResourceWarning)

        # Don't warn that we are not verifying the certificates of VTM GO API.
        warnings.simplefilter("ignore", InsecureRequestWarning)

    def test_get_epg(self):
        from datetime import date

        # Get list of EPG for today
        epg = self._vtmgoepg.get_epg(channel='vitaya')
        self.assertTrue(epg)

        epg = self._vtmgoepg.get_epg(channel='vtm', date=date.today().strftime('%Y-%m-%d'))
        self.assertTrue(epg)

        # Get list of EPG for tomorrow
        epg_tomorrow = self._vtmgoepg.get_epg(channel='vtm', date='tomorrow')
        self.assertTrue(epg_tomorrow)

        # Get list of EPG for yesterday
        epg_yesterday = self._vtmgoepg.get_epg(channel='vtm', date='yesterday')
        self.assertTrue(epg_yesterday)

        # Get list of EPG for today
        epg_today = self._vtmgoepg.get_epg(channel='vtm', date='today')
        self.assertTrue(epg_today)

        combined_broadcasts = epg_today.broadcasts + epg_tomorrow.broadcasts + epg_yesterday.broadcasts

        broadcast = next(b for b in combined_broadcasts if b.playable_type == 'episodes')
        if broadcast:
            details = self._vtmgoepg.get_details(channel='vtm', program_type=broadcast.playable_type, epg_id=broadcast.uuid)
            self.assertTrue(details)
            plugin.run([routing.url_for(plugin.show_program_from_epg, channel='vtm', program=broadcast.uuid), '0', ''])

        broadcast = next(b for b in combined_broadcasts if b.playable_type == 'movies')
        if broadcast:
            details = self._vtmgoepg.get_details(channel='vtm', program_type=broadcast.playable_type, epg_id=broadcast.uuid)
            self.assertTrue(details)
            plugin.run([routing.url_for(plugin.play_epg_program, channel='vtm', program_type=broadcast.playable_type, epg_id=broadcast.uuid, aired='123'), '0', ''])

        broadcast = next(b for b in combined_broadcasts if b.playable_type == 'oneoffs')
        if broadcast:
            details = self._vtmgoepg.get_details(channel='vtm', program_type=broadcast.playable_type, epg_id=broadcast.uuid)
            self.assertTrue(details)

        plugin.run([routing.url_for(plugin.show_program_from_epg, channel='vtm', program='error'), '0', ''])


if __name__ == '__main__':
    unittest.main()
