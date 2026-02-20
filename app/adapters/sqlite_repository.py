from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import Iterable

import aiosqlite

from app.interfaces.print_job_repository import PrintJobRepository
from app.interfaces.queue_repository import QueueRepository
from app.models import PrintJobRecord, PrintJobStatus, PrintRequest, QueueItem


class SqliteRepository(PrintJobRepository, QueueRepository):
    """Repositorio SQLite para trabajos de impresion y cola de impresion."""

    def __init__(self, db_path: str):
        self._db_path = db_path

    async def initialize(self) -> None:
        """Crea tablas e indices si no existen."""
        async with self._connection() as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS print_jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id TEXT,
                    client_code TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    print_type TEXT NOT NULL,
                    status TEXT NOT NULL,
                    print_count INTEGER NOT NULL,
                    host INTEGER,
                    date_created TEXT NOT NULL,
                    date_started TEXT,
                    date_processed TEXT,
                    payload TEXT NOT NULL
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_print_jobs_status_created
                ON print_jobs(status, date_created)
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS queue_items (
                    id INTEGER PRIMARY KEY,
                    client_id TEXT NOT NULL,
                    client_code TEXT NOT NULL,
                    client_name TEXT NOT NULL,
                    order_number INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    type_code TEXT,
                    channel INTEGER NOT NULL,
                    invoice_type TEXT,
                    invoice_number TEXT,
                    invoice_comment TEXT NOT NULL,
                    invoice_total REAL,
                    result INTEGER NOT NULL,
                    result_detail TEXT NOT NULL,
                    retry INTEGER NOT NULL DEFAULT 0,
                    priority INTEGER NOT NULL DEFAULT 0,
                    printed INTEGER NOT NULL DEFAULT 0,
                    print_count INTEGER NOT NULL DEFAULT 0,
                    host INTEGER NOT NULL,
                    redi_code TEXT NOT NULL,
                    redi_id INTEGER NOT NULL,
                    date_created TEXT NOT NULL,
                    date_started TEXT,
                    date_processed TEXT,
                    extra_data TEXT,
                    processing INTEGER NOT NULL DEFAULT 0
                )
                """
            )
            await db.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_queue_items_processing_host
                ON queue_items(processing, host)
                """
            )
            await db.commit()

    async def enqueue_job(
        self,
        request: PrintRequest,
        status: PrintJobStatus,
        created_at: str,
        print_count: int,
        payload: str,
    ) -> PrintJobRecord:
        """Encola un trabajo de impresion."""
        async with self._connection() as db:
            cursor = await db.execute(
                """
                INSERT INTO print_jobs (
                    client_id,
                    client_code,
                    client_name,
                    print_type,
                    status,
                    print_count,
                    host,
                    date_created,
                    date_started,
                    date_processed,
                    payload
                ) VALUES (
                    :client_id,
                    :client_code,
                    :client_name,
                    :print_type,
                    :status,
                    :print_count,
                    :host,
                    :date_created,
                    :date_started,
                    :date_processed,
                    :payload
                )
                """,
                {
                    "client_id": None,
                    "client_code": request.client_code,
                    "client_name": request.client_name,
                    "print_type": request.type,
                    "location": request.location,
                    "status": status.value,
                    "print_count": print_count,
                    "host": request.set_host,
                    "date_created": created_at,
                    "date_started": None,
                    "date_processed": None,
                    "payload": payload,
                },
            )
            await db.commit()
            job_id = cursor.lastrowid

        return PrintJobRecord(
            id=int(job_id),
            status=status,
            date_created=created_at,
            date_processed=None,
        )

    async def enqueue_items(self, items: Iterable[QueueItem]) -> None:
        """Agrega items a la cola local, ignorando duplicados por id."""
        async with self._connection() as db:
            await db.executemany(
                """
                INSERT OR IGNORE INTO queue_items (
                    id, client_id, client_code, client_name, order_number,
                    type, type_code, channel, invoice_type, invoice_number,
                    invoice_comment, invoice_total, result, result_detail,
                    retry, priority, printed, print_count, host, redi_code,
                    redi_id, date_created, date_started, date_processed,
                    extra_data, processing
                ) VALUES (
                    :id, :client_id, :client_code, :client_name, :order_number,
                    :type, :type_code, :channel, :invoice_type, :invoice_number,
                    :invoice_comment, :invoice_total, :result, :result_detail,
                    :retry, :priority, :printed, :print_count, :host, :redi_code,
                    :redi_id, :date_created, :date_started, :date_processed,
                    :extra_data, 0
                )
                """,
                [
                    {
                        "id": item.id,
                        "client_id": item.client_id,
                        "client_code": item.client_code,
                        "client_name": item.client_name,
                        "order_number": item.order_number,
                        "type": item.type,
                        "type_code": str(item.type_code) if item.type_code is not None else None,
                        "channel": item.channel,
                        "invoice_type": item.invoice_type,
                        "invoice_number": str(item.invoice_number) if item.invoice_number is not None else None,
                        "invoice_comment": item.invoice_comment,
                        "invoice_total": item.invoice_total,
                        "result": item.result,
                        "result_detail": item.result_detail,
                        "retry": item.retry,
                        "priority": item.priority,
                        "printed": item.printed,
                        "print_count": item.print_count,
                        "host": item.host,
                        "redi_code": item.redi_code,
                        "redi_id": item.redi_id,
                        "date_created": item.date_created,
                        "date_started": item.date_started,
                        "date_processed": item.date_processed,
                        "extra_data": item.extra_data,
                    }
                    for item in items
                ],
            )
            await db.commit()

    async def dequeue_next(self, limit: int, host: int) -> list[QueueItem]:
        """Obtiene y marca como en proceso los siguientes items pendientes."""
        async with self._connection() as db:
            cursor = await db.execute(
                """
                UPDATE queue_items
                SET processing = 1
                WHERE id IN (
                    SELECT id FROM queue_items
                    WHERE processing = 0 AND host = :host
                    ORDER BY priority DESC, date_created ASC
                    LIMIT :limit
                )
                RETURNING *
                """,
                {"host": host, "limit": limit},
            )
            rows = await cursor.fetchall()
            await db.commit()

        return [
            QueueItem(
                id=row["id"],
                client_id=row["client_id"],
                client_code=row["client_code"],
                client_name=row["client_name"],
                order_number=row["order_number"],
                type=row["type"],
                type_code=row["type_code"],
                channel=row["channel"],
                invoice_type=row["invoice_type"],
                invoice_number=row["invoice_number"],
                invoice_comment=row["invoice_comment"],
                invoice_total=row["invoice_total"],
                result=row["result"],
                result_detail=row["result_detail"],
                retry=row["retry"],
                priority=row["priority"],
                printed=row["printed"],
                print_count=row["print_count"],
                host=row["host"],
                redi_code=row["redi_code"],
                redi_id=row["redi_id"],
                date_created=row["date_created"],
                date_started=row["date_started"],
                date_processed=row["date_processed"],
                extra_data=row["extra_data"],
            )
            for row in rows
        ]

    @asynccontextmanager
    async def _connection(self) -> aiosqlite.Connection:
        if self._db_path != ":memory:":
            db_path = Path(self._db_path)
            if db_path.parent.as_posix() not in (".", ""):
                db_path.parent.mkdir(parents=True, exist_ok=True)

        db = await aiosqlite.connect(self._db_path)
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys = ON")
        try:
            yield db
        finally:
            await db.close()

