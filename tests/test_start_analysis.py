__author__ = 'Abdulrahman Semrie<xabush@singularitynet.io>'

import unittest
import os
import mongomock
import shutil
from config import TEST_DATA_DIR, moses_options, crossval_options
import uuid
from models.dbmodels import Session
from task.task_runner import start_analysis, celery
from unittest.mock import patch
import base64


class TestTaskRunner(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        dataset = os.path.join(TEST_DATA_DIR, "bin_truncated.csv")
        with open(dataset, "rb") as fp:
            content = fp.read()

        cls.dataset = base64.b64encode(content)
        cls.session_id = str(uuid.uuid4())
        cls.cwd = os.path.join(TEST_DATA_DIR, f"session_{cls.session_id}")

    def setUp(self):
        celery.conf.update(CELERY_ALWAYS_EAGER=True)

    @patch("pymongo.MongoClient")
    @patch("task.task_runner.CrossValidation")
    def test_start_analysis(self, cross_val, client):
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        session = {
            "id": self.session_id, "moses_options": moses_options, "crossval_options": crossval_options,
            "dataset": self.dataset, "mnemonic": "abcdr4e", "target_feature": "case", "swd": None,
            "filter_opts": {"score": "precision", "value": 0.4}
        }

        mock_db.sessions.insert_one(session)
        cross_val.return_value.run_folds.return_value = "Run folds"

        start_analysis.delay(**session)

        tmp_session = Session.get_session(mock_db, session_id=self.session_id)
        self.assertEqual(tmp_session.status, 2)
        self.assertEqual(tmp_session.progress, 100)

    @patch("pymongo.MongoClient")
    @patch("task.task_runner.CrossValidation")
    def test_start_analysis_error_path(self, cross_val, client):
        mock_db = mongomock.MongoClient().db
        client().__getitem__.return_value = mock_db
        session = {
            "id": self.session_id, "moses_options": moses_options, "crossval_options": crossval_options,
            "dataset": self.dataset, "mnemonic": "abcdr4e", "target_feature": "case",
            "filter_opts": {"score": "precision", "value": 0.4}
        }

        mock_db.sessions.insert_one(session)
        cross_val.side_effect = Exception("Mock exception")

        self.assertRaises(Exception, start_analysis.delay(**session))

        tmp_session = Session.get_session(mock_db, session_id=self.session_id)

        self.assertEqual(tmp_session.status, -1)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.cwd):
            shutil.rmtree(cls.cwd)


if __name__ == "__main__":
    unittest.main()
