import shutil
import subprocess
import threading


class AudioPlayer:
    def __init__(self, logger, file_path):
        self.logger = logger
        self.file_path = file_path
        self._player = None
        self._thread = None
        self._stop_event = threading.Event()
        self._use_winsound = self._winsound_available()
        self._winsound_playing = False

    @staticmethod
    def _winsound_available():
        try:
            import winsound  # noqa: F401

            return True
        except ImportError:
            return False

    def play(self):
        if self._thread is not None:
            return
        # self.played = True
        # if self.played:
        #     return
        self._stop_event.clear()
        try:
            if self._use_winsound:
                import winsound

                if not self._winsound_playing:
                    winsound.PlaySound(
                        self.file_path,
                        winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP,
                    )
                    self._winsound_playing = True
            else:
                self._thread = threading.Thread(
                    target=self._play_loop,
                    args=(self.file_path,),
                    daemon=True,
                    name='audio',
                )
                self._thread.start()
        except Exception as e:
            self.logger.error(f'AudioPlayer: failed to start playback: {e}')

    def stop(self):
        try:
            # self.played = False
            if self._use_winsound:
                import winsound

                winsound.PlaySound(None, winsound.SND_PURGE)
                self._winsound_playing = False
            elif self._thread is not None:
                self._stop_event.set()
                self._thread = None
        except Exception as e:
            self.logger.error(f'AudioPlayer: failed to stop playback: {e}')

    def _init_player(self):
        if self._player is not None:
            return
        self._winsound_playing = False
        for player in ('paplay', 'aplay', 'ffplay'):
            if shutil.which(player):
                self._player = player
                break
        if self._player is None:
            self.logger.error(
                'AudioPlayer: no audio player (paplay/aplay/ffplay) found'
            )

    def _play_loop(self, file_path):
        try:
            self._init_player()
            if self._player is None:
                return
            args = [self._player, file_path]
            while not self._stop_event.is_set():
                self._stop_event.clear()
                try:
                    subprocess.run(args, check=True)
                except subprocess.CalledProcessError as e:
                    self.logger.error(f'AudioPlayer: player error: {e}')
                    return
        finally:
            self._thread = None


# import logging

# a = AudioPlayer(logging.getLogger(), 'C:\Users\pav\granary-main\app\res\alarm.wav')
# a.play()
