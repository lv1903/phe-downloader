import sys

# url = "http://livews-a.phe.org.uk/GetDataDownload.ashx?pid=55&ati=102&res=55&tem=55&par=E92000001&pds=0&pat=6"
# output_path = "C:/dev/importerScripts/PHE _Data/" 
# sheet = "County & UA"
# required_indicators = ["Deprivation", "Under 75 mortality rate from non alcoholic liver disease (NAFLD)"]


	
def in_array(value, target_array):
	return any(value in target for target in target_array)


def download(url, sheet, required_indicators, output_path, output_filename, profile, version):
		
	import urllib.request, urllib.error, urllib.parse	
	socket = urllib.request.urlopen(url)
	print("opened url")

	import pandas as pd
	xd = pd.ExcelFile(socket)
	df = xd.parse(sheet)
	print("read sheet")
	
	
	#Replace spaces from headers
	df.columns = df.columns.str.replace(" ", "_")
	
	indicators = pd.unique(df.Indicator.ravel())
	if len(required_indicators) == 0:
		required_indicators = indicators
		
	#check required indicators available
	for indicator in required_indicators:
		if in_array(indicator, indicators) == False:
			print(("required indicator missing from file: {}").format(indicator))
			
	#add map period field
	df["Map_Period"] = int("20" + df["Time_Period"].str[-2] + df["Time_Period"].str[-1])
	
	
	#add area type field
	df["Area Type"] = sheet #default to sheet name
	
	if sheet == "County & UA":
		df["Area_Type"] = "CU"
	if sheet == "District & UA":
		df["Area_Type"] = "DU"
	if sheet == "CCG":
		df["Area_Type"] = "CCG"	
		
	#add profile name
	df["Profile"] = profile
		
	
	# hack to deal with nulls

	string_keys = ["Indicator",
					"Time_Period",
					"Parent_Code",
					"Parent_Name",
					"Area_Code",
					"Area_Name",
					"Age",
					"Note",
					"Area_Type",
					"Profile",
					"Sex"
				]
				
	number_keys = [
				"Value",
				"Lower_CI",
				"Upper_CI",
				"Count",
				"Denominator",
				"Map_Period"
				]
	
	#highlight number fields to be removed
	for key in number_keys:
		df[key] = df[key].fillna("remove")
		
	
	#make empty string fields ""	
	for key in string_keys:
		df[key] = df[key].fillna("")
						
		
		

	
	#add date for version
	# if len(version) == 0:
		# import datetime
		# version = str(datetime.datetime.now())
	# df["Download_Version"] = version
	
	
	#remove output file if it already exists
	import os
	try:
		os.remove(output_filename)
	except OSError:
		pass
	
	
	#get the file type
	filename, file_extension = os.path.splitext(output_filename)
	
	#convert to json string
	sJson = df[:100].to_json( path_or_buf=None, orient="records")
	
	#convert to object
	import json
	oJson = json.loads(sJson)
	
	for obj in oJson:
		for key in number_keys:
			if obj[key] == "remove":
				del obj[key]
				
		
	sJson = '{"data":' + json.dumps(oJson) + '}'
	
	print(len(json.loads(sJson)["data"]))
	
	print("output filename: " + output_filename)

	#save json file
	file = open(output_filename, "w")
	file.write(sJson)
	file.close()
	
	
	#todo write straight to json 
	#todo replace string NAs with ""
	#todo remove number fields with no value
	
	#write to new output file
	
	
	# i = 0
	# with open(output_filename, 'a') as f:
		# for indicator in indicators:
		
			# if in_array(indicator, required_indicators) == True:
				# print(indicator)
				# selected_rows_df = df[df.Indicator.isin([indicator])]
				# if i == 0:
					# selected_rows_df.to_csv(f, index = False)
				# else:
					# selected_rows_df.to_csv(f, index = False, header = False)

				
			# i += 1
			
	print("finished")
	
"""----------------------------------------"""
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("--generateConfig", "-g", help="generate a config file called config_PHE_fingertips.json", action="store_true")
parser.add_argument("--configFile", "-c", help="path for config file")
args = parser.parse_args()


if args.generateConfig: 
	obj = {	"url":"type/url/name/here.csv", 
			"out_path":"leave blank for same dir as downloader",
			"output_filename": "output.json",
			"sheet":"sheet name",
			"required_indicators":["indicator1", "indicator2", "etc", "or leave blank for all indicators"],
			"profile":"fingertips profile name",
			"download_version":"today's date, leave blank for auto_complete"
	}
	with open("config_PHE_fingertips.json", "w") as outfile:
		json.dump(obj, outfile, indent=4)
	sys.exit("config file generated")
	
if args.configFile == None:
	args.configFile = "config_PHE_fingertips.json"
	
with open(args.configFile) as json_file:
	oConfig = json.load(json_file)
	print("read config file")
				
download(oConfig["url"], oConfig["sheet"], oConfig["required_indicators"], oConfig["output_path"], oConfig["output_filename"], oConfig["profile"], oConfig["download_version"])