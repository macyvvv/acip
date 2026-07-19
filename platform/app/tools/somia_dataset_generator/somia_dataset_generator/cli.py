from pathlib import Path
import argparse
from .run import make_plan, generate
from .exporter import export_run
from .validation import validate_character

def main():
    parser = argparse.ArgumentParser(prog="somia-dataset")
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan")
    p_plan.add_argument("--character", required=True)
    p_plan.add_argument("--count", type=int, required=True)
    p_plan.add_argument("--runs", default="runs")

    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--character", required=True)
    p_gen.add_argument("--count", type=int, required=True)
    p_gen.add_argument("--runs", default="runs")
    p_gen.add_argument("--dry-run", action="store_true")

    p_val = sub.add_parser("validate")
    p_val.add_argument("--character", required=True)

    p_exp = sub.add_parser("export")
    p_exp.add_argument("--run-id", required=True)
    p_exp.add_argument("--runs", default="runs")

    args = parser.parse_args()
    if args.command == "validate":
        validate_character(Path("specs/characters") / f"{args.character}.yaml")
        print(f"valid: {args.character}")
    elif args.command == "plan":
        run_id, _, _ = make_plan(args.character, args.count, Path(args.runs))
        print(run_id)
    elif args.command == "generate":
        print(generate(args.character, args.count, Path(args.runs), dry_run=args.dry_run))
    else:
        print(export_run(Path(args.runs) / args.run_id))
