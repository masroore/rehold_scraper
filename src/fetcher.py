# Copyright 2023 Dr. Masroor Ehsan
from typing import Any, Optional

from scraper_kit.src.proxies import AbstractProxyPool
from scraper_kit.src.web.task import TaskRequest
from scraper_kit.src.web.worker import BaseWebWorker


class MultiFetcher:
    _tasks: list[TaskRequest]
    _callback_fn: Any
    _workers: BaseWebWorker
    _proxies: Optional[AbstractProxyPool]

    def __init__(
        self,
        workers: BaseWebWorker,
        proxies: Optional[AbstractProxyPool],
        concurrency: int,
    ):
        self._tasks = []
        self._workers = workers
        self._tasks = []
        self._concurrency = concurrency
        self._proxies = proxies

    def add_task(self, task: TaskRequest):
        self._tasks.append(task)

    @property
    def tasks(self) -> list[TaskRequest]:
        return self._tasks

    @tasks.setter
    def tasks(self, urls: list[TaskRequest]):
        self._tasks = urls

    def reset(self):
        self._tasks = []

    def run(self):
        self._workers.add_tasks(self._tasks)
        self._workers.run(reset_queue=True)
        self.reset()
