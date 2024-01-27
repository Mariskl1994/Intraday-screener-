from keep_alive import keep_alive
keep_alive()

import pandas as pd
from tradingview_screener import Scanner, Query, Column
from time import sleep
import pdb
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import urllib
import os
import requests
from datetime import datetime
from pytz import timezone
day1_local = datetime.now(timezone("Asia/Kolkata"))
day10 = day1_local.strftime('%H:%M:%S')
from datetime import datetime
from pytz import timezone
day2_local = datetime.now(timezone("Asia/Kolkata"))
day2 = day2_local.strftime('%d-%m-%Y')





csv_file_path = 'data.csv'  # Replace with your desired CSV file path


class YourClass:
    def crosses_below(self, column, other):
        return {'left': column.name, 'operation': 'crosses_below', 'right': column._extract_value(other)}

    def crosses_above(self, column, other):
        return {'left': column.name, 'operation': 'crosses_above', 'right': column._extract_value(other)}

time_intervals = ['1','5','15','30']

def setup_ui():
    limit = 1
    price_from = 2000
    price_to = 2500
    return price_from, price_to, limit

def main():
    price_from, price_to,limit = setup_ui()
    temp = pd.DataFrame()

    if True:
        final_df = pd.DataFrame()
        for x in time_intervals:
            your_instance = YourClass()

            df_bullish = (Query()
                          .select('Exchange', f'close|{x}', f'volume|{x}', f'ADX-DI|{x}', f'ADX+DI|{x}')
                          .where(your_instance.crosses_below(Column(f'ADX-DI|{x}'), Column(f'ADX+DI|{x}')),
                                 Column(f'close|{x}').between(price_from, price_to))
                          .order_by(f'volume|{x}', ascending=False)
                          .limit(limit))

            df_bearish = (Query()
                          .select('Exchange', f'close|{x}', f'volume|{x}', f'ADX-DI|{x}', f'ADX+DI|{x}')
                          .where(your_instance.crosses_above(Column(f'ADX-DI|{x}'), Column(f'ADX+DI|{x}')),
                                 Column(f'close|{x}').between(price_from, price_to))
                          .order_by(f'volume|{x}', ascending=False)
                          .limit(limit))

            df_bullish = df_bullish.set_markets('india').get_scanner_data()[1]
            df_bullish = df_bullish[df_bullish['exchange'] == 'NSE']
            df_bullish['trend'] = f'Buy|{x}m'
            df_bullish['Entry_time'] = day1_local.strftime('%H:%M:%S')
            df_bullish['Entry_price'] = df_bullish[f'close|{x}']
            df_bullish = df_bullish[['ticker', 'trend', 'Entry_time', 'Entry_price']]

            df_bearish = df_bearish.set_markets('india').get_scanner_data()[1]
            df_bearish = df_bearish[df_bearish['exchange'] == 'NSE']
            df_bearish['trend'] = f'Sell|{x}m'
            df_bearish['Entry_time'] = day1_local.strftime('%H:%M:%S')
            df_bearish['Entry_price'] = df_bearish[f'close|{x}']
            df_bearish = df_bearish[['ticker', 'trend', 'Entry_time', 'Entry_price']]

            merge_cols = ['ticker', 'trend', 'Entry_time', 'Entry_price']
            merged_df = pd.concat([df_bullish, df_bearish], ignore_index=True)
            #merged_df = pd.merge(df_bullish, df_bearish, on=merge_cols, how='outer')
            final_df = pd.concat([merged_df, final_df], ignore_index=True)

        # Fetch data already stored in the CSV file
        try:
            stored_data = pd.read_csv(csv_file_path)
        except FileNotFoundError:
            stored_data = pd.DataFrame(columns=final_df.columns)

        # Convert 'ticker' columns to string data type
        final_df['ticker'] = final_df['ticker'].astype(str)
        stored_data['ticker'] = stored_data['ticker'].astype(str)

        # Remove rows from final_df that are already in the CSV file based on the 'ticker' column
        final_df = final_df[~final_df['ticker'].isin(stored_data['ticker'])]

        # Store new rows in the CSV file
        final_df.to_csv(csv_file_path, mode='a', header=False, index=False)
        print(final_df)
