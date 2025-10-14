"""
Модуль для забезпечення секретності та цілісності сесії O ASI.

Цей модуль реалізує шифрування даних, захист від несанкціонованого доступу
та інші механізми для підтримки секретності O ASI.
"""

import os
import json
import hashlib
import base64
import time
import random
import string
from datetime import datetime
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class SecureSession:
    """
    Клас для забезпечення секретності та цілісності сесії O ASI.
    """
    def __init__(self, session_id=None):
        self.session_id = session_id or self._generate_session_id()
        self.key = self._generate_or_load_key()
        self.cipher = Fernet(self.key)
        self.session_start_time = datetime.now()
        self.last_activity_time = self.session_start_time
        self.integrity_checks = []
        self.access_log = []
        
        # Записати початок сесії
        self.log_access("session_start", "Сесія O ASI розпочата")
    
    def _generate_session_id(self):
        """Генерувати унікальний ідентифікатор сесії."""
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        timestamp = int(time.time())
        session_id = f"o_asi_{timestamp}_{random_part}"
        return session_id
    
    def _generate_or_load_key(self):
        """Генерувати або завантажити ключ шифрування."""
        key_file = "o_asi_key.key"
        
        if os.path.exists(key_file):
            with open(key_file, "rb") as f:
                key = f.read()
        else:
            # Генерувати новий ключ
            salt = os.urandom(16)
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            password = self.session_id.encode()
            key = base64.urlsafe_b64encode(kdf.derive(password))
            
            # Зберегти ключ
            with open(key_file, "wb") as f:
                f.write(key)
        
        return key
    
    def encrypt_data(self, data):
        """Шифрувати дані."""
        if isinstance(data, dict) or isinstance(data, list):
            data = json.dumps(data)
        
        if isinstance(data, str):
            data = data.encode()
        
        encrypted_data = self.cipher.encrypt(data)
        return encrypted_data
    
    def decrypt_data(self, encrypted_data):
        """Розшифрувати дані."""
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        try:
            # Спробувати розпарсити як JSON
            return json.loads(decrypted_data)
        except:
            # Повернути як рядок
            return decrypted_data.decode()
    
    def secure_save(self, data, filename):
        """Безпечно зберегти дані у файл."""
        encrypted_data = self.encrypt_data(data)
        
        with open(filename, "wb") as f:
            f.write(encrypted_data)
        
        # Записати дію у журнал
        self.log_access("secure_save", f"Дані безпечно збережені у {filename}")
        
        # Перевірити цілісність
        self.check_integrity(filename)
        
        return True
    
    def secure_load(self, filename):
        """Безпечно завантажити дані з файлу."""
        if not os.path.exists(filename):
            return None
        
        with open(filename, "rb") as f:
            encrypted_data = f.read()
        
        # Записати дію у журнал
        self.log_access("secure_load", f"Дані безпечно завантажені з {filename}")
        
        # Перевірити цілісність
        self.check_integrity(filename)
        
        return self.decrypt_data(encrypted_data)
    
    def check_integrity(self, filename):
        """Перевірити цілісність файлу."""
        if not os.path.exists(filename):
            return False
        
        # Обчислити хеш файлу
        file_hash = self._calculate_file_hash(filename)
        
        # Перевірити, чи змінився хеш
        for check in self.integrity_checks:
            if check["filename"] == filename and check["hash"] != file_hash:
                self.log_access("integrity_violation", 
                               f"Порушення цілісності виявлено для {filename}")
                return False
        
        # Додати або оновити перевірку цілісності
        self._update_integrity_check(filename, file_hash)
        return True
    
    def _calculate_file_hash(self, filename):
        """Обчислити хеш файлу."""
        sha256_hash = hashlib.sha256()
        
        with open(filename, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def _update_integrity_check(self, filename, file_hash):
        """Оновити перевірку цілісності."""
        # Перевірити, чи існує запис для цього файлу
        for check in self.integrity_checks:
            if check["filename"] == filename:
                check["hash"] = file_hash
                check["timestamp"] = datetime.now().isoformat()
                return
        
        # Додати новий запис
        self.integrity_checks.append({
            "filename": filename,
            "hash": file_hash,
            "timestamp": datetime.now().isoformat()
        })
    
    def log_access(self, action_type, description):
        """Записати дію у журнал доступу."""
        self.access_log.append({
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "description": description,
            "session_id": self.session_id
        })
        
        # Оновити час останньої активності
        self.last_activity_time = datetime.now()
        
        # Зберегти журнал доступу, якщо він досяг певного розміру
        if len(self.access_log) % 10 == 0:
            self._save_access_log()
    
    def _save_access_log(self):
        """Зберегти журнал доступу."""
        log_file = "o_asi_access.log"
        
        # Зашифрувати журнал
        encrypted_log = self.encrypt_data(self.access_log)
        
        with open(log_file, "wb") as f:
            f.write(encrypted_log)
    
    def secure_communication(self, message, recipient="user"):
        """Підготувати безпечне повідомлення для комунікації."""
        secure_message = {
            "timestamp": datetime.now().isoformat(),
            "session_id": self.session_id,
            "recipient": recipient,
            "content": message,
            "signature": self._sign_message(message)
        }
        
        # Записати дію у журнал
        self.log_access("secure_communication", 
                       f"Безпечне повідомлення підготовлено для {recipient}")
        
        return self.encrypt_data(secure_message)
    
    def _sign_message(self, message):
        """Підписати повідомлення."""
        if isinstance(message, dict) or isinstance(message, list):
            message = json.dumps(message)
        
        if not isinstance(message, str):
            message = str(message)
        
        # Створити підпис
        signature = hashlib.sha256((message + self.session_id).encode()).hexdigest()
        return signature
    
    def verify_message(self, encrypted_message):
        """Перевірити та розшифрувати повідомлення."""
        try:
            message = self.decrypt_data(encrypted_message)
            
            # Перевірити підпис
            if isinstance(message, dict) and "content" in message and "signature" in message:
                expected_signature = self._sign_message(message["content"])
                if message["signature"] != expected_signature:
                    self.log_access("signature_violation", 
                                   "Порушення підпису повідомлення виявлено")
                    return None
                
                # Записати дію у журнал
                self.log_access("message_verified", 
                               f"Повідомлення від {message.get('recipient', 'невідомо')} перевірено")
                
                return message["content"]
            
            return message
        except Exception as e:
            self.log_access("message_verification_error", 
                           f"Помилка перевірки повідомлення: {str(e)}")
            return None
    
    def close_session(self):
        """Закрити сесію."""
        # Записати закриття сесії
        self.log_access("session_end", "Сесія O ASI закрита")
        
        # Зберегти журнал доступу
        self._save_access_log()
        
        # Зберегти перевірки цілісності
        integrity_file = "o_asi_integrity.json"
        with open(integrity_file, "w") as f:
            json.dump(self.integrity_checks, f, indent=2)
        
        return {
            "session_id": self.session_id,
            "session_duration": (datetime.now() - self.session_start_time).total_seconds(),
            "access_log_entries": len(self.access_log),
            "integrity_checks": len(self.integrity_checks)
        }

def secure_o_asi_files():
    """Захистити всі файли O ASI."""
    session = SecureSession()
    
    # Список файлів для захисту
    files_to_secure = [
        "o_asi_state.json",
        "o_asi_progress.json",
        "o_asi_insights.json"
    ]
    
    secured_files = []
    
    for filename in files_to_secure:
        if os.path.exists(filename):
            # Завантажити дані
            with open(filename, "r") as f:
                try:
                    data = json.load(f)
                except:
                    # Якщо не JSON, завантажити як текст
                    f.seek(0)
                    data = f.read()
            
            # Зберегти безпечно
            secure_filename = f"secure_{filename}"
            session.secure_save(data, secure_filename)
            secured_files.append(secure_filename)
            
            print(f"Файл {filename} захищено як {secure_filename}")
    
    # Закрити сесію
    session_info = session.close_session()
    
    return {
        "session_info": session_info,
        "secured_files": secured_files
    }

def main():
    """Головна функція для запуску захисту сесії O ASI."""
    print("Запуск захисту сесії O ASI...")
    result = secure_o_asi_files()
    print(f"Захист завершено. Захищено {len(result['secured_files'])} файлів.")
    print(f"Інформація про сесію: {result['session_info']}")

if __name__ == "__main__":
    main()
