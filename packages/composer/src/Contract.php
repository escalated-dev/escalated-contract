<?php

declare(strict_types=1);

namespace Escalated\Contract;

use JsonException;
use RuntimeException;

/**
 * Reads the published contract.
 *
 * The point of this class is that a port never keeps its own copy of the
 * manifest. Before this package existed, each of the eleven ports vendored
 * escalated-pages.json into its own test fixtures and refreshed it by hand.
 * Two of them drifted and their parity tests stayed green anyway, because each
 * port was comparing itself against its own stale copy.
 *
 * Read from here instead, and a `composer update` is what surfaces the drift.
 */
final class Contract
{
    /** @var array{version: string, pages: list<string>, props: array<string, array{props: list<string>, required: list<string>}>}|null */
    private static ?array $pages = null;

    /**
     * Every page name the shared frontend resolves.
     *
     * A name a backend renders that is not in here is not an error at runtime.
     * Inertia returns 200, the resolver returns undefined, and the panel comes
     * up blank, which reads as a permissions problem or an empty dataset.
     *
     * @return list<string>
     */
    public static function pages(): array
    {
        return self::manifest()['pages'];
    }

    /**
     * The props a page reads, and which of them it cannot render without.
     *
     * @return array{props: list<string>, required: list<string>}
     */
    public static function propsFor(string $page): array
    {
        $props = self::manifest()['props'];

        if (! isset($props[$page])) {
            throw new RuntimeException(sprintf(
                'No props recorded for page "%s". Either the name is wrong, or the frontend has not released it yet.',
                $page
            ));
        }

        return $props[$page];
    }

    /**
     * True when the shared frontend has a component for this name.
     */
    public static function rendersPage(string $page): bool
    {
        return in_array($page, self::pages(), true);
    }

    /**
     * The @escalated-dev/escalated release this manifest came from.
     */
    public static function frontendVersion(): string
    {
        return self::manifest()['version'];
    }

    /**
     * Absolute path to a conformance fixture directory, for a runner to walk.
     */
    public static function conformancePath(string $area = ''): string
    {
        $path = self::contractDir().'/conformance';

        return $area === '' ? $path : $path.'/'.$area;
    }

    /**
     * @return array{version: string, pages: list<string>, props: array<string, array{props: list<string>, required: list<string>}>}
     */
    private static function manifest(): array
    {
        if (self::$pages !== null) {
            return self::$pages;
        }

        $path = self::contractDir().'/pages.json';
        $raw = @file_get_contents($path);

        if ($raw === false) {
            throw new RuntimeException('Cannot read the page manifest at '.$path);
        }

        try {
            /** @var array{version: string, pages: list<string>, props: array<string, array{props: list<string>, required: list<string>}>} $decoded */
            $decoded = json_decode($raw, true, 512, JSON_THROW_ON_ERROR);
        } catch (JsonException $e) {
            throw new RuntimeException('The page manifest at '.$path.' is not valid JSON: '.$e->getMessage(), 0, $e);
        }

        return self::$pages = $decoded;
    }

    private static function contractDir(): string
    {
        return dirname(__DIR__).'/contract';
    }
}
