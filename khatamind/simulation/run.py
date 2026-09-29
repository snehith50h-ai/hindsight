import argparse
from datetime import datetime, timezone
from simulation.world import SimWorld
from simulation.archetypes import CHRONIC_PROMISER, DEAL_SEEKER, SILENT_PAYER, LOYAL_FAST_PAYER

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--customers", type=int, default=30)
    parser.add_argument("--days", type=int, default=90)
    parser.add_argument("--memory", choices=["on", "off"], default="on")
    args = parser.parse_args()

    archetypes = [CHRONIC_PROMISER, DEAL_SEEKER, SILENT_PAYER, LOYAL_FAST_PAYER]
    world = SimWorld(args.seed, args.customers, args.days, archetypes, datetime(2024, 1, 1, tzinfo=timezone.utc))

    print(f"Running simulation with {args.customers} customers for {args.days} days (seed={args.seed}, memory={args.memory})...")
    events = world.run()

    print(f"Simulation completed. Generated {len(events)} events.")

if __name__ == "__main__":
    main()
