#!/usr/bin/env python3
import argparse
from datetime import *
from borrow.loan import *
from typing import Tuple


def parse_input() -> Tuple[int, datetime, str]:

    parser = argparse.ArgumentParser()

    parser.add_argument("-a", "--amount", 
                        type=int,
                        required=True,
                        help="Amount borrowed to repay back")

    parser.add_argument("-s", "--start_date", 
                        type=lambda s: datetime.strptime(s, '%d-%m-%Y'),
                        required=True,
                        help="Start date from which interest is acrued")

    parser.add_argument("-r", "--repayment_details", 
                        type=str,
                        required=True,
                        help="YAML file containing repayment details")

    args = parser.parse_args()

    return args


if __name__ == "__main__":

    args = parse_input()
    house = loan(args.amount, args.start_date, args.repayment_details)
    house.payoff()
    print(house)

