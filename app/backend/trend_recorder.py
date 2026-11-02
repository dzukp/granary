import sqlite3
import threading
import queue
from datetime import datetime
from time import time

from engine import Engine
from pylogic.supervisor_manager import BaseSupervisor
import settings


class TrendChannel:
    """Один канал, который пишем в тренды. Логика deadband на один канал.

    Помимо deadband есть ещё максимальное время между записями (max_interval):
    если оно истекло, значение принудительно пишется в БД даже если не менялось.
    Это даёт «сердцебиение» канала — по графикам видно, что канал жив.
    """

    def __init__(self, channel, deadband=0.0, max_interval=600.0, name=None):
        self.channel = channel
        self.name = name if name is not None else channel.name
        self.deadband = deadband
        # Максимальное время между записями (в секундах), по умолчанию 10 минут.
        self.max_interval = max_interval
        self.last_value = None
        # Время (unix, секунды с миллисекундами) последней записи значения канала.
        self.last_saved_at = None

    def should_record(self, value, now):
        # Первая запись — всегда пишем.
        if self.last_value is None:
            return True
        # Истёк максимальный интервал — принудительно пишем, даже без изменения.
        if now - self.last_saved_at >= self.max_interval:
            return True
        # Иначе пишем только при изменении больше deadband.
        return abs(value - self.last_value) > self.deadband


class TrendRecorder(BaseSupervisor):
    """Супервизор: пишет изменения каналов в БД в отдельном потоке-писателе.

    receive_data() вызывается каждый такт из главного потока: сэмплирует каналы
    с deadband'ом и кладёт накопленное в очередь. Отдельный поток-писатель
    забирает данные из очереди, раз в ~секунду делает вставку (executemany),
    и в нём же периодически выполняется очистка старых записей. Благодаря этому
    запись и очистка не блокируют основной цикл управления.
    """

    def __init__(self, name='supervis_trend'):
        super().__init__(name)
        self.db_path = None
        self.init_sql_path = settings.DB_INIT
        self.flush_interval = settings.TREND_FLUSH_INTERVAL
        self.channels = {}
        self.pending = []
        self.queue = queue.Queue()
        self.last_flush = time()
        self.conn = None
        # Очистка старых записей: раз в неделю удалять записи старше 60 дней.
        self.cleanup_interval = settings.TREND_CLEANUP_INTERVAL
        self.cleanup_retention = settings.TREND_CLEANUP_RETENTION
        self.last_cleanup = None
        self._writer_thread = None
        self._stop = threading.Event()

    def set_db_path(self, db_path):
        self.db_path = db_path

    def set_flush_interval(self, interval):
        self.flush_interval = interval

    def set_cleanup_interval(self, interval):
        self.cleanup_interval = interval

    def set_cleanup_retention(self, retention):
        self.cleanup_retention = retention

    def init(self):
        if self.db_path is None:
            self.db_path = settings.DB_PATH
        for obj in self.top_object.get_all_objects():
            if isinstance(obj, Engine) and obj.ai_current and obj.ai_current.name:
                self.add_channel(
                    obj.ai_current, deadband=0.5, name=f'{obj.name}_current'
                )
        self.logger.info(f'Trend recorder: {len(self.channels)} channels to log')
        self._writer_thread = threading.Thread(
            target=self._writer_loop, name='trend_writer', daemon=True
        )
        self._writer_thread.start()

    def add_channel(self, channel, deadband=0.0, max_interval=600.0, name=None):
        self.channels[name if name is not None else channel.name] = TrendChannel(
            channel, deadband=deadband, max_interval=max_interval, name=name
        )

    def _connect(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            # Схема БД (таблица trends, индекс) задаётся в res/init.sql.
            with open(self.init_sql_path, 'r', encoding='utf-8') as f:
                self.conn.executescript(f.read())
            self.conn.commit()

    def _writer_loop(self):
        """Поток-писатель: берёт батчи из очереди, пишет в БД, периодически чистит."""
        while not self._stop.is_set():
            try:
                batch = self.queue.get(timeout=1.0)
            except queue.Empty:
                # Очередь пуста — всё равно проверяем, не пора ли чистить.
                self._maybe_cleanup()
                continue
            try:
                self._connect()
                self._insert_batch(batch)
            except Exception:
                self.logger.exception('Failed to write trends')
            finally:
                self.queue.task_done()
            self._maybe_cleanup()
        # Выход из потока — закрываем соединение здесь же (оно создано в этом потоке).
        try:
            if self.conn is not None:
                self.conn.close()
                self.conn = None
        except Exception:
            self.logger.exception('Failed to close trends db')

    def _insert_batch(self, batch):
        rows = []
        for tstamp, name, value in batch:
            # Время берём из batch (момент сэмплирования), ISO-формат
            # без часового пояса, с миллисекундами.
            dtime = datetime.fromtimestamp(tstamp).isoformat(timespec='milliseconds')
            rows.append((dtime, tstamp, name, value))
        self.conn.executemany(
            """
            INSERT INTO trends (dtime, tstamp, channel_name, value)
            VALUES (?, ?, ?, ?)
            """,
            rows,
        )
        self.conn.commit()

    def _maybe_cleanup(self):
        # Без соединения чистить нечего (соединение создаётся в потоке-писателе
        # при первой записи).
        if self.conn is None:
            return
        now = time()
        if (
            self.last_cleanup is not None
            and now - self.last_cleanup < self.cleanup_interval
        ):
            return
        self._cleanup(now)

    def _cleanup(self, now):
        """Удаляет записи старше retention. Первый раз — при запуске,
        далее не чаще раза в cleanup_interval (раз в неделю)."""
        try:
            cutoff = now - self.cleanup_retention
            cursor = self.conn.execute('DELETE FROM trends WHERE tstamp < ?', (cutoff,))
            self.conn.commit()
            self.logger.info(
                f'Trend cleanup: deleted {cursor.rowcount} rows older than '
                f'{self.cleanup_retention // 86400} days'
            )
        except Exception:
            self.logger.exception('Failed to cleanup trends')
        finally:
            self.last_cleanup = now

    def receive_data(self):
        # Момент сэмплирования фиксируем один раз за такт — это актуальное время
        # значения. Оно одинаково для всех каналов, записанных в этом такте.
        now = time()
        for ch in self.channels.values():
            value = ch.channel.val
            if ch.should_record(value, now):
                ch.last_value = value
                ch.last_saved_at = now
                # Время хранится вместе со значением в pending, чтобы при flush
                # не терять актуальный момент сэмплирования.
                self.pending.append((now, ch.name, value))
        self._maybe_enqueue()

    def _maybe_enqueue(self):
        """Раз в flush_interval отдаём весь накопленный pending потоку-писателю."""
        now = time()
        if now - self.last_flush < self.flush_interval:
            return
        if self.pending:
            self.queue.put(self.pending)
            self.pending = []
        self.last_flush = now

    def send_data(self):
        pass

    def close(self):
        self._stop.set()
        # Поток-писатель сам закроет соединение перед выходом.
        if self._writer_thread is not None:
            self._writer_thread.join(timeout=5.0)
