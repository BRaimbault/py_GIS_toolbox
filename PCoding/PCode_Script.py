#!/usr/bin/python
import csv
import sys, os
import nltk.metrics.distance as distance

def read_csv_to_dict(csv_to_open):
	f = open(csv_to_open, 'rU')
	return csv.DictReader(f), f
    

def read_csv(csv_to_open):
	f = open(csv_to_open, 'rU')
	return csv.reader(f), f
    

def write_csv(csv_to_write):
	f = open(csv_to_write, 'wb')
	return csv.writer(f), f
    

def create_csv_headers(csv_to_write_to, header):
	header.append('pcode')
	header.append('VDC code')
	header.append('User VDC Selection')
	header.append('Cost') #levenshtein cost. calculates the number of letters needed to turn one word into another 
	csv_to_write_to.writerow(header)
    
    
def exact_match(code_list, row, district_index, vdc_index, open_matched_words,admin_district_2,admin_n_2,alter_name_2, alter_code_2, admin_code_2):
    
	for item in code_list:
        
		# first check district name
		if item[admin_district_2] != row[district_index]:
			continue
            
		# next check VDC or OCHA name
		if ((row[vdc_index].lower() == item[admin_n_2].lower()) or 
				(row[vdc_index].lower() == item[alter_name_2].lower())):
            
			row.append(item[alter_code_2])
			row.append(item[admin_code_2])
            
			if row[vdc_index].lower() == item[admin_n_2].lower():
				row.append(item[admin_n_2])
			else:
				row.append(item[alter_name_2])
			row.append('0')
			open_matched_words.writerow(row)
			
			return True  # if we find a match
	return False  # if we do not find a match
            
            
def closest_match(code_list, row, district_index, vdc_index, open_matched_words, admin_district_2, admin_n_2, alter_name_2, alter_code_2, admin_code_2, found_names):
    
	# write the row out if the name is 'unknown'
	if row[vdc_index].lower() == 'unknown' :
		open_matched_words.writerow(row)
		return False
		
	# reduce potential matching items to only those with the same district
	shared_district_list = []
	for item in code_list:
		if item[admin_district_2] == row[district_index]:
			shared_district_list.append(item)
			
	# now we get the five best matches
	matched_names = []
	matched_costs = []
	matched_items = []
	for item in shared_district_list:
	
		# iterate over potential names
		name_list = [item[admin_n_2].lower(), item[alter_name_2].lower()]
		for name in name_list:
		
			# compute levenshtein cost
			cost = distance.edit_distance(row[vdc_index].lower(), name)#levenshtein cost. calculates the number of letters needed to turn one word into another 
            
			# if there is word matched, correct the cost with word cost
			if (' ' in name and row[vdc_index].lower() in name and len(row[vdc_index].split()) != len(name.split())) \
					or (' ' in row[vdc_index] and name in row[vdc_index].lower() and len(row[vdc_index].split()) != len(name.split())) :
				cost =  abs(len(row[vdc_index].split())-len(name.split()))
				
			# do not append the duplicated item
			if name not in matched_names :	
				# add cost and name to list
				matched_names.append(name)
				matched_costs.append(cost)  
				matched_items.append(item)
    
			# if length is greater than 5 then pop worst match from lists and
			# append the new better matching item
			if len(matched_names) > 5:
            
				# find the max levenshtein cost - and remove it
				remove_index = matched_costs.index(max(matched_costs))
				del matched_names[remove_index]
				del matched_costs[remove_index]
				del matched_items[remove_index]
            
	if len(matched_names) == 0:
		open_matched_words.writerow(row)
		return False
		
	# now get the user to select the best match
	while True:

		# get user selection
		user_choice = raw_input('''
                                Please select best match (1, 2, 3, 4, 5 or 6)
								(Option might be repeated, please don't worry about it!)
                                Name to match: %s
                                Option 1: %s
                                Option 2: %s
                                Option 3: %s
                                Option 4: %s
                                Option 5: %s
                                Option 6: No good choice!
                                Please enter your choice (1, 2, 3, 4, 5 or 6):								
                                ''' % (row[vdc_index],
                                       matched_names[0], 
                                       matched_names[1], 
                                       matched_names[2], 
                                       matched_names[3], 
                                       matched_names[4]))
        
		# check if valid choice made
		if user_choice not in ['1','2','3','4','5','6']:
			print "invalid choice - try again!"
			continue
            
		# ask if happy   
		if user_choice == '6':
			good_choice = raw_input('You selected NO GOOD CHOICE are you happy with that (Y/N):') 
		else:
			good_choice = raw_input('You selected %s are you happy with that (Y/N):' % matched_names[int(user_choice)-1])
		if 'n' not in good_choice.lower():
			break

	# write it out
	if user_choice == '6':
		found_names.append({'admin_district_1': row[district_index], 'admin_n_1': row[vdc_index], 'add_col': ['', '', '', '']})
		open_matched_words.writerow(row)
		return False
	else:
		matched_index = int(user_choice)-1
		row.append(matched_items[matched_index][alter_code_2])
		row.append(matched_items[matched_index][admin_code_2])
		row.append(matched_names[int(user_choice)-1])
		row.append(str(matched_costs[matched_index]))
		found_names.append({'admin_district_1': row[district_index], 'admin_n_1': row[vdc_index], 'add_col': [matched_items[matched_index][alter_code_2], matched_items[matched_index][admin_code_2], matched_names[int(user_choice)-1], str(matched_costs[matched_index])]})
		open_matched_words.writerow(row)
			
        return True  # if we find a match
        
