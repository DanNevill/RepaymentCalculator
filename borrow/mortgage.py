#!/usr/bin/env python3
from datetime import date, datetime
from dateutil.rrule import rrule, MONTHLY, YEARLY
from dateutil.relativedelta import relativedelta
from typing import Tuple
from borrow.common import *

class mortgage(object):

    def __init__(self, rate: str, duration: int, repayment: Numeric, overpay: NumStr, downpayment: NumStr):
        self.amount      = "Unknown"
        self.rate        = rate
        self.repayment   = repayment
        self.overpay     = overpay
        self.duration    = duration
        self.downpayment = downpayment
        self.start       = "N/A"


    # What to display when the
    # mortgage class is printed
    #
    def __str__(self) -> str:

        # Determine how to draw downpay as
        # a string. If it's a string then
        # it must be a percentage so also
        # print a percent sign afterwards
        #
        (sign, downpayment) = sign_magnitude(self.downpayment)

        if type(downpayment) is not str:
            (sign, downpayment) = signed_float_to_string(sign, downpayment)
            percent = " "
        else:
            sign = "-" if sign < 0 else " "
            downpayment = "{0:.2f}".format(float(downpayment[:-1]))
            percent = "%"

        # Pad everything to 10 chars
        #
        return ("""


+======  COMMENCING MORTGAGE DETAILS  =======+
        
    Amount     :  £{0:10.2f}
    Downpayment: {1}£{2:>10}{3}
    Repayment  :  £{4:10.2f}  per month
    Overpayment:   {5:10.2f}% per year
    Interest   :   {6:10.2f}% for {7} years

+==========  Commencing:  {8}  ==========+
""".format(self.amount,
           sign,
           downpayment,
           percent,
           self.repayment,
           self.overpay * 100,
           self.rate * 100,
           self.duration,
           self.start.strftime("%b '%y")))


    def repayment_duration(self) -> datetime:

        """Iterator of payment dates during the
        mortgage term.

        Arguments:
          - None.

        Return:
          - datetime: Next mortgage payment date.

        Details:
        Uses relativedelta and rrule to provide
        monthly payment dates starting from a
        month after the mortgage term starts for
        the specified number of years."""


        # Iterator: for the duration
        # of the term of the mortgage
        # return a payment date object
        #
        end   = self.start + relativedelta(years=self.duration)
        start = self.start + relativedelta(months=1)
        for current in rrule(freq=MONTHLY, dtstart=start, until=end):
            yield current


    def repay(self, outstanding: Numeric, start: datetime) -> Tuple[Numeric, Numeric, datetime]:

        """Make repayments from the start date for
        the duration of the mortgage term.

        Arguments:
          - outstanding (Numeric): Amount owed.
          - start (datetime): Date repayments start.

        Return:
          - Tuple:
            - Numeric: Amount of interest accrued
            during the mortgage term.
            - Numeric: Amount repaid during the
            mortgage term.
            - datetime: Mortgage repayment end date.

        Details:
        For each repayment date from the start date
        for the duration of the term or until the
        amount owed is paid in full, taking into
        account both downpayments and overpayment
        associated with the mortgage. Determines
        the amount owed at each repayment stage of
        the term and the total amount repaid and
        accrued in interest.
        """


        self.start  = start
        self.amount = outstanding
        interests   = 0
        repayments  = 0

        # Determine downpayment and
        # substract from the outstanding
        # amount upfront to avoid interest
        # being added to it.
        #
        # NOTE: Downpayment can be negative
        #       in the case where equity is
        #       released upon remortaging
        #
        downpayment  = self.calculate_downpayment(outstanding)
        outstanding -= downpayment 

        # Print mortgage details
        #
        print(self)

        # If downpayment exists then
        # determine how to print it
        # and do so
        #
        if (downpayment):
            (sign, dpayment) = sign_magnitude(downpayment)
            (sign, dpayment) = signed_float_to_string(sign, dpayment)

            print("""---   Downpayment({0}): {1}£{2:>10}   ---
                  """.format(start.strftime("%b '%y"), sign, dpayment))

        # For durartion
        # of the mortgage
        #
        for date in self.repayment_duration():

            # Add on monthly interest
            #
            interest     = self.calculate_interest(outstanding)
            interests   += interest
            outstanding += interest

            # While amount outstanding
            # update remaining and paid 
            #
            if (outstanding > 0):
                repayment    = self.calculate_repayment(date, outstanding)
                repayments  += repayment
                outstanding -= repayment
            else:
                break

        return (interests, repayments + downpayment, date)


    def calculate_downpayment(self, outstanding: Numeric) -> Numeric:

        """Calculates downpayment amount at the beginning
        of the mortgage term.

        Arguments:
          - outstanding (Numeric): Amount owed.

        Return:
          - Numeric: Amount paid upfront, before the 
          mortgage term begins.

        Details:
        Downpayment can be negative which indicates that
        the downpayment amount is paid to the customer
        in event of capital release at beginning of term."""


        (sign, magnitude) = sign_magnitude(self.downpayment)

        # Determine magnitude of amount if
        # the initial is a percentage
        #
        if ((type(magnitude) is str) and (magnitude[-1] == '%')):
            magnitude = sanitize_percent(magnitude) * float(outstanding)

        # Factor in sign of the payment
        # from earlier
        #
        return (magnitude * sign)



    def calculate_repayment(self, date: datetime, outstanding: Numeric) -> Numeric:

        """Calculates repayment associated with
        amount owed.

        Arguments:
          - date (datetime): Date of repayment.
          - outstanding (Numeric): Amount owed.

        Return:
          - Numeric: Amount to repay at date.

        Details:
        Ensures only amount owed is paid. Prints
        outstanding amout. Repayments also take
        into account overpayments."""


        # Calculate standard monthly
        # repayment based on amount
        # remaining or monthly amount
        #
        repayment = self.repayment if (outstanding > self.repayment) else outstanding

        print("      {0} - Outstanding: £{1:10.2f}".format(date.strftime("%b '%y"), 
                                                           (outstanding - repayment)))

        # If overpay specified
        # then calculate the amount
        #
        if self.overpay:
            repayment += self.calculate_overpay(date, outstanding - repayment)
            
        return repayment


    def calculate_overpay(self, date: datetime, outstanding: Numeric) -> Numeric:

        """Calculates amount to overpay based on
        amount owed.

        Arguments:
          - date (datetime): Current payment date.
          - outstanding (Numeric): Amount owed.

        Return:
          - Numeric: Amount of interest accumulated.

        Details:
        Uses relativedelta in order to determine
        overpayment dates in a yearly cadence from
        the initial mortgage date."""


        lump = 0

        # Calculate the first anniversary of
        # the mortgage to start the overpay
        #
        first = self.start + relativedelta(years=1)

        # Foreach year anniversary
        # of the mortgage calculate
        # the amount to overpay by
        #
        if (date in [ d for d in rrule(freq=YEARLY, dtstart=first, count=(self.duration-1))]):

            # Repay lump sum off
            # the oustanding amount
            #
            lump = outstanding * self.overpay
            lump = lump if (outstanding > lump) else outstanding

            # Print overpayment to 2 d.p.
            #
            print("""
---   Overpayment ({0}): £{1:10.2f}   ---
            """.format(date.strftime("%b '%y"), lump))

        return lump


    def calculate_interest(self, outstanding: Numeric) -> Numeric:

        """Calculates interest associated with
        amount owed.

        Arguments:
          - outstanding (Numeric): Amount owed.

        Return:
          - Numeric: Amount of interest accumulated."""


        # calculate monthly interest
        #
        return outstanding * (self.rate/12)

