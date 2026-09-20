<?php

declare(strict_types=1);

namespace Escalated\Contract\Tests;

use Escalated\Contract\Contract;
use PHPUnit\Framework\TestCase;

/**
 * Reference runner for a PHP port. Copy this into the port, point $sourceRoot
 * at its source directory, and delete the port's vendored
 * tests/Fixtures/escalated-pages.json.
 *
 * What this catches, and why a route test cannot:
 *
 * Inertia resolving a page name to nothing is not an error. The response is a
 * 200, the resolver returns undefined, Vue renders nothing, and the panel comes
 * up blank, which reads as a permissions problem or an empty dataset. Four
 * report screens in escalated-laravel shipped that way while route tests
 * asserting a 200 said they were fine.
 *
 * The port's own tests cannot see it alone: a controller test asserts a status,
 * and the frontend never hears the name. This is the comparison, against the
 * manifest the contract package publishes rather than a copy in the repo.
 */
final class PageContractTest extends TestCase
{
    /**
     * Where this port's source lives. Change this line and nothing else.
     */
    private string $sourceRoot = __DIR__.'/../../src';

    /**
     * Names rendered anywhere in the port, mapped to the files that render
     * them, so a failure can name the file and not only the string.
     *
     * @return array<string, list<string>>
     */
    private function renderedPages(): array
    {
        $found = [];

        $files = new \RecursiveIteratorIterator(
            new \RecursiveDirectoryIterator($this->sourceRoot, \FilesystemIterator::SKIP_DOTS)
        );

        foreach ($files as $file) {
            if ($file->getExtension() !== 'php') {
                continue;
            }

            $source = (string) file_get_contents($file->getPathname());

            if (! preg_match_all("/'(Escalated\/[A-Za-z0-9\/_]+)'/", $source, $matches)) {
                continue;
            }

            foreach ($matches[1] as $page) {
                $found[$page][] = basename($file->getPathname());
            }
        }

        return $found;
    }

    public function test_every_page_this_port_renders_has_a_component(): void
    {
        $shipped = Contract::pages();
        $blank = [];

        foreach ($this->renderedPages() as $page => $files) {
            if (! in_array($page, $shipped, true)) {
                $blank[$page] = array_unique($files);
            }
        }

        if ($blank !== []) {
            $lines = [
                'These page names have no component in the frontend, so they render a blank panel:',
                '',
            ];
            foreach ($blank as $page => $files) {
                $lines[] = sprintf('  %s  (%s)', $page, implode(', ', $files));
            }
            $lines[] = '';
            $lines[] = 'Adding a screen goes: component into the frontend, frontend release,';
            $lines[] = 'contract release, bump the contract here, then render the name.';
            $lines[] = 'In that order, or it ships blank.';

            $this->fail(implode("\n", $lines));
        }

        $this->addToAssertionCount(1);
    }

    public function test_the_manifest_is_readable(): void
    {
        $this->assertNotEmpty(Contract::pages());
        $this->assertMatchesRegularExpression('/^\d+\.\d+\.\d+$/', Contract::frontendVersion());
    }

    /**
     * Opt in per port. A port that has not finished a screen will fail this
     * until it sends every required prop, which is the point.
     */
    public function test_required_props_are_known_for_every_rendered_page(): void
    {
        $shipped = Contract::pages();

        foreach (array_keys($this->renderedPages()) as $page) {
            if (! in_array($page, $shipped, true)) {
                continue; // already reported by the test above
            }

            $props = Contract::propsFor($page);
            $this->assertIsArray($props['props'], $page.' has no props entry');
            $this->assertIsArray($props['required'], $page.' has no required list');
        }

        $this->addToAssertionCount(1);
    }
}
