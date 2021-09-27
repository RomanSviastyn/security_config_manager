Welcome Secure Config Manager repository!
---

[![MIT License][license-shield]][license-url]

## Installation

1. install python packages mentioned in 
[requirements.txt](https://github.com/RomanSviastyn/security_config_manager/blob/master/requirements.txt).
   ```sh
   pip install -r requirements.txt
   ```
2. To get the package available in your python scripts you have to deploy package locally.
   ```sh
   cd securityconfigmanager
   pip install .
   ```

## About the project

The main goal of the module is to _**maintain** sensitive information in a **secure** way_.

The module uses the next modules inside:
* [ConfigParser][config-parser-url] to maintain any information as configurations 
* [Fernet](https://cryptography.io/en/latest/) to encrypt/decrypt config file with a key
* [sha256](https://docs.python.org/3/library/hashlib.html) to hash a config file password
* [uuid4](https://docs.python.org/3/library/uuid.html) to generate salt for config file password

---
The module has only one class [SecureConfigManager](https://github.com/RomanSviastyn/security_config_manager/blob/master/secure_config_manager.py).

The constructor of the class `__init__(file_name: str = None, key=None, encryption: bool = False, 
user: str = None, password: str = None)` doesn't require any parameters.
* `file_name` [str] - path to the config file
* `key` [str|bytes] - decryption key if we wanted to read encrypted config file
* `encryption` [bool] - set flag if we wanted encrypt config file or not or if we wanted to read encrypted config file. You must use `generate_key()` before `save()` while creating a file.
* `user` [str] - is just a username/login for config file and additional security level.
* `password` [str] - is just a password of config file and additional security level.

The class has the next properties/setters:
* `config_file` returns name of config file (type `str`)
* `encryption` returns if current configurations are encrypted (type `bool`)

The class is just a kind of extension of [ConfigParser][config-parser-url] object. It has same override methods:
* `add_section(section: str)`
* `remove_section(section: str)`
* `get_sections()`
* `get_section(section: str)`
* `set_option(section: str, option: str, value: Any)`
* `get_option(section: str, option: str)`
* `remove_option(section: str, option: str)`
* `read_string(content: str)`
* `read_dict(element: dict, key: str)`

and extends additional methods:
* `read()`
* `save(file_name: str = None)`
* `generate_key(save: bool = False, verbose: bool = False)`.

A config file has up to three levels of security:
1. OS level: change mod (`chmod 0600`). Use [stat](https://docs.python.org/3.6/library/stat.html) lib and 
os.[chmod](https://docs.python.org/3.6/library/os.html?highlight=chmod#os.chmod).
2. File level: encryption by a key
3. Information access level: user/password

---
# Examples

#### Example 1.1: Create a simple config file
```python
from secure_config_manager import SecureConfigManager

file_name = "configs/empty.ini"
cm = SecureConfigManager(file_name=file_name)
'''or you can create an empty object and set properties'''
# cm = SecureConfigManager()
# cm.config_file=file_name
cm.add_section("GLOBALS")
cm.set_option(section="GLOBALS", option="path", value="current_path")
cm.save()
```
`configs/empty.ini`:
```ini
[GLOBALS]
path = current_path
```


#### Example 1.2: Read existing config file
```python
from secure_config_manager import SecureConfigManager

file_name = "configs/empty.ini"
cm = SecureConfigManager(file_name=file_name)
print(cm.get_sections())
print(cm.get_section("GLOBALS"))
```
Output:
```
['GLOBALS']
{'path': 'current_path'}
```


#### Example 2: Create config file with username/password
```python
from secure_config_manager import SecureConfigManager

file_name = "configs/empty.ini"
user = "adam"
password = "adam_password"
cm = SecureConfigManager(file_name=file_name, user=user, password=password)
cm.add_section("GLOBALS")
cm.set_option(section="GLOBALS", option="path", value="current_path")
cm.save()
```
configs/empty.ini:
```ini
[security]
user = adam
password = 227fbd536d5370b41c94447c94589c3105aeb76b6cd88c085000fc3dee543258
salt = bfb0b66a300d490bafb1111f3d918917

[GLOBALS]
path = current_path
```


#### Example 2.1: Read config file with valid username/password
```python
from secure_config_manager import SecureConfigManager

file_name = "configs/empty.ini"
cm = SecureConfigManager(file_name=file_name, user="adam", password="adam_password")
print(cm.get_sections())
print(cm.get_section("security"))
```
Output:
```
['security', 'GLOBALS']
{'user': 'adam', 'password': '227fbd536d5370b41c94447c94589c3105aeb76b6cd88c085000fc3dee543258', 'salt': 'bfb0b66a300d490bafb1111f3d918917'}
```


#### Example 2.2: Read config file with invalid username/password (wrong password).
```python
from secure_config_manager import SecureConfigManager

file_name = "configs/empty.ini"
cm = SecureConfigManager(file_name=file_name, user="adam", password="adam_Password")
print(cm.get_sections())
print(cm.get_section("security"))
```
Output:
```
Exception: Your credentials are invalid!
```

But still anyone can read content of the config file.


#### Example 3: Encrypt config file

Here we reading existing config file and encrypting all configs. If we wanted to place
encrypted configs into a new file then we have to specify a new file_name under method `save()`.
If you execute method `save()` without file name it fill rewrite existing file. 
```python
from secure_config_manager import SecureConfigManager

file_name = "configs/empty.ini"
encrypt_file_name = "configs/encrypted.ini"
cm = SecureConfigManager(file_name=file_name, user="adam", password="adam_password")
cm.generate_key(save=True, verbose=True)
cm.save(file_name=encrypt_file_name)
```
Output:
```
b'UibGohyBJm1Xz6iOkqavimiF-QAIzXIF3dpInbW5Qp8='
```

configs/empty.ini:
```ini
[security]
user = adam
password = 227fbd536d5370b41c94447c94589c3105aeb76b6cd88c085000fc3dee543258
salt = bfb0b66a300d490bafb1111f3d918917

[GLOBALS]
path = current_path
```

configs/encrypted.ini:
```
gAAAAABhG6t2HzKGNyB1FhgPyk4hUzFLh8XuxkZgmMRyM__fpavq7Et3hCFZYOmN5gmFqOfnhC_rBnVv-KCU-mI-VviPkKaqtmCeB21bWg55LSzasY9pk0vUgqMgorTIsrXqj5EAbY7-9quUeNtH6T1-Ko-v-lJPScqlPauHPyhnpmUCygQSfeJT2Fm5WKB7ehkqrPcRQo5JHbIH4sNuBrYahWtwJnnvqVsyt7nuWfvQf8RDPPTNkGwFTLn0e0mIfJywMOtpDLfqoSX4oPD3pWg2srpUBqwXQC0Ch-4qvMl8PNhqnM3NDdo=
```

You must save the key somewhere so you could restore your data from encrypted file.


#### Example 3.2: Read encrypted config file

```python
from secure_config_manager import SecureConfigManager

key = "UibGohyBJm1Xz6iOkqavimiF-QAIzXIF3dpInbW5Qp8="  # Exactly the same that you got when executed method `generate_key()` in Example 3
encrypt_file_name = "configs/encrypted.ini"
cm = SecureConfigManager(file_name=encrypt_file_name, user="adam", password="adam_password", encryption=True, key=key)
print(cm.get_sections())
print(cm.get_section("GLOBALS"))
print(cm.get_section("security"))
```
Output:
```
['security', 'GLOBALS']
{'path': 'current_path'}
{'user': 'adam', 'password': '227fbd536d5370b41c94447c94589c3105aeb76b6cd88c085000fc3dee543258', 'salt': 'bfb0b66a300d490bafb1111f3d918917'}
```


#### Example 3.2: Read encrypted config file with a wrong key

```python
from secure_config_manager import SecureConfigManager

key = "S_nwFZbX8Cofe_gPRxGAxwd2iBH7Z1wtjMQ5u3axkIQ="
encrypt_file_name = "configs/encrypted.ini"
cm = SecureConfigManager(file_name=encrypt_file_name, user="adam", password="adam_password", encryption=True, key=key)
print(cm.get_sections())
print(cm.get_section("GLOBALS"))
print(cm.get_section("security"))
```
Output:
```
Exception: cryptography.fernet.InvalidToken
```


## License

Distributed under the MIT License. See `LICENSE` for more information.


## Contacts
Roman Sviastyn - [roman.sviastyn@gmail.com](mailto:roman.sviastyn@gmail.com)

Project Link: [https://github.com/RomanSviastyn/security_config_manager](https://github.com/RomanSviastyn/security_config_manager)


<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[license-shield]: https://img.shields.io/github/license/othneildrew/Best-README-Template.svg?style=for-the-badge
[license-url]: https://github.com/RomanSviastyn/security_config_manager/blob/master/LICENSE
[config-parser-url]: https://docs.python.org/3/library/configparser.html