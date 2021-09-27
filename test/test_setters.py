import os
import unittest
from secure_config_manager import SecureConfigManager


CONFIGS_PATH = "examples/configs"
if not os.path.exists(CONFIGS_PATH):
    CONFIGS_PATH = f"../{CONFIGS_PATH}"


class ConfigFileSetterTestCase(unittest.TestCase):
    def setUp(self):
        self.file_name = f"{CONFIGS_PATH}/test_setters.ini"
        self.config_mgr = SecureConfigManager(file_name=self.file_name)
        self.config_mgr.save()

    def test_set_none(self):
        self.config_mgr.config_file = None
        self.assertEqual(self.file_name, self.config_mgr.config_file)

    def test_set_existing_file(self):
        new_file_name: str = f"{CONFIGS_PATH}/without_security.ini"
        self.config_mgr.config_file = new_file_name
        self.assertEqual(new_file_name, self.config_mgr.config_file)

    def test_set_not_existing_file(self):
        new_file_name: str = f"not_existists.ini"
        self.config_mgr.config_file = new_file_name
        self.assertEqual(new_file_name, self.config_mgr.config_file)


class EncryptionSetterTestCase(unittest.TestCase):
    def setUp(self):
        self.file_name = f"{CONFIGS_PATH}/test_setters.ini"
        self.config_mgr = SecureConfigManager(file_name=self.file_name)
        self.config_mgr.save()

    def test_set_none(self):
        self.config_mgr.encryption = None
        self.assertFalse(self.config_mgr.encryption)

    def test_set_false(self):
        self.config_mgr.encryption = False
        self.assertFalse(self.config_mgr.encryption)

    def test_set_true(self):
        self.config_mgr.encryption = True
        self.assertTrue(self.config_mgr.encryption)

    def test_set_empty_str(self):
        self.config_mgr.encryption = ""
        self.assertFalse(self.config_mgr.encryption)

    def test_set_str(self):
        self.config_mgr.encryption = "True"
        self.assertTrue(self.config_mgr.encryption)

    def test_set_zero_int(self):
        self.config_mgr.encryption = 0
        self.assertFalse(self.config_mgr.encryption)

    def test_set_int(self):
        self.config_mgr.encryption = -1
        self.assertTrue(self.config_mgr.encryption)


class SetKeyTestCase(unittest.TestCase):
    def setUp(self):
        self.file_name = f"{CONFIGS_PATH}/test_setters.ini"
        self.config_mgr = SecureConfigManager(file_name=self.file_name)
        self.config_mgr.save()

    def test_set_none(self):
        new_key: str = None
        self.config_mgr.set_key(key=new_key)
        self.assertIsNone(self.config_mgr._key)
        self.assertFalse(self.config_mgr.encryption)

    def test_set_str(self):
        new_key = "None"
        self.config_mgr.set_key(key=new_key)
        self.assertIs(bytes, type(self.config_mgr._key))
        self.assertEqual(new_key.encode("utf-8"), self.config_mgr._key)

    def test_set_bytes(self):
        new_key = b"None"
        self.config_mgr.set_key(key=new_key)
        self.assertIs(bytes, type(self.config_mgr._key))
        self.assertEqual(new_key, self.config_mgr._key)


class GenerateKeyTestCase(unittest.TestCase):
    def setUp(self):
        self.file_name = f"{CONFIGS_PATH}/test_setters.ini"
        self.config_mgr = SecureConfigManager(file_name=self.file_name)
        self.config_mgr.save()

    def test_default(self):
        key = self.config_mgr.generate_key()
        self.assertNotEqual(key, self.config_mgr._key)

    def test_not_save(self):
        key = self.config_mgr.generate_key(save=False)
        self.assertNotEqual(key, self.config_mgr._key)

    def test_save(self):
        key = self.config_mgr.generate_key(save=True)
        self.assertEqual(key, self.config_mgr._key)
        self.assertTrue(self.config_mgr.encryption)


if __name__ == "__main__":
    unittest.main()
