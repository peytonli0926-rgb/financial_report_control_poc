from __future__ import annotations

import argparse
from pathlib import Path

from engine.interbank_interest_mapper import MapperConfig, run_interbank_interest_mapping


def main() -> None:
    parser = argparse.ArgumentParser(description="将5-2-2-1风险明细AB列应计利息映射到5-2-1-1主表K列。")
    parser.add_argument("--principal", required=True, help="5-2-1-1存放同业明细母行文件")
    parser.add_argument("--risk", required=True, help="5-2-2-1存放同业风险明细文件")
    parser.add_argument("--output", required=True, help="输出Excel文件")
    parser.add_argument("--manual", default=None, help="人工核对文件，可选")
    parser.add_argument("--detail-dir", default=None, help="包含5-2-1-2到5-2-1-15明细文件的目录，可选")
    parser.add_argument("--mode", choices=["strict", "force_full"], default="strict", help="零本金有利息处理模式")
    args = parser.parse_args()

    detail_files = []
    if args.detail_dir:
        detail_dir = Path(args.detail_dir)
        detail_files = sorted(
            path
            for path in detail_dir.glob("5-2-1-*-1231*.xlsx")
            if not path.name.startswith("5-2-1-1-")
        )

    output_path = run_interbank_interest_mapping(
        principal_file=args.principal,
        risk_file=args.risk,
        manual_file=args.manual,
        detail_files=detail_files,
        output_file=args.output,
        config=MapperConfig(mapping_mode=args.mode),
    )
    print(f"已生成：{output_path}")


if __name__ == "__main__":
    main()
