from bs4 import BeautifulSoup
import re
import os
import csv
import unittest

def get_listings_from_search_results(html_file):
    """
    [
        ('Title of Listing 1', 'Number of Reviews 1', 'Listing ID 1'),  # format
        ('Loft in Mission District', 422, '1944564'),  # example
    ]
    """
    tup_list = []

    """id pattern"""
    z = '.([0-9]+)'

    """review pattern"""
    y = '\W\s([0-9]+)'


    html = open(html_file, "r", encoding="utf-8-sig")
    text = html.read()
    html.close()
    soup = BeautifulSoup(text, 'html.parser')
    listings = soup.find_all('div', class_='g1qv1ctd')

    for listing in listings:
        tup = ()

        title = listing.find('div', class_="t1jojoys")
        name = title.text
        rough_id = title.get('id')
        id = re.findall(z, rough_id)

        rating = listing.find('span', class_="t5eq1io")
        rough_review = rating.get('aria-label')
        review = re.findall(y, rough_review)
        if len(review) == 0:
            review.append(0)
        
        tup = (name, int(review[0]), id[0])
        tup_list.append(tup)

    return tup_list


def get_listing_information(listing_id):
    """
    (
        policy number,
        place type,
        nightly rate
    )
    """
    z = '.([0-9]+)'

    file_name = "html_files/listing_" + listing_id + ".html"
    html = open(file_name, "r", encoding="utf-8-sig")
    text = html.read()
    html.close()
    soup = BeautifulSoup(text, 'html.parser')

    policy_tag = soup.find('li', class_="f19phm7j")
    policy_number = policy_tag.find('span').text
    if "STR" in policy_number:
        policy_number = policy_number
    elif policy_number == "pending":
        policy_number = "Pending"
    elif policy_number == "exempt":
        policy_number = "Exempt"
    else:
        policy_number = "Invalid"

    listing_subtitle_tag = soup.find('h2', class_="_14i3z6h").text
    if "private" in listing_subtitle_tag or "Private" in listing_subtitle_tag:
        place_type = "Private Room"
    elif "shared" in listing_subtitle_tag or "Shared" in listing_subtitle_tag:
        place_type = "Shared Room"
    else:
        place_type = "Entire Room"

    price_tag = soup.find('div', class_="_1jo4hgw")
    price = price_tag.find('span', class_="_tyxjp1").text
    price = re.findall(z, price)
    
    tup = (policy_number, place_type, int(price[0]))
    return tup


def get_detailed_listing_database(html_file):
    """
    [
        (Listing Title 1,Number of Reviews 1,Listing ID 1,Policy Number 1,Place Type 1,Nightly Rate 1),
        (Listing Title 2,Number of Reviews 2,Listing ID 2,Policy Number 2,Place Type 2,Nightly Rate 2),
        ...
    ]
    """
    final_list = []

    search_list = get_listings_from_search_results(html_file)

    for listing in search_list:
        final_tup = ()
        info_tup = get_listing_information(listing[2])
        final_tup = (listing[0], listing[1], listing[2], info_tup[0], info_tup[1], info_tup[2])
        final_list.append(final_tup)

    return final_list


def write_csv(data, filename):
    """
    Listing Title,Number of Reviews,Listing ID,Policy Number,Place Type,Nightly Rate
    title1,num_reviews1,id1,policy_number1,place_type1,cost1
    title2,num_reviews2,id2,policy_number2,place_type2,cost2
    title3,num_reviews3,id3,policy_number3,place_type3,cost3
    ....
    """
    data.sort(key=lambda x: x[5])

    f = open(filename, "w", newline='')
    writer = csv.writer(f)
    f.write("Listing Title,Number of Reviews,Listing ID,Policy Number,Place Type,Nightly Rate\n")

    for row in data:
        writer.writerow(row)
    
    f.close()
    pass


def check_policy_numbers(data):
    """
    [
        listing id 1,
        listing id 2,
        ...
    ]

    """
    not_matching = []
    z = '[2][0][0-9][0-9].[0][0][0-9][0-9][0-9][0-9][S][T][R]'
    y = '[S][T][R].[0][0][0][0-9][0-9][0-9][0-9]'

    for tup in data:
        check_one = re.findall(z, tup[3])
        check_two = re.findall(y, tup[3])

        if len(check_one) == 0 and len(check_two) == 0 and tup[3] != "Pending" and tup[3] != "Exempt":
            not_matching.append(tup[2])
    
    return not_matching

