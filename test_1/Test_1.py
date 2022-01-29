
# the word to be removed
string1 = 'dolor'
  
# opening a text file
file1 = open("file_1.txt", "r")
file2 = open("file_2.txt", "w") 
# setting flag and index to 0
flag = 0
index = 0
  
# Loop through the file line by line
for line in file1:  
    index += 1 
      
    # checking string is present in line or not
    if string1 in line:
      for i in line:
          if string1 != i:
              file2.write(i)
      flag = 1
      break 
    else:
        file2.write(line)
          
# checking condition for string found or not
if flag == 0: 
   print('String', string1 , 'Not Found') 
else: 
   print('String', string1, 'Found In Line', index)


  
# closing text file    
file1.close() 
file2.close() 