membership_list = ['alston','nimisha','bejo','paul']

search_name = input("Enter the name to search: ")

if search_name in membership_list:
    print(f"{search_name} is a member.")
else:
    print(f"{search_name} is not a member.")