#!/usr/bin/env bash
# Pull the community-maintained RealWorld application as the external,
# independently-developed evaluation subject (paper §4.1).
#
# We do not vendor its source into this monorepo to respect the upstream
# community's licensing and avoid stale forks.

set -euo pipefail
cd "$(dirname "$0")/.."

if [ -d "apps/realworld/.git" ]; then
  echo "RealWorld already present — pulling latest…"
  (cd apps/realworld && git pull --ff-only)
else
  echo "Cloning RealWorld…"
  git clone --depth=1 https://github.com/gothinkster/realworld apps/realworld
fi

cat <<EOF

RealWorld checked out under apps/realworld.
Follow the upstream README to bring up a backend + frontend pair on
http://localhost:4100 (frontend) / http://localhost:3000 (one of the
reference backends). The Doc2Test UAT for RealWorld lives in
uats/realworld_reg_crud.md.
EOF
