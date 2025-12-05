import importlib
import logging
import os
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from types import ModuleType
from typing import TypeVar

from fastapi import APIRouter

log = logging.getLogger("uvicorn")

T = TypeVar("T")


def load_files(name_model: str) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(obj: T, *args, **kwargs) -> T:
            log.info(f"Start load {name_model}")
            base_path = Path(__file__).parent
            for folder in os.listdir(base_path):
                package_path = base_path / folder
                file_path = package_path / f"{name_model}.py"
                if package_path.is_dir() and file_path.exists():
                    module_path = f"src.{folder}.{name_model}"
                    try:
                        module = importlib.import_module(module_path)
                        func(obj, module, *args, **kwargs)
                        log.info(f"{name_model} {file_path} loaded")
                    except Exception as e:
                        log.exception(f"Failed to import {module_path}: {e}")
            return obj

        return wrapper

    return decorator


@load_files("router")
def load_routers(router: APIRouter, module: ModuleType):
    router.include_router(module.router)
    return 

load_files("models")
def load_models():
    pass