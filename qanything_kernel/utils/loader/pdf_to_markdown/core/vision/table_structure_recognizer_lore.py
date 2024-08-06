import re
from qanything_kernel.utils.loader.pdf_to_markdown.core.layout import TableRecognizer
from qanything_kernel.utils.custom_log import insert_logger
import numpy as np
import cv2
import traceback


class TableStructureRecognizer_LORE():
    def __init__(self, device='cpu'):
        self.table_rec = TableRecognizer(device=device)

    @staticmethod
    def is_caption(bx):
        patt = [
            r"[图表]+[ 0-9:：]{2,}"
        ]
        if any([re.match(p, bx["text"].strip()) for p in patt]) \
                or bx["layout_type"].find("caption") >= 0:
            return True
        return False

    def construct_table(self, boxes, image, table_box, height, is_english=False, html=False):
        """
        接收一个表格的ocr结果，同时接收一个表格的图片，最终需要返回该表格的html结果
        """
        ocr_result = []
        table_caption = ''
        zoomin = 3
        t_x1, t_x2, t_y1, t_y2 = table_box
        table_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        for item in boxes:
            if item['layout_type'] == 'caption':
                table_caption += item['text']
            else:
                new_item = []
                x0, y0, x1, y1 = item['x0'], item['top'], item['x1'], item['bottom']
                new_item.append([[zoomin * (x0 - t_x1), zoomin * (y0 - t_y1 - height)],
                                 [zoomin * (x1 - t_x1), zoomin * (y0 - t_y1 - height)],
                                 [zoomin * (x1 - t_x1), zoomin * (y1 - t_y1 - height)],
                                 [zoomin * (x0 - t_x1), zoomin * (y1 - t_y1 - height)]])
                new_item.append(item['text'])
                new_item.append(1.0)
                ocr_result.append(new_item)
        try:
            table_html, table_markdown = self.table_rec.extract_table(table_image, ocr_result)
        except Exception as e:
            insert_logger.warning(f"construct_table error: {traceback.format_exc()}")
            ocr_str = '\n'.join([item[1] for item in ocr_result])
            insert_logger.warning(f"ocr_str: {ocr_str[:100]}")
            table_html, table_markdown = ocr_str, ocr_str
        return {
            'table_html': table_html,
            'table_caption': table_caption,
            'table_markdown': table_markdown
        }
