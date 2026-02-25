from __future__ import annotations

import asyncio
import argparse
import logging
import sys
from pathlib import Path

from .assembler.sdk_layout import assemble_sdk
from .config import PLATFORM_CONFIGS
from .crawler.cache import CacheDB
from .crawler.client import APIClient
from .crawler.framework import crawl_framework_symbols
from .crawler.symbol import parse_symbol
from .crawler.technologies import fetch_technologies, filter_frameworks
from .models.availability import is_available
from .models.symbol import Symbol

logger = logging.getLogger(__name__)


async def run(args: argparse.Namespace) -> None:
    # Configure logging
    level = logging.WARNING
    if args.verbose >= 1:
        level = logging.INFO
    if args.verbose >= 2:
        level = logging.DEBUG

    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )

    output_dir = Path(args.output)
    cache_dir = Path(args.cache_dir)

    cache = CacheDB(cache_dir)
    logger.info("Cache: %d entries", cache.size())

    async with APIClient(
        concurrency=args.concurrency,
        rate_limit=args.rate_limit,
        cache=cache,
    ) as client:
        # Phase 1: Discover frameworks
        print("Discovering frameworks...", file=sys.stderr)
        all_frameworks = await fetch_technologies(client)

        frameworks = filter_frameworks(
            all_frameworks,
            include=args.frameworks if not args.all_frameworks else None,
            exclude=args.exclude_frameworks,
        )

        if not frameworks:
            print("No frameworks matched the filter criteria.", file=sys.stderr)
            sys.exit(1)

        print(f"Processing {len(frameworks)} frameworks...", file=sys.stderr)

        # Phase 2: Crawl symbols for each framework
        framework_symbols: dict[str, list[Symbol]] = {}

        for i, fw in enumerate(frameworks, 1):
            mod_name = fw.module_name
            print(
                f"[{i}/{len(frameworks)}] Crawling {fw.name} ({mod_name})...",
                file=sys.stderr,
            )

            symbol_paths = await crawl_framework_symbols(client, fw)
            logger.info(
                "%s: %d symbol paths discovered", mod_name, len(symbol_paths)
            )

            # Phase 3: Parse each symbol
            symbols: list[Symbol] = []
            batch_size = 50

            for batch_start in range(0, len(symbol_paths), batch_size):
                batch = symbol_paths[batch_start:batch_start + batch_size]
                tasks = [
                    parse_symbol(client, path, mod_name)
                    for path in batch
                ]
                results = await asyncio.gather(*tasks, return_exceptions=True)

                for result in results:
                    if isinstance(result, Exception):
                        logger.warning("Error parsing symbol: %s", result)
                        continue
                    if result is not None:
                        symbols.append(result)

            if symbols:
                framework_symbols[mod_name] = symbols
                logger.info(
                    "%s: %d symbols parsed", mod_name, len(symbols)
                )

        print(
            f"Parsed {sum(len(s) for s in framework_symbols.values())} "
            f"total symbols across {len(framework_symbols)} frameworks",
            file=sys.stderr,
        )

        # Phase 4: Filter by platform availability and generate SDKs
        for platform_key in args.platforms:
            cfg = PLATFORM_CONFIGS[platform_key]
            print(
                f"Generating SDK for {cfg.sdk_prefix} {args.sdk_version}...",
                file=sys.stderr,
            )

            # Filter symbols by availability
            platform_frameworks: dict[str, list[Symbol]] = {}
            for fw_name, symbols in framework_symbols.items():
                available = [
                    sym for sym in symbols
                    if is_available(sym, cfg.name, args.sdk_version)
                ]
                if available:
                    platform_frameworks[fw_name] = available

            # Assemble SDK
            sdk_path = assemble_sdk(
                output_dir=output_dir,
                platform_key=platform_key,
                sdk_version=args.sdk_version,
                frameworks=platform_frameworks,
                include_swift=args.include_swift,
            )

            print(f"SDK generated at: {sdk_path}", file=sys.stderr)

        # Print stats
        stats = client.stats
        print(
            f"\nDone. API requests: {stats['requests']}, "
            f"cache hits: {stats['cache_hits']}, "
            f"errors: {stats['errors']}",
            file=sys.stderr,
        )

    cache.close()
