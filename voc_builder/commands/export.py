"""Handle export command"""
import csv
import sys
from enum import Enum
from typing import Optional, TextIO

from rich.console import Console
from rich.table import Table

from voc_builder.store import get_word_store
from voc_builder.utils import highlight_words

console = Console()


class FormatType(Enum):
    ASCII = 'ascii'
    CSV = 'csv'


def handle_export(format: str, file_path: Optional[str]):
    """Handle the export command

    :param format: The output format, e.g. "ascii", "csv".
    :param file_path: The file path where the output will be written, if not specified,
        use stdout
    """
    if format == FormatType.ASCII.value:
        table = Table(title='', show_header=True)
        table.add_column("单词")
        table.add_column("发音")
        table.add_column("释义", overflow='fold', max_width=24)
        table.add_column("例句 / 翻译", overflow='fold')
        table.add_column("添加时间")
        for w in get_word_store().all():
            table.add_row(
                w.word,
                w.ws.pronunciation,
                w.ws.word_meaning,
                highlight_words(w.ws.orig_text, [w.word]) + '\n' + w.ws.translated_text,
                w.date_added,
            )

        if file_path:
            with open(file_path, 'w', encoding='utf-8') as fp:
                Console(file=fp).print(table)
                console.print(f'Exported to "{file_path}" successfully, format: ascii.')
        else:
            console.print(table)
        return
    elif format == FormatType.CSV.value:
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as fp:
                VocCSVWriter().write_to(fp)
                console.print(f'Exported to "{file_path}" successfully, format: csv.')
        else:
            VocCSVWriter().write_to(sys.stdout)
        return


class VocCSVWriter:
    """Write vocabulary book into CSV file

    :param fp: The file object
    """

    header_row = ('单词', '读音', '释义', '例句/翻译', '添加时间')

    def write_to(self, fp: TextIO):
        """Write to the given file object"""
        self._get_writer(fp).writerow(self.header_row)
        for w in get_word_store().all():
            self._get_writer(fp).writerow(
                (
                    w.word,
                    w.ws.pronunciation,
                    w.ws.word_meaning,
                    '{} / {}'.format(w.ws.orig_text, w.ws.translated_text),
                    w.date_added,
                )
            )

    def _get_writer(self, fp: TextIO):
        """Get the CSV writer obj"""
        return csv.writer(fp, delimiter=",", quoting=csv.QUOTE_MINIMAL)
