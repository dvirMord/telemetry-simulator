import json
import os
import klvdata
from typing import Tuple
from typing import Any
from app.Constants.Constants import ProgramConstants
from app.Core.config import settings
from app.Interfaces.IDecoderService import IMisbDecoder 
from app.Constants.Constants import KafkaConst


class MisbDecoder(IMisbDecoder):

    def decode(self, file_name: str) -> Tuple[str, int]:
        # Generate the output file path using system settings and constants
        out_file_name = os.path.splitext(os.path.basename(file_name))[0] + ProgramConstants.ENCODED_FILE_ENDING
        out_path = os.path.join(settings.STORAGE_DECODED_PATH, out_file_name)
        drone_id = os.path.splitext(os.path.basename(file_name))[0]

        # Open both files simultaneously: read binary from source, write text to destination
        with open(file_name, ProgramConstants.READ_BIN) as f, \
             open(out_path, ProgramConstants.WRITE, encoding=ProgramConstants.BYTE_ENCODEING) as out:
            
            # Pass the file object 'f' directly to StreamParser instead of reading it all into memory
            for packet in klvdata.StreamParser(f):
                packet_dict = self.to_dict(packet)
                
                # Write to the JSONL file only if the packet was successfully parsed and is not empty
                if packet_dict:
                    # json.dumps converting the dict into json in the outputed file 
                    out.write(json.dumps(packet_dict, ensure_ascii=False) + "\n")

        return out_path, os.path.getsize()

    def to_dict(self, packet) -> dict:
        items = getattr(packet, "items", None)
        if not isinstance(items, dict):
            return {}

        #---------------returing dict of: (tag: value, tag: value.....)
        return dict(self._parse_item(tag, item) for tag, item in items.items())

    def _parse_item(self, tag: Any, item: Any) -> tuple[str, str]:
        """Parses a single KLV item into a safe (name, value) pair."""
        key = str(getattr(item, "name", tag))
        try:
            val = getattr(item, "value", item)
            val_str = val.hex() if isinstance(val, bytes) else str(val)
        except Exception as e:
            val_str = f"<Unparseable: {e}>"

        return key, val_str