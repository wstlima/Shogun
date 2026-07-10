#!/usr/bin/env node
// ═══════════════════════════════════════════════════════════════
//  SHOGUN AFM — Docker Installer (logic)
//
//  Runs inside an ephemeral Node container (see the .sh/.bat shims
//  at the repo root) so the host never needs Node installed — only
//  Docker, which is already required to run the app itself.
//
//  This script NEVER runs `docker compose` (or any docker command).
//  It only checks prerequisites (as reported from the host via the
//  shim, see below), writes gensui/.env if missing, and prints the
//  exact command for the user to review and run themselves.
// ═══════════════════════════════════════════════════════════════

import { Command } from 'commander';
import enquirer from 'enquirer';
import pc from 'picocolors';
import { existsSync, copyFileSync, readFileSync, writeFileSync } from 'node:fs';
import { randomBytes } from 'node:crypto';
import path from 'node:path';

const { prompt } = enquirer;
const REPO_ROOT = '/repo'; // bind-mounted by the shim, see Shogun-AFM-Docker-Install.sh
const DOCKER_DIR = path.join(REPO_ROOT, 'docker');
const DEFAULT_IMAGE_TAG = 'latest';

const program = new Command();
program
  .name('shogun-afm-install')
  .description('Shogun AFM — Docker Installer (Shogun + Gensui)')
  .option('--clean', 'Build the Shogun image from source (docker-compose.yml)')
  .option('--image [tag]', 'Pull a published Shogun image from Docker Hub (docker-compose.image.yml)')
  .option('--torch <variant>', '"cpu" (default), "gpu" (requires NVIDIA Container Toolkit), or "skip" (no vector memory/RAG)')
  .option('--playwright <variant>', '"on" (default) or "skip" (no Mado browser automation)')
  .option('--profile <name>', 'Enable a compose profile (e.g. server for Gensui TLS/nginx)')
  .addHelpText('after', `
The Shogun image always ships with zero Python dependencies baked in —
core, torch, and playwright each install into their own volume on
first run, whether you build from source (--clean) or pull the
published image (--image). --torch/--playwright control which
optional modules get installed; core always installs.

Examples:
  shogun-afm-install                              interactive prompt
  shogun-afm-install --clean                       build from source, all modules (CPU torch)
  shogun-afm-install --image                       pull ${DEFAULT_IMAGE_TAG}, all modules
  shogun-afm-install --image=1.2.0 --profile server
  shogun-afm-install --clean --torch=gpu           CUDA torch (needs NVIDIA Container Toolkit)
  shogun-afm-install --image --torch=skip --playwright=skip   core only — no RAG, no browser automation
`);
program.parse();
const opts = program.opts();

function banner() {
  console.log('');
  console.log(pc.yellow('  ╔══════════════════════════════════════════════════════════╗'));
  console.log(pc.yellow('  ║                                                          ║'));
  console.log(pc.yellow('  ║     SHOGUN AFM — Docker Installer                        ║'));
  console.log(pc.yellow('  ║     Shogun (Tenshu) + Gensui (Fleet Management)          ║'));
  console.log(pc.yellow('  ╚══════════════════════════════════════════════════════════╝'));
  console.log('');
}

function section(title) {
  console.log(pc.yellow('  ══════════════════════════════════════════════════'));
  console.log(pc.yellow(`  ${title}`));
  console.log(pc.yellow('  ══════════════════════════════════════════════════'));
  console.log('');
}

