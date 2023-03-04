from flet import *
from geopy.geocoders import Nominatim
# INSTALL geopy IN YOU COMPUTER WITH PIP
from geopy.distance import geodesic
import webbrowser

# INSTALL FOLIUM IN YOU COMPUTER WITH PIP
import folium
import geocoder
import os
import requests

def main(page:Page):
	page.scroll = "auto"
	searchplace = TextField(label="Find place")
	# YOU RADIUS FOR YOU SEARCH LIKE METERS OF YOU SEARCH
	you_radius = TextField(label="Radius in meters")
	listresults = Column(scroll="always")

	# LATITUDE AND LONGITUDE
	you_lat = Text()
	you_lon = Text()


	# AND GET YOU CURRENT LOCATION 
	you_locations_now = Column()

	# AND NOW IF YOU SEARCH PLACE AGAIN THEN LAST RESULT
	# WILL DELETE ALL IN MAPS_RESULT FOLDER
	# AND REPLACE WITH RESULT NEW SEARCH YOU
	def reset():
		dir_path = "maps_result/"
		# CHECK FILES IN FOLDER MAPS_RESULT 
		# IF FOUND THEN ALL DELETE
		for file_name in os.listdir(dir_path):
			file_path = os.path.join(dir_path,file_name)
			if os.path.isfile(file_path):
				# THEN REMOVE ALL
				os.remove(file_path)



	# AND FIRST TRACK YOU LOCATION NOW 
	def track_you_locations():
		geolocator = Nominatim(user_agent="myapplication")
		g = geocoder.ip("me")
		lat = g.latlng[0]
		lon = g.latlng[1]
		you_lat.value = lat
		you_lon.value = lon
		page.update()

		# CEK YOU LAT LONGITUDE
		print(lat,lon)
		# AND NOW REVERSE FROM LATITUDE AND LONGITURE
		# BECOME ADDRESS LOCATION YOU
		point = (lat,lon)
		location = geolocator.reverse(point,exactly_one=True).address
		print("YOu ADDRESS IS = ",location)

		you_locations_now.controls.append(
			Container(
				padding=10,
				bgcolor="yellow200",
				content=Column([
					Text(f"Latitude : {lat}",size=25),
					Text(f"Longitude : {lon}",size=25),
					Text(f"location you : {location}",
						weight="bold"
						)
					])
				)
			)
		page.update()



	# CALL FUCNTION WHEN FLET APP IS FIRST RUNNING
	track_you_locations()

	# SHOW MAPS 
	# IF YOU CLICK LIST TILE
	def showmaps(e,result):
		# AND NOW IF YOU CLICK LIST TILE THEN OPEN FIREFOX
		# FOR SEE MAPS RESULT
		filename = e.control.data
		folder_path = os.path.join(os.getcwd(),"maps_result")
		file_path = os.path.join(folder_path,filename)

		# AND LAST OPEN THE BROWSER FIREFOX AND OPEN FILE
		# HTML FILE
		webbrowser.get("firefox").open(file_path)	



	def showresult(e):
		reset()

		# GET REQUEST TO URL
		overpass_url = "https://overpass-api.de/api/interpreter"
		overpass_query = """
			[out:json];
			node["amenity"="%s"](around:%d,%s,%s);
			out;
		""" % (searchplace.value,int(you_radius.value),you_lat.value,you_lon.value)

		response = requests.get(overpass_url,params={"data":overpass_query})
		data = response.json()
		point = (you_lat.value,you_lon.value)

		# AND NOW CREATE MAPS 
		m = folium.Map(location=point,zoom_start=15)


		# AND NOW LOOP AND CREATE MARKER IN YOU MAPS
		for element in data['elements']:
			lon = element['lon']
			lat = element['lat']
			coord = (lat,lon)

			# AND PREDICTION DISTANCE 
			distance = geodesic(point, coord).m


			name = element.get("tags",{}).get("name","No Name")
			# IF ADDRES NOT FOUND THEN SHOW YOU UNKNOW ADDRESS
			address = element.get("tags",{}).get("addr:full","unknow ADDRESS")

			# AND NOW CREATE POPUP IN MARKER IF YOU CLICK
			# MARKER THEN SHOW POPUP
			popup_html = f"<b>{name}</b><br>{address}</br>"
			popup_html += f"latitude : {lat} <br>"
			popup_html += f"lognitude : {lon} <br>"
			popup_html += f"distance : {distance:.0f} m"

			popup = folium.Popup(popup_html,max_width=250)

			# CREATE MARKER
			folium.Marker(location=coord,popup=popup).add_to(m)


			# NOW I PRINT OUTPUT RESULT
			print(f"Name {searchplace} : {name} ")
			print(f"Location  {address} ")
			print(f"Latitude  {lat} ")
			print(f"lognitude  {lon} ")
			print(f"distance :   {distance:.0f} m\n")


			# AND NOW CREATE HTML FILE AND SAVE IN maps_result
			# FOLDER

			# I CREATE MAPS FOR EACH LOCATION RESULT
			file_name = f"{name},{address}.html"

			html_map = m._repr_html_()


			# AND SAVE TO maps_result folder

			with open(f"maps_result/{file_name}","w") as f:
				f.write(html_map)

			print(f"html file : {file_name}")

			# AND LAST PUSH TO WIDGET listresult FOR SEE RESULT

			listresults.controls.append(
				ListTile(
				title=Text(name,weight="bold"),
				subtitle=Column([
					Row([
				Text(f"latitude : {lat}",weight="bold"),
				Text(f"longitude : {lon}",weight="bold"),
						]),
				Text(f"distance : {distance:.0f} m")
					]),
				data=file_name,
				on_click=lambda e:showmaps(e,file_name)

					)

				)
		html_map = m._repr_html_()
		with open("map.html","w") as f:
			f.write(html_map)
		page.update()

			









	page.add(
	AppBar(
	title=Text("Flet Place find",color="white",weight="bold"),
	bgcolor="blue"
		),

	Column([
	Text("Find place near you ",weight="bold"),
	searchplace,
	you_radius,
	ElevatedButton("Search now",
		bgcolor="blue",color="white",
		on_click=showresult
		),
	Text("you location",weight="bold"),
	you_locations_now,

	# AND SHOW RESULT OF YOU SEARCH PLACE HERE
	listresults

		])

		)


flet.app(target=main)
