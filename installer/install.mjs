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
  .option('--profile <name>', 'Enable a compose profile (e.g. server for Gensui TLS/nginx)')
  .addHelpText('after', `
Examples:
  shogun-afm-install                              interactive prompt
  shogun-afm-install --clean                       build from source
  shogun-afm-install --image                       pull ${DEFAULT_IMAGE_TAG}
  shogun-afm-install --image=1.2.0 --profile server
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

  let mode = opts.clean ? 'clean' : opts.image !== undefined ? 'image' : null;

  if (mode === 'clean' && opts.image !== undefined) {
    console.log(pc.red('  --clean and --image are mutually exclusive.'));
    process.exit(1);
  }

  if (!mode) {
    const { chosenMode } = await prompt({
      type: 'select',
      name: 'chosenMode',
      message: 'Choose install mode',
      choices: [
        { name: 'clean', message: 'Clean install — build images from source' },
        { name: 'image', message: 'Published image — pull agenciasupermix/{shogun-afm,gensui-afm} from Docker Hub' },
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
  const runCmd =
    mode === 'image'
      ? `SHOGUN_IMAGE_TAG=${imageTag} docker compose -f ${composeFile}${profileFlag} up -d`
      : `docker compose -f ${composeFile}${profileFlag} up -d --build`;

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
