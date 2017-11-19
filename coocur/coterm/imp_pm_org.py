# remove:
    # word.space as only

    # all emails:
        field containing @


# code for ad:
    1. initiative
    2. remove all ',', '/', then tokenize by words

    3. if postal code is the same, then most-likely same

# compare:
    first field
    orgnization name (university/universita, colleage, institute/Institutet, center/Centre)
    #
    # considering use only 'univers' as the stem for matching uni
    #
    # if non-org word found, then perhaps ALL CAPITAL LETTERS as org:
    #    AD  - Brain Science Institute, RIKEN, Wako, Saitama, Japan.
    #
    # if all fails, then try to match city and take the one before city as uni

if same org:
    then loosing the constraint for matching departments:
        AD  - Brain and Cognitive Sciences Department and Center for Visual Science,
        AD  - Brain and Cognitive Science Department,
    the above two department text are not quite the same, but they are from the
    same university. So as long as the leading 3 words matches, then i consider
    them to be the same department


# map using city.csv, with a google link q=cityname for each dot plotted for city
http://www.d3noob.org/2013/03/a-simple-d3js-map-explained.html

# yahoo placefinder (not free)
# google geocoding api
http://stackoverflow.com/questions/843549/google-geocoding-api-city-long-lat

# downloadable zip files, free
http://www.geonames.org/export/

# GEOnet names server
http://geonames.nga.mil/gns/html/

# Google Geocoding API
https://developers.google.com/maps/documentation/geocoding/intro

# MaxMind - free database
https://www.drupal.org/node/19983

# from city names to geo, in excel sheet: Geonames(free web service/full text search)
http://gis.stackexchange.com/questions/54405/is-there-a-way-to-populate-a-spreadsheet-of-city-names-with-their-latitudes-and

# latlong - type name to latlong
# also from Univercity name to lat long !!!
http://www.latlong.net/

# stackoverflow - geonames topic:
http://gis.stackexchange.com/questions/tagged/geonames

# dowloaded worldcitiespop.txt.gz
# from
# https://www.maxmind.com/en/free-world-cities-database

