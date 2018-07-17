from sqlite3 import connect
from datetime import datetime

dbFile = 'sakila211.db'
conn = connect(dbFile)
c = conn.cursor()

'''
    Print a summary of monthly activity for a customer for the month specified.
    If it was returned that month, it will only show the return date and if it was late.
    If it was only checked out that month, it will only show the check out date. If it was returned late, 
    it will show on the month it was returned late and the fee will be calculated for that month
    Args: Last name, month, year.
    Effects: Prints a monthly report for rentals.
'''
def sakila_report(last, month, year):
    # Display header for report.
    print_header(last)
    month, year = str(month), str(year)
    
    # Display month with single digits in the format 01, 02, 03, etc...
    if len(month) < 2:
        month = '0' + month
    query = 'select title, rental_date, return_date, rental_rate, rental_duration from rental join customer using (customer_id) \
    join inventory using (inventory_id) join film using (film_id) where last_name = ? order by rental_date'
    cur = c.execute(query, (last,))
    
    # Fetchall gets a list of the results. 
    rentals = cur.fetchall()
    total = 0
    for rental in rentals:
        date_format = "%Y-%m-%d %H:%M:%S.%f"
        title = rental[0]
        rental_date, return_date = rental[1], rental[2]
        rate = rental[3]
        rental_dur = rental[4]
       
        chk_rental_yr, chk_rental_mo = rental_date[0:4],  rental_date[5:7]
        
        # If the rental has or has not been returned.
        if return_date == None:
            return_date = 'not returned'
        else:
            chk_return_yr, chk_return_mo = return_date[0:4], return_date[5:7]
            returned = datetime.strptime(return_date, date_format)
        
        # Format the rental date.
        rented = datetime.strptime(rental_date, date_format)
        
        # late_fee is a bool. True if late fee exists, False otherwise.
        late_fee = calc_fee(rented, returned, rental_dur)

        # If rental year, return year, rental month, return month == user selection.
        if chk_rental_yr == year and chk_return_yr == year and chk_rental_mo == month and chk_return_mo == month:
            total += rate
            print(title.ljust(20),'Checked Out:'.ljust(20), '{}'.format(rented).ljust(32), '$' + str(rate))
            
            if late_fee == True:
                total += rate
                print(''.ljust(20), 'Returned:'.ljust(20), returned, '**Late Fee**', '$' + str(rate) + '\n')
            else:
                print(''.ljust(20), 'Returned:'.ljust(20), returned, '\n')

        # If the rental year, return year, rental month == user selection. Return month != user selection. Or the rental hasn't been returned yet.
        # Since the rental hasn't been returned this month or at all there are no late fees on this montly report.
        elif chk_rental_yr == year and chk_return_yr == year and chk_rental_mo == month and chk_return_mo != month or return_date == 'not returned':
            total += rate
            print(title.ljust(20),'Checked Out:'.ljust(20), '{}'.format(rented).ljust(32), '$' + str(rate) + '\n')

        # If rental year, return year, return month == user selection but rental month != user selection.
        # Only the return is shown on this montly statement.
        elif chk_rental_yr == year and chk_return_yr == year and chk_rental_mo != month and chk_return_mo == month:
            
            if late_fee == True:
                total += rate
                print(title.ljust(20), 'Returned:'.ljust(20), returned, '**Late Fee**', '$' + str(rate) + '\n')
            else:
                print(title.ljust(20), 'Returned:'.ljust(20), returned, '\n')
    
    total = str(round(total, 2))
    print('Monthly Total:', '$' + total)

'''
    A helper function to see if there is a late fee.
    Args: Dated rented, dated returned, and the duration of the rental.
    Returns: True if there is a late fee, or False if there isn't.
'''
def calc_fee(rented, returned, rental_dur):
    diff = returned - rented 
    if diff.days > rental_dur:
        return True
    else:
        return False

'''
    Finds first name and prints a display header.
    Args: Last name.
    Effects: Prints rental display.
'''
def print_header(last):
    query = 'select first_name from customer where last_name = ?'
    cur = c.execute(query, (last,))
    first = cur.fetchone()
    print('--- Sakila DVD Rentals ---\n')
    if first != None:
        print('Monthly Report for', first[0], last, '\n')


if __name__ == "__main__":
    sakila_report('Black', 6, 2005)

