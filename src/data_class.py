from dataclasses import dataclass, field


@dataclass
class Links:

    page_events: str = 'http://ufcstats.com/statistics/events/completed?page=all'

    headers: dict = field(default_factory=lambda: {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,' +
                                                             'image/avif,image/webp,image/apng,*/*;q=0.8,application/' +
                                                             'signed-exchange;v=b3;q=0.9',
                                                   'Accept-Encoding': 'gzip, deflate',
                                                   'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                                                   'Cache-Control': 'max-age=0',
                                                   'Connection': 'keep-alive',
                                                   'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 ' +
                                                                 'Build/MRA58N) AppleWebKit/537.36 (KHTML, like ' +
                                                                 'Gecko) Chrome/107.0.0.0 Mobile Safari/537.36'
                                                   })

    num_rounds: int = 5

    cls: str = 'b-fight-details__table-text'
    cls_flag: str = 'b-flag__text'
    cls_text: str = 'b-fight-details__text-item'
    cls_fg_dt: str = 'b-fight-details__person'
    cls_style: str = 'b-link b-link_style_black'
    cls_charts: str = 'b-fight-details__charts-row'
    cls_person: str = 'b-link b-fight-details__person-link'
    cls_statistics: str = 'b-statistics__table-content'
    cls_fight_details: str = 'b-fight-details__person-title'
    cls_box_list_item: str = 'b-list__box-list-item b-list__box-list-item_type_block'
    cls_fight_details_tb: str = 'b-fight-details__table-row b-fight-details__table-row__hover js-fight-details-click'

