import argparse
from biz import download_data, download_init_area_data
from ui import annual_report_email

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=[
                        'gen_report', 'down_init_areas'])
    args = parser.parse_args()
    if args.command == 'gen_report':
        annual_report_email()
    if args.command == 'down_init_areas':
        download_init_area_data()
