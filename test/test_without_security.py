import unittest
import os
from secure_config_manager import SecureConfigManager


CONFIGS_PATH = "examples/configs"
if not os.path.exists(CONFIGS_PATH):
    CONFIGS_PATH = f"../{CONFIGS_PATH}"


class WithoutSecurityTestCase(unittest.TestCase):
    def setUp(self):
        self.file_names = dict()
        self.file_names["without_security"] = f"{CONFIGS_PATH}/without_security.ini"
        self.config_mgr = SecureConfigManager(file_name=self.file_names["without_security"])
        self.config_mgr.save()

    def test_init(self):
        self.assertIsNotNone(self.config_mgr._parser)
        self.assertIsNone(self.config_mgr._key)
        self.assertFalse(self.config_mgr.encryption)
        self.assertEqual(first=self.file_names["without_security"], second=self.config_mgr.config_file)
        self.assertIsNone(self.config_mgr._user)
        self.assertIsNone(self.config_mgr._pass)
        self.assertFalse(self.config_mgr._is_securable())

    def test_properties(self):
        self.assertEqual(first=self.config_mgr.config_file, second=self.config_mgr._config_file)
        self.assertEqual(first=self.config_mgr.encryption, second=self.config_mgr._encryption)

    def test_files_created(self):
        for k, v in self.file_names.items():
            self.assertTrue(os.path.exists(v), f"{k} file was not created.")

    def test_add_section(self):
        section_name = "new_section"
        self.config_mgr.add_section(section=section_name)
        self.config_mgr.save()
        cm = SecureConfigManager(file_name=self.file_names["without_security"])
        self.assertIn(section_name, cm.get_sections())

    def test_get_set_option(self):
        section_name = "new_section"
        option = "new_option"
        value = "some value"
        self.config_mgr.set_option(section=section_name, option=option, value=value)
        self.config_mgr.save()
        cm = SecureConfigManager(file_name=self.file_names["without_security"])
        self.assertEqual(value, cm.get_option(section=section_name, option=option))

    def test_get_section(self):
        section_name = "new_section"
        option = "new_option"
        value = "some value"
        self.config_mgr.set_option(section=section_name, option=option, value=value)
        self.config_mgr.save()
        cm = SecureConfigManager(file_name=self.file_names["without_security"])
        self.assertDictEqual({option: value}, cm.get_section(section=section_name))


if __name__ == "__main__":
    unittest.main()
