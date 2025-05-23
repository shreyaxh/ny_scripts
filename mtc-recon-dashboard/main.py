import uuid
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, Query
import pandas as pd
import psycopg2
import io
import os

app = FastAPI()


DB_CONFIG = {
    "dbname": "atlas_dev",
    "user": "shreyash",
    "password": None,
    'host': 'host.docker.internal',
    "port": 5434
}
BAP_ID = "19dded4d-51dd-4dcd-a07d-d353649d8595"


@app.post("/reconcile/")
def reconcile(
    file: UploadFile = File(...),
    start_date: str = Query(..., description="YYYY-MM-DD"),
    end_date: str = Query(..., description="YYYY-MM-DD")
):
    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor()

    query = """
    SELECT 
        b.id as booking_id,
        b.provider_name,
        b.search_id,
        b.refund_amount,
        po.id as payment_order_id,
        po.payment_service_order_id,
        po.amount
    FROM 
        atlas_app.frfs_ticket_booking b
    JOIN 
        atlas_app.frfs_ticket_booking_payment bp ON b.id = bp.frfs_ticket_booking_id
    JOIN 
        atlas_app.payment_order po ON bp.payment_order_id = po.id
    WHERE 
        bp.status = 'SUCCESS' AND b.created_at BETWEEN %s AND %s
    """
    cursor.execute(query, (start_date, end_date))
    db_results = cursor.fetchall()

    csv_content = file.file.read()
    csv_df = pd.read_csv(io.StringIO(csv_content.decode("utf-8")))

    summary = {"SETTLED": 0, "PENDING": 0, "MISMATCH": 0}

    for row in db_results:
        booking_id, provider_name, search_id, refund_amount, payment_order_id, settlement_id, actual_amount = row
        settlement_amount = float(actual_amount) - float(refund_amount or 0)

        csv_match = csv_df[csv_df['Settlement Id'] == settlement_id]

        if csv_match.empty:
            status = "PENDING"
        else:
            csv_status = csv_match.iloc[0]["Transaction Status"]
            status = "SETTLED" if csv_status.lower() == "success" else "MISMATCH"

        summary[status] += 1

        insert_query = """
        INSERT INTO atlas_app.settlement (
            id, order_id, bap_id, ticket_provider, transaction_id,
            actual_amount, settlement_amount, difference_amount,
            status, created_at, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
        ON CONFLICT (order_id) DO NOTHING
        """
        cursor.execute(insert_query, (
            str(uuid.uuid4()),
            booking_id,
            BAP_ID,
            provider_name,
            search_id,
            str(actual_amount),
            str(settlement_amount),
            str(refund_amount or 0),
            status
        ))

    db_settlement_ids = set(row[5] for row in db_results)

    for _, row in csv_df.iterrows():
        csv_settlement_id = row['Settlement Id']
        if csv_settlement_id not in db_settlement_ids:
            summary["MISMATCH"] += 1

            # Optional: insert a minimal settlement record
            insert_query = """
            INSERT INTO atlas_app.settlement (
                id, order_id, bap_id, ticket_provider, transaction_id,
                actual_amount, settlement_amount, difference_amount,
                status, created_at, updated_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
            ON CONFLICT DO NOTHING
            """
            cursor.execute(insert_query, (
                str(uuid.uuid4()),
                None,
                BAP_ID,
                "UNKNOWN",
                row.get("Transaction Id", "UNKNOWN"),
                row.get("amount", "0"),
                row.get("Settlement Amount", "0"),
                "0",
                "MISMATCH"
            ))

    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Reconciliation complete", "summary": summary}