class TestCases(unittest.TestCase):

    def test_get_listings_from_search_results(self):
        # call get_listings_from_search_results("html_files/search_results.html")
        # and save to a local variable
        listings = get_listings_from_search_results("html_files/search_results.html")
        # check that the number of listings extracted is correct (18 listings)
        self.assertEqual(len(listings), 18)
        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(listings), list)
        # check that each item in the list is a tuple
        for listing in listings:
            self.assertEqual(type(listing), tuple)
        # check that the first title, number of reviews, and listing id tuple is correct (open the search results html and find it)
        self.assertEqual(listings[0][0], 'Loft in Mission District')
        self.assertEqual(listings[0][1], 422)
        self.assertEqual(listings[0][2], '1944564')
        # check that the last title is correct (open the search results html and find it)
        self.assertEqual(listings[len(listings) - 1][0], 'Guest suite in Mission District')
        pass

    def test_get_listing_information(self):
        html_list = ["467507",
                     "1944564",
                     "4614763",
                     "16204265",
                     "47705504"]
        # call get_listing_information for i in html_list:
        listing_informations = [get_listing_information(id) for id in html_list]
        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_informations), 5)
        for listing_information in listing_informations:
            # check that each item in the list is a tuple
            self.assertEqual(type(listing_information), tuple)
            # check that each tuple has 3 elements
            self.assertEqual(len(listing_information), 3)
            # check that the first two elements in the tuple are string
            self.assertEqual(type(listing_information[0]), str)
            self.assertEqual(type(listing_information[1]), str)
            # check that the third element in the tuple is an int
            self.assertEqual(type(listing_information[2]), int)
        # check that the first listing in the html_list has the correct policy number
        listing_information = get_listing_information(html_list[0])
        self.assertEqual(listing_information[0], "STR-0005349")
        # check that the last listing in the html_list has the correct place type
        listing_information = get_listing_information(html_list[4])
        self.assertEqual(listing_information[1], "Entire Room")
        # check that the third listing has the correct cost
        listing_information = get_listing_information(html_list[2])
        self.assertEqual(listing_information[2], 165)
        pass

    def test_get_detailed_listing_database(self):
        # call get_detailed_listing_database on "html_files/search_results.html"
        # and save it to a variable
        detailed_database = get_detailed_listing_database("html_files/search_results.html")
        # check that we have the right number of listings (18)
        self.assertEqual(len(detailed_database), 18)
        for item in detailed_database:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item), tuple)
            # check that each tuple has a length of 6
            self.assertEqual(len(item), 6)

        # check that the first tuple is made up of the following:
        # 'Loft in Mission District', 422, '1944564', '2022-004088STR', 'Entire Room', 181
        self.assertEqual(detailed_database[0][0], "Loft in Mission District")
        self.assertEqual(detailed_database[0][1], 422)
        self.assertEqual(detailed_database[0][2], "1944564")
        self.assertEqual(detailed_database[0][3], "2022-004088STR")
        self.assertEqual(detailed_database[0][4], "Entire Room")
        self.assertEqual(detailed_database[0][5], 181)

        # check that the last tuple is made up of the following:
        # 'Guest suite in Mission District', 324, '467507', 'STR-0005349', 'Entire Room', 165
        self.assertEqual(detailed_database[len(detailed_database) - 1][0], "Guest suite in Mission District")
        self.assertEqual(detailed_database[len(detailed_database) - 1][1], 324)
        self.assertEqual(detailed_database[len(detailed_database) - 1][2], "467507")
        self.assertEqual(detailed_database[len(detailed_database) - 1][3], "STR-0005349")
        self.assertEqual(detailed_database[len(detailed_database) - 1][4], "Entire Room")
        self.assertEqual(detailed_database[len(detailed_database) - 1][5], 165)
        pass

    def test_write_csv(self):
        # call get_detailed_listing_database on "html_files/search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/search_results.html")
        # call write csv on the variable you saved
        write_csv(detailed_database, "test.csv")
        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        # check that there are 19 lines in the csv
        self.assertEqual(len(csv_lines), 19)
        # check that the header row is correct
        self.assertEqual(csv_lines[0][0], "Listing Title")
        self.assertEqual(csv_lines[0][1], "Number of Reviews")
        self.assertEqual(csv_lines[0][2], "Listing ID")
        self.assertEqual(csv_lines[0][3], "Policy Number")
        self.assertEqual(csv_lines[0][4], "Place Type")
        self.assertEqual(csv_lines[0][5], "Nightly Rate")
        # check that the next row is Private room in Mission District,198,23672181,STR-0002892,Private Room,109
        self.assertEqual(csv_lines[1][0], "Private room in Mission District")
        self.assertEqual(int(csv_lines[1][1]), 198)
        self.assertEqual(csv_lines[1][2], "23672181")
        self.assertEqual(csv_lines[1][3], "STR-0002892")
        self.assertEqual(csv_lines[1][4], "Private Room")
        self.assertEqual(int(csv_lines[1][5]), 109)
        # check that the last row is Guest suite in Mission District,70,50010586,STR-0004717,Entire Room,310
        self.assertEqual(csv_lines[len(csv_lines) - 1][0], "Guest suite in Mission District")
        self.assertEqual(int(csv_lines[len(csv_lines) - 1][1]), 70)
        self.assertEqual(csv_lines[len(csv_lines) - 1][2], "50010586")
        self.assertEqual(csv_lines[len(csv_lines) - 1][3], "STR-0004717")
        self.assertEqual(csv_lines[len(csv_lines) - 1][4], "Entire Room")
        self.assertEqual(int(csv_lines[len(csv_lines) - 1][5]), 310)
        pass

    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        # check that there is exactly one element in the string
        self.assertEqual(len(invalid_listings), 1)
        # check that the element in the list is a string
        self.assertEqual(type(invalid_listings[0]), str)
        # check that the first element in the list is '16204265'
        self.assertEqual(invalid_listings[0], "16204265")
        pass


if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    non_valid_airbnbs = check_policy_numbers(database)
    unittest.main(verbosity=2)