async function main() {
  banner();

  if (!existsSync(path.join(DOCKER_DIR, 'docker-compose.yml'))) {
    console.log(pc.red(`  Could not find docker/docker-compose.yml under ${REPO_ROOT}.`));
    console.log(pc.gray('  This script expects the repo to be bind-mounted at /repo — see the shim script.'));
    process.exit(1);
  }

  // ── [1/4] Install mode ──────────────────────────────────────
  section('[1/4] Install mode');

  if (opts.clean && opts.image !== undefined) {
    console.log(pc.red('  --clean and --image are mutually exclusive.'));
    process.exit(1);
  }

  let mode = opts.clean ? 'clean' : opts.image !== undefined ? 'image' : null;

  if (!mode) {
    const { chosenMode } = await prompt({
      type: 'select',
      name: 'chosenMode',
      message: 'Choose install mode',
      choices: [
        { name: 'clean', message: 'Build the Shogun image from source' },
        { name: 'image', message: 'Pull a published Shogun image from Docker Hub (agenciasupermix/shogun-afm)' },
      ],
    });
    mode = chosenMode;
  }

  let imageTag = null;
  let composeFile;

  if (mode === 'image') {
    composeFile = 'docker-compose.image.yml';
    if (typeof opts.image === 'string') {
      imageTag = opts.image;
    } else {
      const { tagChoice } = await prompt({
        type: 'select',
        name: 'tagChoice',
        message: 'Which image tag?',
        choices: [
          { name: 'latest', message: `latest — most recently published image` },
          { name: 'specific', message: 'Specific version (e.g. 1.0.0.1)' },
        ],
      });
      if (tagChoice === 'specific') {
        const { tag } = await prompt({
          type: 'input',
          name: 'tag',
          message: 'Enter version tag',
          initial: DEFAULT_IMAGE_TAG,
        });
        imageTag = tag || DEFAULT_IMAGE_TAG;
      } else {
        imageTag = DEFAULT_IMAGE_TAG;
      }
    }
    console.log(pc.green(`  Using published image: ${pc.bold(imageTag)}`));
  } else {
    composeFile = 'docker-compose.yml';
    console.log(pc.green('  Building the Shogun image from source.'));
  }
  console.log('');

  // ── [2/4] Optional modules ──────────────────────────────────
  section('[2/4] Optional modules (torch, playwright)');
  console.log(pc.gray('  The Shogun image has no Python dependencies baked in. core always'));
  console.log(pc.gray('  installs (required); torch and playwright are independently optional'));
  console.log(pc.gray('  and install into their own volume on first startup.'));
  console.log('');

  let torchVariant;
  if (opts.torch === 'cpu' || opts.torch === 'gpu' || opts.torch === 'skip') {
    torchVariant = opts.torch;
  } else {
    const { variant } = await prompt({
      type: 'select',
      name: 'variant',
      message: 'Torch module (vector memory / RAG)',
      choices: [
        { name: 'cpu', message: 'CPU-only (default — no GPU/CUDA required)' },
        { name: 'gpu', message: 'GPU (CUDA) — requires NVIDIA Container Toolkit on the host' },
        { name: 'skip', message: 'Skip — no vector memory/RAG' },
      ],
    });
    torchVariant = variant;
  }

  let playwrightVariant;
  if (opts.playwright === 'on' || opts.playwright === 'skip') {
    playwrightVariant = opts.playwright;
  } else {
    const { variant } = await prompt({
      type: 'select',
      name: 'variant',
      message: 'Playwright module (Mado browser automation)',
      choices: [
        { name: 'on', message: 'Install — downloads the Chromium browser (~120MB)' },
        { name: 'skip', message: 'Skip — no browser automation' },
      ],
    });
    playwrightVariant = variant;
  }

  console.log(pc.green(`  torch: ${pc.bold(torchVariant)}, playwright: ${pc.bold(playwrightVariant)}`));
  console.log('');

  let profileServer = opts.profile === 'server';
  if (!profileServer) {
    const { enableTls } = await prompt({
      type: 'confirm',
      name: 'enableTls',
      message: 'Enable Nginx/TLS reverse proxy for Gensui?',
      initial: false,
    });
    profileServer = enableTls;
  }
  console.log('');

  // ── [3/4] Gensui environment ────────────────────────────────
  section('[3/4] Configuring Gensui environment');

  const gensuiEnvPath = path.join(REPO_ROOT, 'gensui', '.env');
  const gensuiEnvExamplePath = path.join(REPO_ROOT, 'gensui', '.env.example');

  if (!existsSync(gensuiEnvPath)) {
    copyFileSync(gensuiEnvExamplePath, gensuiEnvPath);
    const jwtSecret = randomBytes(48).toString('base64').replace(/[+/=]/g, '');
    const contents = readFileSync(gensuiEnvPath, 'utf8').replace(
      'change-me-to-a-random-64-char-string',
      jwtSecret
    );
    writeFileSync(gensuiEnvPath, contents);
    console.log(pc.green('  gensui/.env created with a random JWT secret.'));
  } else {
    console.log(pc.green('  gensui/.env already exists — keeping existing config.'));
  }
  console.log('');

  // ── [4/4] Ready to launch ───────────────────────────────────
  section('[4/4] Ready to launch');

  const profileFlag = profileServer ? ' --profile server' : '';
  const envPrefix = `SHOGUN_TORCH=${torchVariant} SHOGUN_PLAYWRIGHT=${playwrightVariant}`;
  const runCmd =
    mode === 'image'
      ? `${envPrefix} SHOGUN_IMAGE_TAG=${imageTag} docker compose -f ${composeFile}${profileFlag} up -d`
      : `${envPrefix} docker compose -f ${composeFile}${profileFlag} up -d --build`;

  console.log(pc.gray('  This script does not start anything automatically.'));
  console.log(pc.gray('  Review the command below, then run it yourself from docker/:'));
  console.log('');
  console.log(`      ${pc.bold('cd docker')}`);
  console.log(`      ${pc.bold(runCmd)}`);
  console.log('');
  if (profileServer) {
    console.log(pc.gray('  TLS/nginx profile enabled — place certs in gensui/certs/gensui.crt'));
    console.log(pc.gray('  and gensui/certs/gensui.key before running the command above.'));
    console.log('');
  }
  if (torchVariant === 'gpu') {
    console.log(pc.gray('  GPU mode requires the NVIDIA Container Toolkit on the host, and the'));
    console.log(pc.gray('  commented-out deploy.resources block in the compose file (shogun'));
    console.log(pc.gray('  service) uncommented — see docs/RUNBOOK.md.'));
    console.log('');
  }
  if (torchVariant === 'skip' || playwrightVariant === 'skip') {
    const skipped = [torchVariant === 'skip' && 'vector memory/RAG', playwrightVariant === 'skip' && 'Mado browser automation']
      .filter(Boolean)
      .join(' and ');
    console.log(pc.gray(`  Note: ${skipped} will be unavailable — the modules were skipped.`));
    console.log('');
  }
  console.log(pc.green('  Shogun will be available at http://127.0.0.1:8000'));
  console.log(pc.green('  Gensui will be available at http://127.0.0.1:8787'));
  console.log(pc.green('  (default admin: admin@gensui.local / changeme — change immediately)'));
  console.log('');
  console.log(pc.gray('  Full operational guide: docs/RUNBOOK.md'));
  console.log('');
}

main().catch((err) => {
  console.error(pc.red(`  Error: ${err.message}`));
  process.exit(1);
});
