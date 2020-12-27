#!/usr/bin/env python3
import yaml
from borrow.common import *
from borrow.mortgage import mortgage
from datetime import date, datetime
from dateutil.rrule import rrule
from dateutil.relativedelta import relativedelta
from typing import List, NewType

Mortgage = NewType('Mortgage', mortgage)

class loan(object):

    def __init__(self, amount: Numeric, start: datetime, filename: str):
        self.amount      = amount
        self.outstanding = amount
        self.cost        = "Unknown"
        self.start       = start
        self.mortgages   = self.load_mortgages(filename)
        self.duration    = "N/A"


    # What to display when the
    # loan class is printed
    #
    def __str__(self) -> str:

        # Trim outstanding to 2 d.p.
        #
        (sign, outstanding) = sign_magnitude(self.outstanding)
        (sign, outstanding) = signed_float_to_string(sign, outstanding)

        # Pad everything to 10 chars
        #
        return ("""


+============================================+
|           LOAN REPAYMENT SUMMARY           |
+============================================+

    Total amount      :  £{0:10.2f}
    Amount outstanding: {1}£{2:>10}
    Loan cost to date :  £{3:10.2f}
    Loan commencement :  {4}
    Repayment duration:  {5:2} years {6:2} months

+============================================+

        """.format(self.amount,
                   sign,
                   outstanding,
                   self.cost,
                   self.start.strftime("%d %b  '%y"),
                   self.duration.years,
                   self.duration.months))


    def load_mortgages(self, filename: str) -> List[Mortgage]:

        """ Extract mortgage details from YAML file.

        Arguments:
          - filename (str): filename of file to construct
          mortgage objects from.

        Return:
          - List:
            - mortgage: Contains all mortage details.

        Details:
        Mortgage YAML is expected to take the following form:

        <unique_name>:
            rate: <decimal or string % float/int: Percentage e.g. 10% or 0.1.>
            years: <int: Number of years.>
            repayment: <int/float: Monthly repayment amount.>
            [downpayment: <int/float: Initial downpayment amount/percentage.
                          Can be negative in the case where remortgaging to
                          gain access to additional capitial.
                          Default is assumed to be a reduction in capital owed.
                          Examples: 6000, 600.00, -6%.>]
            [overpay:<float/int absolute or string %: Yearly overpay amount/
                     percentage which occurs on each mortgage anniversary
                     Default is no overpayment is performed
                     e.g. 10% or 1500.>]"""


        lm = []

        # Load in mortgage
        # details from file
        #
        with open(filename, 'r') as file:
            mortgages = yaml.safe_load(file)

        for m in mortgages.keys():

            # Extract required fields
            #
            rate      = sanitize_percent(mortgages[m]['rate'])
            years     = mortgages[m]['years']
            repayment = mortgages[m]['repayment']

            # Optional fields
            #
            if 'downpayment' in mortgages[m].keys():
                downpayment = mortgages[m]['downpayment']
            else:
                downpayment = 0.0

            # If overpay is specified
            # then extract the value
            #
            if 'overpay' in mortgages[m].keys():
                overpay = sanitize_percent(mortgages[m]['overpay'])
            else:
                overpay = 0.0

            # Add each mortgage
            #
            lm.append(mortgage(rate, years, repayment, overpay, downpayment))

        return lm



    def payoff(self) -> None:

        """ Execute payoff of the loan with the mortgages
        associated with the loan.

        Arguments:
          - None.

        Return:
          - None.

        Details:
        Iterate through associated mortgages in order
        paying off the outstanding balance whilst computing
        payments throughout the process and the cost of
        the loan."""


        start     = self.start
        self.cost = 0

        # Print header for repayment
        # First payment is in the
        # second month
        #
        paydate = start + relativedelta(months=1)
        paydatestr = paydate.strftime("%d %b '%y")

        print("""
+============================================+
|     LOAN REPAYMENT BEGINS ({0})     |
+============================================+""".format(paydatestr))

        # Foreach specified mortgage
        # pay off oustanding and update
        # metrics
        #
        while (self.mortgages):

            # Repay mortgages in order
            #
            m = self.mortgages.pop(0)
            (increase, decrease, current) = m.repay(self.outstanding, start)

            # Update outstanding capital,
            # interest paid, and end date
            #
            self.outstanding -= (decrease - increase)
            self.cost        += increase
            self.end          = current

            # Once paid off print
            # overall metrics
            #
            self.duration = relativedelta(self.end, self.start)
            
            # Stop repaying when
            # outstanding is zero
            #
            if not(self.outstanding > 0):
                break
            else:
                start = current

