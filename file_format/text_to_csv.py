import glob

file_out = open('file_out.txt','w')
header = "adm_district,adm_vdc,adm_ward,nb_hh,nb_pop,nb_male,nb_female"
file_out.write(header + "\n")

for filename in glob.glob('*.txt'):
    file = open(filename, 'r')
    i = 0
    j = 0
    k = 0
    l = 0
    for line_raw in file:
        i = i+1
        line = line_raw.replace(',','')
        if i == 5:
            adm_district = line[:len(line)-1].capitalize()
        if line[0:19] == 'V.D.C./MUNICIPALITY':
            adm_vdc = line[22:len(line)-1]
        if line[:len(line)-1].isdigit() and k  == 5:
            k = 0
        if line[:len(line)-1].isdigit() and k > 0 and k < 5:
            k =k+1
        if line[0:5] == 'TOTAL':
            if l == 0:
                k = 1
            if l == 1:
                l = 0     
        if line[0:10] == 'POPULATION':
            l = 1
        if line[:len(line)-1].isdigit() and k == 0:
            j = j+1
            if j == 1:
                adm_ward = line[:len(line)-1]
            if j == 2:
                nb_hh = line[:len(line)-1]            
            if j == 3:
                nb_pop = line[:len(line)-1]
            if j == 4:
                nb_male = line[:len(line)-1]
            if j == 5:
                nb_female = line[:len(line)-1]
                record = adm_district+","+adm_vdc+"," + adm_ward +","+ nb_hh+","+ nb_pop+","+ nb_male+","+ nb_female
                print record
                file_out.write(record + "\n")
                j=0
    file.close()
file_out.close()
    
