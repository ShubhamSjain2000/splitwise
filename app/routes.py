from decimal import Decimal

from flask import Response, jsonify, request
from sqlalchemy import or_

from app import app, db
from app.models.split import Balance, Expense, Share
from app.models.user import User
from app.serializers import BalanceSchema, ExpenseSchema, UserSchema


def update_balance(values, paid_by):
    
    for shared in values:
        if shared != paid_by:
            last_transaction = (
                db.session.query(Balance)
                .filter(Balance.owed_by == shared, Balance.owed_to == paid_by)
                .first()
            )
            if last_transaction:
                last_transaction.amount += Decimal(values[shared])
                continue
            last_transaction = (
                db.session.query(Balance)
                .filter(Balance.owed_by == paid_by, Balance.owed_to == shared)
                .first()
            )
            if last_transaction:
                if values[shared] > last_transaction.amount:
                    db.session.add(
                        Balance(
                            owed_to=paid_by,
                            owed_by=shared,
                            amount=values[shared] - last_transaction.amount,
                        )
                    )
                    db.session.delete(last_transaction)
                elif values[shared] < last_transaction.amount:
                    last_transaction.amount -= Decimal(values[shared])
                else:
                    db.session.delete(last_transaction)

            else:
                db.session.add(
                    Balance(owed_to=paid_by, owed_by=shared, amount=values[shared])
                )


@app.route("/health-check", methods=["GET"])
def health_check():
    response = {"message": "heathy"}
    return response


@app.route("/user/create", methods=["POST"])
def create_user():
    try:
        user_schema = UserSchema()
        user_data = request.json
        user = user_schema.load(user_data)
        db.session.add(user)
        db.session.commit()
        return {"message": "User created successfully"}

    except Exception as e:
        return Response(status=400, response="User creation failed , bad Input")


@app.route("/user/<user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user = User.query.get(int(user_id))
        user_schema = UserSchema()
        user = user_schema.dump(user)
        return user
    except Exception as e:
        return Response(status=404, response="Invalid user id")


@app.route("/users", methods=["GET"])
def get_users():
    try:
        user = User.query.all()
        user_schema = UserSchema()
        users = user_schema.dump(user, many=True)
        return users
    except Exception as e:
        return Response(status=400, response=" bad request")


@app.route("/pay-bill", methods=["POST"])
def pay_bill():
    try:
        data = request.json
        expense = ExpenseSchema()
        expense = expense.dump(data)
        distribution = expense.pop("amount_dist")
        expense = Expense(**expense)
        
        final_distribution = expense.get_split_amount(distribution)
        shares = []
        db.session.add(expense)
        db.session.commit()
        
        for each_dist in final_distribution:
            share = Share(
                expense_id=expense.expense_id,
                debtor_id=int(each_dist),
                amount=final_distribution[each_dist],
            )
            shares.append(share)
        update_balance(final_distribution, expense.paid_by)
        
        db.session.add_all(shares)
        db.session.commit()
        return Response(status=201, response="Created")
    except Exception as e:
        return Response(status=400, response="Invalid parameters")


@app.route("/get-expenses/<user_id>", methods=["GET"])
def get_expenses(user_id):
    try:
        expenses = []
        shares = db.session.query(Expense).filter(Expense.paid_by == user_id).all()
        for expense in shares:
            expenses.append({expense.name: expense.total_amount})
        return expenses
    except Exception as e:
        return Response(status=400, response="Invalid request")


@app.route("/get-balances", methods=["GET"])
def get_balances():
    try:
        response = []
        balances = Balance.query.all()
        for balance in balances:
            response.append({"owed_by": balance.owed_by, "owed_to": balance.owed_to, "amount": balance.amount})
        return response
    except Exception as e:
        return Response(status=400, response="Invalid request")


@app.route("/get-balance/<user_id>", methods=["GET"])
def get_balance(user_id):
    try:
        response = []
        balance_schema = BalanceSchema()
        balances = Balance.query.filter(
            or_(Balance.owed_by == user_id, Balance.owed_to == user_id)
        )
        for balance in balances:
            response.append({"owed_by": balance.owed_by, "owed_to": balance.owed_to, "amount": balance.amount})
        return response
    except Exception as e:
        return Response(status=400, response="No Records")
