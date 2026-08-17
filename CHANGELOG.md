# Changelog

## [5.1.0](https://github.com/srobroek/speckit-conductor/compare/v5.0.0...v5.1.0) (2026-08-17)


### Features

* add lean and basic profiles plus four sub-process formulas ([#11](https://github.com/srobroek/speckit-conductor/issues/11)) ([b01ef02](https://github.com/srobroek/speckit-conductor/commit/b01ef02a0904ca958a71c48274e4153872056dc7))
* dispatch per-command guidance when a SpecKit command fires ([#12](https://github.com/srobroek/speckit-conductor/issues/12)) ([45aac25](https://github.com/srobroek/speckit-conductor/commit/45aac25d70552d5c8dac93ed1c51cccfe5c50984))
* gate autonomy at runtime, and make the agent-assign chain optional ([#9](https://github.com/srobroek/speckit-conductor/issues/9)) ([b11bed2](https://github.com/srobroek/speckit-conductor/commit/b11bed206bc9e75be7cf50f45daf0db1b82ef7de))


### Bug Fixes

* SpecKit guidance now fires on the command names spec-kit installs ([#13](https://github.com/srobroek/speckit-conductor/issues/13)) ([4325daa](https://github.com/srobroek/speckit-conductor/commit/4325daa20819f47693b685bc3fd154f7d45f636f))

## [5.0.0](https://github.com/srobroek/speckit-conductor/compare/v4.0.0...v5.0.0) (2026-07-30)


### ⚠ BREAKING CHANGES

* close the defects the first end-to-end run found ([#7](https://github.com/srobroek/speckit-conductor/issues/7))

### Bug Fixes

* close the defects the first end-to-end run found ([#7](https://github.com/srobroek/speckit-conductor/issues/7)) ([e3517f3](https://github.com/srobroek/speckit-conductor/commit/e3517f38d47bdce4cda5cb1369c5ee21426871f7))

## [4.0.0](https://github.com/srobroek/speckit-conductor/compare/v3.0.0...v4.0.0) (2026-07-30)


### ⚠ BREAKING CHANGES

* drop the implement-task and research agents ([#5](https://github.com/srobroek/speckit-conductor/issues/5))

### Code Refactoring

* drop the implement-task and research agents ([#5](https://github.com/srobroek/speckit-conductor/issues/5)) ([e985503](https://github.com/srobroek/speckit-conductor/commit/e985503d30d709b9d586853df3930017a6b2b260))

## [3.0.0](https://github.com/srobroek/speckit-conductor/compare/v2.0.0...v3.0.0) (2026-07-30)


### ⚠ BREAKING CHANGES

* receive the merged SpecKit workflow from agentic-packages

### Features

* receive the merged SpecKit workflow from agentic-packages ([995fb77](https://github.com/srobroek/speckit-conductor/commit/995fb774f1d6dba79a50f109903ca64de29d1661))


### Bug Fixes

* **ci:** init a beads workspace before cooking formulas ([5a2edee](https://github.com/srobroek/speckit-conductor/commit/5a2edeeb0b289d4c1e80bfc7f9b8aa7d121c9086))

## [2.0.0](https://github.com/srobroek/speckit-conductor/compare/v1.1.0...v2.0.0) (2026-07-30)


### ⚠ BREAKING CHANGES

* ship a .apm/ directory, without which apm install rejected the package

### Bug Fixes

* ship a .apm/ directory, without which apm install rejected the package ([d879e42](https://github.com/srobroek/speckit-conductor/commit/d879e4295518c795bfe23d1dbf17f7243108ecfe))

## [1.1.0](https://github.com/srobroek/speckit-conductor/compare/v1.0.0...v1.1.0) (2026-07-30)


### Features

* **ci:** prove the release path tags without hand intervention ([ac8478f](https://github.com/srobroek/speckit-conductor/commit/ac8478fc034a679e8bae2ce765afd2fa0ea2bd64))


### Bug Fixes

* **release:** author the release PR with an App token so the tag actually ships ([c462edc](https://github.com/srobroek/speckit-conductor/commit/c462edc3ea4d94dce29480820d45395bc147f268))

## 1.0.0 (2026-07-30)


### Features

* add the release machinery and CI ([60e6db4](https://github.com/srobroek/speckit-conductor/commit/60e6db4f3d76d8213f1f3b336722ad0c2961978b))


### Bug Fixes

* **ci:** stop the uv cache failing the run before dependencies exist ([02b796f](https://github.com/srobroek/speckit-conductor/commit/02b796f77d6f5e5a7685051f0c32f46f3a85dec1))
* **release:** stamp apm.yml, which extra-files silently skipped ([4527947](https://github.com/srobroek/speckit-conductor/commit/452794748ee553447fed9d89a1b72580de7aa92f))
