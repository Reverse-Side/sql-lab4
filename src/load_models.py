import importlib
import logging
import os
from pathlib import Path

# Логування тут допомагає бачити, що саме завантажується
log = logging.getLogger("uvicorn")


def load_all_orm_models():
    """
    Забезпечує, що всі моделі ORM реєструються в Base.metadata.
    Викликається в src/main.py, щоб розірвати цикл імпорту.
    """
    log.info("Starting load all ORM models for SQLAlchemy metadata registration")
    
    # Визначаємо кореневу папку 'src'
    # Path(__file__).parent - це src/
    base_path = Path(__file__).parent 
    
    # Ітеруємо по папках всередині 'src' (auth, events, payments, tickets, ...)
    for folder in os.listdir(base_path):
        package_path = base_path / folder
        file_path = package_path / "models.py"
        
        # Перевіряємо, чи існує папка і чи містить вона models.py
        if package_path.is_dir() and file_path.exists():
            # Наприклад, створюємо шлях "src.auth.models"
            module_path = f"src.{folder}.models"
            try:
                # Просто імпортуємо, щоб виконати код модуля (реєстрацію ORM)
                importlib.import_module(module_path)
                log.info(f"Model module {module_path} loaded.")
            except Exception as e:
                # Якщо тут помилка, то вона не циклічна, а інша (наприклад, синтаксична)
                log.exception(f"Failed to import {module_path}: {e}")