def create_csv_headers_no_alter(csv_to_write_to, header):

	header.append('VDC code')
	header.append('User VDC Selection')
	header.append('Cost') #levenshtein cost. calculates the number of letters needed to turn one word into another 
	csv_to_write_to.writerow(header)
    
    
def exact_match_no_alter(code_list, row, district_index, vdc_index, open_matched_words, admin_district_2,admin_n_2, admin_code_2):
    
	for item in code_list:
        
		# first check district name
		if item[admin_district_2] != row[district_index]:
			continue
            
		# next check VDC or OCHA name
		if (row[vdc_index].lower() == item[admin_n_2].lower()):
            
			row.append(item[admin_code_2])
			row.append(item[admin_n_2])
                      
			row.append('0')
			open_matched_words.writerow(row)
			
			return True  # if we find a match
	return False  # if we do not find a match
            
            
def closest_match_no_alter(code_list, row, district_index, vdc_index, open_matched_words, admin_district_2,admin_n_2, admin_code_2, found_names):
    
	# write the row out if the name is 'unknown'
	if row[vdc_index].lower() == 'unknown' :
		open_matched_words.writerow(row)
		return False
	
	# reduce potential matching items to only those with the same district
	shared_district_list = []
	for item in code_list:
		if item[admin_district_2].lower() == row[district_index].lower():
			shared_district_list.append(item)
            
	# now we get the five best matches
	matched_names = []
	matched_costs = []
	matched_items = []
	for item in shared_district_list:
    
		# iterate over potential names
		name_list = [item[admin_n_2].lower()]
		for name in name_list:
        
			# compute levenshtein cost
			cost = distance.edit_distance(row[vdc_index].lower(), name)#levenshtein cost. calculates the number of letters needed to turn one word into another 
            
			# if there is word matched, correct the cost with word cost
			if (' ' in name and row[vdc_index].lower() in name and len(row[vdc_index].split()) != len(name.split())) \
					or (' ' in row[vdc_index] and name in row[vdc_index].lower() and len(row[vdc_index].split()) != len(name.split())) :
				cost =  abs(len(row[vdc_index].split())-len(name.split()))
			
			# do not append the duplicated item
			if name not in matched_names :	
				# add cost and name to list
				matched_names.append(name)
				matched_costs.append(cost)  
				matched_items.append(item)
			
			# if length is greater than 5 then pop worst match from lists and
			# append the new better matching item
			if len(matched_names) > 5:
            
				# find the max levenshtein cost - and remove it
				remove_index = matched_costs.index(max(matched_costs))
				del matched_names[remove_index]
				del matched_costs[remove_index]
				del matched_items[remove_index]
	
	if len(matched_names) == 0:
		open_matched_words.writerow(row)
		return False
	
	# now get the user to select the best match
	while True:

		# get user selection
		user_choice = raw_input('''
                                Please select best match (1, 2, 3, 4, 5 or 6)    
                                
                                Name to match: %s
                                Option 1: %s
                                Option 2: %s
                                Option 3: %s
                                Option 4: %s
                                Option 5: %s
                                Option 6: No good choice!
                                Please enter your choice (1, 2, 3, 4, 5 or 6):
                                ''' % (row[vdc_index],
                                       matched_names[0], 
                                       matched_names[1], 
                                       matched_names[2], 
                                       matched_names[3], 
                                       matched_names[4]))
        
		# check if valid choice made
		if user_choice not in ['1','2','3','4','5','6']:
			print "invalid choice - try again!"
			continue
            
		# ask if happy   
		if user_choice == '6':
			good_choice = raw_input('You selected NO GOOD CHOICE are you happy with that (Y/N):') 
		else:
			good_choice = raw_input('You selected %s are you happy with that (Y/N):' % matched_names[int(user_choice)-1])
		if 'n' not in good_choice.lower():
			break

	# write it out
	if user_choice == '6':
		open_matched_words.writerow(row)
		found_names.append({'admin_district_1': row[district_index], 'admin_n_1': row[vdc_index], 'add_col': ['', '', '']})
		return False
	else:
		matched_index = int(user_choice)-1
		row.append(matched_items[matched_index][admin_code_2])
		row.append(matched_items[matched_index][admin_n_2])   
		
		row.append(str(matched_costs[matched_index]))
		found_names.append({'admin_district_1': row[district_index], 'admin_n_1': row[vdc_index], 'add_col': [matched_items[matched_index][admin_code_2], matched_items[matched_index][admin_n_2], str(matched_costs[matched_index])]})
		open_matched_words.writerow(row)
		
		return True  # if we find a match

