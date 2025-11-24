#Logging module for server runtime
import logging, json, os
from pathlib import Path

class MainLog:
    """Main logging class for server runtime."""
    def __init__(self, lang="eng"):
        self.log_buffer = []
        self.log_lang = lang
        self._txt_cache = None
        self.logger = logging.getLogger("server.main")
        self.logger.setLevel(logging.DEBUG)

        # Create console handler with a higher log level
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)

        # Create formatter and add it to the handlers
        formatter = logging.Formatter('Server -- %(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)

        # Add the handlers to the logger
        self.logger.addHandler(ch)

    def log_info(self, message, **fmt_args):
        # Decrypt message if it's an integer code, and format with fmt_args
        if isinstance(message, int):
            text = self.get_log_text(message, **fmt_args)
            self.logger.info(text)
        else:
            # if caller provided formatting args, try to format the message string
            if fmt_args and isinstance(message, str):
                try:
                    message = message.format(**fmt_args)
                except Exception:
                    pass
            
            self.logger.info(message)
        self.log_buffer.append(message)
        
    def log_alert(self, message, **fmt_args):
        # Decrypt message if it's an integer code, and format with fmt_args
        if isinstance(message, int):
            text = self.get_log_text(message, **fmt_args)
            self.logger.info(text)
        else:
            # if caller provided formatting args, try to format the message string
            if fmt_args and isinstance(message, str):
                try:
                    message = message.format(**fmt_args)
                except Exception:
                    pass
            
            self.logger.info(message)
        self.log_buffer.append(message)

    def log_error(self, message, **fmt_args):
        # Decrypt message if it's an integer code, and format with fmt_args
        if isinstance(message, int):
            text = self.get_log_text(message, **fmt_args)
            self.logger.error(text)
        else:
            # if caller provided formatting args, try to format the message string
            if fmt_args and isinstance(message, str):
                try:
                    message = message.format(**fmt_args)
                except Exception:
                    pass
            
            self.logger.error(message)
            
        self.log_buffer.append(message)

    def get_log_text(self, code, **fmt_args):
        """
        Load and cache the language JSON, then resolve `code` to a message string.

        Resolution order:
        1. top-level "log_txt" mapping (legacy numeric codes)
        2. recursive search inside "messages" (new structure)
        3. recursive search across the whole JSON as a last resort

        Returns a fallback like "[log:KEY]" when no entry is found.
        Supports optional str.format keyword arguments via fmt_args.
        """
        if self._txt_cache is None:
            try:
                base = Path(__file__).resolve().parent
                json_path = base / "txtdesc" / f"{self.log_lang}.json"
                if not json_path.exists():
                    json_path = base / "txtdesc" / "eng.json"
                with json_path.open("r", encoding="utf-8") as fh:
                    self._txt_cache = json.load(fh)
            except Exception:
                self._txt_cache = {}

        key = str(code)

        # 1) legacy numeric map
        txt = self._txt_cache.get("log_txt", {}).get(key)
        if txt:
            try:
                return txt.format(**fmt_args) if fmt_args else txt
            except Exception:
                return txt

        # helper: recursive dict search for a string value stored under `key`
        def _recursive_find(obj):
            if isinstance(obj, dict):
                if key in obj and isinstance(obj[key], str):
                    return obj[key]
                for v in obj.values():
                    result = _recursive_find(v)
                    if result:
                        return result
            return None

        # 2) search messages section
        txt = _recursive_find(self._txt_cache.get("messages", {}))
        # 3) last resort: search entire cached JSON
        if not txt:
            txt = _recursive_find(self._txt_cache)

        if not txt:
            txt = f"[log:{key}]"

        try:
            return txt.format(**fmt_args) if fmt_args else txt
        except Exception:
            return txt