from pathlib import Path
import argparse
from .run import make_plan, generate
from .exporter import export_run
from .paths import character_spec_path
from .validate_run import validate_run
from .validation import validate_character

def main():
    parser = argparse.ArgumentParser(prog="somia-dataset")
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan")
    p_plan.add_argument("--character", required=True)
    p_plan.add_argument("--count", type=int, required=True)
    p_plan.add_argument("--runs", default="runs")
    p_plan.add_argument("--seed", type=int, default=None)

    p_gen = sub.add_parser("generate")
    p_gen.add_argument("--character")
    p_gen.add_argument("--count", type=int)
    p_gen.add_argument("--runs", default="runs")
    p_gen.add_argument("--dry-run", action="store_true")
    p_gen.add_argument("--resume", metavar="RUN_ID", default=None)
    p_gen.add_argument("--seed", type=int, default=None)

    p_val = sub.add_parser("validate")
    p_val.add_argument("--character")
    p_val.add_argument("--run-id")
    p_val.add_argument("--runs", default="runs")

    p_exp = sub.add_parser("export")
    p_exp.add_argument("--run-id", required=True)
    p_exp.add_argument("--runs", default="runs")

    args = parser.parse_args()
    if args.command == "validate":
        if args.run_id:
            report = validate_run(Path(args.runs) / args.run_id)
            print(
                f"run {args.run_id}: {report['accepted']} accepted, {report['rejected']} rejected, "
                f"near_duplicate_groups={len(report['near_duplicate_groups'])}, "
                f"coverage_violations={len(report['coverage_violations'])}, "
                f"pairwise_coverage_violations={len(report['pairwise_coverage_violations'])}"
            )
        elif args.character:
            validate_character(character_spec_path(args.character))
            print(f"valid: {args.character}")
        else:
            parser.error("validate requires --character or --run-id")
    elif args.command == "plan":
        run_id, _, _ = make_plan(args.character, args.count, Path(args.runs), seed=args.seed)
        print(run_id)
    elif args.command == "generate":
        if not args.resume and (args.character is None or args.count is None):
            parser.error("generate requires --character and --count, unless --resume is given")
        print(generate(
            args.character,
            args.count,
            Path(args.runs),
            dry_run=args.dry_run,
            resume_run_id=args.resume,
            seed=args.seed,
        ))
    else:
        print(export_run(Path(args.runs) / args.run_id))
