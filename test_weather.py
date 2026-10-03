import unittest
from weather import daytime_summary


def hours(codes):
    return [{'time':f'{i+7:02}:00', 'code':c} for i,c in enumerate(codes)]


class DaytimeTests(unittest.TestCase):
    def test_night_overcast_does_not_override_sunny_day(self):
        self.assertEqual(daytime_summary(hours([0]*12),3), (0,'Sunny','clear',[]))

    def test_sunny_family_combines_clear_codes(self):
        self.assertEqual(daytime_summary(hours([0]*4+[1]*4+[3]*4),3)[:3], (1,'Mostly sunny','clear'))

    def test_brief_rain_is_not_hidden(self):
        result = daytime_summary(hours([0]*6+[61,63]+[0]*4),63)
        self.assertEqual(result[1], 'Mostly sunny')
        self.assertEqual(result[3], ['Rain: 13:00–15:00'])

    def test_snow_and_storm_periods(self):
        result = daytime_summary(hours([71,71,0,95,95,0]),95)
        self.assertEqual(result[3], ['Snow: 07:00–09:00','Thunderstorms: 10:00–12:00'])

    def test_missing_hours_falls_back(self):
        self.assertEqual(daytime_summary([],3), (3,'Overcast','cloudy',[]))

    def test_rain_intensities_count_as_one_family(self):
        self.assertEqual(daytime_summary(hours([61]*3+[63]*3+[0]*5),63)[2], 'rain')
