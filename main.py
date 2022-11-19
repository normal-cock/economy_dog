import argparse
from biz import download_data, download_init_area_data
from ui import annual_report_email_v2
from ui.daily_report import daily_report_by_email

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=[
                        'annual_report', 'down_init_areas', 'daily_report'])
    args = parser.parse_args()
    if args.command == 'annual_report':
        # annual_report_email()
        annual_report_email_v2()
    if args.command == 'daily_report':
        daily_report_by_email()
    if args.command == 'down_init_areas':
        download_init_area_data()
