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
  .option('--clean', 'Build images from source (docker-compose.yml)')
  .option('--image [tag]', 'Use a published image from Docker Hub (docker-compose.image.yml)')
  .option('--slim', 'Build a slim Shogun image; Python deps (incl. torch) install into a shared volume on first run (docker-compose.slim.yml)')
  .option('--torch <variant>', 'With --slim: "cpu" (default, no GPU/CUDA required) or "gpu" (requires NVIDIA Container Toolkit)')
  .option('--profile <name>', 'Enable a compose profile (e.g. server for Gensui TLS/nginx)')
  .addHelpText('after', `
Examples:
  shogun-afm-install                              interactive prompt
  shogun-afm-install --clean                       build from source
  shogun-afm-install --image                       pull ${DEFAULT_IMAGE_TAG}
  shogun-afm-install --image=1.2.0 --profile server
  shogun-afm-install --slim --torch=cpu            smallest Shogun image, torch installed on first run
  shogun-afm-install --slim --torch=gpu            same, but with CUDA torch (needs NVIDIA Container Toolkit)
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

  // ── [1/3] Install mode ──────────────────────────────────────
  section('[1/3] Install mode');

  const modeFlags = [opts.clean, opts.image !== undefined, opts.slim].filter(Boolean).length;
  if (modeFlags > 1) {
    console.log(pc.red('  --clean, --image, and --slim are mutually exclusive.'));
    process.exit(1);
  }

  let mode = opts.clean ? 'clean' : opts.image !== undefined ? 'image' : opts.slim ? 'slim' : null;

  if (!mode) {
    const { chosenMode } = await prompt({
      type: 'select',
      name: 'chosenMode',
      message: 'Choose install mode',
      choices: [
        { name: 'clean', message: 'Clean install — build full images from source' },
        { name: 'image', message: 'Published image — pull agenciasupermix/{shogun-afm,gensui-afm} from Docker Hub' },
        { name: 'slim', message: 'Slim build — smallest Shogun image, torch installs into a volume on first run' },
      ],
    });
    mode = chosenMode;
  }

  let imageTag = null;
  let torchVariant = null;
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
  } else if (mode === 'slim') {
    composeFile = 'docker-compose.slim.yml';
    if (opts.torch === 'cpu' || opts.torch === 'gpu') {
      torchVariant = opts.torch;
    } else {
      const { variant } = await prompt({
        type: 'select',
        name: 'variant',
        message: 'Torch variant for the shared venv',
        choices: [
          { name: 'cpu', message: 'CPU-only (default — no GPU/CUDA required)' },
          { name: 'gpu', message: 'GPU (CUDA) — requires NVIDIA Container Toolkit on the host' },
        ],
      });
      torchVariant = variant;
    }
    console.log(pc.green(`  Slim build, torch variant: ${pc.bold(torchVariant)}`));
    console.log(pc.gray('  Note: first startup installs Python deps into a volume — this takes'));
    console.log(pc.gray(`  as long as pip install normally does (${torchVariant === 'gpu' ? '~5GB download for CUDA torch' : '~800MB for CPU torch'}).`));
  } else {
    composeFile = 'docker-compose.yml';
    console.log(pc.green('  Building images from source.'));
  }

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

  // ── [2/3] Gensui environment ────────────────────────────────
  section('[2/3] Configuring Gensui environment');

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

  // ── [3/3] Ready to launch ───────────────────────────────────
  section('[3/3] Ready to launch');

  const profileFlag = profileServer ? ' --profile server' : '';
  let runCmd;
  if (mode === 'image') {
    runCmd = `SHOGUN_IMAGE_TAG=${imageTag} docker compose -f ${composeFile}${profileFlag} up -d`;
  } else if (mode === 'slim') {
    runCmd = `TORCH_VARIANT=${torchVariant} docker compose -f ${composeFile}${profileFlag} up -d --build`;
  } else {
    runCmd = `docker compose -f ${composeFile}${profileFlag} up -d --build`;
  }

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
  if (mode === 'slim' && torchVariant === 'gpu') {
    console.log(pc.gray('  GPU mode requires the NVIDIA Container Toolkit on the host, and the'));
    console.log(pc.gray('  commented-out deploy.resources block in docker-compose.slim.yml'));
    console.log(pc.gray('  (shogun service) uncommented — see docs/RUNBOOK.md.'));
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
