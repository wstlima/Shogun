"""COM Thread Pool — STA-threaded executor for Office COM automation.

pywin32 COM requires Single-Threaded Apartment (STA) mode. FastAPI
runs on asyncio which defaults to Multi-Threaded Apartment (MTA).
This module provides a dedicated STA thread pool and per-application
async locks to safely bridge the two worlds.

Usage:
    from shogun.office.com_thread_pool import run_com, office_lock

    async with office_lock("excel"):
        result = await run_com(some_com_function, arg1, arg2)
"""

from __future__ import annotations

import asyncio
import functools
import logging
import platform
import threading
from concurrent.futures import ThreadPoolExecutor
from contextlib import asynccontextmanager
from typing import Any, Callable, TypeVar

log = logging.getLogger("shogun.office.com_thread_pool")

T = TypeVar("T")

# ── STA Thread Pool ──────────────────────────────────────────────────

_pool: ThreadPoolExecutor | None = None
_pool_lock = threading.Lock()


def _sta_thread_initializer() -> None:
    """Initialize COM in STA mode on each thread in the pool."""
    if platform.system() != "Windows":
        return
    try:
        import pythoncom
        pythoncom.CoInitialize()
        log.debug("COM STA initialized on thread %s", threading.current_thread().name)
    except ImportError:
        log.warning("pythoncom not available — COM calls will fail")
    except Exception as exc:
        log.warning("COM initialization failed: %s", exc)


def _get_pool() -> ThreadPoolExecutor:
    """Get or create the STA thread pool (lazy singleton)."""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ThreadPoolExecutor(
                    max_workers=2,
                    thread_name_prefix="shogun-office-com",
                    initializer=_sta_thread_initializer,
                )
                log.info("Office COM STA thread pool created (max_workers=2)")
    return _pool


async def run_com(func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
    """Run a synchronous COM function on the STA thread pool.

    This is the primary bridge between FastAPI's async world and
    pywin32's STA-threaded COM world.

    Args:
        func: A synchronous function that makes COM calls.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The return value of the function.
    """
    loop = asyncio.get_running_loop()
    pool = _get_pool()

    if kwargs:
        wrapped = functools.partial(func, *args, **kwargs)
        return await loop.run_in_executor(pool, wrapped)
    else:
        return await loop.run_in_executor(pool, func, *args)


# ── Per-Application Async Locks ──────────────────────────────────────
# One global mutex per Office application prevents concurrent COM
# access to the same Office instance.

_app_locks: dict[str, asyncio.Lock] = {}
_app_locks_init_lock = threading.Lock()


def _get_app_lock(app_name: str) -> asyncio.Lock:
    """Get or create the async lock for an Office application."""
    if app_name not in _app_locks:
        with _app_locks_init_lock:
            if app_name not in _app_locks:
                _app_locks[app_name] = asyncio.Lock()
    return _app_locks[app_name]


@asynccontextmanager
async def office_lock(app_name: str):
    """Async context manager that acquires the per-app mutex.

    Usage:
        async with office_lock("excel"):
            result = await run_com(excel_operation, workbook_path)

    This ensures only one Office operation runs per application at a time.
    """
    lock = _get_app_lock(app_name)
    log.debug("Acquiring office lock for '%s'...", app_name)
    async with lock:
        log.debug("Office lock acquired for '%s'", app_name)
        yield
    log.debug("Office lock released for '%s'", app_name)


# ── Shutdown ─────────────────────────────────────────────────────────


def shutdown_pool() -> None:
    """Shut down the COM thread pool. Called during Shogun shutdown."""
    global _pool
    if _pool is not None:
        log.info("Shutting down Office COM thread pool...")
        _pool.shutdown(wait=True, cancel_futures=False)
        _pool = None
        log.info("Office COM thread pool shut down")
