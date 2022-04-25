import csv
import random
import string


number_of_data = 1000000
length_of_idn = 9

# use set to prevent dulicated data
idns_set = set()
while len(idns_set) < number_of_data:
        new_idn = random.choice(string.ascii_uppercase)+''.join(random.choice(string.digits) for _ in range(length_of_idn))
        idns_set.add(new_idn)

with open('test_set.csv', 'w', encoding='utf-8', newline='') as csvfile:
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    for seq, idn in enumerate(idns_set):
            writer.writerow([seq, idn, "20220419"])



# faster and easier, but there may be duplicates
# with open('test_normal.csv', 'w', encoding='utf-8', newline='') as csvfile:
#     writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
#     for seq in range(number_of_data):
#         idn = random.choice(string.ascii_uppercase)+''.join(random.choice(string.digits) for _ in range(length_of_idn))
#         writer.writerow([seq, idn])