def Report():
    data = pd.read_csv(csv_file_path)
    data['Ltp'] = ''
    ticker_list = data['ticker'].tolist()
    q = Query().select('close')
    try:
        result = q.set_tickers(*ticker_list).get_scanner_data()[1]
        result.set_index('ticker', inplace=True)
        data.set_index('ticker', inplace=True)
        data['Ltp'].update(result['close'])
        data.reset_index(inplace=True)

        # Calculate P/L and P/L percentage
        data['Qty'] = int(10)
        data['Inv_Amount'] = data['Qty'] * data['Entry_price']

        data['P/L'] = (data['Ltp'] - data['Entry_price']) * data['Qty']
        data['P/L'] = round(data['P/L'].astype('float'),2)
        data['P/L %'] = ((data['Ltp'] - data['Entry_price']) / data['Entry_price']) * 100
        data['P/L %'] = round(data['P/L %'].astype('float'),2)
        # Add new columns for trade result and win/loss
        data['Result'] = 'Neutral'
        data['Win/Loss'] = 0  # 1 for win, 0 for loss

        # Identify winning trades
        win_condition = data['P/L'] > 0
        data.loc[win_condition, 'Result'] = 'Win'
        data.loc[win_condition, 'Win/Loss'] = 1

        # Identify losing trades
        loss_condition = data['P/L'] < 0
        data.loc[loss_condition, 'Result'] = 'Loss'

        # Calculate total number of winning and losing trades
        total_wins = data['Win/Loss'].sum()
        total_losses = len(data) - total_wins
        total_pl = data['P/L'].sum()

        # Print the updated dataframe
        #print(data)

        # Print total wins and losses
        print(f'Time:{day2}_{day10}')
        print(f'Total P/L: Rs.{int(total_pl)}')
        print(f'Total Wins: {total_wins}')
        print(f'Total Losses: {total_losses}')

        def ax_logo(ax):
          club_icon = Image.open('duck.png')
          ax.imshow(club_icon)
          ax.axis('off')
          return ax

        fig = plt.figure(figsize=(20,8), dpi=300)
        ax = plt.subplot()
        ncols = 11
        df_example_2 = data
        nrows = df_example_2.shape[0]
        ax.set_xlim(0, ncols + 1)
        ax.set_ylim(0, nrows + 1)
        positions = [0.25, 2.5, 3.5, 4.5, 5.5,6.5,7.5,8.5,9.5,10.5,11.5]
        columns = ['ticker','trend','Entry_time','Entry_price','Ltp','Qty','Inv_Amount','P/L','P/L %','Result','Win/Loss']
        # Add table's main text
        for i in range(nrows):
            for j, column in enumerate(columns):
                if j == 0:
                    ha = 'left'
                    cell_color = 'black'
                elif j == 1 or j == 2 or j == 3 or j == 4 or j == 5 or j == 6 or j == 9:
                    ha = 'center'
                    cell_color ='black'
                else:
                    ha = 'center'
                    value = df_example_2[column].iloc[i]
                    try:
                      cell_color = 'limegreen' if value > 0 else 'red'
                      text_label = f'{df_example_2[column].iloc[i]:,.00f}'
                    except :
                      try:
                        numeric_value = float(value.rstrip('%'))
                        cell_color = 'limegreen' if numeric_value > 0 else 'red'
                      except ValueError:
                        cell_color = 'white'
                if column == 'Min':
                    text_label = f'{df_example_2[column].iloc[i]:,.00f}'
                    weight = 'bold'
                else:
                    text_label = f'{df_example_2[column].iloc[i]}'
                    weight = 'normal'
                ax.annotate(xy=(positions[j], i + .5),text=text_label,ha=ha,va='center',weight=weight,color=cell_color)
        # Add column names
        column_names = ['ticker','trend','Entry_time','Entry_price','Ltp','Qty','Inv_Amount',f'P/L\n₹ {round(total_pl,2)}','P/L %','Result','Win/Loss']
        for index, c in enumerate(column_names):
                if index == 0:
                    ha = 'left'
                    cell_color = 'black'
                else:
                    ha = 'center'
                    value = index
                    try:
                      cell_color = 'limegreen' if value > 0 else 'red'
                    except :
                      try:
                        numeric_value = float(value.rstrip('%'))
                        cell_color = 'limegreen' if numeric_value > 0 else 'red'
                      except ValueError:
                        cell_color = 'white'
                ax.annotate(xy=(positions[index], nrows + .25),text=column_names[index],ha=ha,va='bottom',weight='bold',color=cell_color)
        # Add dividing lines
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [nrows, nrows], lw=1.5, color='black', marker='', zorder=11)
        ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [0, 0], lw=1.5, color='black', marker='', zorder=11)
        for x in range(1, nrows):
            ax.plot([ax.get_xlim()[0], ax.get_xlim()[1]], [x, x], lw=1.15, color='gray', ls=':', zorder=3 , marker='')
        ax.fill_between(x=[0,2],y1=nrows, y2=0,color='lightgrey',alpha=0.5,ec='None')
        ax.set_axis_off()
        logo_ax = fig.add_axes([.825, .31, 0.1, 1.45])
        ax_logo(logo_ax)
        fig.text(x=0.15, y=.91, s=f'Intraday Screener Daily Summery Report on {day2}\nTotal Wins: {total_wins}\nTotal Losses: {total_losses}',color ='blue', ha='left',va='bottom', weight='bold', size=25)

        plt.savefig('Report.jpg', dpi=300, transparent=True, bbox_inches='tight')
        sleep(2)
    except Exception as e:
     print(f"Error: {e}")


def send_report():
  tele_auth_token = '5719015279:AAHTTTus2_dmsVvp9xTlO2QUFuHwtRmUfbY'
  chat_id = {'chat_id' : "-1001954093602"}
  send_photo_url = f"https://api.telegram.org/bot{tele_auth_token}/sendPhoto"
  data = {"photo": open('./Report.jpg','rb')}
  response = requests.post(send_photo_url,chat_id,files=data)
  if response.status_code == 200:
    print(f"Report  sent successfully")
  else:
    print(f"Failed  to send the Report")
    print(response.text)



def clear_csv_data_without_header(file_path):
  import csv
  # Read the header from the existing file
  with open(file_path, 'r', newline='') as csvfile:
    csv_reader = csv.reader(csvfile)
    header = next(csv_reader, None)

  # Write the header back to the file
  with open(file_path, 'w', newline='') as csvfile:
      csv_writer = csv.writer(csvfile)
      if header:
        csv_writer.writerow(header)

if __name__ == "__main__":
    while True:
      report_minutes = [5,10,15,20,25,30,35,40,45,50,55,0]
      from datetime import datetime
      import time
      from pytz import timezone
      day = datetime.now(timezone("Asia/Kolkata"))
      current_time = day.time()
      if day.strptime("09:16:00", "%H:%M:%S").time() <= current_time <= day.strptime("18:16:00", "%H:%M:%S").time():
        main()
        sleep(18)
        print('..........')
        Report()
        if current_time.minute in report_minutes:
          send_report()
          sleep(60)
      else:
        print('Wait for Trading Time...!!')
        clear_csv_data_without_header(csv_file_path)
        sleep(60)
      sleep(60)
