#!/usr/bin/env python3
"""
calculate_mttr.py: Compute Mean Time To Respond (MTTR) from incidents CSV.
"""
import argparse
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute MTTR from incidents CSV."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to incidents CSV with columns 'detection_time' and 'resolution_time'."
    )
    parser.add_argument(
        "--output", required=False,
        help="Optional path to save CSV with added 'mttr_hours' column."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    # Load data with parsed dates
    df = pd.read_csv(
        args.input,
        parse_dates=["detection_time", "resolution_time"]
    )

    # Calculate MTTR in hours
    df["mttr_hours"] = (
        df["resolution_time"] - df["detection_time"]
    ).dt.total_seconds() / 3600.0

    # Compute and print mean MTTR
    mean_mttr = df["mttr_hours"].mean()
    print(f"Mean Time To Respond (hours): {mean_mttr:.2f}")

    # Save extended CSV if requested
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"Extended CSV with MTTR saved to {args.output}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# Compute MTTR
