from datetime import datetime
import pytz


def get_mexico_time():
    mx = pytz.timezone('America/Mexico_City')
    return datetime.now(mx).replace(tzinfo=None)

def time_to_mexico_time(dt):
    try:
        mx = pytz.timezone("America/Mexico_City")
        
        if dt.tzinfo is None:
            # Assume UTC if naive
            aware_utc_dt = pytz.utc.localize(dt)
        else:
            aware_utc_dt =  dt.astimezone(pytz.utc)
            
        aware_to_mexico_city = aware_utc_dt.astimezone(mx)
        

        return aware_to_mexico_city.replace(tzinfo=None)  # Convert to naive datetime
    except:
        return None