#!/usr/bin/env python3
"""
calculate_mttd.py: Compute Mean Time To Detect (MTTD) from incidents CSV.
"""
import argparse
import pandas as pd


def parse_args():
    parser = argparse.ArgumentParser(
        description="Compute MTTD from incidents CSV."
    )
    parser.add_argument(
        "--input", required=True,
        help="Path to incidents CSV with columns 'occurrence_time' and 'detection_time'."
    )
    parser.add_argument(
        "--output", required=False,
        help="Optional path to save CSV with added 'mttd_hours' column."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    # Load data with parsed dates
    df = pd.read_csv(
        args.input,
        parse_dates=["occurrence_time", "detection_time"]
    )

    # Calculate MTTD in hours
    df["mttd_hours"] = (
        df["detection_time"] - df["occurrence_time"]
    ).dt.total_seconds() / 3600.0

    # Compute and print mean MTTD
    mean_mttd = df["mttd_hours"].mean()
    print(f"Mean Time To Detect (hours): {mean_mttd:.2f}")

    # Save extended CSV if requested
    if args.output:
        df.to_csv(args.output, index=False)
        print(f"Extended CSV with MTTD saved to {args.output}")


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
# Compute MTTD
