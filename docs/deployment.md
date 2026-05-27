# ArtBase — Deployment Guide

*CollectiveAccess Providence + Pawtucket2 on Docker.*

> **Status:** Infrastructure not yet provisioned. This document describes the target
> setup once Docker is available and the upstream repos have been cloned.

---

## Prerequisites

- Docker Desktop (macOS) — download from [docker.com](https://www.docker.com/products/docker-desktop/)
- Git
- VS Code with PHP Intelephense and Docker extensions

---

## Step 1 — Clone upstream repos

```bash
cd /path/to/artbase/

# Providence (admin / collections management)
git clone https://github.com/collectiveaccess/providence.git upstream

# Pawtucket2 (public frontend)
git clone https://github.com/collectiveaccess/pawtucket2.git pawtucket
```

**Before proceeding,** check the README in each repo for the current PHP and MySQL
version requirements. These change between releases. Do not assume.

---

## Step 2 — Configure environment

```bash
cp docker-compose.yml.example docker-compose.yml
# Edit docker-compose.yml if needed (ports, volume paths)
```

The compose file defines three services:
- `php` — PHP-FPM 8.2 with Providence + Pawtucket2
- `db` — MySQL 8.0
- `nginx` — Nginx with two vhosts: admin (`:8080`) and public (`:8081`)

---

## Step 3 — Start containers

```bash
docker compose up -d
docker compose logs -f   # watch for errors
```

On first boot, MySQL initialises the database. Allow ~30 seconds before proceeding.

---

## Step 4 — Run the Providence installer

Navigate to `http://localhost:8080` in a browser.

For initial environment verification, select the `dublin_core` profile. Once the
containers are confirmed working:

1. Drop the test database:
   ```bash
   docker compose exec db mysql -uroot -proot -e "DROP DATABASE IF EXISTS providence; CREATE DATABASE providence CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
   ```
2. Copy our installation profile:
   ```bash
   cp profile/artbase.xml upstream/install/profiles/xml/artbase.xml
   ```
3. Re-run the installer at `http://localhost:8080` and select the `artbase` profile.

---

## Step 5 — Deploy our theme

```bash
# Symlink our theme into Pawtucket2
ln -s $(pwd)/theme pawtucket/themes/artbase

# Set the active theme in Pawtucket2 config
# Edit pawtucket/setup.php:
#   $PAWTUCKET_THEME = 'artbase';
```

---

## Useful commands

```bash
# Start / stop
docker compose up -d
docker compose down

# Shell into PHP container
docker compose exec php bash

# Tail logs
docker compose logs -f

# MySQL shell
docker compose exec db mysql -uroot -proot providence

# Run a Providence import script
docker compose exec php php support/bin/caUtils import-data \
  --format=CSV \
  --source=scripts/sample_data/artists_sample.csv \
  --mapping=scripts/import_mappings/artists.xml
```

---

## Port mapping

| Service | URL |
|---|---|
| Providence admin | http://localhost:8080 |
| Pawtucket2 public | http://localhost:8081 |
| MySQL | localhost:3306 (host access) |

---

## Troubleshooting

**`502 Bad Gateway`** — PHP-FPM container hasn't started yet. Wait 10 seconds and retry.

**`Access denied for user 'root'`** — MySQL hasn't finished initialising. Check `docker compose logs db`.

**Profile XML validation errors** — Validate `profile/artbase.xml` against
`upstream/install/profiles/xml/profile.xsd` before running the installer.
