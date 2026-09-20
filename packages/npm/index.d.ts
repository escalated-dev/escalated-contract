export interface PageProps {
  /** Props the component reads. */
  props: string[];
  /** Props it cannot render without. */
  required: string[];
}

/** Every page name the shared frontend resolves. */
export function pages(): string[];

/** The props a page reads. Throws when the name is not in the manifest. */
export function propsFor(page: string): PageProps;

/** True when the shared frontend has a component for this name. */
export function rendersPage(page: string): boolean;

/** The @escalated-dev/escalated release this manifest came from. */
export function frontendVersion(): string;

/** Absolute path to a conformance fixture directory, for a runner to walk. */
export function conformancePath(area?: string): string;

/** Absolute path to the contract directory inside this package. */
export const CONTRACT_DIR: string;
