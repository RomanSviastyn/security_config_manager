from os import chmod
from stat import S_IRUSR, S_IWUSR
from io import StringIO as io_StringIO
from configparser import ConfigParser
from cryptography.fernet import Fernet
from hashlib import sha256
from os.path import exists as os_path_exists
from typing import Any, List, NoReturn
from uuid import uuid4


class SecureConfigManager:
    #   region >>       Internal methods        <<

    #   region Constructor
    def __init__(self, file_name: str = None, key=None, encryption: bool = False,
                 user: str = None, password: str = None):
        # create a parser
        self._parser = ConfigParser()
        self.set_key(key)
        self.encryption = encryption
        self.config_file = file_name
        self._user = user
        self._pass = password
        if self._pass:
            self._set_password()

    # endregion

    #   region Destructor
    def __del__(self):
        del self._parser
        del self._key

    # endregion

    #   endregion

    #   region >>       Properties              <<
    @property
    def config_file(self) -> str:
        return self._config_file

    @property
    def encryption(self) -> bool:
        return self._encryption

    #   endregion

    #   region >>       Setters                 <<
    @config_file.setter
    def config_file(self, file_name: str):
        if file_name is not None:
            if os_path_exists(file_name):
                self._config_file = file_name
                self.read()
            else:
                self._config_file = file_name

    @encryption.setter
    def encryption(self, value: bool):
        self._encryption = True if value else False

    def set_key(self, key):
        if key:
            if isinstance(key, str):
                self._key = key.encode("utf-8")
                self.encryption = True
            if type(key) == bytes:
                self._key = key
                self.encryption = True
        else:
            self._key = None
            self.encryption = False

    #   endregion

    #   region >>       Protected Methods       <<

    def _are_credentials_valid(self) -> bool:
        stored_salt = self._get_option(section="security", option="salt")
        stored_hash = self._get_option(section="security", option="password")
        hash_to_check = self._get_pass_hash(user=self._user, password=self._pass, salt=stored_salt)
        return stored_hash == hash_to_check

    def _is_securable(self) -> bool:
        return bool(self._user) and bool(self._pass)

    def _security(func):
        def wrapper(self, *args, **kwargs):
            if self._is_securable():
                if self._are_credentials_valid():
                    return func(self, *args, **kwargs)
                else:
                    raise Exception("Your credentials are invalid!")
            else:
                return func(self, *args, **kwargs)

        return wrapper

    def _get_pass_hash(self, user: str, password: str, salt: str) -> str:
        return sha256(salt.encode() + password.encode() + user.encode()).hexdigest()

    def _set_password(self):
        salt = uuid4().hex
        if "security" not in self._get_sections():
            self._add_section(section="security")
            self._set_option(section="security", option="user", value=self._user)
            self._set_option(section="security", option="password",
                             value=self._get_pass_hash(user=self._user, password=self._pass, salt=salt))
            self._set_option(section="security", option="salt", value=salt)
        else:
            if "password" not in self._get_section(section="security").keys():
                self._set_option(section="security", option="password",
                                 value=self._get_pass_hash(user=self._user, password=self._pass, salt=salt))
                self._set_option(section="security", option="salt", value=salt)
            if "user" not in self._get_section(section="security").keys():
                self._set_option(section="security", option="user", value=self._user)

    def _get_section_configs(self, section: str) -> dict:
        # get section
        configs = dict()
        if self._parser.has_section(section):
            params = self._parser.items(section)
            for param in params:
                configs[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the file'.format(section))

        return configs

    def _encrypt(self, data: bytes) -> bytes:
        return Fernet(self._key).encrypt(data)

    def _decrypt(self, data: bytes) -> bytes:
        return Fernet(self._key).decrypt(data)

    def _add_section(self, section: str):
        if section and section not in self._parser.sections():
            self._parser.add_section(section=section)
        else:
            pass
            # raise ConfigParser

    def _get_sections(self) -> List[str]:
        return self._parser.sections()

    def _remove_section(self, section: str):
        if section and section in self._parser.sections():
            self._parser.remove_section(section=section)

    def _get_section(self, section: str) -> dict:

        return self._get_section_configs(section=section)

    def _set_option(self, section: str, option: str, value: Any):
        if self._parser.has_section(section) and option:
            self._parser.set(section=section, option=option, value=value)

    def _get_option(self, section: str, option: str) -> str:
        return self._parser.get(section=section, option=option)

    def _set_owner_mode(self, file_name: str):
        chmod(file_name, S_IRUSR | S_IWUSR)
    #   endregion

    #   region >>       Public Methods          <<
    @_security
    def add_section(self, section: str):
        self._add_section(section=section)

    @_security
    def remove_section(self, section: str):
        self._remove_section(section=section)

    @_security
    def get_sections(self) -> List[str]:
        return self._get_sections()

    @_security
    def get_section(self, section: str) -> dict:
        return self._get_section(section=section)

    @_security
    def set_option(self, section: str, option: str, value: Any):
        self._set_option(section=section, option=option, value=value)

    @_security
    def get_option(self, section: str, option: str) -> str:
        return self._get_option(section=section, option=option)

    @_security
    def remove_option(self, section: str, option: str) -> NoReturn:
        self._parser.remove_option(section=section, option=option)

    def read(self) -> str:
        if not os_path_exists(self._config_file):
            raise FileNotFoundError(self._config_file)
        with open(self._config_file, "rb") as outfile:
            content = outfile.read()
        if self._encryption:
            content = self._decrypt(data=content)
        content = content.decode("utf-8")
        # read config file
        self._parser.read_string(content)
        return content

    @_security
    def read_string(self, content: str):
        self._parser.read_string(content)

    @_security
    def read_dict(self, element: dict, key: str):
        self._parser.read_dict(dictionary=element, source=key)

    @_security
    def save(self, file_name: str = None) -> NoReturn:
        if not file_name:
            file_name = self.config_file
        if self._encryption:
            with open(file=file_name, mode="wb") as f:
                with io_StringIO() as s:
                    self._parser.write(s)
                    s.seek(0)
                    content = s.read()
                f.write(self._encrypt(data=content.encode("utf-8")))
            self._set_owner_mode(file_name=file_name)
        else:
            with open(file=file_name, mode="w") as f:
                self._parser.write(f)

    @_security
    def generate_key(self, save: bool = False, verbose: bool = False) -> bytes:
        _key = Fernet.generate_key()
        if verbose:
            print(_key)
        if save:
            self._key = _key
            self._encryption = True
        return _key
    #   endregion
