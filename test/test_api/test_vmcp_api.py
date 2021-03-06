# -*- coding: utf8 -*-
# This file is part of PyBossa.
#
# Copyright (C) 2013 SF Isle of Man Limited
#
# PyBossa is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# PyBossa is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with PyBossa.  If not, see <http://www.gnu.org/licenses/>.
import json
from default import flask_app, with_context
from mock import patch, Mock
from test_api import TestAPI



class TestVmcpAPI(TestAPI):

    @with_context
    def test_vcmp(self):
        """Test VCMP without key fail works."""
        if self.flask_app.config.get('VMCP_KEY'):
            self.flask_app.config.pop('VMCP_KEY')
        res = self.app.get('api/vmcp', follow_redirects=True)
        err = json.loads(res.data)
        assert res.status_code == 501, err
        assert err['status_code'] == 501, err
        assert err['status'] == "failed", err
        assert err['target'] == "vmcp", err
        assert err['action'] == "GET", err

    @with_context
    @patch.dict(flask_app.config, {'VMCP_KEY': 'invalid.key'})
    def test_vmcp_file_not_found(self):
        """Test VMCP with invalid file key works."""
        res = self.app.get('api/vmcp', follow_redirects=True)
        err = json.loads(res.data)
        assert res.status_code == 501, err
        assert err['status_code'] == 501, err
        assert err['status'] == "failed", err
        assert err['target'] == "vmcp", err
        assert err['action'] == "GET", err

    @with_context
    @patch.dict(flask_app.config, {'VMCP_KEY': 'invalid.key'})
    def test_vmcp_01(self):
        """Test VMCP errors works"""
        # Even though the key does not exists, let's patch it to test
        # all the errors
        with patch('os.path.exists', return_value=True):
            res = self.app.get('api/vmcp', follow_redirects=True)
            err = json.loads(res.data)
            assert res.status_code == 415, err
            assert err['status_code'] == 415, err
            assert err['status'] == "failed", err
            assert err['target'] == "vmcp", err
            assert err['action'] == "GET", err
            assert err['exception_msg'] == 'cvm_salt parameter is missing'

    @with_context
    @patch.dict(flask_app.config, {'VMCP_KEY': 'invalid.key'})
    def test_vmcp_02(self):
        """Test VMCP signing works."""
        rsa = Mock()
        rsa.sign.return_value = 'signed'
        with patch('os.path.exists', return_value=True):
            with patch('M2Crypto.RSA.load_key', return_value=rsa):
                res = self.app.get('api/vmcp?cvm_salt=testsalt',
                                   follow_redirects=True)
                out = json.loads(res.data)
                assert res.status_code == 200, out
                assert out.get('signature') is not None, out

                # Now with a post
                res = self.app.post('api/vmcp?cvm_salt=testsalt',
                                   follow_redirects=True)
                assert res.status_code == 405, res.status_code
