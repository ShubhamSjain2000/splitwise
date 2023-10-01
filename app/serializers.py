from marshmallow import Schema, fields, validate
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from app import db
from app.models.split import Balance
from app.models.user import User


class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True
        sqla_session = db.session


class ExpenseSchema(Schema):
    name = fields.Str(required=True)
    total_amount = fields.Int(required=True)
    split_type = fields.Str(required=True)
    amount_dist = fields.Raw(validate=validate.OneOf([list, dict]))
    paid_by = fields.Int(required=True)


class BalanceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Balance
        load_instance = True
        sqla_session = db.session
