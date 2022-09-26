import pandas as pd
from tkinter import *
from tkinter import filedialog, messagebox
import re
from datetime import datetime
from dateutil.relativedelta import relativedelta

start_date = ''
full_sum = 0

root = Tk()

root['bg'] = '#fafafa'
root.title('Анализатор финансов')
root.geometry('500x750')
root.resizable(width=False, height=False)

def confirm():
    date = e.get()
    if re.match(r'\d{4}-\d{2}-\d{2}', date):
        date = date + ' 00:00:00'
        myButton["state"] = 'active'
        global start_date
        start_date = date
        #print(start_date)

def myClick():
    root.filename = filedialog.askopenfilename(initialdir="/", title="Выбрать файл", filetypes=[("csv files", ".csv")])
    #print(root.filename)
    analyze()

def info_popup():
    messagebox.showinfo("Предупреждение", "Анализатор работает только с таблицами .csv со следующим форматом данных:"
                                          "\nКурс-Длительность-Стоимость-Фамилия-Имя-id-Дата оплаты"
                                          "\n\nВо избежание проблем дату необходимо указывать в формате '2021-12-31 23:59:59'")

info_png = PhotoImage(file="output-onlinepngtools.png")

frame_top = Frame(root, bg='#ffb700', bd=5)
frame_top.place(relx=0, rely=0, relwidth=1, relheight=0.3)

frame_mid = Frame(root, bg='#ffb600', bd=5)
frame_mid.place(relx=0, rely=0.35, relwidth=1, relheight=0.15)

frame_bottom = Frame(root, bg='#FFFFFF', bd=5)
frame_bottom.place(relx=0, rely=0.55, relwidth=1, relheight=0.45)

dateLabel = Label(frame_top, text='Укажите конец первого временного\n интервала в формате 2021-12-31',
                  bg='#ffb700', font=('Arial', 12))
e = Entry(frame_top, justify=LEFT)
e.insert(END, '2021-09-15')
infoButton = Button(frame_top, image=info_png, command=info_popup, borderwidth=0, bg='#ffb700')
confButton = Button(frame_top, text='Подтвердить дату', command = confirm, anchor='e')

dateLabel.place(relx=0.1, rely=0.1, relwidth=0.8, relheight=0.3)
e.place(relx=0.2, rely=0.5, relwidth=0.6, relheight=0.2)
infoButton.place(relx=0.92, rely=0.05)
confButton.place(relx=0.2, rely=0.75)

myButton = Button(frame_mid, text = "Указать путь к файлу csv", state='disabled', command=myClick)
myButton.place(relx=0.35, rely=0.4)

def analyze():
    data = pd.read_csv(root.filename)
    fix_first = list(data.columns)
    data.columns = ['Course', 'yearly', 'price', 'surname', 'name', 'id', 'date']
    if fix_first[1] == '1' or fix_first[1] == '0':
        data.loc[-1] = fix_first
        data.index = data.index + 1
        data.sort_index(inplace=True)
        data.loc[0]['price'] = float(data.loc[0]['price'])
        data.loc[0]['yearly'] = int(data.loc[0]['yearly'])

    data = data.drop(data[data['price'] == 0].index)
    data = data.sort_values('date')
    data = data.reset_index(drop=True)

    date_obj = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')

    fst = data.loc[(data['date'] < start_date) & (data['yearly'] == 1)]
    bundle_fst = fst.loc[data['Course'].str.contains('Бандл', case=False)]
    bundle_first_sum = round(bundle_fst['price'].sum() / 2, 2)
    data_fst_filtred = fst.drop(bundle_fst.index)
    other_first_sum_year = round(data_fst_filtred['price'].sum(), 2)
    fst_yearly = other_first_sum_year + bundle_first_sum

    myLabel1 = Label(frame_bottom,
                     text='Стоимость годовых до '+ date_obj.strftime('%Y-%m-%d') +': ' +
                          str('{:10,.2f}'.format(fst_yearly)) +
                          ' р.' + '; 25% = ' + str('{:10,.2f}'.format(fst_yearly/4)) + ' р.;\n Средний чек: ' + str('{:10,.2f}'.format(fst_yearly/len(fst))), anchor=W, width=80, bg='#FFFFFF')
    myLabel1.grid(row=0)

    fst_mon = data.loc[(data['date'] < start_date) & (data['yearly'] == 0)]
    bundle_fst_month = fst_mon.loc[data['Course'].str.contains('Бандл', case=False)]
    bundle_mon_sum = round(bundle_fst_month['price'].sum() / 2, 2)
    data_fst_filtred_month = fst_mon.drop(bundle_fst_month.index)
    other_first_sum_mon = round(data_fst_filtred_month['price'].sum(), 2)
    fst_monthly = other_first_sum_mon + bundle_mon_sum

    myLabel2 = Label(frame_bottom,
                     text='Стоимость месячных до '+ date_obj.strftime('%Y-%m-%d') +': '+
                          str('{:10,.2f}'.format(fst_monthly)) +' р.' + '; 25% = ' +
                          str('{:10,.2f}'.format(fst_monthly/4)) + ' р.;\n Средний чек: ' + str('{:10,.2f}'.format(fst_monthly/len(fst_mon))), anchor=W, width=80, bg='#FFFFFF')
    myLabel2.grid(row=1)

    date_obj = date_obj + relativedelta(months=+1)
    row_num = 2
    full_sum = fst_yearly + fst_monthly
# тк мы берем последний интервал в худшем случае как последняя дата оплаты плюс месяц
    while date_obj <= datetime.strptime(data.iloc[-1]['date'], '%Y-%m-%d %H:%M:%S') + relativedelta(months=+1):
        date_obj_str = date_obj.strftime('%Y-%m-%d %H:%M:%S')
        date_obj_old = date_obj - relativedelta(months=+1)
        date_obj_old_str = date_obj_old.strftime('%Y-%m-%d %H:%M:%S')
        slice = data.loc[(data['date'] < date_obj_str) & (data['date'] > date_obj_old_str)]
        bundle_sep = slice.loc[data['Course'].str.contains('Бандл', case=False)]
        bundle_sum = round(bundle_sep['price'].sum()/2, 2)
        data_filtred = slice.drop(bundle_sep.index)
        other_sum = round(data_filtred['price'].sum(), 2)
        full = other_sum + bundle_sum
        full_sum = full_sum + full

        myLabel = Label(frame_bottom,
                         text='Полная стоимость от ' + date_obj_old.strftime('%Y-%m-%d') + ' до '+
                              date_obj.strftime('%Y-%m-%d') +': ' + str('{:10,.2f}'.format(full)) + ' р.' +
                              '; 25% = ' + str('{:10,.2f}'.format(full/4)) + ' р.;\n Средний чек: ' + str('{:10,.2f}'.format(full/len(slice))), anchor=W, width=80, bg='#FFFFFF')
        myLabel.grid(row=row_num)
        date_obj = date_obj + relativedelta(months=+1)
        row_num = row_num + 1

    myLabel3 = Label(frame_bottom,
                     text='Итого: ' + str('{:10,.2f}'.format(full_sum)) + ' р.' + '; 25% = ' +
                          str('{:10,.2f}'.format(full_sum/4)) + ' р.;\n Средний чек: ' + str('{:10,.2f}'.format(full_sum/len(data))), anchor=W, width=80, bg='#FFFFFF')
    myLabel3.grid(row=row_num)


root.mainloop()