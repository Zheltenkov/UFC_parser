from utils.scripts import save_data
from src.event_parser import EventsParser
from src.fighter_parser import FighterParser


if __name__ == '__main__':
    # Initialization of classes
    fp, ev = FighterParser(), EventsParser()
    print('-----STARTING PARSING DATA-----')

    # Running the fighter parser
    fighters_data = fp.get_fighter_data()
    save_data('fighter.xlsx', fighters_data)
    print('---FIGHTERS DATASET PREPARED AND SAVED---')

    # Running the event parser
    events_data = ev.get_all_event_data()
    save_data('events.xlsx', events_data)
    print('---FIGHTERS EVENTS DATASET PREPARED AND SAVED---')







