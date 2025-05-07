#!/usr/bin/env python3
import os
import glob
import pandas as pd

# Mapping of buyer_app_id to buyer_name
BUYER_NAME_MAP = {
    'api.beckn.juspay.in/bap/frfs/4b17bd06-ae7e-48e9-85bf-282fb310209c': 'Namma Yatri',
    'gateway.rapido.bike': 'Rapido',
    'rb-ondc-metro.redbus.in': 'RedBus'
}


def process_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates ticket quantities by booking_date and buyer_name
    from a single DataFrame containing all records.
    """
    # Ensure necessary columns exist
    required_cols = ['ticket_qty', 'booking_status', 'booking_date', 'buyer_app_id']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise KeyError(f"Missing columns in input DataFrame: {', '.join(missing)}")

    # Create buyer_name from mapping (default to empty string)
    df['buyer_name'] = df['buyer_app_id'].map(BUYER_NAME_MAP).fillna('')

    # Convert ticket_qty to numeric
    df['ticket_qty'] = pd.to_numeric(df['ticket_qty'], errors='coerce').fillna(0).astype(int)

    # Normalize booking_date to YYYY-MM-DD
    df['booking_date'] = pd.to_datetime(df['booking_date']).dt.strftime('%Y-%m-%d')

    # Define aggregation functions
    def agg_fn(group: pd.DataFrame) -> pd.Series:
        total = group['ticket_qty'].sum()
        success = group.loc[group['booking_status'] == 'BOOKED', 'ticket_qty'].sum()
        refunded = group.loc[group['booking_status'] == 'CANCELLED', 'ticket_qty'].sum()
        failed = group.loc[~group['booking_status'].isin(['BOOKED', 'CANCELLED']), 'ticket_qty'].sum()
        return pd.Series({
            'Total_Transactions': total,
            'Successful_Transactions': success,
            'Failed_Transactions': failed,
            'Refunded_Transactions': refunded
        })

    # Group by date and buyer_name
    result = (
        df.groupby(['booking_date', 'buyer_name'])
          .apply(agg_fn)
          .reset_index()
          .rename(columns={'booking_date': 'date'})
    )

    # Reorder columns for output
    result = result[['date', 'buyer_name', 'Total_Transactions',
                     'Successful_Transactions', 'Failed_Transactions', 'Refunded_Transactions']]
    return result


def main():
    # Find .xlsx files in current directory; use the first found
    files = glob.glob(os.path.join(os.getcwd(), '*.xlsx'))
    if not files:
        print("No .xlsx files found in current directory.")
        return

    input_file = files[0]
    print(f"Reading input from {input_file}...")
    df_all = pd.read_excel(input_file, engine='openpyxl')

    try:
        combined = process_dataframe(df_all)
    except Exception as e:
        print(f"Error processing data: {e}")
        return

    # Write combined CSV
    output_file = 'CMRL_ticket_sales.csv'
    combined.to_csv(output_file, index=False)
    print(f"Combined output written to {output_file}")


if __name__ == '__main__':
    main()
