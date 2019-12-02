# coding:utf-8

from datetime import date

FEE = 210.55
all_day = 0.0

START_DATE = [2019, 8, 29]
END_DATE = [2019, 10, 28]

EMMA = START_DATE
SOPHIE = START_DATE
CAROL = [2019, 10, 19]
SHANGE = [2019, 10, 17]
ZZT = [2019, 10, 22]

zoulede_room1 = [2019, 10, 28]
zoulede_room2 = [2019, 9, 30]
zoulede_room3 = [2019, 10, 16]


def daysBetween(END, START):
    d = date(END[0], END[1], END[2]) - date(START[0], START[1], START[2])
    return d.days + 1


def money(NAME):
    return FEE * NAME / all_day


days_count = []

EMMA_DAY = daysBetween(END_DATE, EMMA)
days_count.append(EMMA_DAY)

SOPHIE_DAY = daysBetween(END_DATE, SOPHIE)
days_count.append(SOPHIE_DAY)

CAROL_DAY = daysBetween(END_DATE, CAROL)
days_count.append(CAROL_DAY)

SHANGE_DAY = daysBetween(END_DATE, SHANGE)
days_count.append(SHANGE_DAY)

ZZT_DAY = daysBetween(END_DATE, ZZT)
days_count.append(ZZT_DAY)

room1_DAY = daysBetween(zoulede_room1, START_DATE)
days_count.append(room1_DAY)

room2_DAY = daysBetween(zoulede_room2, START_DATE)
days_count.append(room2_DAY)

room3_DAY = daysBetween(zoulede_room3, START_DATE)
days_count.append(room3_DAY)

for item in days_count:
    all_day += item

print("Start from 29/8 to 28/10, totally 61 days")
pingjun = FEE * 1.0 / all_day
print("平均每天次", pingjun)

print("SOPHIE days: ", SOPHIE_DAY, format(money(SOPHIE_DAY), '.2f'))
print("EMMA days: ", EMMA_DAY, format(money(EMMA_DAY), '.2f'))
print("CAROL days: ", CAROL_DAY, format(money(CAROL_DAY), '.2f'))
print("SHANGE days: ", SHANGE_DAY, format(money(SHANGE_DAY), '.2f'))
print("ZZT days: ", ZZT_DAY, format(money(ZZT_DAY), '.2f'))
print("leave_room1 days: ", room1_DAY, format(money(room1_DAY), '.2f'))
print("leave_room2 days: ", room2_DAY, format(money(room2_DAY), '.2f'))
print("leave_room3 days: ", room3_DAY, format(money(room3_DAY), '.2f'))

print(format(money(SOPHIE_DAY)+money(EMMA_DAY)+money(CAROL_DAY)+money(SHANGE_DAY)+money(ZZT_DAY), '.2f'))