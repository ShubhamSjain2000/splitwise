from enum import Enum
from typing import Dict, List

from sqlalchemy import Float

from app import db
from app.models.user import User


class Percent(object):

    def __init__(self, distribution):
        self.distribution = distribution

    distribution: Dict[str, float]

    def validate(distribution):

        if float(sum(distribution.values())) != 100:
            raise Exception("Incorrect distribution")

    @classmethod
    def get_distribution(cls, distribution, total_amount):
        cls.validate(distribution)
        return dict(
            (int(key), value * total_amount) for key, value in distribution.items()
        )


class Split(object):

    def __init__(self, distribution):
        self.distribution = distribution

    @classmethod
    def get_distribution(cls, distribution, total_amount):
        per_split = round(total_amount / sum(distribution.values()), 2)
        return dict(
            (int(key), value * per_split) for key, value in distribution.items()
        )


class Exact(object):

    def __init__(self, distribution):
        self.distribution = distribution

    distribution: Dict[str, float]

    def validate(distribution, total_amount):
        if sum(distribution.values()) != total_amount:
            raise Exception("Invalid distribution")

    @classmethod
    def get_distribution(cls, distribution, total_amount):
        cls.validate(distribution, total_amount)
        return dict((int(key), value) for key, value in distribution.items())


class Equal(object):

    def __init__(self, distribution):
        self.distribution = distribution

    @classmethod
    def get_distribution(cls, distribution, total_amount):
        splits = round(total_amount / len(distribution), 2)
        distribution_dict = {}
        for i in distribution:
            distribution_dict[int(i)] = splits
        if splits * len(distribution) != total_amount:
            first_payee = int(distribution[0])
            distribution_dict[first_payee] += total_amount - (
                splits * len(distribution)
            )
        return distribution_dict


class SplitType(Enum):

    EXACT = Exact
    PERCENT = Percent
    EQUAL = Equal
    SPLIT = Split


class Expense(db.Model):

    expense_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    note = db.Column(db.String(500))
    total_amount = db.Column(
        Float(precision=2, asdecimal=True), nullable=False)
    split_type = db.Column(db.String(128), nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)

    def get_split_amount(self, distribution):
        split_type = self.split_type
        split_amounts = SplitType[split_type].value.get_distribution(
            distribution, self.total_amount
        )
        return split_amounts


class Share(db.Model):

    share_id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(
        db.Integer, db.ForeignKey("expense.expense_id"), nullable=False
    )
    debtor_id = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)
    amount = db.Column(Float(precision=2, asdecimal=True), nullable=False)


class Balance(db.Model):

    balance_id = db.Column(db.Integer, primary_key=True)
    owed_by = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)
    owed_to = db.Column(db.Integer, db.ForeignKey(
        "user.user_id"), nullable=False)
    amount = db.Column(Float(precision=2, asdecimal=True), nullable=False)
