import datetime
import time

from class_fun import StageResults
from class_fun import GoogleSheet
from class_fun import blank_insert


# Получаем результаты нужного раунда

with open('listid', 'r') as listid:
    sheet_id = [line for line in listid][0].strip()

link = 'https://ru.uefa.com/uefaeuro-2020/matches/2020/libraries/round/'  # ссылка на результаты евро

# ссылки на все этапы плей-офф

if datetime.datetime.today() < datetime.datetime.strptime('30.06.2021 01:10', '%d.%m.%Y %H:%M'):
    stage = '2001025'
    table_range = 'b5:e34'
    pen_range = 'f'
    start_range = 6
elif datetime.datetime.today() < datetime.datetime.strptime('04.07.2021 01:10', '%d.%m.%Y %H:%M'):
    stage = '2001026'
    table_range = 'g13:j26'
    pen_range = 'k'
    start_range = 14
elif datetime.datetime.today() < datetime.datetime.strptime('08.07.2021 01:10', '%d.%m.%Y %H:%M'):
    stage = '2001027'
    table_range = 'l17:o22'
    pen_range = 'p'
    start_range = 18
# elif datetime.datetime.today() < datetime.datetime.strptime('12.07.2021 01:10', '%d.%m.%Y %H:%M'):
else:
    stage = '2001028'
    table_range = 'q19:t20'
    pen_range = 'u'
    start_range = 20


# получаем результаты нужного этапа и преобразовываем их

results = StageResults(link, stage).get_result()

blank_insert(results)

# записываем в таблицу

GoogleSheet(sheet_id).set_values('Результаты!' + table_range, results[:-1])

time.sleep(1)
# пенальти отдельно
for i in range(len(results[4])):
    if results[4][i] != '':
        ran = 'Результаты!' + pen_range + str(start_range + 4 * i) + ':' + pen_range + str(start_range + 4 * i + 1)
        GoogleSheet(sheet_id).set_values(ran, [[results[4][i]]])