def check_selected_match(row, district_index, vdc_index, open_matched_words, found_names):
	for item in found_names:
		if item['admin_district_1'].lower() == row[district_index].lower() and item['admin_n_1'].lower() == row[vdc_index].lower():
			#row.append(item['add_col'])
			for col in item['add_col'] :
				row.append(col) 
			open_matched_words.writerow(row)
			return True
	return False

def check_configfile(conf):
	if os.path.exists(conf['file1 (working file name)']) is False:
		print conf['file1 (working file name)']
		sys.exit("=> This working file in config.csv does not exist.")		# if the file doesn't exist, script stops execution.
	if conf['file1 admin(n) name'] == '':
		sys.exit("Error: the field 'file1 admin(n) name' in config.csv is empty.")
	if conf['file1 admin(n+1) name'] == '':
		sys.exit("Error: the field 'file1 admin(n+1) name' in config.csv is empty.")
	
	if os.path.exists(conf['file2 (reference file name)']) is False:
		print conf['file2 (reference file name)']
		sys.exit("=> This reference file in config.csv does not exist.")		# if the file doesn't exist, script stops execution.	
		
	cnt1 = 0	# count of admin(n+1) names entered in config file ( file2 admin(n+1) name )
	cnt2 = 0	# count of admin(n+1) pcodes entered in config file ( file2 admin(n+1) pcode )
	if conf['file2 admin(n) name'] == '':
		sys.exit("Error: the field 'file2 admin(n) name' in config.csv is empty.")
	if conf['file2 admin(n+1) name1'] != '':
		cnt1 += 1
	else:
		sys.exit("Error: the field 'file2 admin(n+1) name1' in config.csv is empty.")
	if conf['file2 admin(n+1) name2'] != '':
		cnt1 += 1
	if conf['file2 admin(n+1) pcode1'] != '':
		cnt2 += 1
	else:
		sys.exit("Error: the field 'file2 admin(n+1) pcode1' in config.csv is empty.")
	if conf['file2 admin(n+1) pcode2'] != '':
		cnt2 += 1	
			
	return cnt1, cnt2
    
