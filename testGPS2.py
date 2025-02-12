import gps
import time
import folium
import webbrowser

# 创建GPS session
session = gps.gps(mode=gps.WATCH_ENABLE)

def open_map(lat, lon):
    url = f"https://www.google.com/maps?q={lat},{lon}"
    webbrowser.open(url)

def display_map(lat, lon):
    map = folium.Map(location=[lat, lon], zoom_start=15)
    folium.Marker([lat, lon]).add_to(map)
    map.save("map.html")
    webbrowser.open("map.html")

while True:
    try:
        report = session.next()
        
        if report['class'] == 'TPV':
            if hasattr(report, 'lat') and hasattr(report, 'lon'):
                lat = report.lat
                lon = report.lon
                print(f"Latitude: {lat}, Longitude: {lon}")
                display_map(lat, lon)
                
        time.sleep(1)
        
    except KeyboardInterrupt:
        break
