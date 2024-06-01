import io
import calendar
from datetime import datetime, date
from argparse import ArgumentParser
from deutschland import feiertage
from deutschland.feiertage.api import default_api


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-y", "--year", type=str, help="Year generate worktime for", default=str(datetime.today().year))
    parser.add_argument("-l", "--land", type=str, help="State to get the holidays for", default="BE")
    parser.add_argument("-m", "--month", type=int, help="Month to generate worktime for", default=datetime.today().month)
    parser.add_argument("-v", "--vacation", type=int, help="Vacation day", nargs="*", action="extend", default=[])
    parser.add_argument("-w", "--half-vacation", type=int, help="Half vacation day", nargs="*", action="extend", default=[])
    parser.add_argument("-e", "--elternzeit", action="store_true")
    args = parser.parse_args()

    vacation_days = []
    for vd in args.vacation:
        vacation_days.append(date(int(args.year), args.month, vd))
    half_vacation_days = []
    for vd in args.half_vacation:
        half_vacation_days.append(date(int(args.year), args.month, vd))

    output = io.StringIO()

    configuration = feiertage.Configuration(host = "https://feiertage-api.de/api/")
    with feiertage.ApiClient(configuration) as api_client:
        api_instance = default_api.DefaultApi(api_client)
        api_response = {
            date.fromisoformat(value['datum']): key
            for key, value
            in api_instance.get_feiertage(args.year, nur_land=args.land).items()
        }
        print(calendar.month(int(args.year), args.month), sep="\n", end="\n", file=output)
        elternzeit = args.elternzeit
        for day in range(calendar.monthrange(int(args.year), args.month)[1]):
            d = date(int(args.year), args.month, day + 1)
            if d.weekday() > 4:
                continue
            else:
                weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
                weekday = weekdays[d.weekday()]
            print(weekday.rjust(max((len(s) for s in weekdays))), ", ", d.strftime("%d.%m.%Y"), ":", "\t", sep="", end="", file=output)
            if d in api_response.keys():
                print(api_response[d], "(Feiertag)", file=output)
            elif d in vacation_days:
                print("Urlaub", file=output)
            elif elternzeit:
                if d in half_vacation_days:
                    print("Arbeit: 13:00 Uhr bis 14:30 Uhr", file=output)
                elif d.weekday() == 0:
                    print("Arbeit: 10:00-11:00 Uhr, 13:00-14:00 Uhr und 15:00-16:00", file=output)
                elif d.weekday() == 1:
                    print("Arbeit: 10:00-12:00 Uhr, 16:00-17:00", file=output)
                elif d.weekday() == 2:
                    print("Arbeit: 10:00-12:00 Uhr, 14:00-15:00", file=output)
                elif d.weekday() == 3:
                    print("Arbeit: 10:00-12:00 Uhr, 14:00-15:00", file=output)
                elif d.weekday() == 4:
                    print("Arbeit: 10:00-12:00 Uhr, 14:00-15:00", file=output)
            else:
                if d in half_vacation_days:
                    print("Arbeit: 13:00 Uhr bis 17:00 Uhr", file=output)
                elif d.weekday() == 4: # I work 39 hours as per contract, so take the hour off here
                    print("Arbeit: 9:00 Uhr bis 12:00 Uhr, Pause: 12:00 bis 12:30 Uhr, Arbeit: 12:30 bis 16:30 Uhr", file=output)
                else:
                    print("Arbeit: 9:00 Uhr bis 12:00 Uhr, Pause: 12:00 bis 12:30 Uhr, Arbeit: 12:30 bis 17:30 Uhr", file=output)

    print(output.getvalue())
