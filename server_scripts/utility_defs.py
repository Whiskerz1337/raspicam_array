from datetime import datetime
import pytz

def time_conversion(unix_stamp):

    utc_now = datetime.now(pytz.utc)

    # Convert the current UTC time to the desired timezone
    sydney_tz = pytz.timezone('Australia/Sydney')
    sydney_now = utc_now.astimezone(sydney_tz)

    # Format the output to exclude the timezone offset
    formatted_date = sydney_now.strftime('%Y-%m-%d %H:%M:%S')

    return formatted_date



