
# Into the Okavango Twitter Scraper
# Gets feeds from @okavangodata and pipes into server

import geojson, model, json;

from twython import Twython
from twython import TwythonError
from datetime import datetime
from time import mktime
from housepy import util

def init_twitter():
	APP_KEY = "PDtNJXpCD1v6oqtelAA7JuGzq";
	APP_SECRET = "q4mBpZGKIDFEHzURtQpbCBuZyF3tyU0078oWfsYdq4HJ5VLPf6";
	OAUTH_TOKEN = "2690906527-6pdw88pGs2Vrbw4QXb8Y57l4LXfYRb3zUnInrAr";
	OAUTH_TOKEN_SECRET = "Qus7rdrsA0wD4AzJ46J6byeHKmNrPajhoVJMyaXVMG9CG";

	APP_KEY_DATA = "Wsyew6Sx80Xpu5ZKi3FHaQZ9y";
	APP_SECRET_DATA = "00AzBBQBcIFdc3Iy9q3hx0LiS0v3POyVxu7lRKXWG8nHfV2ium";
	OAUTH_TOKEN_DATA = "2690906527-s0R9M3uqPNMgLnNapAGD9Itb0PUmM9BYX5AESZk";
	OAUTH_TOKEN_SECRET_DATA = "H3rzh8fx6zugShxE2tENGCuymkpvFyotYxc46CijWJysH";

	twitter = Twython(APP_KEY, APP_SECRET, OAUTH_TOKEN, OAUTH_TOKEN_SECRET)
	twitter.verify_credentials();

	twitter_data = Twython(APP_KEY_DATA, APP_SECRET_DATA, OAUTH_TOKEN_DATA, OAUTH_TOKEN_SECRET_DATA)
	twitter_data.verify_credentials();

	# 1.  Get timeline for @okavangodata feed
	try: 
		data_timeline = twitter.get_user_timeline(screen_name='okavangodata')
	except TwythonError as e:
	    print(e)

	# Look for tweets that are location reports.
	# ie: I am here Lat+40.704750 Lon-73.988217  Alt+139ft GPS Sats seen: 05 http://map.iridium.com/m?lat=40.704750&lon=-73.988217  Sent via Iridiu 
	for tweet in data_timeline:
		#Does it contain Lat Lon and Alt?
		txt = tweet.get('text')

		if 'dropped!' in txt:
			data = {}
			tokens = txt.split(' ')
			for token in tokens:
				if ':' in token:
					key, value = token.split(':')
					data[key] = value
			if 'lat' in data and 'lon' in data and 'id' in data:
				model.insert_hydrodrop(util.timestamp(), data['id'], data['lat'], data['lon'])

		elif ('Lat' in txt and 'Lon' in txt and 'Alt' in txt):
			lat = 0
			lon = 0
			#Get Lat
			p = txt.index('Lat')
			# is it in degree notation?
			if ('deg' in txt):
				#print txt[p + 3:p + 13]
				print('degrees')
			else:
				lat = float(txt[p + 3:p + 13])

			#print(txt);

			#Get Lon
			p = txt.index('Lon')
			# is it in degree notation?
			if ('deg' in txt):
				#print txt[p + 3:p + 13]
				print('degrees')
			else:
				lon = float(txt[p + 3:p + 13])

			#Get Alt
			p = txt.index('Alt')
			# is it in degree notation?
			alt = float(txt[p + 3:p + 7])

			#Get Time
			#Mon Aug 04 15:21:31 +0000 2014
			dt = tweet.get('created_at')
			date_object = datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')

			#Make JSON
			if (lat != 0):
				t = (date_object - datetime(1970,1,1)).total_seconds();
				coordinates = (lon,lat,alt);
				properties = {'DateTime': date_object.strftime("%Y-%m-%dT%H:%M:%S%z"), 't_utc': t, 'ContentType': 'beacon'}
				feature = geojson.Feature(geometry={'type': "Point", 'coordinates': coordinates}, properties=properties)

				#check protect
				t_protect = model.get_protect('beacon')
				if (t > t_protect):    
					model.insert_feature('beacon', t, geojson.dumps(feature))
				#print(feature);

		elif '!!' in txt:
			atwt = txt.split('!!')[1];
			#twitter.update_status(status=atwt);

			#Get Time
			#Mon Aug 04 15:21:31 +0000 2014
			dt = tweet.get('created_at')
			date_object = datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')

			t = (date_object - datetime(1970,1,1)).total_seconds();




			#print("AUTO TWEET:" + atwt)

	# 2.  Get timeline for all associated feeds

	## a. intotheokavango - all tweets
	try: 
		main_timeline = twitter.get_user_timeline(screen_name='intotheokavango')
	except TwythonError as e:
	    print(e)

	# File these tweets into the DB
	for tweet in main_timeline:
		#Get Time
		#Mon Aug 04 15:21:31 +0000 2014
		dt = tweet.get('created_at')
		date_object = datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')
		t = (date_object - datetime(1970,1,1)).total_seconds();
		coords = model.get_coords_by_time(t);
		properties = {'DateTime': date_object.strftime("%Y-%m-%dT%H:%M:%S%z"), 't_utc': t, 'ContentType': 'tweet', 'tweet': tweet}
		feature = geojson.Feature(geometry=coords, properties=properties)
		#check protect
		t_protect = model.get_protect('tweet')
		if (t > t_protect):  
			model.insert_feature('tweet', t, geojson.dumps(feature))
		#else:
			#print("TWEET NOT NEWEST. NEWEST IS:" + str(t_protect) + " THIS ONE IS:" + str(t))

	## b. others - #okavango14 tagged 
	accts = ('blprnt','shahselbe','rustictoad','AdventurScience','rangerdiaries','jameskydd','okavangowild','drsteveboyes')
	for ac in accts:

		try: 
			main_timeline = twitter.get_user_timeline(screen_name=ac)
		except TwythonError as e:
		    print(e)

		# File these tweets into the DB
		for tweet in main_timeline:
			#Get Time
			#Mon Aug 04 15:21:31 +0000 2014
			if ('#okavango14' in tweet['text']):
				dt = tweet.get('created_at')
				date_object = datetime.strptime(dt, '%a %b %d %H:%M:%S +0000 %Y')
				t = (date_object - datetime(1970,1,1)).total_seconds();
				coords = model.get_coords_by_time(t);
				properties = {'DateTime': date_object.strftime("%Y-%m-%dT%H:%M:%S%z"), 't_utc': t, 'ContentType': 'tweet', 'tweet': tweet}
				feature = geojson.Feature(geometry=coords, properties=properties)
				#check protect
				t_protect = model.get_protect('tweet')
				if (t > t_protect):  
					model.insert_feature('tweet', t, geojson.dumps(feature))
				#else:
					#print("TWEET NOT NEWEST. NEWEST IS:" + str(t_protect) + " THIS ONE IS:" + str(t))

	#4. -  Tweet sightings to okavangodata
	print("LOOKING FOR UNTWEETED SIGHTINGS.")
	query = "SELECT * FROM features WHERE kind = 'sighting' AND tweeted = 0 AND t > 1407890717"
	model.db.execute(query)
	for row in model.db.fetchall():
		j = json.loads(row['data'])
		props = j['properties']
		tweet = props['TeamMember'] + ' spotted: ' + props['Count'] + ' ' + props['Bird Name'] + ' Lat:' + props['Latitude'] + ' Lon:' + props['Longitude'] + ' Activity:' + props['Activity']
		
		try:
			twitter_data.update_status(status=tweet);
		except TwythonError as e:
			print(e)

		print("---- TWEET" + tweet)

	query = "UPDATE features SET tweeted = 1 WHERE kind = 'sighting' AND tweeted = 0 AND t > 1407890717"
	model.db.execute(query)



init_twitter()


