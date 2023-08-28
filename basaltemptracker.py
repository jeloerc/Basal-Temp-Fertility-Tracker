
import pandas as pd
import matplotlib.pyplot as plt

class BasalTempTracker:
    def __init__(self):
        self.temps = {}
        self.day_counter = 1
        self.temp_list = []
        self.load_data()


    def add_temp(self, temp):
        self.temps[self.day_counter] = temp
        self.temp_list.append(temp)
        self.day_counter += 1
        self.save_data()

    def get_average(self, temp_list):
        return sum(temp_list)/ len(temp_list)


    def fertile_day(self, temp):
        fertile_temp=98.6
        return temp >= fertile_temp

    def analyze(self):
        temp_dates = sorted(self.temps.keys())
        temp_values = [self.temps[date] for date in temp_dates]
        cycle_average = self.get_average(temp_values)
        fertile_days = [date for date in temp_dates if self.fertile_day(self.temps[date])]

        print("Analysis:")
        print(f"Average Basal Body Temp: {cycle_average:.2f}°F")
        print("Fertile Days:", fertile_days)
       
        print("Infertile Days:", [date for date in temp_dates if date not in fertile_days])
    def reset_day_counter(self):
        self.day_counter = 1
        self.temp_list=[]
        print("Day counter reset.")

    def display_temp_list(self):
        if self.temp_list:
            print("Temperature History:")
            day_offset = (self.day_counter - 1) % 28
            for i, temp in enumerate(self.temp_list, start=1):
                day_number = (i + day_offset - 1) % 28 + 1
                print(f"Day {day_number}: {temp:.2f}°F")
        else:
            print("No temperature history available.")

    def load_data(self):
        try:
            data = pd.read_csv("temperature_data.csv")
            for index, row in data.iterrows():
                self.temps[int(row["Day"])] = row["Temperature"]
                self.temp_list.append(row["Temperature"])
            self.day_counter = len(self.temps) + 1
        except FileNotFoundError:
            self.day_counter = 1

    def save_data(self):
        data = pd.DataFrame({"Day": list(self.temps.keys()), "Temperature": list(self.temps.values())})
        data.to_csv("temperature_data.csv", index=False)
    
    def plot_data(self):
        fertile_temp=98.6
        temp_dates=sorted(self.temps.keys())
        temp_values=[self.temps[date] for date in temp_dates]
        plt.plot(temp_dates, temp_values, marker='o')
        plt.axhline(y=fertile_temp, color='r', linestyle='--', label='Fertile Threshold')
        plt.xlabel('Day in Menstrual Cycle')
        plt.ylabel('Basal Body Temp (°F)')
        plt.title('Basal Body Temperature Tracking')
        plt.legend()
        plt.show()


tracker = BasalTempTracker()

def get_choice(prompt: str, choices) -> int:
    while True:
        print(prompt)
        for i, c in enumerate(choices, start=1):
            print(f"{i}: {c}")
        try:
            choice = int(input("> "))
            if 1 <= choice <= len(choices):
                return choice
            print("Please provide a valid choice.")
        except ValueError:
            print("Please provide a number.")

while True:
    choice = get_choice('Choose one of the following options by typing the corresponding number:',
                        ['Log morning temperature',
                         'Started menstrual cycle',
                         'Analyze data',
                         'Display temperature history',
                         'Display data plot',
                         'Exit'])

    if choice == 1:
        temp = float(input(f'Enter your morning temperature for day {tracker.day_counter}: '))
        tracker.add_temp(temp)
    elif choice == 2:
        tracker.reset_day_counter()
    elif choice == 3:
        tracker.analyze()
    elif choice == 4:
        tracker.display_temp_list()
    elif choice == 5:
        tracker.plot_data()
    elif choice==6:    
        print("Exit")
        break
    else:
        print('Please select a choice between 1 and 5.')
