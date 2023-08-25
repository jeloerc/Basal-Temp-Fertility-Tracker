
#dont be stupid it is simple when you add average needed

class BasaltempTracker:
    def __init__(self):
        self.temps = {}

    def add_temp(self, date, temp):
        self.temps[date] = temp

    def get_average(self, temp_list):
        return sum(temp_list) / len(temp_list)

    def fertile_day(self, temp):
        return temp > 97.5 

    def analyze(self):
        temp_dates = sorted(self.temps.keys())
        temp_values = [self.temps[date] for date in temp_dates]

        cycle_average = self.get_average(temp_values)
        fertile_days = [date for date in temp_dates if self.fertile_day(self.temps[date])]

        print("Analysis:")
        print(f"Average Basal Body Temp: {cycle_average:.2f}°F")
        print("Fertile Days:", fertile_days)
        print("Infertile Days:", [date for date in temp_dates if date not in fertile_days])

#test casesessss
tracker = BasaltempTracker()
tracker.add_temp("1", 98.0)
tracker.add_temp("2", 98.3)
tracker.add_temp("3", 98.3)
tracker.add_temp("4", 98.6)
tracker.add_temp("5", 98.0)
tracker.add_temp("6", 97.7)
tracker.add_temp("7", 97.9)

tracker.analyze()


#PROMPTING MAYBE 

#SIMPLE CHOICES with elif?????
#INPUT()

#1, add temp; 2,analyze data;
#1=input of date and temp maybe message to onlt do in mornign 
#2 is jsut stupid its already a def but still nice to have interphase??
#need else cause people dumb