def main():

	# read the user input in config file and save the data in config[]
	config = []
	cfile = open('config.csv', 'r')
	reader = csv.DictReader(cfile)
	for row in reader:
		config.append(row)
	cfile.close()
	
	# list for keeping already found match (dict {'admin_n_1': name1, 'admin_district_1': name2, 'add_col': [pcode1, [pcode2,] user selected name2, cost]} in list)
	found_names = []	
	
	# check the user input in config file and get the count of them
	cnt_ref_nplus_name, cnt_ref_nplus_pcode = check_configfile(config[0])
        
	if cnt_ref_nplus_name == 2 :
        
		to_match_file = config[0]['file1 (working file name)']
		code_file = config[0]['file2 (reference file name)']
		matched_words = 'matched_words.csv'
        
		# open the relevant csv files
		open_to_match_file, wfile = read_csv(to_match_file)
		open_code_file, rfile = read_csv_to_dict(code_file)
		open_matched_words, ofile = write_csv(matched_words)
		admin_n_1 = config[0]['file1 admin(n+1) name']
		admin_district_1 = config[0]['file1 admin(n) name']
		admin_n_2 = config[0]['file2 admin(n+1) name1']
		admin_code_2 = config[0]['file2 admin(n+1) pcode1']
		alter_name_2 = config[0]['file2 admin(n+1) name2']
		alter_code_2 = config[0]['file2 admin(n+1) pcode2']
		admin_district_2 = config[0]['file2 admin(n) name']
        
		
		# read in the code file to a list
		code_list = [row for row in open_code_file]  # this puts the dictionary items into a list
        
		# now iterate over the open file that needs matching
		first_line = True
		total_found = 0
		for total_input, row in enumerate(open_to_match_file):
			if first_line:
            
				# first get indexes of VDC and District
				district_index = row.index(admin_district_1) 
				vdc_index = row.index(admin_n_1)
                
				# now create our new csv header
				create_csv_headers(open_matched_words, row)
				first_line = False  
           
			else:
            
				#  Here we do exact matching
				if exact_match(code_list, row, district_index, vdc_index, open_matched_words,admin_district_2, admin_n_2,alter_name_2, alter_code_2, admin_code_2):
					total_found += 1
				# Here we check if the user has already selected a closest matching
				elif check_selected_match(row, district_index, vdc_index, open_matched_words, found_names):
					total_found += 1
				# Here we do the closest matching
				elif closest_match(code_list, row, district_index, vdc_index, open_matched_words, admin_district_2, admin_n_2, alter_name_2, alter_code_2, admin_code_2, found_names):
					total_found += 1
				else:
					continue
                
		print "total input: ", total_input
		print "total found: ", total_found
		
		# close all opened files
		rfile.close()	# close reference file
		wfile.close()	# close working file
		ofile.close()	# close result/output file
        
	else:
		to_match_file = config[0]['file1 (working file name)']
		code_file = config[0]['file2 (reference file name)']
		matched_words = 'matched_words.csv'
        
		# open the relevant csv files
		open_to_match_file, wfile = read_csv(to_match_file)
		open_code_file, rfile = read_csv_to_dict(code_file)
		open_matched_words, ofile = write_csv(matched_words)
		admin_n_1 = config[0]['file1 admin(n+1) name']
		admin_district_1 = config[0]['file1 admin(n) name']
		admin_n_2 = config[0]['file2 admin(n+1) name1']
		admin_code_2 = config[0]['file2 admin(n+1) pcode1']
		admin_district_2 = config[0]['file2 admin(n) name']
		
		# read in the code file to a list
		code_list = [row for row in open_code_file]  # this puts the dictionary items into a list
        
		# now iterate over the open file that needs matching
		first_line = True
		total_found = 0
		for total_input, row in enumerate(open_to_match_file):
			if first_line:
            
				# first get indexes of VDC and District
				district_index = row.index(admin_district_1) 
				vdc_index = row.index(admin_n_1)
                
				# now create our new csv header
				create_csv_headers_no_alter(open_matched_words, row)
				first_line = False  
           
			else:

				if not row[vdc_index]:  # checks for empty cell in csv rown
					continue  # this continues to the next row in the csv
            
				#  Here we do exact matching
				if exact_match_no_alter(code_list, row, district_index, vdc_index, open_matched_words, admin_district_2,admin_n_2, admin_code_2):
					total_found += 1
				# Here we check if the user has already selected a closest matching
				elif check_selected_match(row, district_index, vdc_index, open_matched_words, found_names):
					total_found += 1
				# Here we do the closest matching
				elif closest_match_no_alter(code_list, row, district_index, vdc_index, open_matched_words, admin_district_2,admin_n_2, admin_code_2, found_names):
					total_found += 1
				else:
					continue
                
		print "total input: ", total_input
		print "total found: ", total_found
		
		# close all opened files
		rfile.close()	# close reference file
		wfile.close()	# close working file
		ofile.close()	# close result/output file
		
	    
if __name__=="__main__":
	main()
