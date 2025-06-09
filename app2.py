from datetime import datetime, timedelta
from xero_python.accounting import AccountingApi


from xero_python.accounting import AccountingApi, BankTransaction, Contact, LineItem, Account


from datetime import date
from xero_python.accounting import BankTransactions
"""

Sort of auto-reconcile a bank transaction:

bank_transaction = BankTransaction(
    type="SPEND",
    contact=Contact(
        name="SMART Agency"
    ),
    line_items=[
        LineItem(
            description="Payment to SMART Agency 2",
            quantity=1,
            unit_amount=4500.00,
            account_code="400"
        )
    ],
    bank_account=Account(
        code="090"
    ),
    date=date(2025, 5, 30),
    reference="0195 0210"
)

response = accounting_api.create_bank_transactions(
    xero_tenant_id=xero_tenant_id,
    bank_transactions=BankTransactions(bank_transactions=[bank_transaction])
)

accounting_api.get_bank_transactions(xero_tenant_id, where='Total=4500 && status!="DELETED"').bank_transactions[1]

"""


def find_matching_bank_transaction(xero_tenant_id, api_client):
    """
    Search for bank transactions matching specific amount and date.
    Returns a tuple of (matches, error_message)
    """
    accounting_api = AccountingApi(api_client)

    # Search criteria
    target_date = datetime(2025, 5, 30)
    target_amount = 4500.00

    # Allow for some flexibility in amount (±1%)
    min_amount = target_amount * 0.99
    max_amount = target_amount * 1.01

    try:
        # Query Xero API for unreconciled transactions
        transactions = accounting_api.get_bank_transactions(
            xero_tenant_id,
            where="IsReconciled==false",
            # where="Status==\"AUTHORISED\" AND IsReconciled==false",
            order="Date DESC"
        )

        print("Found transactionsc count:", len(transactions.bank_transactions))
        print("Found transactions:", transactions.to_dict())

        # Format matches
        matches = []
        for tx in transactions.bank_transactions:
            assert not tx.is_reconciled
            if tx.type != 'SPEND' or tx.status == 'DELETED':
                print('skipping', tx.type)
                continue
            matches.append({
                'contact_id': tx.contact.contact_id,
                'contact_name': tx.contact.name,
                'bank_transaction_id': tx.bank_transaction_id,
                'total': tx.total,
                'reference': tx.reference,
                'status': tx.status,
                'type': tx.type,
                'date': tx.date.isoformat(),
                'is_reconciled': tx.is_reconciled,
            })
            # matches.append({
            #     'transaction_id': tx.bank_transaction_id,
            #     'date': tx.date.strftime('%Y-%m-%d') if tx.date else 'N/A',
            #     'amount': float(tx.total) if tx.total else 0,
            #     'contact_name': tx.contact.contact_name if tx.contact and tx.contact.contact_name else 'No Contact',
            #     'reference': tx.reference if tx.reference else 'No Reference',
            #     'is_reconciled': tx.is_reconciled if hasattr(tx, 'is_reconciled') else False
            # })

        print('num matches', len(matches))
        import ipdb; ipdb.set_trace()

        return matches, None

    except Exception as e:
        print(f"Error details: {str(e)}")
        return None, f"Unexpected error: {str(e)}"
