"""Превратить строку даты в посте в формат Datetime."""
import datetime as dt

MONTH = {'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6, 'июля': 7,
         'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12}


def rewrite_format(date: str, year_given=False, has_month=True):
    """
    Преобразовывает ущербный битриксовский формат в адекватный datetime и возвращает.
    :param date: формат даты, в котором пишут только гении с битрикса.
    :param year_given: дан ли в шедевродате год изначально.
    :param has_month: дан ли в шедевродате хотя бы месяц, или это 'вчера'.
    :return: ту же дату в виде, удобном для восприятия здорового человека, то есть в Date.
    """
    if not has_month:
        today = dt.date.today()
        if today.day == 1:
            if today.month in {5, 7, 10, 12}:
                res = dt.date(year=today.year, month=today.month - 1, day=30)
            elif today.month == 3:
                day = 29 if (today.year % 4 == 0 and
                             today.year % 100 != 0) or today.year % 400 == 0 else 28
                res = dt.date(year=today.year, month=2, day=day)
            elif today.month == 1:
                res = dt.date(year=today.year - 1, month=12, day=31)
            else:
                res = dt.date(year=today.year, month=today.month - 1, day=31)
        else:
            res = dt.date(year=today.year, month=today.month, day=today.day - 1)
    elif year_given:
        date = date.split()
        res = dt.date(year=int(date[2]), month=MONTH[date[1]], day=int(date[0]))
    else:
        date = date.split()
        year = dt.datetime.today().year
        res = dt.date(year=year, month=MONTH[date[1]], day=int(date[0]))

    return res


if __name__ == '__main__':
    print(rewrite_format('19 сентября 2023 18:06', year_given=True))
    print(rewrite_format('13 февраля 16:01'))
    print(rewrite_format('Вчера, 15:18', has_month=False))
